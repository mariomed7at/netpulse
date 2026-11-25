# Contributing to NetPulse

Thank you for considering a contribution. NetPulse is an early-stage project and welcomes clear bug reports, documentation improvements, tests, and focused code changes.

## Before opening an issue

- Search existing issues to avoid duplicates.
- Use a current supported Python version (3.11+).
- Include the operating system and Python version when reporting platform-specific behavior.
- Remove passwords, tokens, public IPs that should not be disclosed, hostnames, and customer information from logs.

## Development setup

```bash
git clone https://github.com/mariomed7at/netpulse.git
cd netpulse
python -m venv .venv
# Activate the environment, then:
python -m pip install -e ".[dev]"
pytest
ruff check .
```

## Pull request guidelines

1. Keep pull requests focused and explain the problem they solve.
2. Add or update tests for behavior changes.
3. Update README or documentation when user-facing behavior changes.
4. Run `pytest` and `ruff check .` before submitting.
5. Do not add runtime dependencies without explaining why a standard-library solution is insufficient.
6. Never include real credentials, private network diagrams, or sensitive operational data.

By submitting a contribution, you agree that it may be distributed under the project's MIT License.
