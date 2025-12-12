# Makefile for setup-venv-uv-action
#
# This Makefile provides convenient shortcuts for common development tasks.
# All targets use uv for package management and various linters for code quality.
#
# Available targets:
#   make format          - Run all formatters and linters (markdown, prettier, YAML)
#   make install-invoke  - Install the invoke task runner
#
# Requirements:
#   - uv: Fast Python package installer (https://github.com/astral-sh/uv)
#   - markdownlint: Markdown linter (npm install -g markdownlint-cli)
#   - prettier: Code formatter (npm install -g prettier)
#   - yamllint: YAML linter (pip install yamllint or apt-get install yamllint)

SHELL=/bin/bash

.PHONY : help
help :
	@echo "setup-venv-uv-action - Available Make Targets"
	@echo ""
	@echo "  make help           - Display this help message"
	@echo "  make format         - Run formatting and linting checks"
	@echo "  make install-invoke - Install invoke package using uv"
	@echo ""
	@echo "Formatting tools used:"
	@echo "  - markdownlint: Validates Markdown files"
	@echo "  - prettier: Formats various file types"
	@echo "  - yamllint: Validates YAML files"
	@echo ""

.PHONY : format
format :
	@echo "🔍 Running markdownlint on Markdown files..."
	markdownlint **/*.md
	@echo "✅ Markdownlint passed"
	@echo ""
	@echo "✨ Running prettier to format files..."
	prettier --write .
	@echo "✅ Prettier formatting complete"
	@echo ""
	@echo "🔍 Running yamllint on YAML files..."
	yamllint -f colored .
	@echo "✅ Yamllint passed"
	@echo ""
	@echo "🎉 All format checks passed!"

.PHONY : install-invoke
install-invoke :
	# Install invoke task runner for managing project tasks
	# Version requirement: >= 2.2.0 for compatibility with current tasks
	uv pip install "invoke>=2.2.0"

.DEFAULT_GOAL := help

