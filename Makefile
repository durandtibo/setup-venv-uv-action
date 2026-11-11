SHELL = /bin/bash

include .make/help.mk
include .make/makefile.mk
include .make/markdown.mk
include .make/self.mk
include .make/shell.mk
include .make/toml.mk
include .make/uv.mk
include .make/yaml.mk

.DEFAULT_GOAL := help

.PHONY: format
format: format-yaml format-makefile format-shell format-toml format-markdown ## Format all files

.PHONY: lint
lint: lint-yaml lint-makefile lint-shell lint-markdown check-readme ## Lint all files

.PHONY: check-readme
check-readme: ## Check that the README documents the inputs and outputs of action.yaml
	python3 scripts/check_readme_inputs.py action.yaml README.md
