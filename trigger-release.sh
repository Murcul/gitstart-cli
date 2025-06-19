#!/bin/bash

# GitStart CoPilot CLI - Release Trigger Script
# This script helps you trigger GitHub Actions builds and releases

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║            GitStart CoPilot CLI Release Helper          ║"
    echo "║                     Build & Release                     ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

show_help() {
    cat << EOF
GitStart CoPilot CLI - Release Trigger

USAGE:
    ./trigger-release.sh [COMMAND] [OPTIONS]

COMMANDS:
    tag-release [VERSION]     Create and push a new release tag
    manual-build [VERSION]    Trigger manual workflow dispatch
    check-status             Check GitHub Actions status
    list-releases            List existing releases
    help                     Show this help

EXAMPLES:
    # Create a new release (triggers automatic build)
    ./trigger-release.sh tag-release v1.0.0

    # Trigger manual build without creating tag
    ./trigger-release.sh manual-build v1.0.0-beta

    # Check current workflow status
    ./trigger-release.sh check-status

REQUIREMENTS:
    - gh CLI tool installed and authenticated
    - Git repository with GitHub remote
    - Push access to the repository

WHAT GETS BUILT:
    📦 Cross-platform executables (Windows, macOS, Linux)
    📋 Source code packages (complete, minimal, installers-only)
    🔧 ZIP packages with installation instructions
    📖 Release notes with download links

The GitHub Actions workflow will:
    1. Build executables for all platforms
    2. Embed API keys from GitHub Secrets
    3. Create ZIP packages with installers
    4. Generate source code packages
    5. Create GitHub release with all artifacts
    6. Generate comprehensive release notes

EOF
}

check_requirements() {
    local missing=()
    
    # Check for gh CLI
    if ! command -v gh &> /dev/null; then
        missing+=("GitHub CLI (gh)")
    fi
    
    # Check for git
    if ! command -v git &> /dev/null; then
        missing+=("git")
    fi
    
    if [ ${#missing[@]} -gt 0 ]; then
        echo -e "${RED}❌ Missing requirements:${NC}"
        printf '%s\n' "${missing[@]}" | sed 's/^/  - /'
        echo ""
        echo -e "${YELLOW}Install GitHub CLI: https://cli.github.com/manual/installation${NC}"
        exit 1
    fi
    
    # Check if authenticated with GitHub
    if ! gh auth status &> /dev/null; then
        echo -e "${RED}❌ Not authenticated with GitHub${NC}"
        echo -e "${YELLOW}Run: gh auth login${NC}"
        exit 1
    fi
    
    # Check if in git repository
    if ! git rev-parse --git-dir &> /dev/null; then
        echo -e "${RED}❌ Not in a Git repository${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All requirements met${NC}"
}

tag_release() {
    local version="$1"
    
    if [ -z "$version" ]; then
        echo -e "${RED}❌ Version required${NC}"
        echo "Usage: ./trigger-release.sh tag-release v1.0.0"
        exit 1
    fi
    
    # Validate version format
    if [[ ! "$version" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9-]+)?$ ]]; then
        echo -e "${YELLOW}⚠️  Version should follow format: v1.0.0 or v1.0.0-beta${NC}"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    echo -e "${BLUE}📝 Creating release tag: $version${NC}"
    
    # Check if tag already exists
    if git tag --list | grep -q "^$version$"; then
        echo -e "${RED}❌ Tag $version already exists${NC}"
        exit 1
    fi
    
    # Create and push tag
    git tag -a "$version" -m "Release $version"
    git push origin "$version"
    
    echo -e "${GREEN}✅ Tag created and pushed${NC}"
    echo -e "${BLUE}🚀 GitHub Actions build will start automatically${NC}"
    echo ""
    echo "Monitor progress:"
    echo "  gh run list --workflow=build-release.yml"
    echo "  gh run watch"
}

manual_build() {
    local version="$1"
    
    if [ -z "$version" ]; then
        echo -e "${RED}❌ Version required${NC}"
        echo "Usage: ./trigger-release.sh manual-build v1.0.0-test"
        exit 1
    fi
    
    echo -e "${BLUE}🚀 Triggering manual build for: $version${NC}"
    
    # Trigger workflow dispatch
    gh workflow run build-release.yml \
        --field version="$version"
    
    echo -e "${GREEN}✅ Manual build triggered${NC}"
    echo ""
    echo "Monitor progress:"
    echo "  gh run list --workflow=build-release.yml"
    echo "  gh run watch"
}

check_status() {
    echo -e "${BLUE}📊 Checking GitHub Actions status...${NC}"
    echo ""
    
    # Show recent workflow runs
    echo "Recent workflow runs:"
    gh run list --workflow=build-release.yml --limit=5
    
    echo ""
    echo "Use 'gh run watch' to monitor active runs"
    echo "Use 'gh run view [RUN_ID]' to see details"
}

list_releases() {
    echo -e "${BLUE}📋 Recent releases:${NC}"
    echo ""
    
    gh release list --limit=10
    
    echo ""
    echo "Use 'gh release view [TAG]' to see release details"
}

show_urls() {
    local repo_url
    repo_url=$(gh repo view --json url --jq .url)
    
    echo -e "${BLUE}🔗 Useful URLs:${NC}"
    echo "  Repository: $repo_url"
    echo "  Actions: $repo_url/actions"
    echo "  Releases: $repo_url/releases"
    echo "  Workflows: $repo_url/actions/workflows/build-release.yml"
}

main() {
    print_banner
    
    case "${1:-help}" in
        tag-release)
            check_requirements
            tag_release "$2"
            show_urls
            ;;
        manual-build)
            check_requirements
            manual_build "$2"
            show_urls
            ;;
        check-status)
            check_requirements
            check_status
            ;;
        list-releases)
            check_requirements
            list_releases
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"