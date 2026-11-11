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
- **Debug-Friendly**: Always shows the versions, the installed packages, and the
  dependency tree

## Usage

> **Note**: the examples use the latest release tag. Inputs and outputs that
> the tag does not have yet (`uv-version`, `working-directory`,
> `extra-packages`, `enable-cache` and all the outputs are missing from
> `v0.2.0`) are ignored with a warning. Use `@main` to try them before the next
> release.

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

### With a Project in a Subfolder

```yaml
- name: Setup Python environment for a project in a subfolder
  uses: durandtibo/setup-venv-uv-action@v0.2.0
  with:
    working-directory: "python"
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

| Input                  | Description                                                                                                                                        | Required | Default  |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | -------- |
| `python-version`       | Python version to use (e.g., `"3.13"`, `"3.12"`, `"3.11"`, `"3.10"`) or any version request supported by `uv` (e.g., `">=3.12,<3.14"`)             | No       | `"3.14"` |
| `uv-version`           | Version of `uv` to install (e.g., `"0.9.0"`, `"0.9.x"`, `">=0.9,<0.10"`). Leave empty to use the `required-version` of the project, or the latest. | No       | `""`     |
| `package-name`         | Optional package whose version varies in a test matrix, checked against PyPI and the Python version. Leave empty to skip.                          | No       | `""`     |
| `package-version`      | Optional version of `package-name` (e.g., `"1.0.0"`), not a specifier. Leave empty to install the latest.                                          | No       | `""`     |
| `install-args`         | Optional arguments passed to the `inv env.install` command (e.g., `--no-optional-deps`, `--groups=dev,docs`). Split on whitespace, no globbing.    | No       | `""`     |
| `package-install-args` | Optional arguments passed to `uv pip install` when installing `package-name` (e.g., `--upgrade`). Relative paths start at the workspace root.      | No       | `""`     |
| `working-directory`    | Directory that contains the project (`pyproject.toml`, `uv.lock`, `tasks.py`), relative to the workspace.                                          | No       | `"."`    |
| `enable-cache`         | Enable the GitHub Actions cache of `uv` (`"true"`, `"false"` or `"auto"`). `"auto"` enables it on GitHub-hosted runners only.                      | No       | `"auto"` |
| `extra-packages`       | Optional additional packages to install after the project dependencies, one requirement per line. Not locked. Leave empty to skip.                 | No       | `""`     |

Use `package-name` for one package whose version varies in a matrix and may not
exist for the Python version (the install is skipped with a warning in that
case), and `extra-packages` for tools that always exist (`pytest-xdist`).

## Outputs

| Output              | Description                                                                                                                                                                      |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cache-hit`         | Whether the `uv` cache was restored (`true` or `false`). Empty when the cache is disabled.                                                                                       |
| `uv-version`        | Version of `uv` that was installed (`0.9.0`).                                                                                                                                    |
| `python-version`    | Full version of the Python interpreter of the environment (`3.14.0`)                                                                                                             |
| `package-installed` | Whether `package-name` was installed (`true` or `false`). `false` when `package-name` is empty or when the version is not valid for the Python version (the install is skipped). |

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

