SHELL = /bin/bash

include .make/all.mk

.PHONY: check-readme
check-readme: ## Check that the README documents the inputs and outputs of action.yaml
	python3 scripts/check_readme_inputs.py action.yaml README.md

.PHONY: check-export
check-export: ## Check that the exported files are the files the action needs
	./scripts/check_export.sh

.PHONY: all
all: format lint ## Format and lint everything

.PHONY: test
test: check-readme check-export ## Run the checks of this repository

.PHONY: clean
clean: ## Remove the local tool caches
	rm -rf .ruff_cache
