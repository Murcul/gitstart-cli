# Adapted from https://github.com/Aider-AI/aider/blob/c7e8d297a470f02a685379a024faa817a5ba9c42/aider/repomap.py
import hashlib
import math
import os
import subprocess
import sys
import time
import warnings
from collections import Counter, defaultdict, namedtuple
from pathlib import Path

import diskcache
import networkx as nx
import tiktoken
from grep_ast import TreeContext, filename_to_lang
from grep_ast.parsers import PARSERS
from loguru import logger
from pygments.lexers import guess_lexer_for_filename
from pygments.token import Token

from gsai.security import safe_construct_path
from gsai.special import filter_important_files
from gsai.utils import get_files_excluding_gitignore

# tree_sitter is throwing a FutureWarning
warnings.simplefilter("ignore", category=FutureWarning)
from grep_ast.tsl import get_language, get_parser  # noqa: E402

Tag = namedtuple("Tag", ["rel_fname", "fname", "line", "name", "kind"])

# Module-level cache object to avoid recreation overhead
_disk_cache = None


def get_disk_cache():
    """Get or create the module-level disk cache object."""
    global _disk_cache
    if _disk_cache is None:
        from gsai.config import cli_settings, config_manager

        config_manager.ensure_cache_dir()
        cache_size_bytes = cli_settings.max_cache_size_mb * 1024 * 1024
        _disk_cache = diskcache.Cache(
            str(config_manager.cache_dir), size_limit=cache_size_bytes, tag_index=True
        )
    return _disk_cache


def open_file(file_path: str) -> str:
    """
    Opens and reads the content of a file from a specified repository path.

    Args:
        file_path (str): The absolute path to the file from the repository root.

    Returns:
        str: The content of the file if found, "File not found" if the file doesn't exist.
    """
    try:
        with open(file_path) as f:
            return f.read()
    except FileNotFoundError:
        return "File not found"
    except UnicodeDecodeError as error:
        # fallback to a lossy but safe read
        logger.warning(f"Decode Error Ignored: {file_path} - {error}")
        with open(file_path, encoding="utf-8", errors="replace") as f:
            return f.read()


