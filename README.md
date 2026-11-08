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
- **Cross-Platform**: Tested on the Linux and macOS GitHub-hosted runners
  (Windows is not tested)
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
        uses: durandtibo/setup-venv-uv-action@v0.2.0

      - name: Run tests
        run: |
          python -m pytest
```

### With Custom Python Version

```yaml
- name: Setup Python environment
  uses: durandtibo/setup-venv-uv-action@v0.2.0
  with:
    python-version: "3.11"
```

### With a Python Version Range

```yaml
- name: Setup Python environment with a Python version range
  uses: durandtibo/setup-venv-uv-action@v0.2.0
  with:
    python-version: ">=3.12,<3.14"
```

### With Specific Package Installation

```yaml
- name: Setup Python environment with numpy
  uses: durandtibo/setup-venv-uv-action@v0.2.0
  with:
    python-version: "3.12"
    package-name: "numpy"
    package-version: "1.26.0"
```

### With Custom Install Arguments

```yaml
- name: Setup Python environment without optional dependencies
  uses: durandtibo/setup-venv-uv-action@v0.2.0
  with:
    install-args: "--no-optional-deps"
```

### With Custom Package Install Arguments

```yaml
- name: Setup Python environment and upgrade a specific package
  uses: durandtibo/setup-venv-uv-action@v0.2.0
  with:
    package-name: "numpy"
    package-install-args: "--upgrade"
```

### With UV Progress Bars Enabled

```yaml
- name: Setup Python environment with uv progress bars
  uses: durandtibo/setup-venv-uv-action@v0.2.0
  with:
    uv-no-progress: "false"
```

### With a Specific invoke-tasklib Version

```yaml
- name: Setup Python environment with a pinned invoke-tasklib
  uses: durandtibo/setup-venv-uv-action@v0.2.0
  with:
    invoke-tasklib-version: "==0.0.8"
```

### With a Project in a Subfolder

```yaml
- name: Setup Python environment for a project in a subfolder
  uses: durandtibo/setup-venv-uv-action@v0.2.0
  with:
    working-directory: "python"
```

### With Quieter Logs

```yaml
- name: Setup Python environment without the diagnostic steps
  uses: durandtibo/setup-venv-uv-action@v0.2.0
  with:
    verbose: "false"
```

### With Extra Packages

```yaml
- name: Setup Python environment with extra tools
  uses: durandtibo/setup-venv-uv-action@v0.2.0
  with:
    extra-packages: |
      pytest-xdist
      requests>=2.31
```

### Without the uv Cache

```yaml
- name: Setup Python environment without the uv cache
  uses: durandtibo/setup-venv-uv-action@v0.2.0
  with:
    enable-cache: "false"
```

## Inputs

| Input                    | Description                                                                                                                                          | Required | Default            |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ------------------ |
| `python-version`         | Python version to use (e.g., `"3.13"`, `"3.12"`, `"3.11"`, `"3.10"`) or any version request supported by `uv` (e.g., `">=3.12,<3.14"`)               | No       | `"3.14"`           |
| `package-name`           | Optional package name to install for dependency compatibility testing. Used with `package-version`. Leave empty to skip.                             | No       | `""`               |
| `package-version`        | Optional package version to install (e.g., `"1.0.0"`). Only used when `package-name` is specified. Leave empty to install latest.                    | No       | `""`               |
| `install-args`           | Optional arguments passed to the `inv env.install` command (e.g., `--no-optional-deps`, `--groups=dev,docs`). Split on whitespace, no globbing.      | No       | `""`               |
| `package-install-args`   | Optional arguments passed to `uv pip install` when installing `package-name` (e.g., `--upgrade`).                                                    | No       | `""`               |
| `invoke-tasklib-version` | Version specifier of `invoke-tasklib` installed before running the project tasks (e.g., `">=0.0.8,<1.0.0"`, `"==0.0.8"`). Must include the operator. | No       | `">=0.0.8,<1.0.0"` |
| `working-directory`      | Directory that contains the project (`pyproject.toml`, `tasks.py`, `invoke.yaml`), relative to the workspace.                                        | No       | `"."`              |
| `enable-cache`           | Enable the GitHub Actions cache of `uv` (`"true"`, `"false"` or `"auto"`). `"auto"` enables it on GitHub-hosted runners only.                        | No       | `"auto"`           |
| `extra-packages`         | Optional additional packages to install after the project dependencies, one requirement per line. Leave empty to skip.                               | No       | `""`               |
| `verbose`                | Run the diagnostic steps (Python configuration, installed packages, dependency tree, environment check). Set to `"false"` for quieter logs.          | No       | `"true"`           |
| `uv-no-progress`         | Disable `uv` progress bars (sets the `UV_NO_PROGRESS` env var for the install steps).                                                                | No       | `"true"`           |

## Outputs

| Output           | Description                                                                                |
| ---------------- | ------------------------------------------------------------------------------------------ |
| `cache-hit`      | Whether the `uv` cache was restored (`true` or `false`). Empty when the cache is disabled. |
| `python-version` | Full version of the Python interpreter of the environment (`3.14.0`)                       |

Example:

```yaml
- name: Setup Python environment
  id: setup
  uses: durandtibo/setup-venv-uv-action@v0.2.0

- name: Show the Python version
  run: echo "Python ${{ steps.setup.outputs.python-version }}"
