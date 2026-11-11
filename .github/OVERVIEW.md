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
│   ├── lib-get-test-matrix.yaml       # Loads the OS and Python version matrices
│   ├── ci-format.yaml                 # Formatting checks
│   ├── ci-action.yaml                 # Tests the action of this repository
│   ├── nightly-test-released.yaml     # Tests the last stable release
│   ├── nightly-tests.yaml             # Scheduled nightly test runs
│   ├── ci-verify-workflows.yaml       # Validates workflow file syntax
│   ├── security-scorecard.yaml        # OSSF Scorecard analysis
│   ├── security-dependency-review.yaml # Reviews dependencies changed by a PR
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

- **Trigger**: Push/PR to main branch, nightly schedule, manual dispatch
- **Purpose**: Main continuous integration pipeline
- **Jobs**: Calls lib-get-test-matrix, ci-format and ci-action workflows
- **Permissions**: set per job (`contents: read`)

#### Format (ci-format.yaml)

- **Trigger**: Called by CI workflow, manual dispatch
- **Purpose**: Checks that YAML, Makefile, shell, and Markdown files follow the
  formatting rules
- **Jobs**: Runs `make format`, then fails if `git diff` shows changes
- **Permissions**: `contents: read`

#### Test Action (ci-action.yaml)

- **Trigger**: Called by CI workflow (it has inputs, so it has no manual
  dispatch of its own)
- **Purpose**: Tests the action using the current repository code (`uses: ./`)
- **Config**: The OS and Python version lists come from
  `durandtibo/workflow-config-action`
- **Jobs**: One job per input or behavior of the action, in these groups (the
  workflow file is the list of jobs):
  - defaults and versions: default inputs on every Unix OS of the config, the
    Python versions of the config, `uv-version`
  - installation inputs: `install-args`, the `package-*` inputs,
    `extra-packages`
  - `invoke-tasklib`: the version read from `uv.lock`, a missing entry, a
    dependency group that is excluded
  - project location: `working-directory` and the missing project files
  - `enable-cache` and the `cache-hit` output
  - validation: one matrix case per invalid value, and the ignored inputs
- **Permissions**: `contents: read`

#### Test Released Action (nightly-test-released.yaml)

- **Trigger**: Called by the nightly workflow (it has inputs, so it has no
  manual dispatch of its own)
- **Purpose**: Tests the last published release, which is what consumers run,
  to detect regressions caused by upstream changes (`uv`, `setup-uv`,
  `invoke-tasklib`)
- **Jobs**: Same as ci-action, except for the jobs of inputs added after that
  release, which only exist in ci-action until the release is bumped
- **Permissions**: `contents: read`

### Scheduled Workflows

#### Nightly Tests (nightly-tests.yaml)

- **Trigger**: Daily at 10:30 AM UTC, manual dispatch
- **Purpose**: Regular testing to catch issues early
- **Jobs**: Calls nightly-test-released (ci.yaml runs the current code nightly
  at 9:10 AM UTC; no format check: formatting does not change with time)
- **Permissions**: `contents: read`

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

- **Trigger**: Pull requests, pushes to main, manual dispatch
- **Purpose**: Validates workflow file syntax and structure
- **Uses**: durandtibo/verify-github-workflow-action
- **Permissions**: `contents: read`

#### Scorecard (security-scorecard.yaml)

- **Trigger**: Pushes to main, weekly schedule, branch protection changes,
  manual dispatch
- **Purpose**: Runs the OSSF Scorecard analysis and uploads the results to the
  code-scanning dashboard

#### Dependency Review (security-dependency-review.yaml)

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

`bot-pin-action.yaml` also updates the action pins (with `ratchet`). Whether
both are needed is not decided.

## Workflow Dependencies

```text
ci.yaml
├─→ lib-get-test-matrix.yaml (OS and Python versions)
├─→ ci-format.yaml (make format + git diff)
└─→ ci-action.yaml (test with current code)

nightly-tests.yaml
├─→ lib-get-test-matrix.yaml
└─→ nightly-test-released.yaml (test with published version)
```

## Testing Strategy

The action is tested by two workflows with different roles:

1. **Current code** (`ci-action.yaml`): Tests the code under review with
   `uses: ./`, on every pull request, push and nightly run of `ci.yaml`
2. **Last release** (`nightly-test-released.yaml`): Tests the published action
   version, to detect regressions caused by upstream changes

The two files are identical except for the header comment, the `name` and the
`uses:` line. A job that tests an input added after the last release exists only
in `ci-action.yaml` until the release is bumped.

## Permissions

All workflows follow the principle of least privilege:

- **Read-only by default**: Most workflows only need `contents: read`
- **Actions write**: Required for workflows that manage other workflow runs
- **Explicit permissions**: Each workflow declares exactly what it needs

## Workflow Dispatch

Workflows that are entry points, and reusable workflows without inputs
(`ci-format.yaml`, `lib-get-test-matrix.yaml`), support manual triggering via
`workflow_dispatch`. Reusable workflows with inputs (`ci-action.yaml`,
`nightly-test-released.yaml`) do not. Manual triggering enables:

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