class RepoMap:
    warned_files: set[str] = set()

    def __init__(
        self,
        map_tokens=10000,
        root=None,
        main_model=None,
        repo_content_prefix=None,
        verbose=False,
        max_context_window=None,
        map_mul_no_files=8,
        refresh="auto",
    ):
        self.verbose = verbose
        self.refresh = refresh

        if not root:
            root = os.getcwd()
        self.root = root

        self.cache_threshold = 0.95

        self.max_map_tokens = map_tokens
        self.map_mul_no_files = map_mul_no_files
        self.max_context_window = max_context_window

        self.repo_content_prefix = repo_content_prefix

        self.main_model = main_model

        self.tree_cache = {}
        self.tree_context_cache = {}
        self.map_cache = {}
        self.map_processing_time = 0
        self.last_map = None

        if self.verbose:
            logger.info(
                f"RepoMap initialized with map_mul_no_files: {self.map_mul_no_files}"
            )

    def token_count(self, text):
        # Handle non-string inputs
        if not isinstance(text, str):
            if text is None:
                return 0
            text = str(text)

        len_text = len(text)
        encoding = tiktoken.get_encoding("o200k_base")
        if len_text < 200:
            return len(encoding.encode(text))

        lines = text.splitlines(keepends=True)
        num_lines = len(lines)
        step = num_lines // 100 or 1
        lines = lines[::step]
        sample_text = "".join(lines)
        sample_tokens = len(encoding.encode(sample_text))
        est_tokens = sample_tokens / len(sample_text) * len_text
        return est_tokens

    def get_repo_map(
        self,
        chat_files,
        other_files,
        mentioned_fnames=None,
        mentioned_idents=None,
        force_refresh=False,
    ) -> str:
        if self.max_map_tokens <= 0:
            return ""
        if not other_files:
            return ""
        if not mentioned_fnames:
            mentioned_fnames = set()
        if not mentioned_idents:
            mentioned_idents = set()

        max_map_tokens = self.max_map_tokens

        # With no files in the chat, give a bigger view of the entire repo
        padding = 4096
        if max_map_tokens and self.max_context_window:
            target = min(
                int(max_map_tokens * self.map_mul_no_files),
                self.max_context_window - padding,
            )
        else:
            target = 0
        if not chat_files and self.max_context_window and target > 0:
            max_map_tokens = target

        try:
            files_listing = self.get_ranked_tags_map(
                chat_files,
                other_files,
                max_map_tokens,
                mentioned_fnames,
                mentioned_idents,
                force_refresh,
            )
        except RecursionError:
            logger.info("Disabling repo map, git repo too large?")
            self.max_map_tokens = 0
            return ""

        if not files_listing:
            return ""

        if self.verbose:
            num_tokens = self.token_count(files_listing)
            logger.info(f"Repo-map: {num_tokens / 1024:.1f} k-tokens")

        if chat_files:
            other = "other "
        else:
            other = ""

        if self.repo_content_prefix:
            repo_content = self.repo_content_prefix.format(other=other)
        else:
            repo_content = ""

        repo_content += files_listing

        return str(repo_content)

    def get_rel_fname(self, fname):
        try:
            return os.path.relpath(fname, self.root)
        except ValueError:
            # Issue #1288: ValueError: path is on mount 'C:', start on mount 'D:'
            # Just return the full fname.
            return fname

    def get_mtime(self, fname):
        try:
            return os.path.getmtime(fname)
        except FileNotFoundError:
            logger.info(f"File not found error: {fname}")

    def get_tags(self, fname, rel_fname):
        # Check if the file is in the cache and if the modification time has not changed
        file_mtime = self.get_mtime(fname)
        if file_mtime is None:
            return []

        # miss!
        data = list(self.get_tags_raw(fname, rel_fname))
        return data

    def get_tags_raw(self, fname, rel_fname):
        lang = filename_to_lang(fname)
        if not lang:
            return

        try:
            language = get_language(lang)
            parser = get_parser(lang)
        except Exception as err:
            logger.info(f"Skipping file {fname}: {err}")
            return

        query_scm = get_scm_fname(lang)
        if not query_scm:
            return
        query_scm = open_file(query_scm)

        code = open_file(fname)
        if not code:
            return
        tree = parser.parse(bytes(code, "utf-8"))

        # Run the tags queries
        query = language.query(query_scm)
        captures = query.captures(tree.root_node)

        saw = set()
        all_nodes = []
        for tag, nodes in captures.items():
            all_nodes += [(node, tag) for node in nodes]

        for node, tag in all_nodes:
            if tag.startswith("name.definition."):
                kind = "def"
            elif tag.startswith("name.reference."):
                kind = "ref"
            else:
                continue

            saw.add(kind)

            result = Tag(
                rel_fname=rel_fname,
                fname=fname,
                name=node.text.decode("utf-8"),
                kind=kind,
                line=node.start_point[0],
            )

            yield result

        if "ref" in saw:
            return
        if "def" not in saw:
            return

        # We saw defs, without any refs
        # Some tags files only provide defs (cpp, for example)
        # Use pygments to backfill refs
        try:
            lexer = guess_lexer_for_filename(fname, code)
        except Exception:  # On Windows, bad ref to time.clock which is deprecated?
            logger.info(f"Error lexing {fname}")
            return

        tokens = list(lexer.get_tokens(code))
        tokens = [token[1] for token in tokens if token[0] in Token.Name]
        for token in tokens:
            yield Tag(
                rel_fname=rel_fname,
                fname=fname,
                name=token,
                kind="ref",
                line=-1,
            )

    def get_ranked_tags(
        self,
        chat_fnames,
        other_fnames,
        mentioned_fnames,
        mentioned_idents,
    ):
        defines = defaultdict(set)
        references = defaultdict(list)
        definitions = defaultdict(set)

        personalization = dict()

        fnames = set(chat_fnames).union(set(other_fnames))
        chat_rel_fnames = set()

        fnames = sorted(fnames)

        # Default personalization for unspecified files is 1/num_nodes
        # https://networkx.org/documentation/stable/_modules/networkx/algorithms/link_analysis/pagerank_alg.html#pagerank
        personalize = 100 / len(fnames)

        for fname in fnames:
            if self.verbose:
                logger.info(f"Processing {fname}")
            try:
                file_ok = Path(fname).is_file()
            except OSError:
                file_ok = False

            if not file_ok:
                if fname not in self.warned_files:
                    logger.info(f"Repo-map can't include {fname}")
                    logger.info(
                        "Has it been deleted from the file system but not from git?"
                    )
                    self.warned_files.add(fname)
                continue

            # dump(fname)
            rel_fname = self.get_rel_fname(fname)

            if fname in chat_fnames:
                personalization[rel_fname] = personalize
                chat_rel_fnames.add(rel_fname)

            if rel_fname in mentioned_fnames:
                personalization[rel_fname] = personalize

            tags = self.get_tags(fname, rel_fname)
            if tags is None:
                tags = []
            tags = list(tags)

            for tag in tags:
                if tag.kind == "def":
                    defines[tag.name].add(rel_fname)
                    key = (rel_fname, tag.name)
                    definitions[key].add(tag)

                elif tag.kind == "ref":
                    references[tag.name].append(rel_fname)

        if not references:
            references = dict((k, list(v)) for k, v in defines.items())

        idents = set(defines.keys()).intersection(set(references.keys()))

        g = nx.MultiDiGraph()

        # Add a small self-edge for every definition that has no references
        # Helps with tree-sitter 0.23.2 with ruby, where "def greet(name)"
        # isn't counted as a def AND a ref. tree-sitter 0.24.0 does.
        for ident in defines.keys():
            if ident in references:
                continue
            for definer in defines[ident]:
                g.add_edge(definer, definer, weight=0.1, ident=ident)

        for ident in idents:
            definers = defines[ident]

            mul = 1.0

            is_snake = ("_" in ident) and any(c.isalpha() for c in ident)
            is_camel = any(c.isupper() for c in ident) and any(
                c.islower() for c in ident
            )
            if ident in mentioned_idents:
                mul *= 10
            if (is_snake or is_camel) and len(ident) >= 8:
                mul *= 10
            if ident.startswith("_"):
                mul *= 0.1
            if len(defines[ident]) > 5:
                mul *= 0.1

            for referencer, num_refs in Counter(references[ident]).items():
                for definer in definers:
                    # dump(referencer, definer, num_refs, mul)
                    # if referencer == definer:
                    #    continue

                    use_mul = mul
                    if referencer in chat_rel_fnames:
                        use_mul *= 50

                    # scale down so high freq (low value) mentions don't dominate
                    num_refs = math.sqrt(num_refs)

                    g.add_edge(
                        referencer, definer, weight=use_mul * num_refs, ident=ident
                    )

        if not references:
            pass

        if personalization:
            pers_args = dict(personalization=personalization, dangling=personalization)
        else:
            pers_args = dict()

        try:
            ranked = nx.pagerank(g, weight="weight", **pers_args)
        except ZeroDivisionError:
            # Issue #1536
            try:
                ranked = nx.pagerank(g, weight="weight")
            except ZeroDivisionError:
                return []

        # distribute the rank from each source node, across all of its out edges
        ranked_definitions = defaultdict(float)
        for src in g.nodes:
            src_rank = ranked[src]
            total_weight = sum(
                data["weight"] for _src, _dst, data in g.out_edges(src, data=True)
            )
            # dump(src, src_rank, total_weight)
            for _src, dst, data in g.out_edges(src, data=True):
                data["rank"] = src_rank * data["weight"] / total_weight
                ident = data["ident"]
                ranked_definitions[(dst, ident)] += data["rank"]

        ranked_tags = []
        ranked_definitions = sorted(
            ranked_definitions.items(), reverse=True, key=lambda x: (x[1], x[0])
        )

        for (fname, ident), rank in ranked_definitions:
            # logger.info(f"{rank:.03f} {fname} {ident}")
            if fname in chat_rel_fnames:
                continue
            ranked_tags += list(definitions.get((fname, ident), []))

        rel_other_fnames_without_tags = set(
            self.get_rel_fname(fname) for fname in other_fnames
        )

        fnames_already_included = set(rt[0] for rt in ranked_tags)

        top_rank = sorted(
            [(rank, node) for (node, rank) in ranked.items()], reverse=True
        )
        for rank, fname in top_rank:
            if fname in rel_other_fnames_without_tags:
                rel_other_fnames_without_tags.remove(fname)
            if fname not in fnames_already_included:
                ranked_tags.append((fname,))

        for fname in rel_other_fnames_without_tags:
            ranked_tags.append((fname,))
        return ranked_tags

    def get_ranked_tags_map(
        self,
        chat_fnames,
        other_fnames=None,
        max_map_tokens=None,
        mentioned_fnames=None,
        mentioned_idents=None,
        force_refresh=False,
    ):
        # Create a cache key
        cache_key = [
            tuple(sorted(chat_fnames)) if chat_fnames else None,
            tuple(sorted(other_fnames)) if other_fnames else None,
            max_map_tokens,
        ]

        if self.refresh == "auto":
            cache_key += [
                tuple(sorted(mentioned_fnames)) if mentioned_fnames else None,
                tuple(sorted(mentioned_idents)) if mentioned_idents else None,
            ]
        cache_key = tuple(cache_key)

        use_cache = False
        if not force_refresh:
            if self.refresh == "manual" and self.last_map:
                return self.last_map

            if self.refresh == "always":
                use_cache = False
            elif self.refresh == "files":
                use_cache = True
            elif self.refresh == "auto":
                use_cache = self.map_processing_time > 1.0

            # Check if the result is in the cache
            if use_cache and cache_key in self.map_cache:
                return self.map_cache[cache_key]

        # If not in cache or force_refresh is True, generate the map
        start_time = time.time()
        result = self.get_ranked_tags_map_uncached(
            chat_fnames,
            other_fnames,
            max_map_tokens,
            mentioned_fnames,
            mentioned_idents,
        )
        end_time = time.time()
        self.map_processing_time = end_time - start_time

        # Store the result in the cache
        self.map_cache[cache_key] = result
        self.last_map = result

        return result

    def get_ranked_tags_map_uncached(
        self,
        chat_fnames,
        other_fnames=None,
        max_map_tokens=None,
        mentioned_fnames=None,
        mentioned_idents=None,
    ):
        if not other_fnames:
            other_fnames = list()
        if not max_map_tokens:
            max_map_tokens = self.max_map_tokens
        if not mentioned_fnames:
            mentioned_fnames = set()
        if not mentioned_idents:
            mentioned_idents = set()

        ranked_tags = self.get_ranked_tags(
            chat_fnames,
            other_fnames,
            mentioned_fnames,
            mentioned_idents,
        )

        other_rel_fnames = sorted(
            set(self.get_rel_fname(fname) for fname in other_fnames)
        )
        special_fnames = filter_important_files(other_rel_fnames)
        ranked_tags_fnames = set(tag[0] for tag in ranked_tags)
        special_fnames = [fn for fn in special_fnames if fn not in ranked_tags_fnames]
        special_fnames = [(fn,) for fn in special_fnames]

        ranked_tags = special_fnames + ranked_tags

        num_tags = len(ranked_tags)
        lower_bound = 0
        upper_bound = num_tags
        best_tree = None
        best_tree_tokens = 0

        chat_rel_fnames = set(self.get_rel_fname(fname) for fname in chat_fnames)

        self.tree_cache = dict()

        middle = min(int(max_map_tokens // 25), num_tags)
        while lower_bound <= upper_bound:
            tree = self.to_tree(ranked_tags[:middle], chat_rel_fnames)
            num_tokens = self.token_count(tree)
            pct_err = abs(num_tokens - max_map_tokens) / max_map_tokens
            ok_err = 0.15
            if (
                num_tokens <= max_map_tokens and num_tokens > best_tree_tokens
            ) or pct_err < ok_err:
                best_tree = tree
                best_tree_tokens = num_tokens

                if pct_err < ok_err:
                    break

            if num_tokens < max_map_tokens:
                lower_bound = middle + 1
            else:
                upper_bound = middle - 1

            middle = int((lower_bound + upper_bound) // 2)

        return best_tree or ""

    tree_cache: dict[str, str] = dict()

    def render_tree(self, abs_fname, rel_fname, lois):
        mtime = self.get_mtime(abs_fname)
        key = (rel_fname, tuple(sorted(lois)), mtime)

        if key in self.tree_cache:
            return self.tree_cache[key]

        if (
            rel_fname not in self.tree_context_cache
            or self.tree_context_cache[rel_fname]["mtime"] != mtime
        ):
            code = open_file(abs_fname) or ""
            if not code.endswith("\n"):
                code += "\n"

            context = TreeContext(
                rel_fname,
                code,
                color=False,
                line_number=False,
                child_context=False,
                last_line=False,
                margin=0,
                mark_lois=False,
                loi_pad=0,
                show_top_of_file_parent_scope=False,
            )
            self.tree_context_cache[rel_fname] = {"context": context, "mtime": mtime}

        context = self.tree_context_cache[rel_fname]["context"]
        context.lines_of_interest = set()
        context.add_lines_of_interest(lois)
        context.add_context()
        res = context.format()
        self.tree_cache[key] = res
        return res

    def to_tree(self, tags, chat_rel_fnames):
        if not tags:
            return ""

        cur_fname = None
        cur_abs_fname = None
        lois = None
        output = ""

        # add a bogus tag at the end so we trip the this_fname != cur_fname...
        dummy_tag = (None,)
        for tag in sorted(tags) + [dummy_tag]:
            this_rel_fname = tag[0]
            if this_rel_fname in chat_rel_fnames:
                continue

            # ... here ... to output the final real entry in the list
            if this_rel_fname != cur_fname:
                if lois is not None:
                    output += "\n"
                    output += cur_fname + ":\n"
                    output += self.render_tree(cur_abs_fname, cur_fname, lois)
                    lois = None
                elif cur_fname:
                    output += "\n" + cur_fname + "\n"
                if type(tag) is Tag:
                    lois = []
                    cur_abs_fname = tag.fname
                cur_fname = this_rel_fname

            if lois is not None:
                lois.append(tag.line)

        # truncate long lines, in case we get minified js or something else crazy
        output = "\n".join([line[:100] for line in output.splitlines()]) + "\n"

        return output


def get_scm_fname(lang):
    # Load the tags queries
    # return "./queries/tree-sitter-language-pack/{lang}-tags.scm"
    try:
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the path to the resource
        path = os.path.join(
            current_dir, "queries", "tree-sitter-language-pack", f"{lang}-tags.scm"
        )

        if os.path.exists(path):
            return path
    except KeyError:
        pass
    return None


def get_supported_languages_md():
    res = """
| Language | File extension | Repo map | Linter |
|:--------:|:--------------:|:--------:|:------:|
"""
    data = sorted((lang, ex) for ex, lang in PARSERS.items())

    for lang, ext in data:
        fn = get_scm_fname(lang)
        repo_map = "✓" if fn and Path(fn).exists() else ""
        linter_support = "✓"
        res += f"| {lang:20} | {ext:20} | {repo_map:^8} | {linter_support:^6} |\n"

    res += "\n"

    return res


def is_git_repo(repo_path: str) -> bool:
    """Check if the given path is a git repository."""
    git_dir = os.path.join(repo_path, ".git")
    return os.path.exists(git_dir)


def generate_git_cache_key(repo_path: str) -> str | None:
    """Generate an ultra-fast cache key using only git commit hash and index mtime."""
    hasher = hashlib.md5()
    hasher.update(repo_path.encode())

    try:
        # Just get commit hash (fast)
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=2,
        )

        # Return None if git command failed
        if result.returncode != 0:
            return None

        # Git command succeeded, add commit hash
        hasher.update(result.stdout.strip().encode())

        # Add git index mtime for staged changes detection (fast)
        git_index_path = os.path.join(repo_path, ".git", "index")
        if os.path.exists(git_index_path):
            index_mtime = os.path.getmtime(git_index_path)
            hasher.update(str(index_mtime).encode())

        return hasher.hexdigest()

    except (
        subprocess.TimeoutExpired,
        subprocess.SubprocessError,
        FileNotFoundError,
        OSError,
    ) as e:
        logger.debug(f"Git command failed for cache key generation: {e}")
        return None


def generate_simple_cache_key(repo_path: str, all_files: list[str]) -> str:
    """Generate a lightweight cache key using file list only (no stat calls)."""
    hasher = hashlib.md5()

    # Include repo path
    hasher.update(repo_path.encode())

    # Sort files for consistent ordering
    sorted_files = sorted(all_files)

    # Include file count
    hasher.update(str(len(sorted_files)).encode())

    # Include file list (but not modification times)
    for file_path in sorted_files:
        hasher.update(file_path.encode())

    # Include directory modification time as a rough change indicator
    try:
        dir_stat = os.stat(repo_path)
        hasher.update(str(dir_stat.st_mtime).encode())
    except OSError:
        pass

    return hasher.hexdigest()


def generate_full_cache_key(repo_path: str, all_files: list[str]) -> str:
    """Generate a comprehensive cache key based on repo path, files, and modification times (original implementation)."""
    hasher = hashlib.md5()

    # Include repo path
    hasher.update(repo_path.encode())

    # Sort files for consistent ordering
    sorted_files = sorted(all_files)

    # Include file count and total size for quick validation
    hasher.update(str(len(sorted_files)).encode())

    total_size = 0
    for file_path in sorted_files:
        try:
            stat = os.stat(file_path)
            # Include file path, modification time, and size
            file_info = f"{file_path}:{stat.st_mtime}:{stat.st_size}"
            hasher.update(file_info.encode())
            total_size += stat.st_size
        except OSError:
            # File might have been deleted, include just the path
            hasher.update(file_path.encode())

    # Include total size for additional validation
    hasher.update(str(total_size).encode())

    return hasher.hexdigest()


def generate_cache_key(
    repo_path: str, all_files: list[str], strategy: str = "auto"
) -> tuple[str, str]:
    """Generate a cache key using the specified strategy.

    Returns:
        tuple: (cache_key, strategy_used)
    """
    start_time = time.time()

    if strategy == "auto":
        # Auto-detect best strategy
        if is_git_repo(repo_path):
            cache_key = generate_git_cache_key(repo_path)
            if cache_key:
                strategy_used = "git"
            else:
                # Fallback to simple if git fails
                cache_key = generate_simple_cache_key(repo_path, all_files)
                strategy_used = "simple"
        else:
            cache_key = generate_simple_cache_key(repo_path, all_files)
            strategy_used = "simple"
    elif strategy == "git":
        cache_key = generate_git_cache_key(repo_path)
        if not cache_key:
            raise ValueError("Git strategy failed and no fallback specified")
        strategy_used = "git"
    elif strategy == "simple":
        cache_key = generate_simple_cache_key(repo_path, all_files)
        strategy_used = "simple"
    elif strategy == "full":
        cache_key = generate_full_cache_key(repo_path, all_files)
        strategy_used = "full"
    else:
        raise ValueError(f"Unknown cache strategy: {strategy}")

    generation_time = time.time() - start_time
    logger.debug(f"Cache key generation ({strategy_used}): {generation_time:.3f}s")

    return cache_key, strategy_used


def get_repo_map_for_prompt_cached(repo_path: str) -> str:
    """Get repo map with ultra-fast caching support."""
    from gsai.config import cli_settings

    # Only show debug output in verbose mode
    if cli_settings.verbose:
        print(f"🔍 CACHE DEBUG: Starting repo map for {repo_path}")
        print(f"🔍 CACHE DEBUG: Cache enabled: {cli_settings.cache_enabled}")
        print(f"🔍 CACHE DEBUG: Cache strategy: {cli_settings.cache_strategy}")

    # Check if caching is enabled
    if not cli_settings.cache_enabled:
        if cli_settings.verbose:
            print("🔍 CACHE DEBUG: Caching disabled, generating uncached")
        return get_repo_map_for_prompt(repo_path)

    try:
        # Get reusable cache object
        cache = get_disk_cache()
        if cli_settings.verbose:
            print(f"🔍 CACHE DEBUG: Cache object created: {cache}")

        # For git repos, try ultra-fast git-based cache key first (no file enumeration needed)
        cache_key = None
        strategy_used = None

        is_git = is_git_repo(repo_path)
        if cli_settings.verbose:
            print(f"🔍 CACHE DEBUG: Is git repo: {is_git}")

        if cli_settings.cache_strategy in ["auto", "git"] and is_git:
            try:
                start_time = time.time()
                cache_key = generate_git_cache_key(repo_path)
                key_gen_time = time.time() - start_time
                if cli_settings.verbose:
                    print(
                        f"🔍 CACHE DEBUG: Git cache key generated in {key_gen_time:.3f}s: {cache_key}"
                    )

                if cache_key:
                    strategy_used = "git"
                    # Try cache lookup with git-based key
                    cached_result = cache.get(cache_key)
                    if cached_result is not None:
                        if cli_settings.verbose:
                            print(f"✅ CACHE HIT (git strategy) for {repo_path}")
                        logger.debug(
                            f"Repo map cache hit (git strategy) for {repo_path}"
                        )
                        return cached_result
                    else:
                        if cli_settings.verbose:
                            print(f"❌ CACHE MISS (git strategy) for {repo_path}")
            except Exception as e:
                if cli_settings.verbose:
                    print(f"🔍 CACHE DEBUG: Git cache key generation failed: {e}")
                logger.debug(f"Git cache key generation failed: {e}")

        # If git strategy failed or not applicable, get file list for other strategies
        if not cache_key:
            if cli_settings.verbose:
                print("🔍 CACHE DEBUG: Falling back to file enumeration for cache key")
            start_time = time.time()
            all_files = get_files_excluding_gitignore(repo_path, repo_path)
            file_enum_time = time.time() - start_time
            if cli_settings.verbose:
                print(
                    f"🔍 CACHE DEBUG: File enumeration took {file_enum_time:.3f}s, found {len(all_files)} files"
                )

            # Check if repo is too large (same check as original function)
            if len(all_files) > 10000:
                if cli_settings.verbose:
                    print(f"🔍 CACHE DEBUG: Repo too large ({len(all_files)} files)")
                logger.warning(f"{repo_path} too large to generate repo map")
                return "Repo is too large to generate a repo map."

            # Generate cache key with file list
            start_time = time.time()
            cache_key, strategy_used = generate_cache_key(
                repo_path, all_files, cli_settings.cache_strategy
            )
            key_gen_time = time.time() - start_time
            if cli_settings.verbose:
                print(
                    f"🔍 CACHE DEBUG: {strategy_used} cache key generated in {key_gen_time:.3f}s: {cache_key}"
                )

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                if cli_settings.verbose:
                    print(f"✅ CACHE HIT ({strategy_used} strategy) for {repo_path}")
                logger.debug(
                    f"Repo map cache hit ({strategy_used} strategy) for {repo_path}"
                )
                return cached_result
            else:
                if cli_settings.verbose:
                    print(f"❌ CACHE MISS ({strategy_used} strategy) for {repo_path}")

        # Cache miss - generate repo map
        if cli_settings.verbose:
            print("🔍 CACHE DEBUG: Generating repo map (cache miss)")
        logger.debug(f"Repo map cache miss ({strategy_used} strategy) for {repo_path}")

        # Generate repo map (this will re-enumerate files if needed)
        start_time = time.time()
        result = get_repo_map_for_prompt(repo_path)
        generation_time = time.time() - start_time

        if cli_settings.verbose:
            print(f"🔍 CACHE DEBUG: Repo map generation took {generation_time:.3f}s")
        logger.debug(f"Repo map generation time: {generation_time:.3f}s")

        # Store in cache with TTL and repo-path tag
        from gsai.config import cli_settings

        ttl_seconds = cli_settings.cache_ttl_days * 24 * 60 * 60
        cache.set(
            cache_key,
            result,
            expire=ttl_seconds,
            tag=f"repo:{hashlib.md5(repo_path.encode()).hexdigest()[:8]}",
        )
        if cli_settings.verbose:
            print(f"🔍 CACHE DEBUG: Result stored in cache with key {cache_key}")

        return result

    except Exception as e:
        # If caching fails, fall back to uncached generation
        if cli_settings.verbose:
            print(f"🔍 CACHE DEBUG: Cache operation failed: {e}")
        logger.warning(
            f"Cache operation failed, falling back to uncached generation: {e}"
        )
        return get_repo_map_for_prompt(repo_path)


def get_repo_map_for_prompt(repo_path: str) -> str:
    assert repo_path and len(repo_path) > 0, (
        "No Repo Path provided for repo map creation"
    )
    all_files = get_files_excluding_gitignore(repo_path, repo_path)
    # TODO: Either make this configurable or find a better solution to dealing with massive codebases.
    if len(all_files) > 10000:
        logger.warning(f"{repo_path} too large to generate repo map")
        return "Repo is too large to generate a repo map."
    rm = RepoMap(root=repo_path)
    repo_map_for_prompt = rm.get_repo_map([], all_files)
    return repo_map_for_prompt


if __name__ == "__main__":
    # e.g. in /app run this: python gsai.shared/repo_map.py "." "."
    repo_path = sys.argv[1]
    directory_path = sys.argv[2]
    abs_repo_path = os.path.abspath(repo_path)
    abs_path = safe_construct_path(abs_repo_path, directory_path)
    logger.info(f"Extracting code context for repo '{abs_repo_path}' in '{abs_path}'")
    other_fnames = get_files_excluding_gitignore(abs_repo_path, abs_path)
    rm = RepoMap(root=abs_repo_path)
    # repo_map = rm.get_ranked_tags_map(chat_fnames, other_fnames)
    repo_map = rm.get_repo_map([], other_fnames)

    logger.info(repo_map)
