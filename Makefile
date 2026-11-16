SHELL = /bin/bash

include .make/all.mk

.PHONY: check-readme
check-readme: ## Check that the README documents the inputs and outputs of action.yaml
	python3 scripts/check_readme_inputs.py action.yaml README.md

.PHONY: all
all: format lint ## Format and lint everything

.PHONY: test
test: check-readme ## Run the checks of this repository

.PHONY: clean
clean: ## Remove the local tool caches
	rm -rf .ruff_cache
