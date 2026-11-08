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
- **Linux and macOS**: Tested on the Linux and macOS GitHub-hosted runners.
  Windows runners are not tested and not supported
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
      - uses: actions/checkout@v7

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

### With a Specific uv Version

```yaml
- name: Setup Python environment with a pinned uv version
  uses: durandtibo/setup-venv-uv-action@v0.2.0
  with:
    uv-version: "0.9.0"
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

| Input                    | Description                                                                                                                                                           | Required | Default            |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ------------------ |
| `python-version`         | Python version to use (e.g., `"3.13"`, `"3.12"`, `"3.11"`, `"3.10"`) or any version request supported by `uv` (e.g., `">=3.12,<3.14"`)                                | No       | `"3.14"`           |
| `uv-version`             | Version of `uv` to install (e.g., `"0.9.0"`, `"0.9.x"`, `">=0.9,<0.10"`). Leave empty to use the `required-version` of the project, or the latest.                    | No       | `""`               |
| `package-name`           | Optional package name to install for dependency compatibility testing. Used with `package-version`. Leave empty to skip.                                              | No       | `""`               |
| `package-version`        | Optional package version to install (e.g., `"1.0.0"`). Must be a version, not a specifier. Only used when `package-name` is specified. Leave empty to install latest. | No       | `""`               |
| `install-args`           | Optional arguments passed to the `inv env.install` command (e.g., `--no-optional-deps`, `--groups=dev,docs`). Split on whitespace, no globbing.                       | No       | `""`               |
| `package-install-args`   | Optional arguments passed to `uv pip install` when installing `package-name` (e.g., `--upgrade`). Relative paths start at the workspace root.                         | No       | `""`               |
| `invoke-tasklib-version` | Version specifier of `invoke-tasklib` installed before running the project tasks (e.g., `">=0.0.8,<1.0.0"`, `"==0.0.8"`). Must include the operator.                  | No       | `">=0.0.8,<1.0.0"` |
| `working-directory`      | Directory that contains the project (`pyproject.toml`, `tasks.py`, `invoke.yaml`), relative to the workspace.                                                         | No       | `"."`              |
| `enable-cache`           | Enable the GitHub Actions cache of `uv` (`"true"`, `"false"` or `"auto"`). `"auto"` enables it on GitHub-hosted runners only.                                         | No       | `"auto"`           |
| `extra-packages`         | Optional additional packages to install after the project dependencies, one requirement per line, not options (no `-` at the start of a line). Leave empty to skip.   | No       | `""`               |
| `verbose`                | Run the diagnostic steps (Python configuration, installed packages, dependency tree, environment check). Set to `"false"` for quieter logs.                           | No       | `"true"`           |
| `uv-no-progress`         | Disable `uv` progress bars (sets the `UV_NO_PROGRESS` env var for the steps that run `uv`).                                                                           | No       | `"true"`           |

## Outputs

| Output           | Description                                                                                |
| ---------------- | ------------------------------------------------------------------------------------------ |
| `cache-hit`      | Whether the `uv` cache was restored (`true` or `false`). Empty when the cache is disabled. |
| `uv-version`     | Version of `uv` that was installed (`0.9.0`).                                              |
| `python-version` | Full version of the Python interpreter of the environment (`3.14.0`)                       |

Example:

```yaml
- name: Setup Python environment
  id: setup
  uses: durandtibo/setup-venv-uv-action@v0.2.0

- name: Show the Python and uv versions
  run: |
    echo "Python ${{ steps.setup.outputs.python-version }}"
    echo "uv ${{ steps.setup.outputs.uv-version }}"
