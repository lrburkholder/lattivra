"""Compare an explicit fixture inventory with observed results, without rewriting it."""

from dataclasses import asdict
from datetime import date, datetime
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import subprocess

from .reader import BASELINE, Registration, scan, timestamp


def snapshot(root: Path) -> dict[str, str]:
    result = {}
    def visit(directory):
        for path in sorted(directory.iterdir()):
            if path.is_symlink() or path.is_junction():
                result[path.relative_to(root).as_posix()] = "filesystem-alias"
            elif path.is_dir():
                visit(path)
            elif path.is_file():
                result[path.relative_to(root).as_posix()] = sha256(path.read_bytes()).hexdigest()
    visit(root)
    return result


def codes(diagnostics):
    return sorted(f"{d.category}:{d.code}" for d in diagnostics)


def run_corpus(manifest: Path) -> dict:
    manifest = manifest.resolve()
    before = snapshot(manifest.parent)
    config = json.loads(manifest.read_text(encoding="utf-8"))
    now = timestamp(config["clock"])
    if now is None:
        raise ValueError("manifest clock must be an RFC 3339 date or offset date-time")
    registrations = [Registration(e["id"], manifest.parent / e["root"], e.get("profile", False), e.get("legacy_paths", False))
                     for e in config["bundles"] + config.get("registration_attempts", [])]
    bundles, diagnostics = scan(registrations, now=now, mappings=config.get("mappings"))
    failures = []
    expected = set()
    for entry in config["bundles"]:
        bundle_id = entry["id"]
        expected.add(bundle_id)
        if bundle_id not in bundles:
            failures.append(f"{bundle_id}: bundle not registered")
            continue
        bundle = bundles[bundle_id]
        if bundle.conformant != entry["expected_conformant"]:
            failures.append(f"{bundle_id}: unexpected format verdict")
        if sorted(bundle.assets) != sorted(entry["assets"]):
            failures.append(f"{bundle_id}: asset inventory differs")
        if set(bundle.documents) != set(entry["documents"]):
            failures.append(f"{bundle_id}: document inventory differs")
        if any(d.file not in entry["documents"] for d in bundle.diagnostics):
            failures.append(f"{bundle_id}: diagnostic outside document inventory")
        for path, expectation in entry["documents"].items():
            doc = bundle.documents.get(path)
            if doc is None:
                continue
            if doc.kind != expectation["kind"]:
                failures.append(f"{bundle_id}/{path}: expected {expectation['kind']}, got {doc.kind}")
            if doc.profile != expectation.get("profile", "not_applied"):
                failures.append(f"{bundle_id}/{path}: profile outcome differs")
            actual_codes = codes(d for d in bundle.diagnostics if d.file == path)
            if actual_codes != sorted(expectation.get("diagnostics", [])):
                failures.append(f"{bundle_id}/{path}: diagnostics {actual_codes} differ from inventory")
            # Include duplicate targets in detailed output, while the inventory checks
            # the target's observed states independently of Markdown token order.
            actual_refs = {}
            for ref in doc.references:
                actual_refs.setdefault(ref["target"], set()).add(ref["state"])
            expected_refs = {target: {state} for target, state in expectation.get("references", {}).items()}
            if actual_refs != expected_refs:
                failures.append(f"{bundle_id}/{path}: reference outcomes differ")
    if set(bundles) != expected:
        failures.append("registered bundle inventory differs")
    if codes(diagnostics) != sorted(config.get("expected_registration_diagnostics", [])):
        failures.append("registration diagnostics differ")
    after = snapshot(manifest.parent)
    if before != after:
        failures.append("fixture sources changed during the run")
    try:
        revision = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True).stdout.strip())
    except (OSError, subprocess.CalledProcessError):
        revision, dirty = "unavailable", None
    serialized_bundles = {}
    for bundle_id, bundle in bundles.items():
        value = asdict(bundle)
        value["root"] = next(e["root"] for e in config["bundles"] + config.get("registration_attempts", []) if e["id"] == bundle_id)
        value["conformant"] = bundle.conformant
        value["concept_ids"] = list(bundle.concepts)
        value["edges"] = bundle.edges
        serialized_bundles[bundle_id] = value
    return {
        "baseline": BASELINE,
        "harness_revision": revision,
        "working_tree_dirty": dirty,
        "dependencies": {p: version(p) for p in ("ruamel.yaml", "markdown-it-py", "mdit-py-plugins")},
        "clock": config["clock"],
        "sources_unchanged": before == after,
        "fixture_hashes": before,
        "expectation_failures": failures,
        "registration_diagnostics": [asdict(d) for d in diagnostics],
        "bundles": serialized_bundles,
    }


def json_default(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    raise TypeError(f"Unsupported report value: {type(value).__name__}")
