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
- **Linux and macOS**: Tested on the Linux and macOS GitHub-hosted runners
- **Debug-Friendly**: Always shows the Python interpreters, the installed
  packages, and the dependency tree

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

### With the Python Version of the Project

By default, `python-version` is empty and `uv` selects the Python version of the
project: the `.python-version` file of `working-directory`, otherwise the
`requires-python` of its `pyproject.toml`.

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

### With a Specific Package Version

```yaml
- name: Setup Python environment with numpy 1.26.0
  uses: durandtibo/setup-venv-uv-action@v0.2.0
  with:
    python-version: "3.12"
    extra-packages: "numpy==1.26.0"
```

### With Custom Install Arguments

```yaml
- name: Setup Python environment without optional dependencies
  uses: durandtibo/setup-venv-uv-action@v0.2.0
  with:
    install-args: "--no-optional-deps"
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
      requests[socks]>=2.31
      numpy==1.26.0
```

### Without the uv Cache

```yaml
- name: Setup Python environment without the uv cache
  uses: durandtibo/setup-venv-uv-action@v0.2.0
  with:
    enable-cache: "false"
```

## Inputs

The table is generated from `action.yaml` by `make generate-readme-inputs`.

<!-- inputs:start -->

| Input               | Description                                                                                                                                                                                                                                                                                          | Required | Default  |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | -------- |
| `python-version`    | Python version to use (e.g., `3.13`, `3.12`, `3.11`, `3.10`) or any version request supported by uv (e.g., `>=3.12,<3.14`). Leave empty to let uv select the version of the project (`.python-version`, then `requires-python` of `pyproject.toml`).                                                 | No       | `""`     |
| `uv-version`        | Version of uv to install (e.g., `0.9.0`, `0.9.x`, `>=0.9,<0.10` or `latest`). Leave empty to use the `required-version` of the project (`uv.toml` or `pyproject.toml`) if any, and the latest version otherwise.                                                                                     | No       | `""`     |
| `install-args`      | Optional arguments passed to the `inv env.install` command (e.g., `--no-optional-deps`, `--groups=dev,docs`, or custom flags supported by your invoke-tasklib configuration). The value is split on whitespace: quotes are not interpreted and glob characters are kept as is.                       | No       | `""`     |
| `extra-packages`    | Optional additional packages to install after the project dependencies, one requirement per line (e.g., `pytest-xdist`, `numpy==1.26.0` or `requests[socks]>=2.31`). Use it to test a specific version of a dependency. A line cannot be an option: it must not start with `-`. Leave empty to skip. | No       | `""`     |
| `enable-cache`      | Enable the GitHub Actions cache of uv (`true`, `false` or `auto`). `auto` (default) enables the cache on GitHub-hosted runners and disables it elsewhere, like astral-sh/setup-uv. The cache is keyed on the lock files of the project.                                                              | No       | `"auto"` |
| `working-directory` | Directory that contains the project (`pyproject.toml`, `uv.lock`, `tasks.py`, `invoke.yaml`), relative to the workspace. Use it for repositories where the Python project is in a subfolder.                                                                                                         | No       | `"."`    |

<!-- inputs:end -->

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

