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

.PHONY : format
format :
	# Lint all markdown files for style and formatting issues
	markdownlint **/*.md
	# Format code files with prettier (YAML, JSON, etc.)
	prettier --write .
	# Lint YAML files with colored output for better readability
	yamllint -f colored .

.PHONY : install-invoke
install-invoke :
	# Install invoke task runner for managing project tasks
	# Version requirement: >= 2.2.0 for compatibility with current tasks
	uv pip install "invoke>=2.2.0"