```

## What This Action Does

This action performs the following steps:

1. **Validates Boolean Inputs**: Fails with a clear message when
   `uv-no-progress`, `verbose` or `enable-cache` is invalid
2. **Validates the Working Directory**: Fails when `working-directory` is
   absolute, outside of the workspace or not an existing directory
3. **Validates the invoke-tasklib Version**: Fails when `invoke-tasklib-version`
   is not a version specifier that starts with an operator
4. **Validates Python and Package Inputs**: Fails when `package-name` is not a
   package name, when `package-version` is not a version, or when a line of
   `extra-packages` starts with `-` (an option instead of a requirement). It
   warns about inputs that are ignored (`package-version` or
   `package-install-args` without `package-name`)
5. **Installs uv and Python**: Uses
   [astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) to install the
   `uv` package manager (see `uv-version`), set up the requested
   `python-version`, and activate the environment, and restores the `uv` cache
   (see `enable-cache`)
6. **Verifies Installation**: Checks that `uv` and `python` are available in
   PATH, and logs their paths and versions
7. **Installs Task Runner**: Installs
   [`invoke-tasklib`](https://github.com/durandtibo/invoke-tasklib) for
   running project tasks. Steps 6 and 7 run in `working-directory`, so `uv`
   reads the `uv.toml` of the project (for example its index settings)
8. **Verifies Project Tasks**: Fails early with a clear message if `tasks.py`
   or the `env.install` task is missing
9. **Installs Dependencies**: Runs `inv env.install ${install-args}` to run
   `uv sync --frozen` and install the current project in editable mode. When
   `verbose` is `"true"`, it warns if `invoke-tasklib` is no longer installed
   afterwards, because it is not a dependency of the project
10. **Optional Package**: If `package-name` is set, installs that specific
    package/version via
    [durandtibo/uv-install-package-action](https://github.com/durandtibo/uv-install-package-action)
    (useful for dependency compatibility testing)
11. **Extra Packages**: If `extra-packages` is set, installs each listed
    requirement with `uv pip install`
12. **Shows Python Config**: Runs `inv env.show-python-config` to display all
    Python versions managed by `uv`, the active interpreter, and its full path
13. **Shows Installed Packages**: Runs `inv env.show-installed-packages` to
    list every installed package and version
14. **Shows Dependency Tree**: Runs `uv pip tree --show-version-specifiers` to
    display the full dependency graph
15. **Verifies Environment**: Runs `uv pip check` to detect missing
    dependencies, version conflicts, or broken installations
16. **Sets Outputs**: Exposes the full `python-version` of the environment
    (the `uv-version` output comes from `astral-sh/setup-uv`)

Steps 12 to 15 are diagnostic steps: they only run when `verbose` is `"true"`,
and they use `continue-on-error: true`, so a failure is logged but does not fail
the action (see [Failure Behavior](#failure-behavior)).

## Failure Behavior

| Steps                                                                                                               | On error                                                    |
| ------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Validate inputs, install `uv`, verify project tasks, install dependencies, install packages, install extra packages | The action fails                                            |
| Show Python config, show installed packages, show dependency tree, `uv pip check`                                   | Logged, but the action succeeds (`continue-on-error: true`) |

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
      - uses: actions/checkout@v7

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
      - uses: actions/checkout@v7

      - name: Setup with specific dependency version
        uses: durandtibo/setup-venv-uv-action@v0.2.0
        with:
          package-name: "requests"
          package-version: ${{ matrix.package-version }}

      - name: Test with this version
        run: python -m pytest
```

### Testing on Linux and macOS

Windows runners are not tested, so they are not part of this example.

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v7

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

### Warning: `invoke-tasklib removed`

The action installs `invoke-tasklib` before your project dependencies, and
`inv env.install` runs `uv sync --frozen`, which removes every package that is
not in your lock file. If `invoke-tasklib` is not a dependency of your project,
it is removed and the diagnostic steps (`inv env.show-python-config`,
`inv env.show-installed-packages`) fail. Their failure is only logged, so the
only visible signs are this warning and the errors in these steps.

Add `invoke-tasklib` to a dependency group installed by `inv env.install` (the
`dev` group by default), then update `uv.lock`:

```toml
[dependency-groups]
dev = [
    "invoke-tasklib >=0.0.8,<1.0.0",
]
```

The warning is only emitted when `verbose` is `"true"`. With `verbose: "false"`,
the diagnostic steps are skipped, but your own later steps that use `inv` would
fail for the same reason.

### Error: `Invalid input`

The inputs `uv-no-progress`, `verbose` and `enable-cache` must be `"true"` or
`"false"` (`enable-cache` also accepts `"auto"`). Quote the values in YAML so
that they are passed as strings.

The input `working-directory` must be a path relative to the workspace, without
`..`, of a directory that exists. If it does not exist, check that
`actions/checkout` runs before the action.

The input `invoke-tasklib-version` must be a version specifier whose clauses
start with an operator, separated by commas (e.g., `">=0.0.8,<1.0.0"` or
`"==0.0.8"`). A bare version such as `"0.0.8"` is rejected: use `"==0.0.8"`. An
empty value is accepted and installs the latest version of `invoke-tasklib`.

The input `package-name` must be a package name made of letters, digits, `.`,
`_` and `-`, optionally followed by extras in brackets (e.g., `"numpy"` or
`"uvicorn[standard]"`). Put the version in `package-version` and the options in
`package-install-args`, not in `package-name`.

The input `package-version` must be a version (e.g., `"1.26.0"`, `"2.12.*"` or
`"2.0.0rc1"`), because the package is installed as
`package-name==package-version`. A specifier (`">=1.0"`), a value with spaces
or an option (`"1.0 --pre"`) is rejected. Put the options in
`package-install-args`. The input is only validated when `package-name` is set,
otherwise it is ignored with a warning.

The input `extra-packages` must contain one requirement per line (e.g.,
`pytest-xdist` or `requests>=2.31`). A line that starts with `-` is rejected,
because it would be an option of `uv pip install` (such as `--index-url=...`,
`--pre` or `-e .`) and not a requirement. Put the options that you need in the
configuration of `uv` (`uv.toml`, `UV_*` environment variables).

### Warning: `Ignored input`

`package-version` and `package-install-args` only apply when `package-name` is
set. Set `package-name` or remove the input.

### Relative Paths in `package-install-args`

The package of `package-name` is installed by
[durandtibo/uv-install-package-action](https://github.com/durandtibo/uv-install-package-action),
which has no working directory option, so this step runs in the workspace root
and not in `working-directory`. A relative path in `package-install-args` (for
example `--constraint constraints.txt`) starts at the workspace root. Other
inputs, such as `install-args` and `extra-packages`, run in `working-directory`.

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
