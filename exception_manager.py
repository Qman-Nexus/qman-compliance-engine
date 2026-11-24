from datetime import UTC, datetime
from pathlib import Path

import yaml


def load_exceptions(path):
    """Load the operational exception registry."""

    path = Path(path)

    if not path.exists():
        return []

    with path.open(encoding="utf-8") as file:
        registry = yaml.safe_load(file)

    if not isinstance(registry, dict):
        raise ValueError("Invalid exception registry")

    if registry.get("schema_version") != "1.0":
        raise ValueError("Unsupported exception schema")

    exceptions = registry.get("exceptions")

    if not isinstance(exceptions, list):
        raise ValueError("Invalid exceptions list")

    return exceptions


def apply_exceptions(results, exceptions, organization, plan, today=None):
    """Apply approved and valid risk exceptions."""

    today = today or datetime.now(UTC).date()
    evaluated = []

    for result in results:
        result = result.copy()

        if result["status"] != "FAIL":
            evaluated.append(result)
            continue

        for exception in exceptions:
            if exception["control_id"] != result["id"]:
                continue

            if exception["organization"] != organization:
                continue

            if exception["status"] != "approved":
                continue

            if not exception.get("approved_by"):
                continue

            if not exception.get("compensating_controls"):
                continue

            created = datetime.strptime(exception["created_at"], "%Y-%m-%d").date()

            expires = datetime.strptime(exception["expires_at"], "%Y-%m-%d").date()

            if not created <= today < expires:
                continue

            conditions = exception["conditions"]

            if conditions["plan"] != plan:
                continue

            actual = result["actual"]
            expected_actual = conditions["actual"]

            if type(actual) is not type(expected_actual) or actual != expected_actual:
                continue

            result["original_status"] = "FAIL"
            result["status"] = "WARN"

            result["exception"] = {
                "id": exception["id"],
                "reason": exception["reason"],
                "owner": exception["owner"],
                "approved_by": exception["approved_by"],
                "expires_at": exception["expires_at"],
            }

            break

        evaluated.append(result)

    return evaluated
