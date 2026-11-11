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

| #   | Property            | Meaning                                                                                                                                                      |
| --- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| P1  | Single purpose      | Install `uv`, set up Python, and install the project dependencies with the `inv env.install` task of `invoke-tasklib`. Nothing else.                         |
| P2  | Reproducible        | Dependencies come from the committed `uv.lock` (`--frozen`). The bootstrap tool (`invoke-tasklib`) is also taken from the lock file, so nothing is unpinned. |
| P3  | Fail early, clearly | Every invalid input or missing project file fails in the first step, before anything is installed, with an `::error title=Invalid input::` style message.    |
| P4  | Fast                | Few steps (each step is a process and a log group), no network call that is not needed, `uv` cache on by default on GitHub-hosted runners.                   |
| P5  | Small surface       | Few inputs, each one tested and documented. Little third-party code: only `astral-sh/setup-uv`, pinned to a SHA with a `ratchet` comment.                    |
| P6  | Safe                | Inputs reach shell code only through `env:`. `shell: bash` on every `run:`. Least-privilege permissions in the workflows.                                    |
| P7  | Observable          | Installation steps fail the action. Reporting steps never do (`continue-on-error: true`). The result is exposed as outputs.                                  |
| P8  | Portable            | Linux and macOS GitHub-hosted runners (and self-hosted runners with `bash`). Windows is not supported and not tested.                                        |
| P9  | Maintainable        | Docs, `action.yaml` and tests say the same thing. The step list is short enough to read in one sitting. Every input has a test that asserts its effect.      |

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
   - `verbose` toggles 4 diagnostic steps that cost about a second in total.
     They are most useful exactly when a build breaks, so switching them off
     saves little.
   - `python-version` defaults to a hard-coded `"3.14"` that must be bumped by
     hand. `uv` already knows how to pick the project's version
     (`.python-version`, `requires-python`).

4. **Too many steps for the work done (P4, P9).** Three validation steps
   (three process spawns, three log groups) could be one. Step 6 (`which uv`,
   `uv --version`, ...) re-checks what `setup-uv` just did and would already
   have failed on. Four diagnostic steps are one logical report. Step 16 calls
   `uv python find` and then a Python to print a version, where `python` is
   already on `PATH`.

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

- `pyproject.toml` and a committed `uv.lock` (checked in step 1).
- `tasks.py` exposing the `invoke-tasklib` collection (checked in step 1) and
  an `invoke.yaml` configuring it.
- `invoke-tasklib` in a dependency group or extra that `install-args` installs
  (the `dev` group by default). It must therefore be in `uv.lock`; the action
  reads its exact version there.

If `invoke-tasklib` is absent from the lock file, the action fails in step 3
with an error that shows the `pyproject.toml` snippet to add. This replaces the
"unpinned" warning and the "reinstalled" notice: one rule instead of three
behaviours.

If the caller's `install-args` excludes the group that holds `invoke-tasklib`,
`uv sync` removes it after use. The action no longer depends on `inv` after
`env.install`, so this is harmless to the action. A later step of the caller
that needs `inv` is the caller's responsibility (documented in one sentence).

## 4. Target `action.yaml`

Seven steps instead of sixteen. Step comments follow the `CLAUDE.md` rule
(`# Step N:` directly above `- name:`).

| #   | Step                               | Fails the action | Replaces (current steps) |
| --- | ---------------------------------- | ---------------- | ------------------------ |
| 1   | Validate inputs and project files  | Yes              | 1, 2, 3, 8 (partly)      |
| 2   | Install uv and Python (`setup-uv`) | Yes              | 4, 5, 6                  |
| 3   | Install invoke-tasklib (from lock) | Yes              | 7, 9 (reinstall)         |
| 4   | Install dependencies               | Yes              | 9                        |
| 5   | Install extra packages (optional)  | Yes              | 10, 11                   |
| 6   | Show the environment               | No               | 12, 13, 14, 15           |
| 7   | Set outputs                        | Yes              | 16                       |

Third-party actions after the change: `astral-sh/setup-uv` only (was 3).

### Step 1: Validate inputs and project files

One script, one `env:` block, one helper that records an error and continues, so
that all problems of a run are reported together and the step ends with a single
`exit 1`.

Checks:

