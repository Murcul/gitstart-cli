# GitStart CoPilot CLI Build Makefile

# Variables
PYTHON := python3
UV := uv
APP_NAME := gsai
DIST_DIR := dist
BUILD_SCRIPT := build_executable.py

# Default target
.PHONY: help
help:
	@echo "GitStart CoPilot CLI Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  install        - Install dependencies using uv"
	@echo "  dev-install    - Install development dependencies"
	@echo "  build          - Build executable (requires API keys as env vars)"
	@echo "  build-prompt   - Build executable with interactive API key prompts"
	@echo "  clean          - Clean build artifacts"
	@echo "  test           - Run tests"
	@echo "  lint           - Run linting and formatting"
	@echo "  typecheck      - Run type checking"
	@echo "  quality        - Run all quality checks (test, lint, typecheck)"
	@echo ""
	@echo "Environment variables for build:"
	@echo "  OPENAI_API_KEY     - OpenAI API key to embed"
	@echo "  ANTHROPIC_API_KEY  - Anthropic API key to embed"
	@echo ""
	@echo "Example usage:"
	@echo "  make install"
	@echo "  OPENAI_API_KEY=sk-... ANTHROPIC_API_KEY=sk-... make build"
	@echo "  make build-prompt  # Interactive key input"

# Install dependencies
.PHONY: install
install:
	$(UV) sync

# Install development dependencies
.PHONY: dev-install
dev-install: install
	$(UV) sync --dev

# Build executable with environment variables
.PHONY: build
build: dev-install
	@if [ -z "$$OPENAI_API_KEY" ] && [ -z "$$ANTHROPIC_API_KEY" ]; then \
		echo "Warning: No API keys found in environment variables."; \
		echo "Set OPENAI_API_KEY and/or ANTHROPIC_API_KEY environment variables."; \
		echo "Or use 'make build-prompt' for interactive input."; \
		exit 1; \
	fi
	$(PYTHON) $(BUILD_SCRIPT) \
		$(if $(OPENAI_API_KEY),--openai-key "$(OPENAI_API_KEY)") \
		$(if $(ANTHROPIC_API_KEY),--anthropic-key "$(ANTHROPIC_API_KEY)") \
		--output-dir $(DIST_DIR) \
		--app-name $(APP_NAME)

# Build executable with interactive prompts
.PHONY: build-prompt
build-prompt: dev-install
	@echo "Building GitStart CoPilot CLI executable..."
	@echo "Please provide your API keys (press Enter to skip):"
	@read -p "OpenAI API Key: " openai_key; \
	read -p "Anthropic API Key: " anthropic_key; \
	$(PYTHON) $(BUILD_SCRIPT) \
		$$([ -n "$$openai_key" ] && echo "--openai-key $$openai_key") \
		$$([ -n "$$anthropic_key" ] && echo "--anthropic-key $$anthropic_key") \
		--output-dir $(DIST_DIR) \
		--app-name $(APP_NAME)

# Clean build artifacts
.PHONY: clean
clean:
	rm -rf $(DIST_DIR)
	rm -rf build
	rm -rf *.spec
	rm -rf gsai/build_config.py
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.egg-info" -type d -exec rm -rf {} +

# Run tests
.PHONY: test
test:
	$(UV) run pytest

# Run linting and formatting
.PHONY: lint
lint:
	$(UV) run ruff format
	$(UV) run ruff check --fix

# Run type checking
.PHONY: typecheck
typecheck:
	$(UV) run mypy .

# Run all quality checks
.PHONY: quality
quality: test lint typecheck
	@echo "All quality checks completed successfully!"

# Install the CLI globally for testing
.PHONY: install-global
install-global: 
	$(UV) tool install .

# Uninstall the CLI globally
.PHONY: uninstall-global
uninstall-global:
	$(UV) tool uninstall $(APP_NAME)

# Development mode - install in editable mode
.PHONY: dev-mode
dev-mode:
	$(UV) pip install -e .

# Quick build for testing (no API keys embedded)
.PHONY: build-test
build-test: dev-install
	$(PYTHON) $(BUILD_SCRIPT) --output-dir $(DIST_DIR) --app-name $(APP_NAME)

# Create a release build with optimizations
.PHONY: release
release: quality build
	@echo "Release build completed!"
	@echo "Executable: $(DIST_DIR)/$(APP_NAME)"
	@ls -lh $(DIST_DIR)/$(APP_NAME)

.PHONY: all
all: install quality build