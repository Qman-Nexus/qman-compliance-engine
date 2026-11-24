import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import requests
import yaml

from exception_manager import apply_exceptions, load_exceptions
from github_client import GitHubClient
from policy_loader import load_policy

BASE_DIR = Path(__file__).resolve().parent

CONFIG_PATH = BASE_DIR / "config.json"
POLICY_PATH = BASE_DIR / "policies/github-organization.yaml"
EXCEPTIONS_PATH = BASE_DIR / "exceptions/github-organization.yaml"

STATUSES = ("PASS", "FAIL", "WARN", "UNKNOWN")


def check(control, name, data, field, expected):
    """Evaluate a security control against its expected value."""

    actual = data.get(field)

    if actual is None:
        status = "UNKNOWN"

    elif type(actual) is type(expected) and actual == expected:
        status = "PASS"

    else:
        status = "FAIL"

    return {
        "control": control,
        "name": name,
        "field": field,
        "expected": expected,
        "actual": actual,
        "status": status,
    }


def evaluate_policy(policy, sources):
    """Evaluate all controls defined in the policy."""

    results = []

    for rule in policy["controls"]:
        result = check(
            rule["control"],
            rule["name"],
            sources[rule["source"]],
            rule["field"],
            rule["expected"],
        )

        result["id"] = rule["id"]
        result["severity"] = rule["severity"]

        results.append(result)

    return results


def generate_report(organization, policy, results):
    """Generate a structured compliance report."""

    return {
        "schema_version": "1.0",
        "engine_version": "0.3.0",
        "organization": organization,
        "policy": policy["name"],
        "timestamp": datetime.now(UTC).isoformat(),
        "checks": results,
        "summary": {
            status: sum(result["status"] == status for result in results)
            for status in STATUSES
        },
    }


def get_exit_code(results):
    """Determine the exit code based on compliance results."""

    if not results:
        return 2

    if any(r["status"] == "FAIL" for r in results):
        return 1

    if any(r["status"] == "UNKNOWN" for r in results):
        return 2

    if any(r["status"] not in STATUSES for r in results):
        return 2

    return 0


def main():
    """Execute the GitHub organization compliance assessment."""

    client = None

    try:
        # Load local configuration
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

        organization = config["organization"]

        # Load and validate policy before authentication
        policy = load_policy(POLICY_PATH)

        print(
            f"Policy loaded: {policy['name']}",
            file=sys.stderr,
        )

        # Authenticate using the GitHub App
        client = GitHubClient(config)
        client.authenticate()

        print(
            "Authentication successful",
            file=sys.stderr,
        )

        # Retrieve current organization settings
        org = client.get(f"orgs/{organization}")

        # Retrieve GitHub Actions permissions
        actions = client.get(f"orgs/{organization}/actions/permissions")

        # Retrieve default workflow permissions
        workflow = client.get(f"orgs/{organization}/actions/permissions/workflow")

        # Map policy sources to API responses
        sources = {
            "organization": org,
            "actions": actions,
            "workflow": workflow,
        }

        # Evaluate security controls
        results = evaluate_policy(
            policy,
            sources,
        )

        # Load and apply security exceptions
        exceptions = load_exceptions(EXCEPTIONS_PATH)

        results = apply_exceptions(
            results=results,
            exceptions=exceptions,
            organization=organization,
            plan=org.get("plan", {}).get("name"),
        )

        # Generate compliance report
        report = generate_report(
            organization,
            policy,
            results,
        )

        # Write JSON report to stdout
        print(json.dumps(report, indent=2))

        # Return compliance status
        return get_exit_code(results)

    except FileNotFoundError as error:
        print(
            f"File not found: {error.filename}",
            file=sys.stderr,
        )
        return 2

    except json.JSONDecodeError:
        print(
            "Configuration error: invalid JSON",
            file=sys.stderr,
        )
        return 2

    except yaml.YAMLError:
        print(
            "Policy error: invalid YAML",
            file=sys.stderr,
        )
        return 2

    except requests.RequestException as error:
        print(
            f"GitHub API error: {error}",
            file=sys.stderr,
        )
        return 2

    except (ValueError, KeyError, TypeError) as error:
        print(
            f"Configuration or policy error: {error}",
            file=sys.stderr,
        )
        return 2

    except OSError:
        print(
            "Unable to read configuration or credential file",
            file=sys.stderr,
        )
        return 2

    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    sys.exit(main())
