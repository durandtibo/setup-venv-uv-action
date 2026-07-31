r"""Define tasks that are executed with invoke for project management.

This module contains invoke tasks for setting up and managing the Python
environment. These tasks are used by the GitHub Action to install dependencies,
display configuration, and verify the environment setup.

Example:
    Run tasks using the inv command:

    $ inv install
    $ inv show-installed-packages
    $ inv show-python-config
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from invoke.tasks import task

if TYPE_CHECKING:
    from invoke.context import Context


@task(
    help={
        "all_extras": "Install all optional dependency groups.",
        "no_dev": "Skip installing development dependencies.",
    }
)
def install(c: Context, all_extras: bool = False, no_dev: bool = False) -> None:
    r"""Install project packages and dependencies.

    This task performs a two-step installation process:
    1. Syncs dependencies from uv.lock (frozen install for reproducibility)
    2. Installs the current project in editable mode

    Args:
        c: The invoke context object for running commands.
        all_extras: If ``True``, pass ``--all-extras`` to ``uv sync``.
        no_dev: If ``True``, pass ``--no-dev`` to ``uv sync``.

    Note:
        The --frozen flag ensures dependencies match uv.lock exactly,
        preventing unexpected version changes during installation.
    """
    sync_args = ["uv", "sync", "--frozen"]
    if all_extras:
        sync_args.append("--all-extras")
    if no_dev:
        sync_args.append("--no-dev")
    c.run(" ".join(sync_args), pty=True)
    c.run("uv pip install -e .", pty=True)


@task
def show_installed_packages(c: Context) -> None:
    r"""Display all installed packages in the current environment.
    
    Lists all packages installed in the Python environment with their
    versions. Useful for debugging and verifying the environment setup.
    
    Args:
        c: The invoke context object for running commands.
    
    Example Output:
        Package           Version
        ----------------- -------
        invoke            2.2.0
        myproject         0.0.0a0
    """
    c.run("uv pip list", pty=True)


@task
def show_python_config(c: Context) -> None:
    r"""Display Python configuration and environment details.
    
    Shows comprehensive information about the Python environment:
    - All installed Python versions managed by uv
    - The active Python interpreter being used
    - The full path to the Python executable
    
    Args:
        c: The invoke context object for running commands.
    
    Note:
        This is particularly useful in CI/CD environments to verify
        that the correct Python version is being used.
    """
    c.run("uv python list --only-installed", pty=True)
    c.run("uv python find", pty=True)
    c.run("which python", pty=True)

