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

LOCAL_WORKFLOW := .github/workflows/test-local.yaml
STABLE_WORKFLOW := .github/workflows/test-stable.yaml

.PHONY: generate-stable-workflow
generate-stable-workflow: ## Generate test-stable.yaml from test-local.yaml
	scripts/generate-stable-workflow.sh $(LOCAL_WORKFLOW) $(STABLE_WORKFLOW) > $(STABLE_WORKFLOW).tmp
	mv $(STABLE_WORKFLOW).tmp $(STABLE_WORKFLOW)

.PHONY: format
format: generate-stable-workflow format-yaml format-makefile format-shell format-toml format-markdown ## Format all files

.PHONY: lint
lint: lint-yaml lint-makefile lint-shell lint-markdown ## Lint all files
