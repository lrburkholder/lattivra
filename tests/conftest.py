"""Emit traceability to the contract without claiming complete row coverage."""

import json
from pathlib import Path
import re

import pytest

from m0_harness.reader import BASELINE


OUTCOMES = {}


def pytest_addoption(parser):
    parser.addoption("--contract-report", help="Write checklist traceability as JSON")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    report = (yield).get_result()
    if report.when == "call" or report.failed or report.skipped:
        for marker in item.iter_markers("contract"):
            for check_id in marker.args:
                OUTCOMES.setdefault(check_id, {})[item.nodeid] = report.outcome


def pytest_sessionfinish(session, exitstatus):
    output = session.config.getoption("--contract-report")
    if not output:
        return
    root = Path(__file__).resolve().parents[1]
    text = (root / "docs/compatibility/okf-v0.3-conformance.md").read_text(encoding="utf-8")
    ids = re.findall(r"^\| ((?:DISC|RES|FM|META|PATH|STATE|VER|ATT|LAT|U)-\d+) \|", text, re.M)
    results = {}
    for check_id in ids:
        tests = OUTCOMES.get(check_id, {})
        outcomes = set(tests.values())
        status = "pending"
        if check_id.startswith("U-"):
            status = "unresolved"
        elif "failed" in outcomes:
            status = "failed"
        elif "passed" in outcomes:
            status = "exercised"
        elif "skipped" in outcomes:
            status = "skipped"
        results[check_id] = {"status": status, "tests": tests}
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"baseline": BASELINE, "meaning": "exercised records passing examples, not exhaustive coverage of every row variant", "pytest_exitstatus": int(exitstatus), "checklist": results}, indent=2) + "\n", encoding="utf-8")
