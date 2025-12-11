#!/usr/bin/env bash
#
# This script creates a minimal invoke tasks.py file that can be used to test the action.
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

content='r"""Define some tasks that are executed with invoke."""

from __future__ import annotations

from typing import TYPE_CHECKING

from invoke.tasks import task

if TYPE_CHECKING:
    from invoke.context import Context

@task
def install(c: Context) -> None:
    r"""Install packages."""
    c.run("uv sync --frozen", pty=True)
    c.run("uv pip install -e .", pty=True)

@task
def show_installed_packages(c: Context) -> None:
    r"""Show the installed packages."""
    c.run("uv pip list", pty=True)

@task
def show_python_config(c: Context) -> None:
    r"""Show the python configuration."""
    c.run("uv python list --only-installed", pty=True)
    c.run("uv python find", pty=True)
    c.run("which python", pty=True)
'

# Create the file and write the content
echo "$content" >"$filepath"

# Confirm the file has been created
echo "File '$filepath' has been created with the provided content."
