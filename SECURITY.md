# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the latest version only.

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < Latest| :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in peakbagger-cli, please report it responsibly.

### How to Report

**Preferred:** Use GitHub's Security Advisories feature:

1. Go to <https://github.com/dreamiurg/peakbagger-cli/security/advisories>
2. Click "Report a vulnerability"
3. Provide a detailed description of the vulnerability

**Alternative:** Email the maintainer directly at <the@dreamiurg.net> with:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)

### What to Expect

- **Initial Response:** Within 48 hours
- **Status Update:** Within 5 business days
- **Fix Timeline:** Depends on severity:
  - Critical: Within 7 days
  - High: Within 30 days
  - Medium: Within 90 days
  - Low: Best effort

## Security Scope

### In Scope

Security issues that qualify for reporting:

- Vulnerabilities in package dependencies
- Command injection vulnerabilities
- Authentication or authorization bypass
- Exposure of sensitive data
- Cross-site scripting (XSS) in HTML parsing
- Denial of service issues

### Out of Scope

The following are NOT considered security issues:

- Feature requests
- Questions about usage
- Bugs without security impact
- Issues in third-party dependencies (report to those projects)
- Social engineering attacks
- Physical attacks
- Issues requiring compromised credentials

## Best Practices

When using peakbagger-cli:

- Keep the package updated to the latest version
- Use the official PyPI package: `pip install peakbagger`
- Do not expose API credentials in version control
- Follow rate limiting guidelines to avoid being blocked
