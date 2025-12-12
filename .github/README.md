# GitHub Configuration

This directory contains GitHub-specific configuration files that control the
behavior of this repository's automation, issue tracking, and CI/CD pipelines.

## Directory Structure

```text
.github/
├── ISSUE_TEMPLATE/          # Issue templates for bug reports and feature requests
│   ├── bug-report.yml       # Bug report form template
│   └── feature-request.yml  # Feature request form template
├── workflows/                        # GitHub Actions workflow definitions
│   ├── ci.yaml                      # Main CI pipeline (runs format and tests)
│   ├── format.yaml                  # Code formatting and linting checks
│   ├── test-local.yaml              # Tests using local action code
│   ├── test-stable.yaml             # Tests using published stable version
│   ├── nightly-tests.yaml           # Scheduled nightly test runs
│   ├── verify-workflows.yaml        # Validates workflow file syntax
│   └── cancel-stale-queued-runs.yaml # Cleanup for queued workflow runs
├── dependabot.yml          # Dependabot configuration for dependency updates
└── PULL_REQUEST_TEMPLATE.md # Template for pull request descriptions
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
- **Purpose**: Validates code formatting and style
- **Jobs**:
  - `markdown`: Runs markdownlint on all Markdown files
  - `yaml`: Runs yamllint on all YAML files
- **Permissions**: `contents: read`

#### Test Local Action (test-local.yaml)

- **Trigger**: Called by CI workflow, manual dispatch
- **Purpose**: Tests the action using the current repository code
- **Matrix**: Tests across multiple OS versions (Ubuntu, macOS, ARM variants)
- **Permissions**: `actions: write`, `contents: read`

#### Test Stable Action (test-stable.yaml)

- **Trigger**: Called by CI workflow, manual dispatch
- **Purpose**: Tests the published stable version (v0.0.1)
- **Matrix**: Same OS matrix as test-local
- **Permissions**: `actions: write`, `contents: read`

### Scheduled Workflows

#### Nightly Tests (nightly-tests.yaml)

- **Trigger**: Daily at 9:00 AM UTC, manual dispatch
- **Purpose**: Regular testing to catch issues early
- **Jobs**: Runs complete CI pipeline (format + tests)
- **Permissions**: `actions: write`, `contents: read`

#### Cancel Stale Queued Runs (cancel-stale-queued-runs.yaml)

- **Trigger**: Hourly, manual dispatch
- **Purpose**: Cleanup queued workflow runs to save resources
- **Uses**: durandtibo/cancel-queued-runs-action@v1.7
- **Permissions**: `actions: write`, `contents: read`

### Validation Workflows

#### Verify Workflows (verify-workflows.yaml)

- **Trigger**: Changes to `.github/workflows/*`, manual dispatch
- **Purpose**: Validates workflow file syntax and structure
- **Uses**: durandtibo/verify-github-workflow-action@v0.0.2
- **Permissions**: `contents: read`

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
├─→ format.yaml (markdown + yaml linting)
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
4. Test with `verify-workflows.yaml` before committing
5. Update this README if adding new workflows

## References

- [GitHub Actions
  Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax
  Reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Dependabot Configuration
  Options](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file)