- `enable-cache` is `true`, `false` or `auto`.
- `working-directory` is not absolute (`/`, `\`, `C:`), has no `..` segment, and
  is a directory of `${GITHUB_WORKSPACE}`. The message keeps the hint about
  `actions/checkout`.
- In that directory: `pyproject.toml`, `uv.lock` and `tasks.py` exist. This
  moves the `tasks.py` check of step 8 before any installation and adds the
  missing lock-file check, which today surfaces as an obscure `uv sync` error.
- No line of `extra-packages` starts with `-` after trimming (the existing rule,
  kept as is).

Not validated, and stated in the README and in the PR: `python-version`,
`uv-version`, `install-args` (see the table in 3.1).

The file checks run only if `working-directory` is valid.

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
install, and the version is printed by step 6.

### Step 3: Install invoke-tasklib from the lock file

```bash
# in working-directory
pin=$(uv export --frozen --no-hashes --no-emit-project --all-groups --all-extras \
  | grep -E '^invoke-tasklib==' | head -n 1 | cut -d' ' -f1)   # e.g. invoke-tasklib==0.0.9
if [ -z "${pin}" ]; then
  echo "::error title=Missing invoke-tasklib::... add it to a dependency group, then run 'uv lock'."
  exit 1
fi
uv pip install "${pin}"
```

Why this is better than reading `pyproject.toml`:

- The version is the locked one, so the bootstrap is reproducible (P2).
- No third-party action, no Python 3.11 requirement before the setup.
- No unpinned case, so no warning, and no "reinstalled" path.
- `uv export --frozen` does not modify the lock file or resolve anything.

### Step 4: Install dependencies

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
blank lines ignored. It now also covers the former `package-*` use case.

### Step 6: Show the environment

One step, `continue-on-error: true`, with a collapsed group per section:

```bash
echo "::group::Versions"; uv --version; which python; python --version; echo "::endgroup::"
echo "::group::Python interpreters"; uv python list --only-installed; echo "::endgroup::"
echo "::group::Installed packages"; uv pip list; echo "::endgroup::"
echo "::group::Dependency tree"; uv pip tree --show-version-specifiers; echo "::endgroup::"
echo "::group::Environment check"; uv pip check; echo "::endgroup::"
```

Each command must not stop the others: use `|| true` per command (or run without
`set -e`, which is the composite default for `bash` only if `-e` is not
requested; set it explicitly). Not conditional on an input.

### Step 7: Set outputs

```bash
echo "python-version=$(python -c 'import platform; print(platform.python_version())')" >> "${GITHUB_OUTPUT}"
```

`python` is the activated virtual environment of the project (`activate-environment`),
so `uv python find` is not needed. The command substitution is inside `echo`,
so a failure of `python` would still write an empty value: assign to a variable
first, as the current step does, to fail the step instead.

### Cross-cutting rules (unchanged, all kept)

- Inputs only through `env:`; `shell: bash` everywhere.
- Installation steps fail the action; only step 6 uses `continue-on-error`.
- Third-party actions pinned to a SHA with a `ratchet` comment.
- Only the steps that need a project directory set `working-directory:`
  (2 to 7).

## 5. Expected effect

| Metric                          | Current                                | Target                           |
| ------------------------------- | -------------------------------------- | -------------------------------- |
| Steps                           | 16                                     | 7                                |
| `action.yaml` lines             | 452                                    | about 220 (estimate)             |
| Inputs                          | 11                                     | 6                                |
| Validated inputs                | 7 (+ 2 ignored)                        | 3                                |
| Third-party actions             | 3                                      | 1                                |
| Python 3.11 needed before setup | Yes                                    | No                               |
| `invoke-tasklib` version        | `pyproject.toml` spec, may be unpinned | exact, from `uv.lock`, mandatory |
| Tasks required from the project | 1 required, 2 optional                 | 1 (`env.install`)                |
| Test jobs                       | 28                                     | about 11                         |

Speed: the target removes about 9 step start-ups and the extraction action, and
adds one `uv export` (milliseconds). The expected gain is a few seconds per run;
the main time (Python download, dependency install, cache restore) is
unchanged. This is an estimate to confirm on a real run.

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
| `test-missing-files`         | No `tasks.py`; no `uv.lock`: the action fails in step 1 (nothing installed).                                                                 |
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
  - "What This Action Does": 7 steps.
  - A single `Invalid input` section holding the rules, and not repeated in the
    step list.
  - A migration section (section 7).
  - Replace the `invoke-tasklib` troubleshooting entries (`Unpinned`,
    `reinstalled`, `Relative Paths`, `Custom Install Arguments` kept) with
    `Missing invoke-tasklib`.
  - Keep the Linux and macOS statement; add the project contract of 3.3.
- `.github/OVERVIEW.md`: describe test groups, not job names; update the
  nightly description.
- `CLAUDE.md`: update the repository purpose paragraph only if the decision in
  section 8 changes; otherwise keep it. Update the test rules to mention the
  generated stable file and the matrix for invalid inputs.

## 7. Migration and release

This is a breaking release (the project is `0.x`, so bump the minor version:
`v0.3.0`). The PR description must say, as `CLAUDE.md` requires:

- **Changed**: the 7-step structure, the removal of the inputs `package-name`,
  `package-version`, `package-install-args`, `verbose`, `uv-no-progress`, the
  default of `python-version`, the `invoke-tasklib` bootstrap from `uv.lock`,
  the new early checks of `uv.lock` and `tasks.py`.
- **Not changed**: `inv env.install` as the installation method,
  `uv sync --frozen` semantics, the three outputs, the inputs `uv-version`,
  `install-args`, `extra-packages`, `enable-cache`, `working-directory`.
- **Behaviour changes** (a table in the PR and in the release notes):

| Before                                                  | After                                                               |
| ------------------------------------------------------- | ------------------------------------------------------------------- |
| `package-name: x` + `package-version: 1.0`              | `extra-packages: x==1.0`                                            |
| `package-install-args: --upgrade`                       | Pin or range in `extra-packages` (`x>=1`)                           |
| `verbose: "false"`                                      | Input removed; diagnostics always run, in collapsed groups          |
| `uv-no-progress: "false"`                               | Input removed; `UV_NO_PROGRESS` can be set by the caller's `env:`   |
| `python-version` default `3.14`                         | Default empty: `.python-version` or `requires-python` is used       |
| `invoke-tasklib` missing from the project               | Fails in step 3 with the fix (was a warning/notice and a reinstall) |
| `invoke-tasklib` version from the `pyproject.toml` spec | Exact version from `uv.lock`                                        |
| Project without `uv.lock`                               | Fails in step 1 (was an error from `uv sync`)                       |

- **Not validated and why**: `python-version`, `uv-version`, `install-args`
  (only `uv`, `setup-uv` and `invoke-tasklib` can interpret them).
- **Not verified**: the workflows cannot run locally, and CI was not awaited.
  Report `make format` and `make lint` results.

Split the work into small PRs (one branch and PR per logical change, per
`CLAUDE.md`), in this order, each one green on its own:

1. `refactor/single-validation-step`: merge steps 1 to 3 and the file checks;
   matrix-based invalid-input test.
2. `refactor/tasklib-from-lock`: remove the metadata action, the reinstall
   path and the `inv --list` parsing; add the lock-file bootstrap.
3. `refactor/uv-diagnostics`: one report step with `uv` commands; remove step 6
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

## 8. Decision for the maintainer

**Keep or drop `invoke-tasklib`.** This review keeps it because `CLAUDE.md`
defines it as the purpose of the action (P1). Be aware of what it costs: with
the target above, `inv env.install` is the only use left, and it wraps
`uv sync --frozen` plus a few options. Dropping it would remove step 3, the
`tasks.py` and `invoke.yaml` requirements, the lock-file contract, and the
`install-args` quirks (whitespace splitting), replacing them with
`uv sync --frozen ${UV_SYNC_ARGS}`. The action would then work on any `uv`
project with no setup. The price is a different public contract (`install-args`
would take `uv sync` options such as `--group docs` or `--no-dev`, not the
`invoke-tasklib` ones) and that projects relying on a customised
`env.install` task lose it. If the plan is to keep the action only for the
author's own repositories, which all use `invoke-tasklib`, keep it. If the plan
is wider use, drop it. This is the only decision in this document that changes
the purpose, so it should be made before step 2 of the plan in section 7.

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
