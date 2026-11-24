# Contributing

Thank you for your interest in the Qman Compliance Engine.

## Development Workflow

1. Create a feature branch.
2. Implement a focused change.
3. Run local quality and security checks.
4. Submit a pull request.
5. Ensure all required CI checks pass.

## Local Quality Checks

```bash
python -m ruff format --check .
python -m ruff check .
python -m pytest tests/ -v
python -m pip_audit -r requirements.txt
python -m pip_audit -r requirements-dev.txt
actionlint .github/workflows/ci.yml
gitleaks git . --redact=100
```

## Security Requirements

- Never commit credentials or operational configuration.
- Use synthetic data in tests.
- Pin GitHub Actions to full commit SHAs.
- Review dependency updates before merging.
- Do not bypass security controls.

## Commit Messages

Use clear and descriptive commit messages.

- `feat: add policy validation`
- `fix: correct exception handling`
- `ci: improve security scanning`
- `docs: update installation instructions`

## Vulnerability Reporting

Please follow the instructions in [SECURITY.md](SECURITY.md).

## License

Contributions are licensed under the project's [Apache License 2.0](LICENSE).
