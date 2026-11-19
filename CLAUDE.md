# CLAUDE.md

Guidance for coding agents working in this repository.

## Repository purpose

This repository is a GitHub composite action (`action.yaml`) that installs
`uv`, sets up Python, and installs the project dependencies with the `inv
env.install` task of `invoke-tasklib`. `pyproject.toml`, `tasks.py`,
`invoke.yaml` and `src/` form a minimal dummy project (`myproject`) that the
workflows use to test the action. They are not a library: do not add features
there. `scripts/` holds the maintainer checks, which are not part of the action:
`check_readme_inputs.py` (README against `action.yaml`) and `check_export.sh`
(the exported set). `review/` holds the design documents, not part of the action:
`target_state.md` (the design ideas of this action) and `testing.md` (the testing
strategy shared by the action repositories).

## Environment

- Use the virtual environment in `.venv`: `.venv/bin/python`, `.venv/bin/inv`.
- Use the `Makefile`; run `make help` to list the targets. `make test` runs
  the checks of this repository (`make check-readme`, `make check-export`).
- Do not edit `.make/`: it is a shared subtree synced by
  `bot-sync-shared-makefile.yaml`.
- Format and lint before committing: `make format` and `make lint` (yamllint,
  markdownlint, prettier, ...). Fix the issues they raise. Disabling a rule is
  not fixing it.
- `scripts/check_readme_inputs.py` (run by `make check-readme`) only uses the
  standard library. Keep it that way, so that it runs without installing
  anything.
- Run `make test` before committing when `action.yaml`, `README.md` or
  `.gitattributes` change.
- Some workflows cannot be run locally (the action and the CI jobs need GitHub
  runners). Say so in the PR instead of claiming they pass.

## Git workflow

- One branch and one pull request per logical change. Branch from an up to date
  `main`, and do not commit or push to `main`.
- Name the branch `<type>/<short-description>` in lowercase kebab-case, with one
  of these types: `feat`, `bugfix`, `hotfix`, `docs`, `refactor`, `perf`,
  `test`, `chore`, `ci`.
- Write commit messages and PR titles as a short imperative sentence starting
  with a verb such as `Add`, `Fix`, `Update`, `Remove` or `Improve`. Do not use
  conventional-commit prefixes like `docs:` or `feat:` (the type prefix is only
  for branch names). The squash-merge appends the PR number, so do not add one.
- In the PR description, say what was changed, what was deliberately not
  changed, and any behaviour change (for example a changed input, default or
  output of the action).
- Do not escape special characters such as the backtick in PR titles and
  descriptions (no backslash before it): the escape characters are not rendered
  well. Write them as plain Markdown.
- When a PR conflicts with `main`, merge `origin/main` into the branch (do not
  rebase and force-push).
- Update `README.md` and `.github/OVERVIEW.md` when inputs, behaviour or
  workflows change. `make check-readme` (part of `make lint`) fails when the
  inputs, outputs or defaults of the README tables differ from `action.yaml`.
- Releases are immutable exact version tags (`v0.3.1`, ...). Do not create or
  move floating tags (`v0`, `latest`) and do not document them as an option.
  The README examples and the `released` steps of `ci-action.yaml` pin an exact
  release.

## Action rules (`action.yaml`)

- Keep the input names, defaults and descriptions consistent with `README.md`.
  Renaming or removing an input is a breaking change: call it out in the PR.
- Put the `# Step N:` comment directly above each `- name:`, with no blank lines
  inside the comment block. Keep the numbering in sync with the order of the
  steps. A group of related steps (for example the validation) is numbered
  `N.M` (`1.1`, `1.2`, ...). A step does one thing: validate one input, run one
  report command.
- Pin every third-party action, in `action.yaml` and in the workflows, to a
  commit SHA followed by a `# ratchet:<owner>/<repo>@<tag>` comment, as the
  existing steps do. Do not use a tag or a branch.
- Pass inputs to shell scripts through `env:`, never by interpolating
  `${{ inputs.* }}` in `run:`.
- Every `run:` step sets `shell: bash` (required in composite actions).
- Reporting steps (show config, packages, tree, check) use
  `continue-on-error: true`. Installation steps must fail the action.
- Only ship what the action needs at runtime. Files the action itself uses
  (`action.yaml`, `LICENSE`, and any file it reads through
  `${{ github.action_path }}`) are exported, and `.gitattributes` marks
  everything else `export-ignore` (the dummy project `pyproject.toml`,
  `tasks.py`, `invoke.yaml`, `src/`, `scripts/`, `.github/`, tests, docs).
  Today the action reads no file of this repository. When it starts using one,
  un-ignore it in `.gitattributes`. Never make the action read the dummy
  project or other repo files that are not exported. Check the exported set
  with `git archive --worktree-attributes HEAD | tar t`.
