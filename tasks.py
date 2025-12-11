r"""Define some tasks that are executed with invoke."""

from __future__ import annotations

from typing import TYPE_CHECKING

from invoke.tasks import task

if TYPE_CHECKING:
    from invoke.context import Context

@task
def install(c: Context) -> None:
    r"""Install packages."""
    c.run("uv sync --frozen", pty=True)
    # c.run("uv pip install -e .", pty=True)
    
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

