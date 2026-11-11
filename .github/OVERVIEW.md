# GitHub Configuration

This directory contains GitHub-specific configuration files that control the
behavior of this repository's automation, issue tracking, and CI/CD pipelines.

## Directory Structure

```text
.github/
├── ISSUE_TEMPLATE/                    # Issue templates
│   ├── bug-report.yml                 # Bug report form template
│   └── feature-request.yml            # Feature request form template
├── workflows/                         # GitHub Actions workflow definitions
│   ├── ci.yaml                        # Main CI pipeline (format + tests)
│   ├── format.yaml                    # Formatting checks
│   ├── test-local.yaml                # Tests the action of this repository
│   ├── test-stable.yaml               # Tests the last stable release
│   ├── nightly-tests.yaml             # Scheduled nightly test runs
│   ├── ci-verify-workflows.yaml       # Validates workflow file syntax
│   ├── dependency-review.yml          # Reviews dependencies changed by a PR
│   ├── bot-cancel-stale-queued-runs.yaml # Cleans up queued workflow runs
│   ├── bot-format-files.yaml          # Weekly formatting PR
│   ├── bot-pin-action.yaml            # Weekly PR pinning actions to SHAs
│   └── bot-sync-shared-makefile.yaml  # Weekly PR syncing the .make subtree
├── CODEOWNERS                         # Code owners
├── dependabot.yml                     # Dependabot configuration
└── PULL_REQUEST_TEMPLATE.md           # Template for pull request descriptions
```

## Workflows Overview

### Primary Workflows

#### CI (ci.yaml)

- **Trigger**: Push/PR to main branch, manual dispatch
- **Purpose**: Main continuous integration pipeline
- **Jobs**: Calls format, test-local, and test-stable workflows
- **Permissions**: `actions: write`, `contents: read`

#### Format (format.yaml)

- **Trigger**: Called by CI workflow, manual dispatch
- **Purpose**: Checks that YAML, Makefile, shell, and Markdown files follow the
  formatting rules, and that test-stable is up to date with test-local
- **Jobs**: Runs `make format`, then fails if `git diff` shows changes
- **Permissions**: `contents: read`

#### Test Local Action (test-local.yaml)

- **Trigger**: Called by CI workflow, manual dispatch
- **Purpose**: Tests the action using the current repository code (`uses: ./`)
- **Config**: The OS and Python version lists come from
  `durandtibo/workflow-config-action`
- **Jobs**: The jobs are grouped by what they cover (the job names are in the
  file):
  - Defaults and outputs: the default inputs on every Unix OS of the config,
    and the `python-version` and `uv-version` outputs
  - Python and `uv` versions: every standard Python version of the config, a
    version range, the `.python-version` file, a pinned `uv` version
  - Installation inputs: `install-args` (including glob characters),
    `extra-packages` (pins, extras, ranges), `enable-cache`,
    `working-directory` (including its `uv.toml`)
  - `invoke-tasklib`: the version of `uv.lock` is installed, a project without
    it fails, a group that is not installed does not break the action
  - Failures: one matrix job with a case per invalid input, and one with a case
    per missing project file. Each case asserts that the action failed before
    `uv` was installed
- **Permissions**: `actions: write`, `contents: read`

#### Test Stable Action (test-stable.yaml)

- **Trigger**: Called by CI workflow, manual dispatch
- **Purpose**: Tests the last published release to detect regressions
- **Jobs**: Generated from test-local by `make generate-stable-workflow`
  (`scripts/generate-stable-workflow.sh`), without the jobs marked
  `# local-only` (inputs and behaviours added after that release). Do not edit
  it by hand: the format workflow fails when it differs
- **Permissions**: `actions: write`, `contents: read`

### Scheduled Workflows

#### Nightly Tests (nightly-tests.yaml)

- **Trigger**: Daily at 9:00 AM UTC, manual dispatch
- **Purpose**: Regular testing to catch issues early
- **Jobs**: Runs complete CI pipeline (format + tests)
- **Permissions**: `actions: write`, `contents: read`

#### Cancel Stale Queued Runs (bot-cancel-stale-queued-runs.yaml)

- **Trigger**: Hourly, manual dispatch
- **Purpose**: Cleanup queued workflow runs to save resources
- **Uses**: durandtibo/cancel-queued-runs-action
- **Permissions**: `actions: write`, `contents: read`

#### Bot Workflows (bot-*.yaml)

- **bot-format-files.yaml**: Fridays at 6:00 AM UTC, opens a PR when files
  drifted out of format
- **bot-pin-action.yaml**: Wednesdays at 8:00 AM UTC, opens a PR that pins
  actions to commit SHAs with ratchet
- **bot-sync-shared-makefile.yaml**: Wednesdays at 6:00 AM UTC, opens a PR that
  syncs the `.make` subtree from durandtibo/shared-makefiles

### Validation Workflows

#### Verify Workflows (ci-verify-workflows.yaml)

- **Trigger**: Changes to `.github/workflows/**`, manual dispatch
- **Purpose**: Validates workflow file syntax and structure
- **Uses**: durandtibo/verify-github-workflow-action
- **Permissions**: `contents: read`

#### Dependency Review (dependency-review.yml)

- **Trigger**: Pull requests
- **Purpose**: Surfaces known-vulnerable dependencies introduced by a PR

## Issue Templates

### Bug Report (ISSUE_TEMPLATE/bug-report.yml)

Structured form for reporting bugs with fields for:

- Bug description with workflow YAML and error logs
- Environment details (action version, runner OS, etc.)

### Feature Request (ISSUE_TEMPLATE/feature-request.yml)

Form for proposing new features with fields for:

- Feature description and motivation
- Alternative solutions considered
- Additional context

## Pull Request Template

The `PULL_REQUEST_TEMPLATE.md` provides a standardized format for PRs including:

- Description of changes
- Checklist for code review, testing, and documentation

## Dependabot

The `dependabot.yml` configures automatic dependency updates for:

- GitHub Actions: Weekly updates for action versions in workflows

## Workflow Dependencies

```text
ci.yaml
├─→ format.yaml (make format + git diff)
├─→ test-local.yaml (test with current code)
└─→ test-stable.yaml (test with published version)

nightly-tests.yaml
├─→ format.yaml
├─→ test-local.yaml
└─→ test-stable.yaml
```

## Testing Strategy

The repository uses a dual-testing approach:

1. **Local Testing** (`test-local.yaml`): Tests uncommitted changes using `uses:
./`
2. **Stable Testing** (`test-stable.yaml`): Tests the published action version
   for regression detection

This ensures both new changes work correctly and the published version remains
functional.

## Permissions

All workflows follow the principle of least privilege:

- **Read-only by default**: Most workflows only need `contents: read`
- **Actions write**: Required for workflows that manage other workflow runs
- **Explicit permissions**: Each workflow declares exactly what it needs

## Workflow Dispatch

All workflows support manual triggering via `workflow_dispatch`, enabling:

- On-demand testing during development
- Manual verification before releases
- Troubleshooting and debugging

## Contributing

When adding or modifying workflows:

1. Follow the existing naming convention (lowercase with hyphens)
2. Add comprehensive comments explaining the workflow purpose
3. Document all inputs and permissions
4. Test with `ci-verify-workflows.yaml` before committing
5. Update this README if adding new workflows

## References

- [GitHub Actions
  Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax
  Reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Dependabot Configuration
  Options](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file)