```

## What This Action Does

This action performs the following steps:

1. **Validates Inputs**: Fails with a clear message when a boolean-like input
   (`uv-no-progress`, `verbose`, `enable-cache`) is invalid, or when
   `working-directory` is absolute, outside of the workspace or not an existing
   directory. It warns about inputs that are ignored (`package-version` or
   `package-install-args` without `package-name`)
2. **Installs uv and Python**: Uses
   [astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) to install the
   `uv` package manager, set up the requested `python-version`, and activate
   the environment, and restores the `uv` cache (see `enable-cache`)
3. **Verifies Installation**: Checks that `uv` and `python` are available in
   PATH
4. **Installs Task Runner**: Installs
   [`invoke-tasklib`](https://github.com/durandtibo/invoke-tasklib) for
   running project tasks
5. **Verifies Project Tasks**: Fails early with a clear message if `tasks.py`
   or the `env.install` task is missing
6. **Installs Dependencies**: Runs `inv env.install ${install-args}` to run
   `uv sync --frozen` and install the current project in editable mode. When
   `verbose` is `"true"`, it warns if `invoke-tasklib` is no longer installed
   afterwards, because it is not a dependency of the project
7. **Optional Package**: If `package-name` is set, installs that specific
   package/version via
   [durandtibo/uv-install-package-action](https://github.com/durandtibo/uv-install-package-action)
   (useful for dependency compatibility testing)
8. **Extra Packages**: If `extra-packages` is set, installs each listed
   requirement with `uv pip install`
9. **Shows Python Config**: Runs `inv env.show-python-config` to display all
   Python versions managed by `uv`, the active interpreter, and its full path
10. **Shows Installed Packages**: Runs `inv env.show-installed-packages` to
    list every installed package and version
11. **Shows Dependency Tree**: Runs `uv pip tree --show-version-specifiers` to
    display the full dependency graph
12. **Verifies Environment**: Runs `uv pip check` (with
    `continue-on-error: true`) to detect missing dependencies, version
    conflicts, or broken installations without failing the workflow
13. **Sets Outputs**: Exposes the full `python-version` of the environment

## Failure Behavior

| Steps                                                                                       | On error                                                    |
| ------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Validate inputs, install `uv`, verify project tasks, install dependencies, install packages | The action fails                                            |
| Show Python config, show installed packages, show dependency tree, `uv pip check`           | Logged, but the action succeeds (`continue-on-error: true`) |

The four diagnostic steps are skipped when `verbose` is `"false"`.

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
        uses: durandtibo/setup-venv-uv-action@v0.2.0
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
        uses: durandtibo/setup-venv-uv-action@v0.2.0
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
        uses: durandtibo/setup-venv-uv-action@v0.2.0

      - name: Run tests
        run: python -m pytest
```

## Requirements

This action expects the following files in the project directory (the
repository root, or the `working-directory` input):

- A `pyproject.toml` file (for dependency management)
- A `uv.lock` file, committed to the repository: dependencies are installed
  with `uv sync --frozen`, which never updates the lock file
- A `tasks.py` file that exposes the
  [`invoke-tasklib`](https://github.com/durandtibo/invoke-tasklib) task
  collection
- An `invoke.yaml` file configuring `invoke-tasklib` with your package name
- `invoke-tasklib>=0.0.8,<1.0.0` in your project dependencies (e.g., in a dev
  dependency group)

The action uses the following tasks of the collection:

| Task                          | Used by                      | If missing                                                             |
| ----------------------------- | ---------------------------- | ---------------------------------------------------------------------- |
| `env.install`                 | Installs the dependencies    | The action fails                                                       |
| `env.show-python-config`      | Shows the Python config      | A warning, then the diagnostic step fails but does not fail the action |
| `env.show-installed-packages` | Shows the installed packages | A warning, then the diagnostic step fails but does not fail the action |

Note: While the action installs `invoke-tasklib` before running your tasks, it
must be included in your project dependencies to ensure it remains available
after the `uv sync` step. Use the `invoke-tasklib-version` input to change the
version installed by the action.

### Example `pyproject.toml`

```toml
[dependency-groups]
dev = [
    "invoke-tasklib >=0.0.8,<1.0.0",
]
```

### Example `tasks.py`

```python
from invoke_tasklib import ns
```

### Example `invoke.yaml`

```yaml
tasklib:
  package:
    name: my_package
```

## Troubleshooting

### Environment Verification Warnings

The action runs `uv pip check` to verify environment integrity. This step uses
`continue-on-error: true`, so dependency conflicts won't fail your workflow but
will be visible in the logs for debugging.

### Missing Dependencies

If the action fails during dependency installation, check:

1. Your `pyproject.toml` has correct dependency specifications
2. The `tasks.py` file exists and exposes the `invoke-tasklib` task collection
3. An `invoke.yaml` file exists with your package name configured

### Error: `Missing tasks.py` or `Missing env.install task`

The step "Verify project tasks" runs `inv --list` in the project directory and
fails if the `env.install` task is not defined. Check that `tasks.py` exists in
the project directory (set `working-directory` if the project is in a
subfolder) and contains:

```python
from invoke_tasklib import ns
```

### Error: `Invalid input`

The inputs `uv-no-progress`, `verbose` and `enable-cache` must be `"true"` or
`"false"` (`enable-cache` also accepts `"auto"`). Quote the values in YAML so
that they are passed as strings.

The input `working-directory` must be a path relative to the workspace, without
`..`, of a directory that exists. If it does not exist, check that
`actions/checkout` runs before the action.

### Warning: `Ignored input`

`package-version` and `package-install-args` only apply when `package-name` is
set. Set `package-name` or remove the input.

### Custom Install Arguments Not Working

The `install-args` input is passed directly to the `inv env.install` command
(e.g., `--no-optional-deps`, `--groups=dev,docs`). The value is split on
whitespace: quotes are not interpreted, so an argument cannot contain a space,
and glob characters (`*`, `?`, `[`) are passed as is instead of being expanded
to file names. See the
[invoke-tasklib documentation](https://durandtibo.github.io/invoke-tasklib/)
for the full list of supported options.

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
