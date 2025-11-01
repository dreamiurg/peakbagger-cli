# Security Policy

## About This Project

This is a hobby project maintained by a single developer in my spare time. I'll do my best to address
security issues, but please set realistic expectations.

## Reporting a Vulnerability

If you find a security issue, please report it privately:

**Option 1 (Preferred):** Use GitHub's private vulnerability reporting:

1. Go to <https://github.com/dreamiurg/peakbagger-cli/security/advisories>
2. Click "Report a vulnerability"
3. Describe the issue and how to reproduce it

**Option 2:** Open a regular GitHub issue if the vulnerability is already public or low severity.

## What to Expect

**Response time:** I'll try to respond within a week or two, but it might take longer depending on my
availability. This is a hobby project, not my day job.

**Fixes:** Critical issues affecting data security or remote code execution will be prioritized. Less
severe issues will be addressed as time permits.

**Supported versions:** Only the latest release gets security updates. Old versions won't be patched.

## What Counts as a Security Issue?

**Real security issues:**

- Command injection or code execution vulnerabilities
- Exposure of sensitive data (credentials, personal info)
- Dependency vulnerabilities that affect this tool's usage

**Not security issues:**

- Feature requests or general bugs
- Issues that require physical access to your computer
- Vulnerabilities in dependencies (report those upstream)
- Rate limiting bypasses (that's between you and PeakBagger.com)

## Using This Tool Safely

- Install from PyPI: `pip install peakbagger`
- Keep it updated to get latest fixes
- This tool scrapes public data from PeakBagger.com - there are no credentials or sensitive data to protect
