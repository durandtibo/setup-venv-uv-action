# Instructions for coding agents

## Repository

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
  steps.
- Pin every third-party action to a commit SHA followed by a `#
ratchet:<owner>/<repo>@<tag>` comment, as the existing steps do. Do not use a
  tag or a branch.
- Pass inputs to shell scripts through `env:`, never by interpolating `${{
inputs.* }}` in `run:`.
- Every `run:` step sets `shell: bash` (required in composite actions).
- Reporting steps (show config, packages, tree, check) use `continue-on-error:
true`. Installation steps must fail the action.

## Tests

The action is tested by `.github/workflows/test-local.yaml` (`uses: ./`) and
`.github/workflows/test-stable.yaml` (the last release).

- The two files must stay identical except for the header comment, the `name`
  and the `uses:` line. Change one, then apply the same change to the other.
  Exception: a job that tests an input added after the latest release goes only
  in `test-local.yaml`, because the stable release does not know the input. Add
  it to `test-stable.yaml` when the release in `test-stable.yaml` is bumped.
- Every input of the action needs a job that sets it and asserts its effect (not
  only that the action succeeds). Add a job when adding an input.
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
