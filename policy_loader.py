from pathlib import Path

import yaml


def load_policy(path):
    path = Path(path)

    with path.open(encoding="utf-8") as file:
        policy = yaml.safe_load(file)

    if not isinstance(policy, dict):
        raise TypeError("Invalid policy format")

    if policy.get("schema_version") != "1.0":
        raise ValueError("Unsupported policy schema")

    controls = policy.get("controls")

    if not isinstance(controls, list) or not controls:
        raise ValueError("Policy contains no controls")

    required_fields = {
        "id",
        "control",
        "name",
        "source",
        "field",
        "expected",
        "severity",
    }

    allowed_sources = {"organization", "actions", "workflow"}

    allowed_severities = {"critical", "high", "medium", "low"}

    seen_ids = set()

    for control in controls:
        if not isinstance(control, dict):
            raise TypeError("Invalid control")

        if not required_fields.issubset(control):
            raise ValueError("Missing required fields")

        if control["id"] in seen_ids:
            raise ValueError("Duplicate control ID")

        if control["source"] not in allowed_sources:
            raise ValueError("Invalid control source")

        if control["severity"] not in allowed_severities:
            raise ValueError("Invalid severity")

        seen_ids.add(control["id"])

    return policy
