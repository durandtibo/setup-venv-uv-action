# setup-venv-uv-action

[![CI](https://github.com/durandtibo/setup-venv-uv-action/actions/workflows/ci.yaml/badge.svg)](https://github.com/durandtibo/setup-venv-uv-action/actions/workflows/ci.yaml)
[![Nightly Tests](https://github.com/durandtibo/setup-venv-uv-action/actions/workflows/nightly-tests.yaml/badge.svg)](https://github.com/durandtibo/setup-venv-uv-action/actions/workflows/nightly-tests.yaml)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://github.com/durandtibo/setup-venv-uv-action/blob/main/LICENSE)

A GitHub Action to setup a Python virtual environment using
[uv](https://github.com/astral-sh/uv), the ultra-fast Python package installer
and resolver.

## Features

- **Fast Setup**: Uses `uv` for lightning-fast Python environment setup and
  package installation
- **Flexible Configuration**: Supports custom Python versions, optional package
  installations, and additional install arguments
- **Environment Verification**: Automatically verifies the environment setup
  with dependency checks and diagnostics
- **Cross-Platform**: Tested on Ubuntu (x64/ARM), macOS (Intel/Apple Silicon)
- **Debug-Friendly**: Provides detailed output of Python configuration,
  installed packages, and dependency tree

## Usage

### Basic Example

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python environment
        uses: durandtibo/setup-venv-uv-action@v0.0.3

      - name: Run tests
        run: |
          python -m pytest
```

### With Custom Python Version

```yaml
- name: Setup Python environment
  uses: durandtibo/setup-venv-uv-action@v0.0.3
  with:
    python-version: "3.11"
```

### With Specific Package Installation

```yaml
- name: Setup Python environment with numpy
  uses: durandtibo/setup-venv-uv-action@v0.0.3
  with:
    python-version: "3.12"
    package-name: "numpy"
    package-version: "1.26.0"
```

### With Custom Install Arguments

```yaml
- name: Setup Python environment with extras
  uses: durandtibo/setup-venv-uv-action@v0.0.3
  with:
    install-args: "--all-extras"
```

## Inputs

| Input                  | Description                                          | Required | Default  |
| ---------------------- | ---------------------------------------------------- | -------- | -------- |
| `python-version`       | Python version to use (e.g., "3.13", "3.12")         | No       | `"3.13"` |
| `package-name`         | Optional package name for dependency testing         | No       | `""`     |
| `package-version`      | Optional package version (used with `package-name`)  | No       | `""`     |
| `install-args`         | Additional arguments for the install command         | No       | `""`     |
| `package-install-args` | Additional arguments for the package install command | No       | `""`     |
| `uv-no-progress`       | Disable UV progress bars                             | No       | `"true"` |

## What This Action Does

This action performs the following steps:

1. **Installs uv**: Uses
   [astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) to install the
   `uv` package manager
2. **Verifies Installation**: Checks that `uv` and `python` are available in
   PATH
3. **Installs Task Runner**: Installs `invoke` for running project tasks
4. **Installs Dependencies**: Runs `inv install` with optional custom arguments
   to install project dependencies
5. **Optional Package**: Installs a specific package version if provided (useful
   for compatibility testing)
6. **Environment Diagnostics**: Displays Python configuration, installed
   packages, and dependency tree
7. **Verification**: Runs `uv pip check` to verify environment integrity

## Advanced Usage

### Testing Against Multiple Python Versions

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python ${{ matrix.python-version }}
        uses: durandtibo/setup-venv-uv-action@v0.0.3
        with:
          python-version: ${{ matrix.python-version }}

      - name: Run tests
        run: python -m pytest
```

### Testing Dependency Compatibility

```yaml
jobs:
  test-compatibility:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        package-version: ["1.0.0", "2.0.0"]
    steps:
      - uses: actions/checkout@v4

      - name: Setup with specific dependency version
        uses: durandtibo/setup-venv-uv-action@v0.0.3
        with:
          package-name: "requests"
          package-version: ${{ matrix.package-version }}

      - name: Test with this version
        run: python -m pytest
```

### Cross-Platform Testing

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python environment
        uses: durandtibo/setup-venv-uv-action@v0.0.3

      - name: Run tests
        run: python -m pytest
```

## Requirements

This action expects:

- A `pyproject.toml` file in your repository root (for dependency management)
- A `tasks.py` file with `invoke` tasks (specifically an `install` task)
- `invoke>=2.2.0` in your project dependencies (e.g., in a dev dependency group)

Note: While the action installs invoke before running your tasks, it must be
included in your project dependencies to ensure it remains available after the
`uv sync` step.

### Example `pyproject.toml`

```toml
[dependency-groups]
dev = [
    "invoke >=2.2.0,<3.0",
]
```

### Example `tasks.py`

```python
from invoke.tasks import task
from invoke.context import Context


@task
def install(c: Context) -> None:
    """Install packages."""
    c.run("uv sync --frozen", pty=True)
    c.run("uv pip install -e .", pty=True)
```

## Troubleshooting

### Environment Verification Warnings

The action runs `uv pip check` to verify environment integrity. This step uses
`continue-on-error: true`, so dependency conflicts won't fail your workflow but
will be visible in the logs for debugging.

### Missing Dependencies

If the action fails during dependency installation, check:

1. Your `pyproject.toml` has correct dependency specifications
2. The `tasks.py` file exists and has an `install` task

### Custom Install Arguments Not Working

The `install-args` input is passed directly to your `inv install` command.
Ensure your `install` task in `tasks.py` accepts and handles these arguments if
needed.

## Related Actions

- [astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) - Used internally
  for uv installation
- [durandtibo/uv-install-package-action](https://github.com/durandtibo/uv-install-package-action)
  \- Used internally for package installation

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for
details.

## License

This project is licensed under the BSD 3-Clause License - see the
[LICENSE](LICENSE) file for details.
