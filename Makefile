SHELL = /bin/bash

include .make/all.mk

.PHONY: check-readme
check-readme: ## Check that the README documents the inputs and outputs of action.yaml
	python3 scripts/check_readme_inputs.py action.yaml README.md
