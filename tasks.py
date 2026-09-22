r"""Define tasks that are executed with invoke for project management.

This module re-exports the shared task collection from ``invoke-tasklib``,
which is used by the GitHub Action to install dependencies, display
configuration, and verify the environment setup.

Example:
    Run tasks using the inv command:

    $ inv env.install
    $ inv env.show-installed-packages
    $ inv env.show-python-config
"""

from __future__ import annotations

from invoke_tasklib import ns

__all__ = ["ns"]
