# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of setup-venv-uv-action seriously. If you believe you have
found a security vulnerability, please report it to us as described below.

### How to Report a Security Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via GitHub's Security Advisory feature:

1. Go to the
   [Security](https://github.com/durandtibo/setup-venv-uv-action/security)
   tab
2. Click "Report a vulnerability"
3. Fill out the form with details about the vulnerability

Alternatively, you can email the maintainer directly. You can find the contact
information in the [repository](https://github.com/durandtibo/setup-venv-uv-action).

### What to Include

Please include the following information in your report:

- Type of issue (e.g., command injection, credential exposure, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

This information will help us triage your report more quickly.

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report
  within 3 business days
- **Updates**: We will send you regular updates about our progress
- **Disclosure**: We will coordinate with you on the disclosure timeline
- **Credit**: If you'd like, we will publicly thank you for the responsible
  disclosure

### Security Update Process

1. The security report is received and assigned to a primary handler
2. The problem is confirmed and affected versions are determined
3. Code is audited to find any similar problems
4. Fixes are prepared for all supported versions
5. New releases are issued and announcements are made

## Security Considerations for Users

When using this action in your workflows:

### Secrets Management

- **Never hardcode secrets**: Always use GitHub Secrets for sensitive data
- **Limit secret scope**: Only grant secrets to workflows that need them
- **Rotate secrets**: Regularly update credentials and tokens

### Workflow Permissions

- **Principle of least privilege**: This action only requires `contents: read`
  and `actions: write` for the cancel-stale-runs workflow
- **Review permissions**: Always review the permissions section in workflows
  using this action

### Dependency Security

- **Pin action versions**: Use specific version tags (e.g., `@v0.0.1`) instead
  of `@main`
- **Monitor updates**: Watch for security updates via Dependabot or GitHub
  Security Advisories
- **Review dependencies**: This action depends on:
  - [astral-sh/setup-uv](https://github.com/astral-sh/setup-uv)
  - [durandtibo/uv-install-package-action](https://github.com/durandtibo/uv-install-package-action)

### Code Execution

This action executes code in your repository through:

- `tasks.py` with invoke tasks
- `uv sync` and `uv pip install` commands

**Best practices**:

- Review your `tasks.py` file for security issues
- Audit dependencies in `pyproject.toml`
- Use `uv.lock` to pin dependency versions

## Known Security Considerations

### Supply Chain Security

This action installs packages using `uv`, which downloads packages from PyPI.
To mitigate supply chain risks:

- Use `uv.lock` for reproducible builds
- Consider using a private package index for sensitive projects
- Regularly audit your dependencies with tools like `pip-audit`

### Command Injection

The action passes user inputs to shell commands. While we sanitize inputs,
users should:

- Avoid using untrusted input in workflow configurations
- Be cautious with `install-args` input from external sources

## Security-Related Configuration

### yamllint Configuration

Our `.yamllint.yaml` helps prevent common YAML syntax issues that could lead to
security misconfigurations.

## Additional Resources

- [GitHub Actions Security Best
  Practices](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [Securing GitHub Actions
  Workflows](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [uv Security
  Considerations](https://github.com/astral-sh/uv#security)

## Questions?

If you have questions about security but don't have a vulnerability to report,
feel free to:

- Open a GitHub Discussion
- Open a regular GitHub Issue labeled "security"

Thank you for helping keep setup-venv-uv-action and its users safe!