1. **Validates the Inputs and the Project** (one step per input or check): fails
   with a clear message, before anything is installed, when an input is invalid or a project file is missing. The rules are in
   [Error: `Invalid input`](#error-invalid-input) and
   [Error: `Missing project file`](#error-missing-project-file). It warns about
   [ignored inputs](#warning-ignored-input)
2. **Installs uv and Python**: Uses
   [astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) to install the
   `uv` package manager (see `uv-version`), set up the requested
   `python-version`, and activate the environment, and restores the `uv` cache
   (see `enable-cache`). It fails if `uv` or Python cannot be installed
3. **Installs Task Runner** (two steps): Reads the exact version of
   [`invoke-tasklib`](https://github.com/durandtibo/invoke-tasklib) from
   `uv.lock` (`uv export --frozen`), then installs it for running project tasks.
   It fails when `invoke-tasklib` is not in `uv.lock`
   (see [Error: `Missing invoke-tasklib`](#error-missing-invoke-tasklib)). These
   steps run in `working-directory`, so `uv` reads the `uv.toml` of the project
   (for example its index settings)
4. **Installs Dependencies**: Runs `inv env.install ${install-args}` to run
   `uv sync --frozen` and install the current project in editable mode
5. **Optional Package**: If `package-name` is set, installs that specific
   package/version via
   [durandtibo/uv-install-package-action](https://github.com/durandtibo/uv-install-package-action)
   (useful for dependency compatibility testing: it checks that the version
   exists for the Python version)
6. **Extra Packages**: If `extra-packages` is set, installs each listed
   requirement with `uv pip install`. These packages are not locked: they are
   not in `uv.lock`, and they are not checked against PyPI
7. **Reports the Environment** (one command per step, always run):
   shows the versions of `uv` and Python, the installed packages
   (`uv pip list`), the dependency tree (`uv pip tree --show-version-specifiers`)
   and the result of `uv pip check`, which detects missing dependencies, version
   conflicts and broken installations
8. **Sets Outputs**: Exposes the full `python-version` of the environment and
   `package-installed` (the `uv-version` and `cache-hit` outputs come from
   `astral-sh/setup-uv`)

The steps of the report use `continue-on-error: true`, so a failure
is logged but does not fail the action (see
[Failure Behavior](#failure-behavior)).

## Failure Behavior

| Steps                                                                                                                                     | On error                                                    |
| ----------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Validate inputs and project files, install `uv`, install `invoke-tasklib`, install dependencies, install packages, install extra packages | The action fails                                            |
| The report steps, including `uv pip check`                                                                                                | Logged, but the action succeeds (`continue-on-error: true`) |

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
        id: setup
        uses: durandtibo/setup-venv-uv-action@v0.2.0
        with:
          package-name: "requests"
          package-version: ${{ matrix.package-version }}

      - name: Test with this version
        if: ${{ steps.setup.outputs.package-installed == 'true' }}
        run: python -m pytest
```

A version that does not exist for the Python version is skipped with a warning,
and the action succeeds. `package-installed` is then `false`, so the tests of
that combination can be skipped, as above. A matrix of packages and Python
versions does not fail for the combinations that do not exist.

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
- A configuration of `invoke-tasklib` with your package name
  (`tasklib.package.name`), usually in an `invoke.yaml` file. `inv env.install`
  fails without it, unless `--groups` is passed in `install-args`. The action
  does not check it, because `invoke` reads other configuration sources too
- `invoke-tasklib>=0.0.8,<1.0.0` in your project dependencies (e.g., in a dev
  dependency group), so that it is in `uv.lock`: the action installs the exact
  locked version

The action uses one task of the collection, `env.install`, which installs the
dependencies. If it is missing, the action fails.

Note: The action installs the version of `invoke-tasklib` that is locked in
`uv.lock` before running your tasks, and fails when it is not in the lock file.
If your `install-args` excludes the dependency group of `invoke-tasklib`,
`inv env.install` may remove it from the environment afterwards: the action
does not need `inv` after that step, but a later step of your workflow that
uses `inv` must install the group itself.

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
3. The `invoke-tasklib` configuration has your package name
   (`tasklib.package.name`, usually in `invoke.yaml`)

### Error: `Missing project file`

The action checks, before installing anything, that `pyproject.toml`, `uv.lock`
and `tasks.py` exist in the project directory. A missing file is reported by
name. Set `working-directory` if the project is in a subfolder, commit
`uv.lock` (`uv lock`), and check that `actions/checkout` runs before the action.
`tasks.py` must contain:

```python
from invoke_tasklib import ns
```

### Error: `Missing env.install task`

`inv env.install` fails with `No idea what 'env.install' is!` if the task is
not defined. Check that `tasks.py` exposes the `invoke-tasklib` collection (see
above).

### Error: `Missing invoke-tasklib`

The action reads the exact version of `invoke-tasklib` from `uv.lock` before
installing the dependencies, so that the version is locked with the other
dependencies. The error means that `invoke-tasklib` is not in the lock file. Add
it to a dependency group, then update and commit `uv.lock`:

```toml
[dependency-groups]
dev = [
    "invoke-tasklib >=0.0.8,<1.0.0",
]
```

```shell
uv lock
```

### Error: `Invalid input`

The input `enable-cache` must be `"true"`, `"false"` or `"auto"`. Quote the values in YAML so
that they are passed as strings.

The input `working-directory` must be a path relative to the workspace (it does
not start with `/`), without `..`, of a directory that exists. If it does not exist, check that
`actions/checkout` runs before the action.

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

### Progress Bars of `uv`

The action does not configure the progress bars of `uv`: `uv` draws them only
when its output is a terminal, which a workflow log is not. To change the
behavior, set the environment variable `UV_NO_PROGRESS` in the `env:` of the
job or of the step.

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
