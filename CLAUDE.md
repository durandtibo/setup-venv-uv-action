# CLAUDE.md

Guidance for coding agents working in this repository.

## Repository purpose

This repository is a GitHub composite action (`action.yaml`) that installs
`uv`, sets up Python, and installs the project dependencies with the `inv
env.install` task of `invoke-tasklib`. `pyproject.toml`, `tasks.py`,
`invoke.yaml` and `src/` form a minimal dummy project (`myproject`) that the
workflows use to test the action. They are not a library: do not add features
there.

## Environment

- Use the virtual environment in `.venv`: `.venv/bin/python`, `.venv/bin/inv`.
- Use the `Makefile` (`make help` lists the targets). `.make/` is a shared
  subtree synced by a bot (`bot-sync-shared-makefile.yaml`): do not edit it
  here.
- Format and lint before committing: `make format` and `make lint` (yamllint,
  markdownlint, prettier, ...). Fix the issues they raise. Disabling a rule is
  not fixing it.
- Workflows cannot be run locally. Say so in the PR instead of claiming they
  pass.

## Workflow

- One branch and one pull request per logical change. Branch from an up to date
  `main`, and do not commit or push to `main`.
- Name the branch `<type>/<short-description>` in lowercase kebab-case, with one
  of these types: `feat`, `bugfix`, `hotfix`, `docs`, `refactor`, `perf`,
  `test`, `chore`, `ci`.
- In the PR description, say what was changed, what was deliberately not
  changed, and any behaviour change (for example a changed input, default or
  output of the action).
- When a PR conflicts with `main`, merge `origin/main` into the branch (do not
  rebase and force-push).
- Update `README.md` and `.github/OVERVIEW.md` when inputs or workflows change.

## Action (`action.yaml`)

- Keep the input names, defaults and descriptions consistent with `README.md`.
  Renaming or removing an input is a breaking change: call it out in the PR.
- Put the `# Step N:` comment directly above each `- name:`, with no blank lines
  inside the comment block. Keep the numbering in sync with the order of the
  steps. A group of related steps (for example the validation) is numbered
  `N.M` (`1.1`, `1.2`, ...). A step does one thing: validate one input, run one
  report command.
- Pin every third-party action to a commit SHA followed by a `#
ratchet:<owner>/<repo>@<tag>` comment, as the existing steps do. Do not use a
  tag or a branch.
- Pass inputs to shell scripts through `env:`, never by interpolating `${{
inputs.* }}` in `run:`.
- Every `run:` step sets `shell: bash` (required in composite actions).
- Reporting steps (show config, packages, tree, check) use `continue-on-error:
true`. Installation steps must fail the action.
- Validate every input in the validation steps (the first steps of the action)
  when it is possible to do so, so that an invalid value fails early with an
  `::error title=Invalid input::` message, before anything is installed,
  instead of an obscure error from a later step. Warn about the inputs that are
  ignored. Do not validate a value that only the tool receiving it can
  interpret (for example a `uv` version request or a `python-version` range),
  and say in the PR which inputs are not validated and why. Document the rule
  of each validated input in `README.md` (the validation steps and the
  `Invalid input` section).

## Workflow structure (`.github/workflows/`)

Files are prefixed by role:

- `ci.yaml`: entry point for pull requests, pushes to `main`, a nightly
  schedule and manual runs. It holds no steps, only jobs that call the reusable
  workflows below.
  - `lib-get-test-matrix.yaml`: loads the OS and Python version lists from
    `durandtibo/workflow-config-action` once, and passes them to the callers.
  - `ci-format.yaml`: YAML, Makefile, shell and Markdown format check.
  - `ci-action.yaml`: tests the action from this checkout (`uses: ./`), i.e.
    the version not released yet.
- `nightly-tests.yaml`: scheduled entry point that calls
  `nightly-test-released.yaml`, which tests the last release (the current code
  is tested nightly by `ci.yaml`).
- `ci-verify-workflows.yaml`: lints the workflow files themselves. It has its
  own triggers and is not called from `ci.yaml`.
- `bot-*.yaml`: scheduled automation that opens PRs or acts on runs (format
  files, pin actions, sync `.make/`, cancel stale runs, report queued runs).
- `security-dependency-review.yaml`: dependency review on pull requests.
- `security-scorecard.yaml`: OSSF Scorecard supply-chain analysis.

Conventions:

- Set least-privilege `permissions` (explicit, never broader than needed) and
  `timeout-minutes` on jobs. `bot-*.yaml` workflows use `permissions: {}` at the
  workflow level and grant per job. So do `ci.yaml` and its callees.
- Reusable workflows without inputs (`ci-format.yaml`) also have `workflow_dispatch`, so they
  can be run alone.
- Put `make` targets in the steps rather than duplicating commands, so local
  runs and CI match.
- Start each file with a comment saying what it does, and update it when the
  behaviour changes.

## Tests

The action is tested by `.github/workflows/ci-action.yaml` (`uses: ./`) and
`.github/workflows/nightly-test-released.yaml` (the last release).

- The two files must stay identical except for the header comment, the `name`
  and the `uses:` line. Change one, then apply the same change to the other.
  Exception: a job that tests an input added after the latest release goes only
  in `ci-action.yaml`, because the stable release does not know the input. Add
  it to `nightly-test-released.yaml` when its release is bumped.
- Every input of the action needs a job that sets it and asserts its effect (not
  only that the action succeeds). Add a job when adding an input.
- Every validated input needs a test that passes an invalid value and asserts
  that the action fails. Assert that it failed because of the validation, for
  example by checking that nothing was installed, not only that it failed.
- Read OS and Python version lists from `durandtibo/workflow-config-action`
  outputs; do not hardcode them.
- Assert the expected value with an explicit check (for example `assert
numpy.__version__ == '2.4.0'`), and pass matrix values to scripts through
  `env:`.
- Keep each job independent and short; set `timeout-minutes`.
- Test-stable runs the released version, so new checks may fail there for a real
  reason. Report it instead of weakening the check.

## Reporting

- Report faithfully: say which checks were run (`make lint`, `make format`),
  which were not, and that the workflows and CI were not awaited.
- Mention failures that already exist on `main` instead of hiding them.