- Validate every input in the validation steps (the first steps of the action)
  when it is possible to do so, so that an invalid value fails early with an
  `::error title=Invalid input::` message, before anything is installed,
  instead of an obscure error from a later step. Warn about the inputs that are
  ignored. Do not validate a value that only the tool receiving it can
  interpret (for example a `uv` version request or a `python-version` range),
  and say in the PR which inputs are not validated and why. Document the rule
  of each validated input in `README.md` (the validation steps and the
  `Invalid input` section).

## Shell script rules (`scripts/check_export.sh`, inline `run:` steps)

- Quote all variables. Code must pass `shellcheck` and `shfmt` via `make lint`
  / `make format`.
- Keep the scripts short and readable: `scripts/check_export.sh` uses
  `set -euo pipefail` and no functions. If a script grows functions, end a
  function that can fail with an explicit `return 1`
  (`cmd || { echo ...; return 1; }`) and do not rely on `set -e`: a caller in
  an `||` list turns it off.
- Fail early with a clear `::error` message (`::error title=Invalid input::` for
  an input).
- `scripts/check_export.sh` lists the files the action needs (`EXPECTED`). When
  the action starts using a new file, add it there and un-ignore it in
  `.gitattributes`.
- Keep `scripts/check_readme_inputs.py` standard-library only.

## Workflow structure (`.github/workflows/`)

Files are prefixed by role:

- `ci.yaml`: entry point for pull requests, pushes to `main`, a nightly
  schedule and manual runs. It holds no steps, only jobs that call the reusable
  workflows below.
  - `lib-get-test-matrix.yaml`: loads the OS and Python version lists from
    `durandtibo/workflow-config-action` once. The callers pass the result down
    through the `test-matrix` input of `ci-action.yaml`.
  - `ci-format.yaml`: YAML, Makefile, shell and Markdown format check.
  - `ci-export.yaml`: `make check-export`, the exported set is what the action
    needs.
  - `ci-action.yaml`: tests the action, with the input `use-released`
    (default `false`): the checkout (`uses: ./`), i.e. the version not
    released yet, or the last release.
- `nightly.yaml`: scheduled entry point that calls `ci-action.yaml` with
  `use-released: true`, which tests the last release (the current code is
  tested nightly by `ci.yaml`).
- `ci-verify-workflows.yaml`: lints the workflow files themselves. It has its
  own triggers and is not called from `ci.yaml`, so it can be a required check.
- `bot-*.yaml`: scheduled automation that opens PRs or acts on runs (format
  files, pin actions, sync `.make/`, cancel stale runs, report queued runs).
- `security-dependency-review.yaml`: dependency review on pull requests.
- `security-scorecard.yaml`: OSSF Scorecard supply-chain analysis.

Conventions:

- Every workflow has `permissions: {}` at the workflow level (it grants
  nothing, never a grant). Set explicit least-privilege `permissions` on every
  job (including jobs that call a reusable workflow), never broader than
  needed, and set `timeout-minutes` on jobs.
- Each reusable workflow without inputs (`ci-format.yaml`,
  `lib-get-test-matrix.yaml`) is a `workflow_call` workflow that also has
  `workflow_dispatch`, so it can be run alone. `ci-action.yaml` has inputs but
  also `workflow_dispatch` (with `use-released`): its `get-matrix` job, which
  only runs on a manual dispatch, loads the matrix that the callers pass
  otherwise. Add a new check as a new `ci-<name>.yaml` plus a job in `ci.yaml`.
- Put `make` targets in the steps rather than duplicating commands, so local
  runs and CI match.
- Start each file with a comment saying what it does, and update it when the
  behaviour changes.

## Tests

The action is tested by one workflow, `.github/workflows/ci-action.yaml`, with
the input `use-released`: `false` (called by `ci.yaml`) runs the checkout
(`uses: ./`), `true` (called by `nightly.yaml`) runs the last release.

- One behaviour per job. Cover the success, the failure and the edge cases
  (empty value, unusual value) of an input.
- Every step that runs the action exists twice in a job: a `local` step
  (`if: ${{ !inputs.use-released }}`, `uses: ./`) and a `released` step
  (`if: ${{ inputs.use-released }}`, pinned to the release SHA with a
  `ratchet` comment), with the same `with:`. The steps after them read
  `steps.local.outputs.x || steps.released.outputs.x` (a skipped step has no
  outputs) and, for a failure path,
  `steps.local.outcome == 'skipped' && steps.released.outcome || steps.local.outcome`.
  Change both steps together.
- A job that tests an input added after the latest release has
  `if: ${{ !inputs.use-released }}` on the job, because the stable release does
  not know the input. Remove the `if` when its release is bumped.
