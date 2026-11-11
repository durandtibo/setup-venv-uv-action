# Target state of `setup-venv-uv-action`

Review date: 2026-11-11. Reviewed: `action.yaml` (452 lines, 16 steps, 11
inputs, 3 outputs), `README.md`, `.github/OVERVIEW.md`, `CLAUDE.md`, the dummy
project, and the workflows (`test-local.yaml` has 28 jobs and 792 lines).

Nothing was run. The proposals below are design decisions, not tested code. The
points that need a prototype before they are relied on are listed in
[Open points](#open-points-to-verify-before-implementing).

## 1. Properties of the action

These are the properties the target state must satisfy. They come from
`CLAUDE.md` and `README.md`, tightened where the current action drifts from
them.

| #   | Property            | Meaning                                                                                                                                                              |
| --- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| P1  | Single purpose      | Install `uv`, set up Python, and install the project dependencies with the `inv env.install` task of `invoke-tasklib`. Nothing else.                                 |
| P2  | Reproducible        | Dependencies come from the committed `uv.lock` (`--frozen`). The bootstrap tool (`invoke-tasklib`) is also taken from the lock file, so nothing is unpinned.         |
| P3  | Fail early, clearly | Every invalid input or missing project file fails in the first steps (group 1), before anything is installed, with an `::error title=Invalid input::` style message. |
| P4  | Fast                | No network call or action that is not needed (no extra action before the setup), `uv` cache on by default on GitHub-hosted runners.                                  |
| P5  | Small surface       | Few inputs, each one tested and documented. Little third-party code: only `astral-sh/setup-uv`, pinned to a SHA with a `ratchet` comment.                            |
| P6  | Safe                | Inputs reach shell code only through `env:`. `shell: bash` on every `run:`. Least-privilege permissions in the workflows.                                            |
| P7  | Observable          | Installation steps fail the action. Reporting steps never do (`continue-on-error: true`). The result is exposed as outputs.                                          |
| P8  | Portable            | Linux and macOS runners with `bash`. Windows is not a target: no code, test or documentation handles it.                                                             |
| P9  | Maintainable        | Docs, `action.yaml` and tests say the same thing. The step list is short enough to read in one sitting. Every input has a test that asserts its effect.              |
| P10 | Simple steps        | One concern per step, a few lines each, numbered `N.M` inside a group. Several small steps are preferred to one big step. The log shows which check failed.          |

## 2. Findings on the current state

Ordered by impact on the properties above.

1. **The `invoke-tasklib` bootstrap is the main source of complexity (P4, P5,
   P9).** Four steps and about 100 lines exist only to get `inv` available:
   - Step 4 calls a third-party action (`extract-pyproject-metadata-action`) to
     read a version specifier. It forces a Python 3.11+ on `PATH` _before_ the
     Python setup.
   - Step 7 installs `invoke-tasklib` from that specifier, with a warning
     when there is none (so the version is unlocked).
   - Step 8 re-implements `inv --list` checks for 3 tasks.
   - Step 9 reinstalls `invoke-tasklib` because `uv sync` removed it, and
     reports a notice.

   The version is already locked in `uv.lock` when the project follows the
   recommended setup. The action should read it there.

2. **Two ways to add packages (P5).** `package-name`, `package-version` and
   `package-install-args` (3 inputs, 1 third-party action, 1 validation block,
   2 "ignored input" warnings, 7 test jobs) do what `extra-packages` already
   does with a requirement line such as `numpy==1.26.0`. The package step also
   runs in the workspace root, not in `working-directory`, which is a documented
   trap (`Relative Paths in package-install-args`) and exists only because of
   the third-party action.

3. **Inputs that carry no weight.**
   - `uv-no-progress` sets `UV_NO_PROGRESS`, copied into 11 steps. `uv` hides
     its progress bars when the output is not a terminal, which is always the
     case in a workflow log. To be confirmed (open point 3).
   - `verbose` toggles the diagnostic steps that cost about a second in total.
     They are most useful exactly when a build breaks, so switching them off
     saves little.
   - `python-version` defaults to a hard-coded `"3.14"` that must be bumped by
     hand. `uv` already knows how to pick the project's version
     (`.python-version`, `requires-python`).

4. **Steps that are redundant or too big (P9, P10).** Step 6 (`which uv`,
   `uv --version`, ...) re-checks what `setup-uv` just did and would already
   have failed on. Step 9 mixes the installation with a reinstall workaround.
   Step 3 mixes five validations in one 60-line script, where a failure
   names the step but not the input. Step 16 calls `uv python find` and then a
   Python to print a version, where `python` is already on `PATH`. The
   target keeps small steps (one per validated input, one per report) and
   removes the redundant ones.

5. **The diagnostics depend on tasks that are not needed.**
   `env.show-python-config` and `env.show-installed-packages` can be replaced
   by `uv python list --only-installed` and `uv pip list`. The action then
   needs exactly one task (`env.install`), and the "missing task" warnings
   disappear.

6. **Tests are large and repetitive (P9).** `test-local.yaml` has 28 jobs;
   `test-invalid-*` jobs repeat the same pattern (run `uses: ./` with
   `continue-on-error`, assert the outcome, assert that `uv` is absent) four
   times each. `test-stable.yaml` is a hand-maintained copy that must follow
   `test-local.yaml` by rule, which is error-prone.

7. **Smaller points.**
   - `nightly-tests.yaml` runs `format`; formatting cannot change overnight, it
     only costs minutes.
   - `OVERVIEW.md` lists test jobs by name. That list goes stale on every test
     change; describe the groups, not the jobs.
   - `README.md` repeats the validation rules three times (step list, inputs
     table, `Invalid input` section). `CLAUDE.md` asks for the rules in the
     validation steps and the `Invalid input` section only.
   - The `README.md` table lacks the `verbose` and `uv-no-progress` details that
     `action.yaml` has, and says `uv-version` is empty-able in one place and not
     the other. Generating the table from `action.yaml` would end this class
     of drift (see section 6).

## 3. Target interface

### 3.1 Inputs: 11 become 6

| Input               | Default | Validated | Notes                                                                                                                                                                                     |
| ------------------- | ------- | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `python-version`    | `""`    | No        | Any `uv` version request. Empty means `uv` picks the project's version (`.python-version`, then `requires-python`). Not validated: only `uv` can interpret it.                            |
| `uv-version`        | `""`    | No        | Passed to `setup-uv`. Empty means the `required-version` of the project, else latest. Not validated: only `setup-uv` and `uv` can interpret it.                                           |
| `install-args`      | `""`    | No        | Split on whitespace, no quotes, no globbing, passed to `inv env.install`. Not validated: only `invoke-tasklib` can interpret it.                                                          |
| `extra-packages`    | `""`    | Yes       | One requirement per line, installed after the project with `uv pip install`. A line that starts with `-` is rejected. Replaces `package-name`, `package-version`, `package-install-args`. |
| `enable-cache`      | `auto`  | Yes       | `true`, `false` or `auto`. Passed to `setup-uv`.                                                                                                                                          |
| `working-directory` | `.`     | Yes       | Relative path of an existing directory inside the workspace, which contains `pyproject.toml`, `uv.lock` and `tasks.py`.                                                                   |

Removed: `package-name`, `package-version`, `package-install-args`, `verbose`,
`uv-no-progress`.

Consequences:

- **No "ignored input" warning is left**, because no input depends on another.
- **Compatibility matrices keep working** with one line:
  `extra-packages: numpy==${{ matrix.numpy }}`. The README example shows it.
  Behaviours that are lost: `--upgrade` style flags and "install the latest
  version of a package that is already installed". Both are done by pinning or
  with a range (`numpy>=2`). If real usage shows the need, add
  `extra-packages-args` later, not now.
- **Unknown inputs only produce a workflow warning in GitHub Actions**, so
  callers that still pass a removed input keep running. They lose the feature,
  so the release notes must list them (section 7).

### 3.2 Outputs: unchanged

| Output           | Source                                    |
| ---------------- | ----------------------------------------- |
| `cache-hit`      | `setup-uv`                                |
| `uv-version`     | `setup-uv`                                |
| `python-version` | `python -c` in the last installation step |

### 3.3 Project contract (what the caller's repository must contain)

Under `working-directory`:

- `pyproject.toml` and a committed `uv.lock` (checked in step 1.3).
- `tasks.py` exposing the `invoke-tasklib` collection (checked in step 1.3) and
  an `invoke.yaml` configuring it.
- `invoke-tasklib` in a dependency group or extra that `install-args` installs
  (the `dev` group by default). It must therefore be in `uv.lock`; the action
  reads its exact version there.

If `invoke-tasklib` is absent from the lock file, the action fails in step 3.1
with an error that shows the `pyproject.toml` snippet to add. This replaces the
"unpinned" warning and the "reinstalled" notice: one rule instead of three
behaviours.

If the caller's `install-args` excludes the group that holds `invoke-tasklib`,
`uv sync` removes it after use. The action no longer depends on `inv` after
`env.install`, so this is harmless to the action. A later step of the caller
that needs `inv` is the caller's responsibility (documented in one sentence).

## 4. Target `action.yaml`

Design rule: **one concern per step.** A step is a few lines that one reader can
check at a glance, with its own name, so the log shows which check or action
failed. Steps are grouped by a number and numbered `N.M` inside a group
(`1.1`, `1.2`, ...), and the `# Step N.M:` comment sits directly above each
`- name:` (the `CLAUDE.md` rule, extended to sub-steps). The number of steps is
not a goal: 16 steps become 15, but 4 of them are one-line reports and the 3
validation steps become 4 that are each shorter than today's.

| #   | Step                                     | Fails the action | Replaces (current steps) |
| --- | ---------------------------------------- | ---------------- | ------------------------ |
| 1.1 | Validate `enable-cache`                  | Yes              | 1 (part)                 |
| 1.2 | Validate `working-directory`             | Yes              | 2                        |
| 1.3 | Validate the project files               | Yes              | 8 (part)                 |
| 1.4 | Validate `extra-packages`                | Yes              | 3 (part)                 |
| 2   | Install uv and Python (`setup-uv`)       | Yes              | 4, 5, 6                  |
| 3.1 | Read the locked `invoke-tasklib` version | Yes              | 4 (replaced)             |
| 3.2 | Install `invoke-tasklib`                 | Yes              | 7                        |
| 4   | Install the project dependencies         | Yes              | 9                        |
| 5   | Install extra packages (optional)        | Yes              | 10, 11                   |
| 6.1 | Show the uv and Python versions          | No               | 6, 12 (part)             |
| 6.2 | Show the Python interpreters             | No               | 12                       |
| 6.3 | Show the installed packages              | No               | 13                       |
| 6.4 | Show the dependency tree                 | No               | 14                       |
| 6.5 | Check the environment                    | No               | 15                       |
| 7   | Set the outputs                          | Yes              | 16                       |

Third-party actions after the change: `astral-sh/setup-uv` only (was 3).

Every validation step has the same shape: the input in `env:`, an optional
`if:`, a short `run:` that prints an `::error title=Invalid input::` message
and exits 1. A step validates one input, and reports all the problems of that
input (for example every bad line of `extra-packages`). The first failing step
stops the action, before anything is installed.

### Group 1: validation

**Step 1.1: Validate `enable-cache`.** `true`, `false` or `auto`.

**Step 1.2: Validate `working-directory`.** Not absolute (starts with `/`), no
`..` segment, and a directory of `${GITHUB_WORKSPACE}`. The error keeps the hint
about `actions/checkout`.

**Step 1.3: Validate the project files.** In `working-directory`:
`pyproject.toml`, `uv.lock` and `tasks.py` exist. Today a missing `uv.lock`
surfaces as an obscure `uv sync` error after the installation, and `tasks.py`
is checked only after `uv` and Python are installed. It runs after 1.2, so the
directory is known to be valid.

**Step 1.4: Validate `extra-packages`.** No line starts with `-` after trimming
the leading whitespace (that would be an option of `uv`, not a requirement).
Skipped (`if:`) when the input is empty.

Not validated, and stated in the README and in the PR: `python-version`,
`uv-version`, `install-args` (see the table in 3.1).

### Step 2: Install uv and Python

`astral-sh/setup-uv` as today, minus `UV_NO_PROGRESS`:

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

No separate "which uv / python --version" step: `setup-uv` fails if it cannot
install, and the versions are printed by step 6.1.

### Group 3: invoke-tasklib

Two steps, so that a missing entry in the lock file and a failing installation
are different lines in the log.

**Step 3.1: Read the locked `invoke-tasklib` version** (`id: tasklib`, in
`working-directory`):

```bash
pin=$(uv export --frozen --no-hashes --no-emit-project --all-groups --all-extras |
  grep -E '^invoke-tasklib==' | head -n 1 | cut -d' ' -f1)
if [ -z "${pin}" ]; then
  echo "::error title=Missing invoke-tasklib::'invoke-tasklib' is not in uv.lock. Add it to a dependency group, then run 'uv lock'."
  exit 1
fi
echo "requirement=${pin}" >> "${GITHUB_OUTPUT}"   # e.g. invoke-tasklib==0.0.9
```

**Step 3.2: Install `invoke-tasklib`:**
`uv pip install "${REQUIREMENT}"`, with
`REQUIREMENT: ${{ steps.tasklib.outputs.requirement }}` in `env:`.

Why this is better than reading `pyproject.toml`:

- The version is the locked one, so the bootstrap is reproducible (P2).
- No third-party action, no Python 3.11 requirement before the setup.
- No unpinned case, so no warning, and no "reinstalled" path.
- `uv export --frozen` does not modify the lock file or resolve anything.

### Step 4: Install the project dependencies

```bash
set -f                  # no globbing of install-args
inv env.install ${INSTALL_ARGS}
```

Same as today without the reinstall block. If the task is missing, `inv` prints
`No idea what 'env.install' is!`, which is clear enough; the separate
`inv --list` parsing is dropped. The shell quirks of `install-args` stay
documented.

### Step 5: Install extra packages

Same as the current step 11, in `working-directory`, one requirement per line,
blank lines ignored, `if: inputs.extra-packages != ''`. It now also covers the
former `package-*` use case.

### Group 6: reports

Five steps, each one command, each `continue-on-error: true`, each in
`working-directory`. Because they are separate steps, a failure of one never
hides the output of the others, and no `|| true` or group markers are needed.
They always run: there is no `verbose` input.

| Step | Name                         | Command                                        |
| ---- | ---------------------------- | ---------------------------------------------- |
| 6.1  | Show the versions            | `uv --version; which python; python --version` |
| 6.2  | Show the Python interpreters | `uv python list --only-installed`              |
| 6.3  | Show the installed packages  | `uv pip list`                                  |
| 6.4  | Show the dependency tree     | `uv pip tree --show-version-specifiers`        |
| 6.5  | Check the environment        | `uv pip check`                                 |

### Step 7: Set the outputs

```bash
python_version="$(python -c 'import platform; print(platform.python_version())')"
echo "python-version=${python_version}" >> "${GITHUB_OUTPUT}"
```

`python` is the activated virtual environment of the project
(`activate-environment`), so `uv python find` is not needed. The assignment
is on its own line, so a failure of `python` fails the step instead of writing
an empty output.

### Cross-cutting rules (unchanged, all kept)

- Inputs only through `env:`; `shell: bash` everywhere.
- Installation steps fail the action; only the steps of group 6 use
  `continue-on-error`.
- Third-party actions pinned to a SHA with a `ratchet` comment.
- Only the steps that need a project directory set `working-directory:`
  (1.3, 3 to 7).

## 5. Expected effect

| Metric                          | Current                                | Target                           |
| ------------------------------- | -------------------------------------- | -------------------------------- |
| Steps                           | 16, three of them 40 to 60 lines       | 15, each one a few lines         |
| `action.yaml` lines             | 452                                    | about 300 (estimate)             |
| Inputs                          | 11                                     | 6                                |
| Validated inputs                | 7 (+ 2 ignored)                        | 3                                |
| Third-party actions             | 3                                      | 1                                |
| Python 3.11 needed before setup | Yes                                    | No                               |
| `invoke-tasklib` version        | `pyproject.toml` spec, may be unpinned | exact, from `uv.lock`, mandatory |
| Tasks required from the project | 1 required, 2 optional                 | 1 (`env.install`)                |
| Test jobs                       | 28                                     | about 11                         |

Speed: the target removes the extraction action (which needs its own setup
before Python) and the redundant checks, and adds one `uv export`
(milliseconds). A composite step costs little, so splitting the validation and
the reports into small steps has no measurable cost. The gain is small, a few
seconds per run; the main time (Python download, dependency install, cache
restore) is unchanged. This is an estimate to confirm on a real run. The
target is chosen for simplicity, not for speed.

## 6. Tests and workflows

### 6.1 Rules kept

- `test-local.yaml` (`uses: ./`) and `test-stable.yaml` (last release) stay
  identical except for the header, the `name` and the `uses:` line, with the
  existing exception for inputs added after the release.
- Every input has a job that asserts its effect; every validated input has a
  job that asserts failure _because of the validation_ (nothing installed).
- OS and Python lists come from `durandtibo/workflow-config-action`; matrix
  values go through `env:`; `timeout-minutes` on every job.

### 6.2 Target job list (`test-local.yaml`)

| Job                          | Input / behaviour covered                                                                                                                    |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `test`                       | Defaults, all Unix OS of the config. Asserts the `python-version`, `uv-version` and `cache-hit` outputs are set and `inv` and `python` work. |
| `test-python-version`        | `python-version`: matrix of the standard versions; also a range (`>=3.12,<3.14`) and the empty value (reads `.python-version`).              |
| `test-uv-version`            | `uv-version`: exact version, asserts the `uv-version` output and `uv --version`.                                                             |
| `test-install-args`          | `install-args`: a flag that changes the result, plus the glob case (`*` stays literal), merged into one job with two steps.                  |
| `test-extra-packages`        | `extra-packages`: two lines, a blank line, a pin (`numpy==2.4.0` asserted by `import numpy`), extras in brackets, a range.                   |
| `test-cache`                 | `enable-cache`: `true`, `false`, `auto`; asserts `cache-hit` is empty when disabled and `true` on the second run.                            |
| `test-working-directory`     | `working-directory`: project in a subfolder; a `uv.toml` there is honoured (merges today's `-uv-config` job).                                |
| `test-invalid-inputs`        | One job with a matrix, see below.                                                                                                            |
| `test-missing-files`         | No `tasks.py`; no `uv.lock`: the action fails in step 1.3 (nothing installed).                                                               |
| `test-tasklib-lock`          | The installed `invoke-tasklib` version equals the one in `uv.lock`; a project without it fails with the `Missing invoke-tasklib` error.      |
| `test-tasklib-not-in-groups` | `install-args` excluding the group: the action still succeeds and the environment check does not fail.                                       |

`test-invalid-inputs` uses a matrix of cases, each case setting one input, so the
four copy-pasted blocks become one:

```yaml
strategy:
  fail-fast: false
  matrix:
    include:
      - { name: enable-cache, enable-cache: maybe }
      - { name: working-directory-absolute, working-directory: /tmp }
      - { name: working-directory-parent, working-directory: ../x }
      - { name: working-directory-missing, working-directory: does-not-exist }
      - { name: extra-packages-option, extra-packages: "--index-url=https://x" }
steps:
  - uses: actions/checkout@<sha>
  - id: action
    uses: ./
    continue-on-error: true
    with:
      enable-cache: ${{ matrix.enable-cache || 'auto' }}
      working-directory: ${{ matrix.working-directory || '.' }}
      extra-packages: ${{ matrix.extra-packages }}
  - name: Assert it failed in the validation
    env:
      OUTCOME: ${{ steps.action.outcome }}
    run: |
      test "${OUTCOME}" = "failure"
      ! command -v uv   # nothing was installed
```

Every case runs in its own fresh runner, so "uv is absent" is a true check.

### 6.3 Stable copy

Keep both files (a `uses:` value cannot be an expression, so one parameterised
workflow is not possible), but stop editing the copy by hand: add a `make`
target in the top-level `Makefile` (not in `.make/`) that derives
`test-stable.yaml` from `test-local.yaml` with a `sed` on the header, the
`name` and the `uses:` line, and make `format.yaml` fail when the generated
file differs. This enforces the existing "identical except" rule instead of
relying on discipline. The "input added after the release" exception becomes a
marker comment that the generator skips (`# local-only`).

Important consequence of the breaking change: until the release is bumped, the
jobs of `test-stable.yaml` that use removed inputs (`package-*`, `verbose`,
`uv-no-progress`) would test the old release with the old inputs. They stay
valid for the old release and disappear at the bump, since the generator then
copies the new file. State this in the PR.

### 6.4 Other workflows

- `nightly-tests.yaml`: drop the `format` job (formatting does not depend on
  time); keep `test-local` and `test-stable`, which catch upstream changes in
  `uv`, `setup-uv` and `invoke-tasklib`. Update its header comment.
- `ci.yaml`, `format.yaml`, `ci-verify-workflows.yaml`, `bot-*.yaml`,
  `dependency-review.yml`: no change proposed. They follow the documented
  conventions (least-privilege permissions, `workflow_dispatch` on callees,
  `make` targets in steps). I did not audit the bot workflows beyond their
  headers.
- `dependabot.yml` and `bot-pin-action.yaml` both update action pins. With one
  third-party action left in `action.yaml` plus a handful in workflows, check
  whether both are still needed. No change proposed without that check.

### 6.5 Documentation

- `README.md`:
  - One inputs table generated from, or checked against, `action.yaml` (a small
    `make` target that fails on a mismatch of names, defaults and descriptions)
    to enforce the `CLAUDE.md` consistency rule.
  - "What This Action Does": the 15 steps, listed by number (1.1 to 7).
  - A single `Invalid input` section holding the rules, and not repeated in the
    step list.
  - A migration section (section 7).
  - Replace the `invoke-tasklib` troubleshooting entries (`Unpinned`,
    `reinstalled`, `Relative Paths`, `Custom Install Arguments` kept) with
    `Missing invoke-tasklib`.
  - Keep the Linux and macOS statement; remove the sentences about Windows
    (not a target); add the project contract of 3.3.
- `.github/OVERVIEW.md`: describe test groups, not job names; update the
  nightly description.
- `CLAUDE.md`: keep the repository purpose paragraph (decision in section 8).
  Add the `N.M` step numbering and the one-concern-per-step rule. Update the test rules to mention the
  generated stable file and the matrix for invalid inputs.

## 7. Migration and release

This is a breaking release (the project is `0.x`, so bump the minor version:
`v0.3.0`). The PR description must say, as `CLAUDE.md` requires:

- **Changed**: the 15 small steps (groups 1 to 7), the removal of the inputs `package-name`,
  `package-version`, `package-install-args`, `verbose`, `uv-no-progress`, the
  default of `python-version`, the `invoke-tasklib` bootstrap from `uv.lock`,
  the new early checks of `uv.lock` and `tasks.py`.
- **Not changed**: `inv env.install` as the installation method,
  `uv sync --frozen` semantics, the three outputs, the inputs `uv-version`,
  `install-args`, `extra-packages`, `enable-cache`, `working-directory`.
- **Behaviour changes** (a table in the PR and in the release notes):

| Before                                                  | After                                                                 |
| ------------------------------------------------------- | --------------------------------------------------------------------- |
| `package-name: x` + `package-version: 1.0`              | `extra-packages: x==1.0`                                              |
| `package-install-args: --upgrade`                       | Pin or range in `extra-packages` (`x>=1`)                             |
| `verbose: "false"`                                      | Input removed; diagnostics always run, in collapsed groups            |
| `uv-no-progress: "false"`                               | Input removed; `UV_NO_PROGRESS` can be set by the caller's `env:`     |
| `python-version` default `3.14`                         | Default empty: `.python-version` or `requires-python` is used         |
| `invoke-tasklib` missing from the project               | Fails in step 3.1 with the fix (was a warning/notice and a reinstall) |
| `invoke-tasklib` version from the `pyproject.toml` spec | Exact version from `uv.lock`                                          |
| Project without `uv.lock`                               | Fails in step 1.3 (was an error from `uv sync`)                       |

- **Not validated and why**: `python-version`, `uv-version`, `install-args`
  (only `uv`, `setup-uv` and `invoke-tasklib` can interpret them).
- **Not verified**: the workflows cannot run locally, and CI was not awaited.
  Report `make format` and `make lint` results.

Split the work into small PRs (one branch and PR per logical change, per
`CLAUDE.md`), in this order, each one green on its own:

1. `refactor/split-validation-steps`: one step per validated input (1.1 to
   1.4) and the project file checks; matrix-based invalid-input test.
2. `refactor/tasklib-from-lock`: remove the metadata action, the reinstall
   path and the `inv --list` parsing; add the lock-file bootstrap.
3. `refactor/uv-diagnostics`: one step per report command (6.1 to 6.5); remove step 6
   and `verbose`.
4. `refactor/remove-package-inputs`: remove `package-*` and the third-party
   action; extend `extra-packages` tests and README.
5. `refactor/remove-uv-no-progress`, then `feat/default-python-version`.
6. `test/generate-stable-workflow`, `ci/nightly-without-format`, docs
   (`README.md`, `OVERVIEW.md`, `CLAUDE.md`).
7. Release `v0.3.0`, then bump the `uses:` of `test-stable.yaml`.

Steps 1 to 3 are not breaking and can ship first. Steps 4 and 5 hold the
breaking changes and can be dropped independently if the usage of those inputs
turns out to be real.

## 8. Decisions taken

- **`invoke-tasklib` is kept.** `inv env.install` stays the installation method
  and `CLAUDE.md` keeps its repository purpose paragraph. The project contract
  (3.3) therefore requires `tasks.py`, `invoke.yaml` and `invoke-tasklib` in the
  lock file. Dropping it in favour of `uv sync --frozen` is not planned.
- **Small steps over big steps.** Validation and reports are split into
  numbered sub-steps (`N.M`).
- **Windows is ignored.** No path handling, test or documentation for it.

## Open points to verify before implementing

1. `uv export --frozen --no-hashes --no-emit-project --all-groups --all-extras`
   prints `invoke-tasklib==X.Y.Z` on its own line for a group dependency, with
   the installed `uv` versions the action supports (check the output format and
   the line-continuation characters with `--no-hashes`).
2. `inv env.install` behaves the same when `invoke-tasklib` was installed with
   `uv pip install` before the sync (it does today: step 7 then step 9).
3. `uv` shows no progress bar in a GitHub Actions log without `UV_NO_PROGRESS`.
   If it does, document `env: UV_NO_PROGRESS: 1` at the job level of the caller
   in the README instead of an input.
4. `setup-uv` with an empty `python-version` creates the virtual environment with
   the interpreter chosen by `.python-version`/`requires-python` of
   `working-directory`, on Linux and macOS runners.
5. `uv python list --only-installed` and `uv pip check` exit codes and output
   are acceptable inside a `continue-on-error` step on all supported `uv`
   versions.
6. The matrix expression `${{ matrix.working-directory || '.' }}` is passed as a
   string to `uses: ./` inputs, including the empty `extra-packages` case.
