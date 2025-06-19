import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

# SetUp Jinja
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic_ai import ImageUrl

jinja_env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)


def get_repo_name(url: str) -> str:
    # Path.stem removes the last suffix (e.g. “.git”)
    return Path(urlparse(url).path.rstrip("/")).stem


def split_keep_whitespace(s: str) -> list[str]:
    # Match either non-whitespace sequences OR newline/tab characters
    return re.findall(r"[^\s]+|[\n\t]", s)


def validate_is_url(url: str) -> bool:
    regex = re.compile(
        r"^(?:http|ftp)s?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    return re.match(regex, url) is not None


def process_template(template_file: str, data: dict[str, Any]) -> str:
    template = jinja_env.get_template(template_file)
    return template.render(**data)


def process_gitstart_asset(word: str) -> ImageUrl | str:
    """
    Extract an asset URL and turn into an ImageUrl object.

    Args:
        word (str): the word from which the asset URL should be extracted.

    Returns:
        ImageUrl | str: the ImageUrl object if successfully extracted, otherwise returns the original word.
    """
    match = re.search(
        r"(?:!\[[^\]]*\]\()((?:https://assets-service\.gitstart[^)]+))(?:\))", word
    )
    if match:
        return ImageUrl(match.group(1))
    else:
        return word


def process_prompt_with_images(prompt: str, client_id: str) -> list[str | ImageUrl]:
    """
    Process a prompt with images, handling both GitStart assets and Figma links.

    Args:
        prompt (str): The prompt to process
        client_id (str, optional): The client ID for the GraphQL API calls. Defaults to None.

    Returns:
        list[str | ImageUrl]: The processed prompt
    """
    # Split the prompt into words
    words = split_keep_whitespace(prompt)
    results: list[str | ImageUrl] = []

    current_text = ""
    for word in words:
        if "https://assets-service.gitstart" in word:
            results.append(current_text)
            current_text = ""

            results.append(process_gitstart_asset(word))
        else:
            current_text += word + " "

    results.append(current_text)
    results = list(filter(lambda result: result != "", results))

    return results