- Every input of the action needs a job that sets it and asserts its effect (not
  only that the action succeeds). Add a job when adding an input.
- Every validated input needs a test that passes an invalid value and asserts
  that the action fails. Assert that it failed because of the validation, for
  example by checking that nothing was installed, not only that it failed.
- Read OS and Python version lists from `durandtibo/workflow-config-action`
  outputs; do not hardcode them.
- Assert the expected value with an explicit check (for example
  `assert numpy.__version__ == '2.4.0'`), and pass matrix values to scripts
  through `env:`.
- Keep each job independent and short; set `timeout-minutes`.
- The nightly run tests the released version, so a new check may fail there for
  a real reason. Report it instead of weakening the check.
- Cases that only differ by their inputs are rows of one matrix job
  (`test-package`, `test-invalid-inputs`, `test-uv-version-range`), not one job
  each: a new case is a row.
- Every bug fix needs a regression test (a job or a matrix row) that fails
  without the fix.

## Testing strategy

The strategy is shared by the action repositories of `durandtibo`. This
repository follows it: the local and released runs are one workflow file with
a `use-released` input (see [Tests](#tests)). The full reasoning and the
properties (T1 to T16) are in `review/testing.md`; the design ideas of this
action are in `review/target_state.md`.

Three levels:

1. **Code**: the logic of a script, tested alone without GitHub. This
   repository has no such code to test: the scripts, `check_readme_inputs.py`
   (`make check-readme`) and `check_export.sh` (`make check-export`), are
   checks run by `make test`, and the action runs shell inline.
2. **Local action**: the action from this checkout (`uses: ./`) in a real
   workflow (`ci-action.yaml`).
3. **Released action**: the latest stable release, run nightly with the same
   cases as level 2 (`ci-action.yaml` with `use-released: true`). Never run it on pull
   requests.

Rules:

- Test a behaviour at the cheapest level that can show it. The action tests
  check the contract and the wiring: inputs reach the step that uses them,
  outputs are set, the action fails on an invalid input. Do not duplicate in a
  job what `make check-readme` already checks.
- Split the action tests in two. **General behaviour** (the default usage and
  the main documented usage) runs on the full matrix: `os_matrix`, and
  `python_versions_standard` or `python_versions` when the action depends on
  Python. **Edge cases** (one input, one invalid value, an unusual file) run on
  one runner (`ubuntu-latest`), or on `os_latest` (the `*-latest` runners, Linux
  and macOS) when the case depends on the OS (paths, glob expansion, whitespace
  handling: `test-working-directory-paths`, `test-install-args-glob`,
  `test-extra-packages`). There is no reduced matrix on pull requests: the same
  matrix runs on pull requests, pushes and the schedule.
- Supported platforms: Linux and macOS (`os_matrix` is the `os_unix` list of
  `durandtibo/workflow-config-action`), as the README says. Windows is not
  supported and not tested. Every OS and Python version the README claims is in
  a matrix, and every cell of a matrix is claimed.
- Never write an OS or a Python version in a workflow to select a runner or an
  interpreter matrix: read the lists from `durandtibo/workflow-config-action`
  through `lib-get-test-matrix.yaml`. A version that a test asserts (the
  default Python, a pinned package) is an expected value, not a matrix.
- Failure paths use `continue-on-error: true`, an `id`, and a step that asserts
  `steps.<id>.outcome`. Assert that the failure came from the validation (for
  example that `uv` was not installed), not a message text. A negative test
  must not be able to pass for the wrong reason: check the precondition (for
  example that `uv` is not installed before the action runs), and when the
  case allows it, run a positive case on the same runner before it.
- Assert the value or the format of outputs (`cache-hit`, `uv-version`,
  `python-version`, `package-installed`), never just print them.
- Tests have no side effect outside the runner: throwaway files in the
  checkout, no push, no change to a repository. If something cannot be tested
  in CI, write down which check covers it.
- Check what is shipped: the exported set
  (`git archive --worktree-attributes HEAD | tar t`) must contain every file
  the action needs, because `uses: ./` runs the whole checkout and hides a
  missing file. `make check-export` lists the set, and the `test-export` job of
  `ci-action.yaml` runs the action from the exported archive.
- Set `timeout-minutes` on every job, and `fail-fast: false` and `max-parallel`
  on matrix jobs.
- Keep the README inputs and outputs in step with `action.yaml`
  (`make check-readme`, `scripts/check_readme_inputs.py`).
- Put an assertion in one place: a check shared by the `local` and `released`
  steps reads the merged outputs (`steps.local.outputs.x ||
steps.released.outputs.x`) in one step, not in two copies.

## Reporting

- State which checks ran (`make lint`, `make format`, `make test`) and which
  did not.
- Note that the workflows and CI were not awaited.
- Report failures that already exist on `main` rather than hiding them.
