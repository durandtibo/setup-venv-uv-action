#!/usr/bin/env bash
#
# This script creates a minimal Makefile that can be used to test the action.
#

set -euo pipefail

# Check if the user provided a file path as an argument
if [[ -z "$1" ]]; then
	echo "Usage: $0 <file-path>"
	exit 1
fi

# Assign the first argument to the filename
filepath="$1"

# Extract the directory path from the full file path
dirpath=$(dirname "$filepath")

# Check if the directory exists, and create it if it doesn't
if [[ ! -d "$dirpath" ]]; then
	echo "Directory '$dirpath' does not exist. Creating it..."
	mkdir -p "$dirpath"
fi

content='SHELL=/bin/bash

.PHONY : install-invoke
install-invoke :
	uv pip install "invoke>=2.2.0"'

# Create the file and write the content
echo "$content" >"$filepath"

# Confirm the file has been created
echo "File '$filepath' has been created with the provided content."
