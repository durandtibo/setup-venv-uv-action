SHELL=/bin/bash

.PHONY : format
format :
	markdownlint **/*.md
	shellcheck **/*.sh
	shfmt -l -w **/*.sh
	prettier --write .
	yamllint -f colored .

.PHONY : install-invoke
install-invoke :
	uv pip install "invoke>=2.2.0"