1. **Validates the Inputs and the Project** (steps 1.1 to 1.4, one step per
   input or check): fails with a clear message, before anything is installed,
   when an input is invalid or a project file is missing. The rules are in
   [Error: `Invalid input`](#error-invalid-input) and
   [Error: `Missing project file`](#error-missing-project-file)
2. **Installs uv and Python**: Uses
   [astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) to install the
   `uv` package manager (see `uv-version`), set up the requested
   `python-version`, and activate the environment, and restores the `uv` cache
   (see `enable-cache`). It fails if `uv` or Python cannot be installed
3. **Installs Task Runner** (steps 3.1 and 3.2): Reads the exact version of
   [`invoke-tasklib`](https://github.com/durandtibo/invoke-tasklib) from
   `uv.lock` (`uv export --frozen`), then installs it for running project tasks.
   It fails when `invoke-tasklib` is not in `uv.lock`
   (see [Error: `Missing invoke-tasklib`](#error-missing-invoke-tasklib)). These
   steps run in `working-directory`, so `uv` reads the `uv.toml` of the project
   (for example its index settings)
4. **Installs Dependencies**: Runs `inv env.install ${install-args}` to run
   `uv sync --frozen` and install the current project in editable mode
5. **Extra Packages**: If `extra-packages` is set, installs each listed
   requirement with `uv pip install`, after the project dependencies (useful to
   test a specific version of a dependency, such as `numpy==1.26.0`)
6. **Reports the Environment** (steps 6.1 to 6.5, one command each, always run):
   shows the versions of `uv` and Python, the Python interpreters managed by
   `uv` (`uv python list --only-installed`), the installed packages
   (`uv pip list`), the dependency tree (`uv pip tree --show-version-specifiers`)
   and the result of `uv pip check`, which detects missing dependencies, version
   conflicts and broken installations
7. **Sets Outputs**: Exposes the full `python-version` of the environment
   (the `uv-version` output comes from `astral-sh/setup-uv`)

The steps of the report (6.1 to 6.5) use `continue-on-error: true`, so a failure
is logged but does not fail the action (see
[Failure Behavior](#failure-behavior)).

## Failure Behavior

| Steps                                                                                                                   | On error                                                    |
| ----------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Validate inputs and project files, install `uv`, install `invoke-tasklib`, install dependencies, install extra packages | The action fails                                            |
| The report steps (6.1 to 6.5), including `uv pip check`                                                                 | Logged, but the action succeeds (`continue-on-error: true`) |

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
        requests-version: ["2.31.0", "2.32.5"]
    steps:
      - uses: actions/checkout@v7

      - name: Setup with specific dependency version
        uses: durandtibo/setup-venv-uv-action@v0.2.0
        with:
          extra-packages: "requests==${{ matrix.requests-version }}"

      - name: Test with this version
        run: python -m pytest
```

### Testing on Linux and macOS

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

The project contract: the project directory (the repository root, or the
`working-directory` input) must contain the following files. The action checks
the first three before installing anything (see
[Error: `Missing project file`](#error-missing-project-file)).

- A `pyproject.toml` file (for dependency management)
- A `uv.lock` file, committed to the repository: dependencies are installed
  with `uv sync --frozen`, which never updates the lock file
- A `tasks.py` file that exposes the
  [`invoke-tasklib`](https://github.com/durandtibo/invoke-tasklib) task
  collection
- An `invoke.yaml` file configuring `invoke-tasklib` with your package name
- `invoke-tasklib>=0.0.8,<1.0.0` in a dependency group or an extra of
  `pyproject.toml` that `install-args` installs (the `dev` group by default).
  It must be in `uv.lock`: the action installs the exact locked version and
  fails otherwise (see
  [Error: `Missing invoke-tasklib`](#error-missing-invoke-tasklib))

The action uses one task of the collection, `env.install`, which installs the
dependencies. If it is missing, the action fails.

If your `install-args` excludes the dependency group of `invoke-tasklib`,
`inv env.install` may remove it from the environment afterwards. The action
does not need `inv` after that step, but a later step of your workflow that
uses `inv` is responsible for installing the group.

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

## Migrating from v0.2.0

The next release removes inputs and tightens the checks. Unknown inputs only
produce a workflow warning, so a workflow that still passes a removed input
keeps running, but loses the feature.

| Before                                                  | After                                                                         |
| ------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `package-name: x` + `package-version: 1.0`              | `extra-packages: x==1.0`                                                      |
| `package-install-args: --upgrade`                       | Pin or range in `extra-packages` (`x>=1`)                                     |
| `verbose: "false"`                                      | Input removed; the report steps always run                                    |
| `uv-no-progress: "false"`                               | Input removed; set `UV_NO_PROGRESS` in the `env:` of your job if needed       |
| `python-version` default `3.14`                         | Default empty: `.python-version` or `requires-python` is used                 |
| `invoke-tasklib` missing from the project               | Fails in step 3.1 with the fix (was a warning or notice and a reinstall)      |
| `invoke-tasklib` version from the `pyproject.toml` spec | Exact version from `uv.lock`                                                  |
| Project without `uv.lock`                               | Fails in step 1.3 (was an error from `uv sync`)                               |
| `env.show-*` tasks used by the diagnostics              | Not needed: the reports use `uv` commands, and only `env.install` is required |

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

Each validated input has its own step (1.1 to 1.4), which fails before anything
is installed. The inputs `python-version`, `uv-version` and `install-args` are
not validated, because only `uv`, `setup-uv` and `invoke-tasklib` can interpret
them: an invalid value fails in the step that uses it.

The input `enable-cache` must be `"true"`, `"false"` or `"auto"`. Quote the
value in YAML so that it is passed as a string.

The input `working-directory` must be a path relative to the workspace (it does
not start with `/`), without `..`, of a directory that exists. If it does not
exist, check that `actions/checkout` runs before the action.

The input `extra-packages` must contain one requirement per line (e.g.,
`pytest-xdist` or `requests>=2.31`). A line that starts with `-` is rejected,
because it would be an option of `uv pip install` (such as `--index-url=...`,
`--pre` or `-e .`) and not a requirement. Put the options that you need in the
configuration of `uv` (`uv.toml`, `UV_*` environment variables). To get the
latest version of a package, list it without a version; to bound it, use a range
(`numpy>=2`).

### Progress Bars

`uv` hides its progress bars when its output is not a terminal, which is the
case in the log of a workflow, so the action has no input for it. To force a
`uv` setting for all the steps, set the environment variable in your workflow,
for example `env: { UV_NO_PROGRESS: "1" }` at the job level.

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

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for
details.

## License

This project is licensed under the BSD 3-Clause License - see the
[LICENSE](LICENSE) file for details.
