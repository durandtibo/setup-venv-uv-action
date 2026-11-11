# Target state of `setup-venv-uv-action`

Review date: 2026-11-11. This review replaces the previous one, which described
a state that no longer exists (it mentioned `test-local.yaml`, `verbose`, the
metadata action and a 452-line `action.yaml`). Several of its proposals are now
implemented (small validation steps, `invoke-tasklib` read from `uv.lock`, one
step per report command, matrix-based invalid-input test).

Reviewed: `action.yaml` (430 lines, 21 steps, 10 inputs, 3 outputs),
`README.md`, `.github/OVERVIEW.md`, `CLAUDE.md`, the dummy project (`tasks.py`,
`invoke.yaml`, `pyproject.toml`, `uv.lock`) and the workflows
(`ci-action.yaml`: 666 lines, 21 jobs; `nightly-test-released.yaml`: 210 lines,
9 jobs).

Nothing was run. The proposals are design decisions, not tested code. What must
be checked on a prototype before relying on it is listed in
[Open points](#9-open-points-to-verify-before-implementing).

## 1. Properties of the action

The target state must satisfy these properties. They come from `CLAUDE.md` and
`README.md`, with three additions (P2, P4, P11) that the current action only
partly meets.

| #   | Property            | Meaning                                                                                                                                                                        |
| --- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| P1  | Single purpose      | Install `uv`, set up Python, and install the project dependencies with the `inv env.install` task of `invoke-tasklib`. Nothing else.                                           |
| P2  | Project-driven      | The project decides what is installed: dependencies from the committed `uv.lock` (`--frozen`), `invoke-tasklib` from the same lock file, Python from the project when asked.   |
| P3  | Fail early, clearly | Every invalid input or missing project file fails in the first steps (group 1), before anything is installed, with an `::error title=Invalid input::` message.                 |
| P4  | One way to do it    | One input per need. No input that only changes a tool default. Logic that is not trivial (version compatibility) lives in one tested place, not re-implemented here.           |
| P5  | Fast                | No network call or third-party action that is not needed. The `uv` cache is on by default on GitHub-hosted runners.                                                            |
| P6  | Small surface       | Few inputs, each one tested and documented. One third-party action: `astral-sh/setup-uv`, pinned to a SHA with a `ratchet` comment.                                            |
| P7  | Safe                | Inputs reach shell code only through `env:`. `shell: bash` on every `run:`. Least-privilege `permissions` in the workflows.                                                    |
| P8  | Observable          | Installation steps fail the action. Reporting steps never do (`continue-on-error: true`). The result is exposed as outputs.                                                    |
| P9  | Portable            | Linux and macOS runners with `bash`. Windows is not a target: no code, test or documentation handles it.                                                                       |
| P10 | Simple steps        | One concern per step, a few lines each, numbered `N` or `N.M` inside a group. The log shows which check failed.                                                                |
| P11 | One source of truth | `action.yaml` is the reference. The README, the overview and the tests say the same thing, and a test exists for every input. A rule is written once, and drift is detectable. |

## 2. Findings on the current state

Ordered by impact. Each finding names the property it breaks.

### 2.1 The package inputs do real work, but are costly (P4, P6)

`package-name`, `package-version` and `package-install-args` are **not** a
duplicate of `extra-packages`. `durandtibo/uv-install-package-action` (built on
[`feu`](https://github.com/durandtibo/feu)) queries PyPI and checks that the
requested version exists and is installable for the active Python version. In
the pinned release, an invalid combination is skipped with a warning
(`is-valid-version=false`) instead of failing; the README of that action says an
earlier release substituted the closest valid version. This is what makes a
package x Python matrix usable: `numpy 1.24` on Python 3.13 does not exist, and
the job must not fail for it. `uv pip install numpy==1.24.0` cannot do that.
The feature is kept.

What is wrong is the surroundings:

- The step runs in the workspace root, not in `working-directory`, so a relative
  path in `package-install-args` starts somewhere else than every other path
  (documented trap).
- The caller cannot tell whether the package was installed or skipped. The
  nested action exposes `is-valid-version` and `installed-successfully`, but
  this action does not forward them.
- The nested action installs `feu` on every run (a network call) and is pinned
  by hand in `action.yaml`.
- Three inputs depend on each other, which needs two validation steps and a
  warning step.

### 2.2 `uv-no-progress` carries no weight (P4, P10)

It is copied as `UV_NO_PROGRESS` into 12 steps, has its own validation step
(1.5), a test job and a test case, and a README example. `uv` draws progress
bars only when stderr is a terminal, and a workflow log is not one (to confirm,
open point 3). A caller who wants other behaviour sets `UV_NO_PROGRESS` in
`env:` of the job.

### 2.3 The `python-version` default is hard-coded (P2)

The default `"3.14"` must be bumped by hand, and bumping it changes what every
caller gets without them touching anything. `uv` already has a convention for
the project to say it: `.python-version`, then `requires-python`. The action
should follow it, and the empty value becomes the default. Step 1.9 (the notice
about an empty value) disappears, because empty is then the normal case.

### 2.4 Documentation has drifted (P11)

Verified against the files:

| Where                 | Says                                                                                                                                       | Reality                                                                                    |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ |
| `README.md`           | Examples use `@v0.2.0` with `working-directory`, `extra-packages`, `uv-version`, `enable-cache`                                            | `v0.2.0` has none of these inputs (it has 6 inputs, no outputs): the examples cannot work. |
| `README.md`           | "Validates ... (steps 1.1 to 1.10)"                                                                                                        | The action has steps 1.1 to 1.9.                                                           |
| `README.md`           | `invoke.yaml` is required                                                                                                                  | Nothing checks it (open point 5): either it is required and validated, or it is optional.  |
| `.github/OVERVIEW.md` | Lists `bot-report-queued-runs.yaml`                                                                                                        | The file does not exist.                                                                   |
| `.github/OVERVIEW.md` | Nightly runs at 9:00 UTC; `nightly-test-released` is "called by CI workflow"                                                               | `nightly-tests.yaml` runs at 10:30 UTC and is the caller; `ci.yaml` runs at 9:10.          |
| `.github/OVERVIEW.md` | "All workflows support `workflow_dispatch`"                                                                                                | Reusable workflows with inputs do not (and `CLAUDE.md` says so).                           |
| `.github/OVERVIEW.md` | Lists the test jobs by name                                                                                                                | The list goes stale at every test change.                                                  |
| `tasks.py`            | Docstring documents `env.show-installed-packages` and `env.show-python-config`                                                             | The action uses only `env.install`.                                                        |
| `README.md` rules     | The validation rules are written in the inputs table, the step list, the `Invalid input` section, the `Troubleshooting` section and the PR | `CLAUDE.md` asks for the step list and the `Invalid input` section only.                   |
| `.github/OVERVIEW.md` | `PULL_REQUEST_TEMPLATE.md`, `dependabot.yml`, `bot-pin-action.yaml` described separately                                                   | Both `dependabot.yml` and `bot-pin-action.yaml` update action pins (open point 8).         |

The common cause is that nothing checks the documents against the code. The fix
is to write each rule once, and to add one cheap check (section 6.4).

### 2.5 The two test workflows have different roles (P11)

`ci-action.yaml` tests the code under review (`uses: ./`) on every pull request
and push. `nightly-test-released.yaml` tests the last release, which is what
consumers run, to catch regressions caused by upstream changes (`uv`,
`setup-uv`, `invoke-tasklib`). They answer different questions and both stay.

The `CLAUDE.md` rule (identical except for the header, `name` and `uses:`
line, plus jobs of inputs added after the release) is right, but the release
lag makes it invisible: `ci-action.yaml` has 21 jobs and 666 lines, the
released copy 9 jobs and 210 lines, because `v0.2.0` is 74 commits behind and
lacks most of the features. The exception now covers most of the file. The fix
is to release more often (section 8), not to merge the workflows.

### 2.6 Smaller points

- **Step 3.1** pipes `grep | sed -n '1p' | cut`. `sed -n '1p'` is redundant
  after `grep` when read by `cut`, and `|| true` hides the pipeline failure on
  purpose. One `awk` (or `grep -m1`) is enough.
- **Step 8** calls `uv python find` and then runs that interpreter to print a
  version. `python` is already the activated environment (`activate-environment:
true`), so `python -c ...` is the same and shorter.
- **Step 7.2** (`uv python list --only-installed`) lists every interpreter that
  `uv` ever downloaded on the runner. The environment's interpreter is already
  shown by 7.1. It is noise in the log and can be dropped.
- **Step 4** is correct but fragile for the caller: `install-args` is split on
  whitespace. That is a deliberate choice (documented), and cheaper than
  parsing quotes. Kept.
- **Step 6** (`extra-packages`) and **step 1.4** both implement the "trim and
  skip blank lines" loop. They validate and install different things, so they
  stay two steps, but the install loop should be the only place that builds the
  package list (step 1.4 only needs to look for a leading `-`).
- **Permissions**: the 33 job-level `actions: write` in `ci-action.yaml` and
  `nightly-test-released.yaml` look broader than needed. `setup-uv` saves the
  cache with the runtime token and does not need `actions: write` (open point
  7). If confirmed, `contents: read` is enough, which also helps the Scorecard
  `Token-Permissions` check.
- **Release lag**: the latest release is 74 commits behind `main`. The
  nightly test of the "released" action tests a version that nobody should use,
  and the README points to it. A release should follow this change (section 8).

## 3. Target interface

### 3.1 Inputs: 10 become 9

| Input                  | Default | Validated | Notes                                                                                                                                                                               |
| ---------------------- | ------- | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `python-version`       | `""`    | No        | Any `uv` version request (`3.13`, `>=3.12,<3.14`). Empty means `uv` follows the project (`.python-version`, then `requires-python`). Not validated: only `uv` can interpret it.     |
| `uv-version`           | `""`    | No        | Passed to `setup-uv` (`0.9.0`, `0.9.x`, `>=0.9,<0.10`, `latest`). Empty means the `required-version` of the project, else the latest. Not validated: only `setup-uv` can interpret. |
| `install-args`         | `""`    | No        | Split on whitespace, no quotes, no globbing, passed to `inv env.install`. Not validated: only `invoke-tasklib` can interpret it.                                                    |
| `package-name`         | `""`    | Yes       | Package for compatibility testing, installed by `uv-install-package-action` (version checked against PyPI and the Python version). Name and optional extras only.                   |
| `package-version`      | `""`    | Yes       | Version (`1.26.0`, `2.12.*`), not a specifier. Ignored with a warning without `package-name`. An invalid version for the Python version skips the install (see output).             |
| `package-install-args` | `""`    | No        | Arguments for `uv pip install` of `package-name`. Relative paths start at the workspace root (documented). Not validated: only `uv` can interpret them.                             |
| `extra-packages`       | `""`    | Yes       | One requirement per line, installed after the project with `uv pip install`, not checked against PyPI. A line that starts with `-` is rejected.                                     |
| `enable-cache`         | `auto`  | Yes       | `true`, `false` or `auto`. Passed to `setup-uv`.                                                                                                                                    |
| `working-directory`    | `.`     | Yes       | Relative path, without `..`, of an existing directory of the workspace that contains `pyproject.toml`, `uv.lock` and `tasks.py`.                                                    |

Removed: `uv-no-progress`. The package inputs and their rules are unchanged.

Consequences:

- **`package-*` vs `extra-packages`**: `package-*` is for one package whose
  version varies in a matrix and may not exist for the Python version.
  `extra-packages` is for tools that always exist (`pytest-xdist`). The README
  says so in one sentence each, so the choice is obvious.
- **A removed input is only a workflow warning in GitHub Actions.** Callers
  that still pass `uv-no-progress` keep running without it. The release notes
  list it (section 8).

### 3.2 Outputs: 3 become 4

| Output              | Source                                                                                                                                                     |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cache-hit`         | `setup-uv`                                                                                                                                                 |
| `uv-version`        | `setup-uv`                                                                                                                                                 |
| `python-version`    | `python -c` in the last step, from the venv                                                                                                                |
| `package-installed` | New. `true` if `package-name` was installed, `false` if skipped (invalid version) or not set. From `is-valid-version` of the nested action (open point 9). |

With it, a matrix job can skip its test step instead of guessing why the
package is missing: `if: steps.setup.outputs.package-installed == 'true'`.

### 3.3 Project contract (what the caller's repository must contain)

Under `working-directory`:

- `pyproject.toml` and a committed `uv.lock` (checked by step 1.3).
- `tasks.py` exposing the `invoke-tasklib` collection (checked by step 1.3).
- `invoke-tasklib` in `uv.lock`, in a dependency group or extra (step 3.1 fails
  with the fix if it is not). By default the action installs the `dev` group,
  so that is where it belongs.
- `invoke.yaml`: required or optional depending on open point 5. The README
  states whichever is true, and step 1.3 checks it only if it is required.

If `install-args` excludes the group that holds `invoke-tasklib`, `uv sync`
removes it after `env.install`. The action does not need `inv` afterwards, so it
still succeeds. A later step of the caller that needs `inv` must install the
group itself (one sentence in the README, as today).

## 4. Target `action.yaml`

Design rule: **one concern per step**, with the `# Step N.M:` comment directly
above each `- name:` (the `CLAUDE.md` rule). The step count goes from 21 to 18.
The number of steps is not a goal; the goal is that each step fits on a screen,
has one reason to fail, and has a name that tells which.

| #   | Step                                     | Fails the action | Change                                              |
| --- | ---------------------------------------- | ---------------- | --------------------------------------------------- |
| 1.1 | Validate `enable-cache`                  | Yes              | Same                                                |
| 1.2 | Validate `working-directory`             | Yes              | Same                                                |
| 1.3 | Validate the project files               | Yes              | Same (+ `invoke.yaml` if required, open point 5)    |
| 1.4 | Validate `extra-packages`                | Yes              | Same                                                |
| 1.5 | Validate `package-name`                  | Yes              | Was 1.6                                             |
| 1.6 | Validate `package-version`               | Yes              | Was 1.7                                             |
| 1.7 | Warn about ignored package inputs        | No               | Was 1.8                                             |
| 2   | Install uv and set the Python version    | Yes              | No `UV_NO_PROGRESS`; empty `python-version` allowed |
| 3.1 | Read the locked `invoke-tasklib` version | Yes              | Simpler pipeline                                    |
| 3.2 | Install `invoke-tasklib`                 | Yes              | No `UV_NO_PROGRESS`                                 |
| 4   | Install the project dependencies         | Yes              | No `UV_NO_PROGRESS`                                 |
| 5   | Install a specific package version       | Yes              | Same; `id` added to expose `package-installed`      |
| 6   | Install extra packages                   | Yes              | Same                                                |
| 7.1 | Show the versions                        | No               | Same                                                |
| 7.2 | Show the installed packages              | No               | Was 7.3                                             |
| 7.3 | Show the dependency tree                 | No               | Was 7.4                                             |
| 7.4 | Check the environment                    | No               | Was 7.5                                             |
| 8   | Set the outputs                          | Yes              | `python` instead of `uv python find`; adds output   |

Removed: 1.5 (`uv-no-progress`), 1.9 (empty `python-version` notice), old
7.2 (interpreters). Third-party actions are unchanged: `astral-sh/setup-uv` and
`durandtibo/uv-install-package-action`. The file is estimated at about 350
lines (was 430): the `UV_NO_PROGRESS` blocks about 25, the removed steps about
30, the input about 8, the rest in comments.

The rules of `CLAUDE.md` are unchanged and all kept: inputs through `env:`,
`shell: bash`, third-party actions pinned with `ratchet`, `continue-on-error`
only on the reports, `working-directory:` set only on the steps that need it.

### Group 1: validation

Every step has the same shape: the input in `env:`, an optional `if:`, a short
`run:` that prints `::error title=Invalid input::` and exits 1. A step validates
one input and reports all the problems of that input (every bad line of
`extra-packages`). The first failing step stops the action, before anything is
installed.

- **1.1 `enable-cache`**: `true`, `false` or `auto`.
- **1.2 `working-directory`**: not absolute, no `..` segment, and a directory
  of `${GITHUB_WORKSPACE}`. The error keeps the hint about `actions/checkout`.
- **1.3 Project files**: `pyproject.toml`, `uv.lock` and `tasks.py` exist in
  `working-directory`, all missing files reported in one message. It runs after
  1.2, so the directory is known to be valid.
- **1.4 `extra-packages`**: no line starts with `-` after trimming the leading
  whitespace. Skipped when the input is empty.
- **1.5, 1.6 `package-name`, `package-version`**: unchanged rules (name with
  optional extras; a version, not a specifier). **1.7** warns when
  `package-version` or `package-install-args` is set without `package-name`.

Not validated, and stated in the README and the PR: `python-version`,
`uv-version`, `install-args`, `package-install-args` (only `uv`,
`setup-uv`, `invoke-tasklib` can interpret them; a duplicate parser here would drift from the
tool).

### Step 2: Install uv and Python

```yaml
- name: Install uv and set the python version
  id: setup-uv
  uses: astral-sh/setup-uv@<sha> # ratchet:astral-sh/setup-uv@<tag>
  with:
    version: ${{ inputs.uv-version }}
    python-version: ${{ inputs.python-version }}
    working-directory: ${{ github.workspace }}/${{ inputs.working-directory }}
    enable-cache: ${{ inputs.enable-cache }}
    activate-environment: true
```

Unchanged except for the removed `env:` block. `setup-uv` creates the virtual
environment in `working-directory`, so `uv venv` reads the `.python-version` of
the project when `python-version` is empty (open point 4).

### Group 3: invoke-tasklib

Two steps, so a missing entry in the lock file and a failing installation are
different lines in the log.

**3.1 Read the locked version** (`id: tasklib`, in `working-directory`):

```bash
requirement="$(uv export --frozen --no-hashes --no-emit-project --all-groups --all-extras |
  awk '/^invoke-tasklib==/ { print $1; exit }')"
if [ -z "${requirement}" ]; then
  echo "::error title=Missing invoke-tasklib::'invoke-tasklib' is not in 'uv.lock'. Add it to a dependency group of 'pyproject.toml', then run 'uv lock' and commit the result."
  exit 1
fi
echo "requirement=${requirement}" >> "${GITHUB_OUTPUT}"
```

With `pipefail` (the default of `shell: bash`), a failure of `uv export` fails
the step; the current `|| true` that hides it is removed. `awk` replaces three
processes (`grep`, `sed`, `cut`).

**3.2 Install it**: `uv pip install "${REQUIREMENT}"`, with
`REQUIREMENT: ${{ steps.tasklib.outputs.requirement }}` in `env:`.

This stays a bootstrap from the lock file: the bootstrap is reproducible, needs
no Python before the setup, and has one failure mode.

### Step 4: Install the project dependencies

```bash
set -f # no globbing of install-args
inv env.install ${INSTALL_ARGS}
```

Same as today. If the task is missing, `inv` prints
`No idea what 'env.install' is!`, which is clear enough.

### Step 5: Install a specific package version

Same as today. Add `id: package` so that step 8 can read its `is-valid-version`
output. It stays in the workspace root (documented), because a step that uses an
action cannot set `working-directory`.

### Step 6: Install extra packages

Same as today, in `working-directory`, with `if: inputs.extra-packages != ''`.
One requirement per line, blank lines ignored, every line passed to `uv` as a
single argument. It is the only step that adds packages beyond the lock file,
and the README says so: these packages are not locked.

### Group 7: reports

Four steps, one command each, `continue-on-error: true`, in `working-directory`.
They always run, so a failure of one never hides the output of the others.

| Step | Name                        | Command                                        |
| ---- | --------------------------- | ---------------------------------------------- |
| 7.1  | Show the versions           | `uv --version; which python; python --version` |
| 7.2  | Show the installed packages | `uv pip list`                                  |
| 7.3  | Show the dependency tree    | `uv pip tree --show-version-specifiers`        |
| 7.4  | Check the environment       | `uv pip check`                                 |

### Step 8: Set the outputs

```bash
python_version="$(python -c 'import platform; print(platform.python_version())')"
echo "python-version=${python_version}" >> "${GITHUB_OUTPUT}"
echo "package-installed=${PACKAGE_VALID:-false}" >> "${GITHUB_OUTPUT}"
```

with `PACKAGE_VALID: ${{ steps.package.outputs.is-valid-version }}` in `env:`
(empty when the step did not run, hence the default). The assignment is on
its own line, so a failure of `python` fails the step
instead of writing an empty output.

## 5. Expected effect

| Metric                 | Current                             | Target                            |
| ---------------------- | ----------------------------------- | --------------------------------- |
| Inputs                 | 10                                  | 9                                 |
| Validated inputs       | 7 (+ 2 warned as ignored)           | 6 (+ 2 warned as ignored)         |
| Steps in `action.yaml` | 21                                  | 18                                |
| `action.yaml` lines    | 430                                 | about 350 (estimate)              |
| Third-party actions    | 2                                   | 2                                 |
| Python version         | Action default `3.14`               | The project's (`.python-version`) |
| Outputs                | 3                                   | 4 (`package-installed`)           |
| Test jobs              | 21 (+ 9 in the released copy)       | 17 (same set in both files)       |
| `ci-action.yaml` lines | 666 (+ 210 in the copy)             | about 560 (estimate)              |
| Documents out of date  | At least 8 statements (section 2.4) | A check in CI (section 6.4)       |

Speed: the target removes three process spawns in step 3.1 and the 12 `env:`
blocks. The gain is negligible. The
main time (Python download, dependency installation, cache restore) is
unchanged. The target is chosen for simplicity and maintainability, not for
speed, and the gain should be confirmed on a real run.

## 6. Tests and workflows

### 6.1 Rules kept

- Every input has a job that sets it and asserts its effect (not only that the
  action succeeds). Every validated input has a case that passes an invalid
  value and asserts that the action failed _in the validation_ (nothing
  installed).
- OS and Python lists come from `durandtibo/workflow-config-action`. Matrix
  values go through `env:`. Each job is independent and has `timeout-minutes`.
- A new check that fails against the released version is reported, not
  weakened.

### 6.2 Two test workflows, kept

Keep both files, with the roles of 2.5 and the `CLAUDE.md` rule unchanged:

- `ci-action.yaml` (`uses: ./`) is called by `ci.yaml`.
- `nightly-test-released.yaml` (`uses: durandtibo/setup-venv-uv-action@<sha>`
  of the last release) is called by `nightly-tests.yaml`.
- The jobs are the same, except for the jobs of inputs or behaviour added after
  the release, which exist only in `ci-action.yaml` until the release is bumped.

To keep the discipline cheap, release `v0.3.0` right after the changes of
section 8 are merged and bump the pin and the README examples in the same PR.
The two files are then identical again, except for the three lines. In the
target, `package-installed` and the empty `python-version` default are the
jobs that exist only in `ci-action.yaml` until that release.

A generator (a `make` target deriving the released file from `ci-action.yaml`
with `sed`) is not proposed: it would need a marker for the local-only jobs and
adds machinery for a rule that a release already restores.

### 6.3 Target job list

| Job                          | Input / behaviour covered                                                                                                                                                                                       |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test`                       | Defaults on every Unix OS of the config: venv active, `myproject` importable, version of the project, `cache-hit` and the 3 outputs set, `uv pip check`.                                                        |
| `test-python-version`        | `python-version`: every standard version of the config; a range (`>=3.12,<3.14`); the empty value reads `.python-version`.                                                                                      |
| `test-uv-version`            | `uv-version`: exact version, asserts the `uv-version` output and `uv --version`.                                                                                                                                |
| `test-install-args`          | `install-args`: a flag that changes the result, and the glob case (`*` stays literal), as two steps of one job.                                                                                                 |
| `test-extra-packages`        | `extra-packages`: two lines, a blank line, a pin (`numpy==2.4.0` asserted by `import numpy`), extras in brackets, a range. Tools that always exist.                                                             |
| `test-package`               | `package-name` + `package-version`: pinned version asserted by `import`; `package-install-args` effect; extras in brackets; a wildcard version (`2.12.*`).                                                      |
| `test-package-skip`          | A version that does not exist for the Python version: the action succeeds, nothing is installed, `package-installed` is `false`.                                                                                |
| `test-package-latest`        | `package-name` without `package-version` installs the latest version; `package-installed` is `true`.                                                                                                            |
| `test-cache`                 | `enable-cache`: `true`, `false`, `auto`; `cache-hit` empty when disabled.                                                                                                                                       |
| `test-working-directory`     | `working-directory`: project in a subfolder, and its `uv.toml` honoured (merges the `-uv-config` job).                                                                                                          |
| `test-missing-files`         | One case per missing project file (`pyproject.toml`, `uv.lock`, `tasks.py`): fails in step 1.3, nothing installed.                                                                                              |
| `test-tasklib-version`       | The installed `invoke-tasklib` version equals the one in `uv.lock`.                                                                                                                                             |
| `test-tasklib-missing`       | A project without it fails with `Missing invoke-tasklib`.                                                                                                                                                       |
| `test-tasklib-not-in-groups` | `install-args` excluding the group: the action succeeds.                                                                                                                                                        |
| `test-invalid-inputs`        | Matrix: `enable-cache`, `working-directory` (absolute, `..`, missing), `extra-packages` (option, indented option), `package-name` (option), `package-version` (specifier, option). Asserts failure and no `uv`. |

The dummy project gets a `.python-version` file (the same value as the newest
entry of the matrix, for example `3.14`). Without it, an empty `python-version`
picks whatever interpreter the runner image has, and the `test` job cannot
assert a version.

### 6.4 Documentation check

A drift check is cheaper than the manual care the repository relies on today.
Add one job in `ci-format.yaml` (or a `make` target in the top-level
`Makefile`, not in `.make/`) with a short script that fails when the input
names or defaults of `action.yaml` differ from the README inputs table. About 15
lines of Python or `yq`. It does not replace review, but it catches the
`v0.2.0` / `1.10` kind of drift.

### 6.5 Other workflows

- `ci.yaml`, `ci-format.yaml`, `lib-get-test-matrix.yaml`,
  `ci-verify-workflows.yaml`, `security-*.yaml`: no change proposed. They
  follow the conventions of `CLAUDE.md`.
- `nightly-tests.yaml`: calls the same `ci-action.yaml` with the latest release
  (section 6.2). It no longer calls a separate file.
- `bot-*.yaml`: not audited beyond their headers.
- `dependabot.yml` and `bot-pin-action.yaml` both update action pins (open
  point 8). No change proposed before that check.
- `actions: write` on the test jobs: reduce to `contents: read` if open point 7
  confirms that it is not needed.

## 7. Documentation

- **`README.md`**:
  - Remove the `uv-no-progress` example. Keep the package examples, and add the
    `package-installed` output to the compatibility matrix example (skip the
    tests when the combination does not exist). Say which input to use:
    `package-*` for one package whose version varies, `extra-packages` for
    tools.
  - Write each rule once: the inputs table gives the short form, the
    `Invalid input` section gives the rule. Remove the validation rules from
    the step list and from the troubleshooting text.
  - "What this action does": list the steps by group and name, without
    repeating the numbers (`1.1 to 1.10` was the drift).
  - State that the packages of `extra-packages` are not locked, and that the
    project's Python version is used when `python-version` is empty
    (`.python-version`, committed).
  - Keep the Linux and macOS statement; add the project contract of 3.3.
  - Use the new release tag in the examples, once it exists.
- **`.github/OVERVIEW.md`**: describe the test groups, not job names; fix the
  workflow list (remove `bot-report-queued-runs.yaml`), the schedules and the
  callers; fix the `workflow_dispatch` claim; describe the two test workflows
  and their roles.
- **`CLAUDE.md`**: keep the repository purpose and all rules, including the
  two test workflows. Note the `N.M` numbering for the
  groups.
- **`tasks.py`**: fix the docstring (only `env.install` is used).

## 8. Migration and release

This is a breaking release (`0.x`, so the next minor: `v0.3.0`; the previous
tag is `v0.2.0`). The PR descriptions say, as `CLAUDE.md` requires:

- **Changed**: removal of `uv-no-progress`; the new `package-installed`
  output; the empty default of
  `python-version`; the removal of the interpreter listing from the log.
- **Not changed**: `inv env.install` as the installation method,
  `uv sync --frozen` semantics, the 3 existing outputs, the inputs `uv-version`,
  `install-args`, `extra-packages`, `package-*`, `enable-cache`,
  `working-directory`, the
  early validation and the `invoke-tasklib` read from `uv.lock`.
- **Not validated, and why**: `python-version`, `uv-version`,
  `install-args`, `package-install-args`.
- **Not verified**: the workflows cannot run locally and CI was not awaited.
  Report the result of `make format` and `make lint`.

Behaviour changes, for the PR and the release notes:

| Before                          | After                                                             |
| ------------------------------- | ----------------------------------------------------------------- |
| `uv-no-progress: "false"`       | Removed. Set `UV_NO_PROGRESS` in the `env:` of the job if needed. |
| `python-version` default `3.14` | Default empty: `.python-version` or `requires-python` is used.    |
| Interpreter listing in the log  | Removed (the active interpreter is still shown).                  |

Callers that pass a removed input get a workflow warning and keep running
without it; callers that rely on the old `python-version` default and have no
`.python-version` get the interpreter that `uv` selects instead of 3.14. Both
must be in the release notes.

One branch and one pull request per logical change (`CLAUDE.md`), in this
order, each green on its own:

1. `docs/fix-documentation-drift`: the facts of 2.4 (no behaviour change), plus
   the `tasks.py` docstring.
2. `refactor/simplify-tasklib-and-outputs`: step 3.1 with `awk`, step 8 with
   `python`, drop the interpreter listing (renumber the reports).
3. `test/reduce-test-permissions`: `actions: write` to `contents: read` on the
   test jobs of both files (after open point 7); merge the `-glob` and
   `-uv-config` jobs into their parent jobs in both files.
4. `feat/package-installed-output`: `id` on step 5, the `package-installed`
   output, the skip test, README.
5. `refactor/remove-uv-no-progress`: remove the input, the 12 `env:` blocks,
   step 1.5, tests, README (after open point 3).
6. `feat/default-python-version`: empty default, `.python-version` in the dummy
   project, tests, README (after open point 4).
7. `ci/check-readme-inputs`: the drift check of 6.4.
8. Release `v0.3.0`, then update the examples of the README.

PRs 1 to 4 are not breaking and can ship first. PRs 5 and 6 hold the breaking
changes and can each be dropped independently if the usage turns out to be
real.

## 9. Open points to verify before implementing

1. `uv export --frozen --no-hashes --no-emit-project --all-groups --all-extras`
   prints `invoke-tasklib==X.Y.Z ; markers` on its own line for a group
   dependency, on the `uv` versions allowed by `uv-version` (so
   `awk '{print $1}'`
   is correct). Already working on `main`; check the `awk` form and the
   `pipefail` behaviour.
2. `inv env.install` behaves the same when `invoke-tasklib` was installed with
   `uv pip install` before the sync (it does today).
3. `uv` shows no progress bar in a GitHub Actions log without `UV_NO_PROGRESS`,
   including during the Python download in `setup-uv`. If it does, document
   `UV_NO_PROGRESS: 1` at the job level and still remove the input.
4. `setup-uv` with an empty `python-version` creates the virtual environment
   with the interpreter chosen by `.python-version` / `requires-python` of
   `working-directory`, on Linux and macOS. If the choice depends on the runner
   image when no file exists, say it in the README (this is the risk of the new
   default; the alternative is to keep a default and bump it by hand).
5. Does `inv env.install` need `invoke.yaml`? If not, `invoke.yaml` is optional
   and the README says so; if yes, step 1.3 checks it.
6. The merged `-glob` and `-uv-config` jobs keep their independence (a failure
   of one step does not hide the other); otherwise keep them separate.
7. The test jobs work with `permissions: contents: read` only (cache save and
   restore included).
8. Whether `dependabot.yml` and `bot-pin-action.yaml` are both needed:
   Dependabot does not understand `# ratchet:` comments, so the two may fight
   over the same lines. Check the history of both before dropping one.
9. What `uv-install-package-action` exposes: `is-valid-version` exists in the
   pinned release (`v0.2.0`); check that the pinned SHA of `action.yaml` does
   too, and decide whether a failed install (`installed-successfully`) must
   also be reflected in `package-installed`. Also check whether the closest-
   version substitution of older releases is still reachable, since the README
   of the nested action and its `action.yaml` disagree.

## 10. Decisions taken and alternatives rejected

- **`invoke-tasklib` is kept.** `inv env.install` stays the installation method
  and the purpose paragraph of `CLAUDE.md` is unchanged. Dropping it for a plain
  `uv sync --frozen` would remove steps 3.1, 3.2, the `tasks.py` and
  `invoke.yaml` requirements, and the "excluded group" caveat, about 40 lines in
  all, but it would change the contract with every caller, and the tasks
  (`env.install` flags in `install-args`) are the point of the action. This is
  the
  one decision left to the owner; the recommendation is to keep it.
- **`package-*` is kept, `extra-packages` stays separate.** The nested action
  validates the version against PyPI and the Python version, and skips an
  impossible combination; `uv pip install pkg==X` cannot. Dropping it would
  break compatibility matrices. The cost (a step in the workspace root, three
  linked inputs) is documented, and the new output makes the skip visible.
- **Empty `python-version`.** The project decides (P2). The risk is a variable
  interpreter for projects without `.python-version`; the README tells them to
  commit one.
- **Small steps over big steps.** Validation and reports stay split into
  numbered sub-steps, because the log then names the failing check.
- **Windows is ignored.** No path handling, test or documentation for it.
- **Rejected: a `verbose` input.** The diagnostics cost about a second and are
  most useful exactly when the build breaks.
- **Rejected: validating `python-version`, `uv-version`, `install-args`,
  `package-install-args`.** A copy
  of the tool's parser would drift from the tool.
- **Rejected: generating the README inputs table.** A check (6.4) gives the
  same protection with less machinery.
