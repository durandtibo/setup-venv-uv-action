r"""Test project module for validating GitHub Action functionality.

This minimal Python package is used to verify that the setup-venv-uv-action
correctly installs project dependencies and makes packages importable in
the configured Python environment.

Example:
    In workflows, this module is imported to verify installation:

    >>> import myproject
    >>> print(myproject)
    <module 'myproject' from '...'>
"""

__version__ = "0.0.0a0"
__all__: list[str] = []
