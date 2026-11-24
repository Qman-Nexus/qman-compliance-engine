# Qman Compliance Engine

A lightweight, extensible Policy as Code engine for
automated security and compliance verification.

Part of the Qman Enterprise Platform reference architecture.

## Features

- GitHub App authentication
- Short-lived installation access tokens
- Declarative YAML security policies
- Automated compliance evaluation
- Time-bound security exceptions
- Structured JSON reporting
- Automated unit tests

## Architecture

The engine separates authentication, policy evaluation,
exception management and reporting.

## Requirements

- Python 3.13
- A GitHub organization
- A GitHub App with appropriate read-only permissions

## Installation

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Configuration

Copy config.example.json to config.json and configure
your GitHub App credentials.

Store private keys outside the repository.

## Usage

```bash
python compliance.py
```

## Development

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

## Compliance statuses

| Status | Description |
|--------|-------------|
| PASS | Control satisfied |
| FAIL | Control not satisfied |
| WARN | Approved security exception |
| UNKNOWN | Control could not be verified |

## Exit codes

| Code | Description |
|------|-------------|
| 0 | No failed or unknown controls |
| 1 | Compliance failure |
| 2 | Technical or verification error |

## Security

See SECURITY.md for security requirements
and vulnerability reporting.

## Project status

Version 0.3.0 — Early development.

This project is not a certification or a guarantee
of infrastructure security.

## License

Apache License 2.0.
