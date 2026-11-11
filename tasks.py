r"""Define tasks that are executed with invoke for project management.

This module re-exports the shared task collection from ``invoke-tasklib``,
which is used by the GitHub Action to install the dependencies.

Example:
    Run tasks using the inv command:

    $ inv env.install
"""

from __future__ import annotations

from invoke_tasklib import ns

__all__ = ["ns"]
