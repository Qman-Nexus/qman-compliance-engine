import pytest

from compliance import check


@pytest.mark.parametrize(
    "data, expected, expected_status",
    [
        ({"enabled": True}, True, "PASS"),
        ({"enabled": False}, True, "FAIL"),
        ({}, True, "UNKNOWN"),
        ({"enabled": None}, True, "UNKNOWN"),
        ({"enabled": "true"}, True, "FAIL"),
        ({"enabled": 1}, True, "FAIL"),
        ({"enabled": False}, False, "PASS"),
        ({"enabled": "none"}, "none", "PASS"),
        ({"enabled": "read"}, "none", "FAIL"),
    ]
)
def test_security_control(
    data, expected, expected_status
):
    result = check(
        "SEC-TEST",
        "Test security control",
        data,
        "enabled",
        expected
    )

    assert result["status"] == expected_status

