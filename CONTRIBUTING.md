# Contributing to setup-venv-uv-action

Thank you for your interest in contributing! This document provides guidelines
and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected
to uphold this code. Please read
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:

   ```bash
   git clone https://github.com/YOUR-USERNAME/setup-venv-uv-action.git
   cd setup-venv-uv-action
   ```

3. **Add the upstream repository**:

   ```bash
   git remote add upstream https://github.com/durandtibo/setup-venv-uv-action.git
   ```

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- [invoke](https://www.pyinvoke.org/) task runner
- Node.js (for markdown linting)

### Installation

1. **Install uv** (if not already installed):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install invoke**:

   ```bash
   uv pip install "invoke>=2.2.0"
   ```

   Or use the Makefile shortcut:

   ```bash
   make install-invoke
   ```

3. **Install project dependencies**:

   ```bash
   inv install
   ```

### Available Make Commands

The Makefile is provided for convenience during local development:

```bash
make format          # Format and lint all code (markdown, YAML)
make install-invoke  # Install invoke task runner (optional shortcut)
```

Note: The GitHub Action does not depend on the Makefile. It installs invoke
directly using `uv pip install "invoke>=2.2.0"`.

### Available Invoke Tasks

```bash
inv install                      # Install project dependencies
inv show-installed-packages      # Display all installed packages
inv show-python-config           # Display Python configuration
```

## Making Changes

### Branching Strategy

1. **Create a feature branch** from `main`:

   ```bash
   git checkout -b feature/your-feature-name
   ```

   or for bug fixes:

   ```bash
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes** in logical, well-documented commits

3. **Keep your branch updated** with upstream:

   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

### Commit Messages

Write clear, concise commit messages following these guidelines:

- Use the imperative mood ("Add feature" not "Added feature")
- First line should be 50 characters or less
- Reference issues and pull requests when relevant
- Examples:
  - `Add support for Python 3.13`
  - `Fix dependency resolution issue (#123)`
  - `Update documentation for install-args input`

## Testing

### Running Tests Locally

The action is tested through GitHub Actions workflows. To test locally:

1. **Test with the local action**:
   Create a test workflow in `.github/workflows/test-local.yaml` (already
   exists)

2. **Verify formatting**:

   ```bash
   make format
   ```

### Testing Workflows

The project includes several test workflows:

- **test-local.yaml**: Tests the action from the local repository
- **test-stable.yaml**: Tests the published stable version
- **format.yaml**: Validates code formatting (markdown, YAML)
- **ci.yaml**: Main CI pipeline that runs all checks

Test your changes by pushing to your fork and checking the Actions tab.

## Code Style

### YAML Files

- Use 2 spaces for indentation
- Follow yamllint rules (see `.yamllint.yaml`)
- Add comments for complex configurations

### Markdown Files

- Follow markdownlint rules (see `.markdownlint.json`)
- Use proper heading hierarchy
- Include code examples where appropriate
- Keep line length reasonable (no strict limit, but avoid very long lines)

### Python Files

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Include docstrings for functions and classes
- Use raw docstrings (r"""...""") for consistency

### Formatting Commands

Before submitting, run:

```bash
make format
```

This will:

- Lint markdown files with markdownlint
- Format files with prettier
- Lint YAML files with yamllint

## Pull Request Process

### Before Submitting

1. **Test your changes** thoroughly
2. **Run formatting** checks: `make format`
3. **Update documentation** if you've changed functionality
4. **Update README.md** if you've added features or changed usage
5. **Check that CI passes** on your fork

### Submitting a Pull Request

1. **Push your branch** to your fork:

   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub with:
   - Clear title describing the change
   - Description of what changed and why
   - Reference to related issues (e.g., "Fixes #123")
   - Screenshots for UI/output changes (if applicable)

3. **Complete the PR checklist**:
   - [ ] I have performed a self-review of my code
   - [ ] If it is a new feature, I have added thorough tests and updated the
         documentation
   - [ ] My submission passes tests

4. **Respond to review feedback** promptly

### After Submission

- Address reviewer feedback
- Keep the PR updated with the main branch
- Be patient - maintainers volunteer their time

## Reporting Bugs

### Before Reporting

1. **Check existing issues** - your bug might already be reported
2. **Test with the latest version** - it might already be fixed
3. **Gather information**:
   - GitHub Actions runner OS and version
   - Python version being used
   - Action version
   - Relevant workflow configuration
   - Error messages and logs

### Creating a Bug Report

Use the bug report template (`.github/ISSUE_TEMPLATE/bug-report.yml`) and include:

- Clear, descriptive title
- Steps to reproduce
- Expected behavior
- Actual behavior
- Relevant logs and error messages
- Workflow configuration (YAML)
- Environment details

## Suggesting Enhancements

### Feature Requests

Use the feature request template (`.github/ISSUE_TEMPLATE/feature-request.yml`) and include:

- Clear description of the feature
- Use cases and benefits
- Possible implementation approach
- Alternatives you've considered

### Enhancement Ideas

For smaller improvements:

1. Open an issue with the "enhancement" label
2. Describe the current behavior
3. Describe the improved behavior
4. Explain why this would be useful

## Questions?

If you have questions that aren't covered here:

1. Check the [README.md](README.md) for usage documentation
2. Search existing issues and discussions
3. Open a new issue with your question

## License

By contributing, you agree that your contributions will be licensed under the
same BSD 3-Clause License that covers the project.

## Thank You

Your contributions make this project better for everyone. We appreciate your
time and effort! 🎉
