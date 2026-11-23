from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
from shutil import copytree
import subprocess
import sys

import pytest

from m0_harness.corpus import run_corpus, snapshot
from m0_harness.reader import BASELINE, Registration, scan, timestamp


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
NOW = datetime(2026, 11, 22, tzinfo=timezone.utc)


def concept(metadata="type: Reference", body=""):
    return f"---\n{metadata}\n---\n\n{body}"


def read(tmp_path, files, *, profile=False, legacy=False):
    root = tmp_path / "bundle"
    root.mkdir(exist_ok=True)
    for name, content in files.items():
        file = root / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
    bundles, config = scan([Registration("fixture", root, profile, legacy)], now=NOW)
    assert not config
    return bundles["fixture"]


def diagnostic_codes(bundle, category=None):
    return [d.code for d in bundle.diagnostics if category is None or d.category == category]


@pytest.mark.contract("DISC-01", "DISC-02", "DISC-03", "DISC-04", "FM-02", "FM-04", "FM-06", "PATH-01", "PATH-05", "PATH-07", "META-08", "LAT-01", "LAT-02", "LAT-03", "LAT-05", "LAT-06", "VER-02")
def test_independent_corpus_matches_inventory_without_mutation():
    before = snapshot(FIXTURES)
    report = run_corpus(FIXTURES / "corpus.json")
    assert report["expectation_failures"] == []
    assert report["baseline"] == BASELINE
    assert report["sources_unchanged"]
    assert snapshot(FIXTURES) == before
    assert "decisions/shared" in report["bundles"]["alpha"]["concept_ids"]
    assert "decisions/shared" in report["bundles"]["beta"]["concept_ids"]
    assert not report["bundles"]["alpha"]["conformant"]
    assert report["bundles"]["beta"]["conformant"]


@pytest.mark.contract("VER-01", "FM-06", "META-08")
def test_fixture_versions_extensions_and_projection_provenance():
    bundles = run_corpus(FIXTURES / "corpus.json")["bundles"]
    for bundle_id in ("alpha", "beta"):
        assert bundles[bundle_id]["metadata"]["okf_version"] == "0.3"
    unknown = bundles["alpha"]["documents"]["unknown.md"]["metadata"]
    assert unknown["type"] == "Unregistered Fixture Type"
    assert unknown["x-top"] == {"enabled": "yes", "truth": True, "version": "0.3"}
    assert unknown["sources"][0]["x-source"] == "retained"
    assert unknown["executor"]["x-executor"] == unknown["attester"]["x-attester"] == "retained"
    for bundle_id, name, requirement in [
        ("alpha", "projected", "SYNTHETIC-001"),
        ("beta", "unversioned", "SYNTHETIC-002"),
    ]:
        doc = bundles[bundle_id]["documents"][f"specifications/{name}.md"]
        source = {"id": "authoritative-source", "resource": f"https://fixtures.example/battalion/requirements/{requirement}"}
        if bundle_id == "alpha":
            source.update({"x-lattivra-revision": "synthetic-revision-007", "x-fixture-detail": "preserved"})
        for metadata in (doc["raw"], doc["metadata"]):
            assert metadata["type"] == "Specification"
            assert metadata["sources"] == [source]
            assert metadata["generated"] == {"by": "fixture-exporter/0.1", "at": "2026-06-19T00:00:00Z"}


@pytest.mark.contract("PATH-07", "LAT-01", "LAT-02", "LAT-05")
def test_shared_decision_backlinks_keep_bundle_identity():
    bundles = run_corpus(FIXTURES / "corpus.json")["bundles"]
    incoming = {}
    for bundle in bundles.values():
        for edge in bundle["edges"]:
            incoming.setdefault(edge["target"], set()).add((edge["source"], edge["field"]))
    assert incoming["alpha:decisions/shared"] == {
        ("alpha:specifications/native", "body"), ("alpha:nested/concept", "body"), ("alpha:unknown", "sources[0].resource")
    }
    assert incoming["beta:decisions/shared"] == {
        ("alpha:specifications/native", "body"), ("beta:specifications/unversioned", "body"), ("beta:decisions/shared", "resource")
    }
    assert incoming["alpha:specifications/native"] == {("alpha:decisions/shared", "body"), ("alpha:plans/example", "body")}


def test_inventory_detects_uri_mapped_to_wrong_bundle(tmp_path):
    path = copytree(FIXTURES, tmp_path / "fixtures") / "corpus.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["mappings"]["https://fixtures.example/unique"][0]["bundle"] = "alpha"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    failures = run_corpus(path)["expectation_failures"]
    assert any("https://fixtures.example/unique expected concept=beta:decisions/shared, got alpha:decisions/shared" in f for f in failures)


@pytest.mark.contract("FM-01", "FM-03", "FM-05")
def test_yaml_12_minimal_concept_and_body_delimiters(tmp_path):
    bundle = read(tmp_path, {"minimal.md": concept("type: Reference\nx: {on: yes, truth: true, version: '0.3'}", "body\n---\nmore")})
    doc = bundle.concepts["minimal"]
    assert doc.raw["x"] == {"on": "yes", "truth": True, "version": "0.3"}
    assert doc.body == "\nbody\n---\nmore"
    assert bundle.conformant


@pytest.mark.contract("FM-02", "FM-04", "LAT-06")
@pytest.mark.parametrize("bad,code", [
    ("---\ntype: [broken\n---\n", "INVALID_YAML"),
    ("---\ntype: Reference\n", "UNCLOSED_FRONTMATTER"),
    (concept("- sequence"), "FRONTMATTER_NOT_MAPPING"),
    (concept("scalar"), "FRONTMATTER_NOT_MAPPING"),
    (concept(""), "FRONTMATTER_NOT_MAPPING"),
    (concept("type: Reference\ntype: Metric"), "DUPLICATE_KEY"),
    (concept("type: Reference\nx: {a: 1, a: 2}"), "DUPLICATE_KEY"),
    (b"---\ntype: Reference\n---\n\xff", "INVALID_UTF8"),
])
def test_bad_neighbors_do_not_block_valid_concepts(tmp_path, bad, code):
    bundle = read(tmp_path, {"bad.md": bad, "good.md": concept()})
    assert list(bundle.concepts) == ["good"]
    assert code in diagnostic_codes(bundle, "format")
    assert not bundle.conformant
    if code != "INVALID_UTF8":
        assert next(d for d in bundle.diagnostics if d.code == code).line is not None


@pytest.mark.contract("RES-01", "RES-02", "RES-03", "RES-06", "VER-01")
@pytest.mark.parametrize("name,text,code", [
    ("index.md", concept("type: Reference\nokf_version: '0.3'\nx-extra: retained"), None),
    ("nested/index.md", concept(), "RESERVED_FRONTMATTER"),
    ("log.md", concept(), "RESERVED_FRONTMATTER"),
    ("nested/log.md", "# Log\n\n## yesterday\n\n- Entry", "INVALID_LOG_DATE"),
    ("log.md", "# Log\n\n## 2026-02-30\n\n- Entry", "INVALID_LOG_DATE"),
    ("log.md", "# Log\n\n## 2026-01-01\n\n- Entry\n\n## 2026-02-01\n\n- Entry", "LOG_DATE_ORDER"),
])
def test_reserved_files_are_never_concepts(tmp_path, name, text, code):
    bundle = read(tmp_path, {name: text, "good.md": concept()})
    assert bundle.documents[name].kind == "reserved"
    assert list(bundle.concepts) == ["good"]
    assert bundle.conformant == (code is None)
    if code:
        assert code in diagnostic_codes(bundle)
    if name == "index.md":
        assert "okf_version" not in bundle.concepts["good"].metadata
        assert bundle.metadata["x-extra"] == "retained"


@pytest.mark.contract("DISC-02", "FM-05", "LAT-04")
def test_profile_is_explicit_and_independent_of_format(tmp_path):
    files = {"generic.md": concept("type: Decision"), "other.md": concept("type: Custom")}
    ordinary = read(tmp_path, files)
    selected = read(tmp_path, files, profile=True)
    assert ordinary.conformant and selected.conformant
    assert ordinary.concepts["generic"].profile == "not_applied"
    assert selected.concepts["generic"].profile == "failed"
    assert selected.concepts["other"].profile == "not_applied"
    assert len(diagnostic_codes(selected, "profile")) == 4


@pytest.mark.contract("RES-06")
@pytest.mark.parametrize("newline", ["\n", "\r\n"], ids=["lf", "crlf"])
@pytest.mark.parametrize("heading,valid", [("2026-11-22", True), ("2026-02-30", False), ("yesterday", False)])
def test_log_dates_use_logical_lines_without_rewriting_source(tmp_path, newline, heading, valid):
    text = newline.join(["# Log", "", f"## {heading}", "", "- Entry", ""])
    content = text.encode("utf-8")
    bundle = read(tmp_path, {"log.md": content, "neighbor.md": concept()})
    assert bundle.conformant is valid
    assert diagnostic_codes(bundle, "format") == ([] if valid else ["INVALID_LOG_DATE"])
    assert "neighbor" in bundle.concepts
    assert bundle.documents["log.md"].body == text
    assert (tmp_path / "bundle" / "log.md").read_bytes() == content


@pytest.mark.contract("LAT-04")
@pytest.mark.parametrize("metadata,code", [
    ("status: accepted", "INVALID_STATUS"),
    ("sources: {resource: 'https://example.invalid', x-lattivra-revision: 7}", "INVALID_REVISION"),
    ("sources: [{id: authoritative-source, resource: a}, {id: authoritative-source, resource: b}]", "COMPETING_AUTHORITIES"),
])
def test_selected_profile_extension_rules_do_not_change_format_verdict(tmp_path, metadata, code):
    files = {"doc.md": concept("type: Specification\n" + metadata, "# Context\n\n# Requirements\n\n# Acceptance Criteria")}
    selected = read(tmp_path, files, profile=True)
    ordinary = read(tmp_path, files)
    assert selected.conformant and ordinary.conformant
    assert code in diagnostic_codes(selected, "profile")
    assert not diagnostic_codes(ordinary, "profile")
    assert selected.concepts["doc"].profile == "failed"


@pytest.mark.contract("META-01", "META-02", "META-03", "FM-06")
@pytest.mark.parametrize("empty", ["null", "''", "[]"])
def test_optional_absence_and_raw_preservation(tmp_path, empty):
    metadata = f"type: Reference\nstatus: {empty}\nstale_after: {empty}\nverified: {empty}\nx-raw: {empty}"
    doc = read(tmp_path, {"doc.md": concept(metadata)}).concepts["doc"]
    assert "status" in doc.raw and "verified" in doc.raw
    assert "status" not in doc.metadata and "verified" not in doc.metadata
    assert doc.state == {"status": "stable", "current": True, "freshness": "unspecified", "trust": "unverified"}


@pytest.mark.contract("META-02", "META-03", "ATT-02")
def test_singletons_and_incomplete_entries(tmp_path):
    metadata = """type: Reference
tags: alpha,beta
sources: [{id: incomplete}, {resource: 'https://example.invalid', x-nested: preserved}]
generated: {at: '2026-01-01'}
verified: [{by: 'human:missing-time'}, {by: 'team:synthetic', at: '2026-01-01'}]
parameters: [{name: missing-type}, {name: foo, type: custom-runtime-type}]
"""
    bundle = read(tmp_path, {"doc.md": concept(metadata)})
    doc = bundle.concepts["doc"]
    assert doc.metadata["tags"] == ["alpha,beta"]
    assert doc.metadata["sources"] == [{"resource": "https://example.invalid", "x-nested": "preserved"}]
    assert len(doc.metadata["verified"]) == 1
    assert len(doc.metadata["parameters"]) == 1
    assert doc.metadata["parameters"][0]["required"] is False
    assert "generated" not in doc.metadata
    assert len(doc.raw["sources"]) == 2
    assert diagnostic_codes(bundle).count("INCOMPLETE_ENTRY") == 4
    assert bundle.conformant


@pytest.mark.contract("META-07")
@pytest.mark.parametrize("value", ["2026-11-22", "2026-11-22T00:00:00Z", "2026-11-21T16:00:00-08:00", date(2026, 11, 22), NOW])
def test_timestamp_representations(value):
    assert timestamp(value) == NOW


@pytest.mark.contract("META-07")
def test_yaml_native_timestamp_and_quoted_dates_agree(tmp_path):
    bundle = read(tmp_path, {"native.md": concept("type: Reference\nstale_after: 2026-11-22"),
                             "quoted.md": concept("type: Reference\nstale_after: '2026-11-22'")})
    assert bundle.concepts["native"].state == bundle.concepts["quoted"].state


@pytest.mark.contract("META-07", "STATE-06")
@pytest.mark.parametrize("value", ["2026-11-22T00:00:00", "2026-02-30", "not-a-time", 123, False])
def test_invalid_timestamp_is_not_an_instant(value):
    assert timestamp(value) is None


@pytest.mark.contract("STATE-01", "STATE-02", "STATE-03")
@pytest.mark.parametrize("events,expected", [
    ("[]", "unverified"),
    ("[{by: 'human:old', at: '2026-01-01'}]", "unverified"),
    ("{by: 'human:equal', at: '2026-06-01'}", "human-reviewed"),
    ("[{by: 'human:old', at: '2026-01-01'}, {by: 'process:new', at: '2026-06-02'}]", "machine-confirmed"),
    ("{by: 'team:reviewers', at: '2026-06-01'}", "machine-confirmed"),
    ("{by: 'unknown:actor', at: '2026-06-01'}", "machine-confirmed"),
    ("{by: 'tool/1.0', at: '2026-06-01'}", "machine-confirmed"),
])
def test_only_current_events_contribute_to_trust(tmp_path, events, expected):
    metadata = f"type: Reference\ngenerated: {{by: 'tool/1.0', at: '2026-06-01'}}\nverified: {events}"
    assert read(tmp_path, {"doc.md": concept(metadata)}).concepts["doc"].state["trust"] == expected


@pytest.mark.contract("STATE-01")
def test_verification_without_generation_is_current(tmp_path):
    doc = read(tmp_path, {"doc.md": concept("type: Reference\nverified: {by: 'human:synthetic', at: '2026-01-01'}")}).concepts["doc"]
    assert doc.state["trust"] == "human-reviewed"


@pytest.mark.contract("STATE-04")
@pytest.mark.parametrize("status,current", [("draft", True), ("stable", True), ("deprecated", False), ("accepted", False), ("{unexpected: shape}", False)])
def test_status_values_remain_separate_from_approval(tmp_path, status, current):
    bundle = read(tmp_path, {"doc.md": concept(f"type: Reference\nstatus: {status}")})
    assert bundle.concepts["doc"].state["current"] is current
    assert bundle.conformant
    if status not in ("draft", "stable", "deprecated"):
        assert "UNKNOWN_STATUS" in diagnostic_codes(bundle)


@pytest.mark.contract("STATE-06", "STATE-07")
@pytest.mark.parametrize("deadline,expected", [("2026-11-21", "stale"), ("2026-11-22", "stale"), ("2026-11-23", "fresh"), ("garbage", "malformed")])
def test_freshness_uses_fixed_deadline(tmp_path, deadline, expected):
    doc = read(tmp_path, {"doc.md": concept(f"type: Reference\nstale_after: '{deadline}'")}).concepts["doc"]
    assert doc.state["freshness"] == expected


@pytest.mark.contract("PATH-01", "PATH-02", "PATH-04", "PATH-05", "PATH-06", "PATH-07", "PATH-08")
def test_links_fields_assets_and_case(tmp_path):
    body = """[relative](target.md#part) [root](/target.md) [encoded](my%20concept.md)
[wrong case](TARGET.md) [asset](/asset.txt) ![image](/asset.txt)
[directory](/a/) [notes](/README.md) [missing](missing.md) [[wikilink]]
[reference][id]

[id]: target.md
"""
    fields = """type: Reference
resource: target.md
sources: {resource: /target.md}
computation: target.md
executor: {resource: target.md}
attester: {resource: target.md}
superseded_by: target.md
"""
    bundle = read(tmp_path, {"a/source.md": concept(fields, body), "a/target.md": concept(), "target.md": concept(),
                             "a/my concept.md": concept(), "asset.txt": "asset", "README.md": "notes"})
    refs = bundle.concepts["a/source"].references
    by_target = {r["target"]: r for r in refs}
    assert by_target["target.md#part"]["concept"] == "fixture:a/target"
    assert by_target["/target.md"]["concept"] == "fixture:target"
    assert by_target["my%20concept.md"]["concept"] == "fixture:a/my concept"
    assert by_target["TARGET.md"]["state"] == "unresolved"
    assert by_target["/asset.txt"]["state"] == "asset"
    assert by_target["/README.md"]["state"] == "skipped"
    assert by_target["/a/"]["state"] == "directory"
    assert "wikilink" not in by_target
    assert {r["field"] for r in refs if r.get("concept") == "fixture:a/target"} >= {"body", "resource", "computation", "executor.resource", "attester.resource", "superseded_by"}
    assert {e["field"] for e in bundle.edges} >= {"body", "resource", "sources[0].resource"}
    assert all(e["field"] != "image" for e in bundle.edges)
    assert all("asset.txt" not in e["target"] for e in bundle.edges)
    assert bundle.conformant


@pytest.mark.contract("PATH-03", "META-04")
def test_external_escaped_and_descriptor_references(tmp_path):
    doc = concept("type: Reference\nsources: {resource: 'all synthetic queries'}", "[escape](../../secret.md) [encoded escape](%2e%2e/%2e%2e/secret.md) [remote](custom:thing) [net](//example.invalid/foo)")
    bundle = read(tmp_path, {"a/source.md": doc})
    refs = bundle.concepts["a/source"].references
    assert [r["state"] for r in refs] == ["blocked", "blocked", "external", "external", "descriptor"]
    assert len([d for d in bundle.diagnostics if d.category == "access"]) == 2
    assert bundle.conformant


@pytest.mark.contract("VER-03", "VER-04")
@pytest.mark.parametrize("version,legacy,expected", [(None, True, "concept"), ("0.2", True, "concept"), ("0.1", True, "concept"), ("0.3", True, "unresolved"), (None, False, "unresolved")])
def test_legacy_fallback_is_optional_and_field_only(tmp_path, version, legacy, expected):
    files = {"a/source.md": concept("type: Reference\nresource: target.md", "[link](target.md)"), "target.md": concept()}
    if version:
        files["index.md"] = concept(f"okf_version: '{version}'")
    bundle = read(tmp_path, files, legacy=legacy)
    refs = bundle.concepts["a/source"].references
    assert refs[0]["state"] == "unresolved"
    assert refs[1]["state"] == expected


@pytest.mark.contract("VER-03")
def test_legacy_fallback_never_overrides_existing_relative_target(tmp_path):
    bundle = read(tmp_path, {"a/source.md": concept("type: Reference\nresource: target.md"), "a/target.md": concept(), "target.md": concept()}, legacy=True)
    assert bundle.concepts["a/source"].references[0]["concept"] == "fixture:a/target"


@pytest.mark.contract("ATT-01", "ATT-03", "ATT-04", "ATT-05")
@pytest.mark.parametrize("fields,body,available", [
    ("", "# Computation\n\n```sql\nselect 1\n```", True),
    ("", "### Computation\n\n```sql\nselect 1\n```\n\n```sql\nselect 2\n```", True),
    ("", "# Computation\n\nNo code.\n\n# Other\n\n```sql\nselect 1\n```", False),
    ("computation: missing.sql", "# Computation\n\n```sql\nselect 1\n```", False),
    ("computation: /query.sql", "", True),
])
def test_static_computation_locator_never_attests_runs(tmp_path, fields, body, available):
    bundle = read(tmp_path, {"doc.md": concept("type: Attested Computation\nruntime: synthetic\nattester: {resource: /asset.txt}\n" + fields, body), "query.sql": "select 1", "asset.txt": "not executable"})
    state = bundle.concepts["doc"].state
    assert state["computation_available"] is available
    assert state["attested"] is False


@pytest.mark.contract("ATT-01")
def test_missing_runtime_is_not_a_structural_bundle_failure(tmp_path):
    bundle = read(tmp_path, {"doc.md": concept("type: Attested Computation")})
    assert "MISSING_RUNTIME" in diagnostic_codes(bundle, "contract")
    assert bundle.conformant
    assert bundle.concepts["doc"].state["attested"] is False


@pytest.mark.contract("DISC-05", "LAT-06")
def test_escaping_symlinks_and_chains_never_read_outside(tmp_path, monkeypatch):
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.md").write_text(concept(), encoding="utf-8")
    (root / "good.md").write_text(concept(body="[escape](escape/secret.md)"), encoding="utf-8")
    try:
        (root / "escape").symlink_to(outside, target_is_directory=True)
        (root / "chain").symlink_to(root / "escape", target_is_directory=True)
    except OSError as exc:
        if os.name == "nt":
            pytest.skip(f"Windows symlink privilege unavailable: {exc}")
        raise
    original = Path.read_bytes
    def guarded(path):
        assert not path.resolve().is_relative_to(outside), "outside target was read"
        return original(path)
    monkeypatch.setattr(Path, "read_bytes", guarded)
    bundles, _ = scan([Registration("fixture", root)], now=NOW)
    bundle = bundles["fixture"]
    assert list(bundle.concepts) == ["good"]
    assert diagnostic_codes(bundle, "access").count("OUTSIDE_ROOT") == 2
    assert bundle.concepts["good"].references[0]["state"] == "blocked"
    assert bundle.conformant


@pytest.mark.contract("LAT-03")
def test_conflicting_roots_leave_accepted_registration_unchanged(tmp_path):
    parent = tmp_path / "root"
    child = parent / "nested"
    child.mkdir(parents=True)
    bundles, diagnostics = scan([Registration("child", child), Registration("parent", parent), Registration("duplicate", child)], now=NOW)
    assert list(bundles) == ["child"]
    assert len(diagnostics) == 2
    assert all("child" in d.field for d in diagnostics)


@pytest.mark.skipif(os.name != "nt", reason="Windows filesystem junction check")
@pytest.mark.contract("DISC-05", "LAT-03", "LAT-06")
def test_windows_junction_cannot_escape_or_register_same_tree_twice(tmp_path, monkeypatch):
    root, outside = tmp_path / "root", tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    (root / "good.md").write_text(concept(body="[escape](escape/secret.md)"), encoding="utf-8")
    (outside / "secret.md").write_text(concept(), encoding="utf-8")
    link = root / "escape"
    result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(outside)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    original = Path.read_bytes
    def guarded(path):
        assert not path.resolve().is_relative_to(outside), "junction target was read"
        return original(path)
    with monkeypatch.context() as guard:
        guard.setattr(Path, "read_bytes", guarded)
        bundles, _ = scan([Registration("fixture", root)], now=NOW)
    assert "OUTSIDE_ROOT" in diagnostic_codes(bundles["fixture"], "access")
    assert bundles["fixture"].concepts["good"].references[0]["state"] == "blocked"
    _, diagnostics = scan([Registration("fixture", root), Registration("outside", outside), Registration("alias", link)], now=NOW)
    assert any(d.category == "configuration" and d.file == "alias" for d in diagnostics)


def test_unresolved_generation_comparison_and_recursive_yaml_are_visible(tmp_path):
    bundle = read(tmp_path, {"generation.md": concept("type: Reference\ngenerated: {by: 'tool/1'}\nverified: {by: 'human:synthetic', at: '2026-01-01'}"),
                             "recursive.md": concept("type: Reference\nx: &a [*a]")})
    assert bundle.concepts["generation"].state["trust"] == "unverified"
    assert "GENERATION_TIME_UNRESOLVED" in diagnostic_codes(bundle, "compatibility")
    assert bundle.documents["recursive.md"].kind == "unsupported"
    assert bundle.conformant


def test_unknown_yaml_tag_is_a_compatibility_limit(tmp_path):
    bundle = read(tmp_path, {"custom.md": concept("type: Reference\nx-value: !unknown value"), "good.md": concept()})
    assert bundle.documents["custom.md"].kind == "unsupported"
    assert "UNSUPPORTED_YAML" in diagnostic_codes(bundle, "compatibility")
    assert "good" in bundle.concepts
    assert bundle.conformant


@pytest.mark.parametrize("change_source", [False, True])
def test_manifest_verifies_independently_located_bundle(tmp_path, monkeypatch, change_source):
    from hashlib import sha256
    from m0_harness import corpus

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "unrelated.txt").write_bytes(b"outside the fixture inventory")
    root = tmp_path / "bundle"
    root.mkdir()
    source = root / "good.md"
    original = concept().encode()
    source.write_bytes(original)
    manifest = config_dir / "corpus.json"
    manifest.write_text(json.dumps({
        "clock": "2026-11-22",
        "bundles": [{"id": "example", "root": str(root), "expected_conformant": True,
                     "assets": [], "documents": {"good.md": {"kind": "concept"}}}],
    }), encoding="utf-8")

    if change_source:
        def scan_and_edit(*args, **kwargs):
            result = scan(*args, **kwargs)
            source.write_bytes(original + b"changed")
            return result
        monkeypatch.setattr(corpus, "scan", scan_and_edit)

    report = run_corpus(manifest)
    assert report["fixture_hashes"] == {
        manifest.name: sha256(manifest.read_bytes()).hexdigest(),
        source.as_posix(): sha256(original).hexdigest(),
    }
    assert report["sources_unchanged"] == (not change_source)
    assert report["expectation_failures"] == (["fixture sources changed during the run"] if change_source else [])


def test_inventory_mismatch_is_reported_not_rewritten(tmp_path):
    manifest = json.loads((FIXTURES / "corpus.json").read_text(encoding="utf-8"))
    for entry in manifest["bundles"] + manifest["registration_attempts"]:
        entry["root"] = str(FIXTURES / entry["root"])
    manifest["bundles"][0]["documents"]["generic.md"]["kind"] = "skipped"
    path = tmp_path / "corpus.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    before = path.read_bytes()
    report = run_corpus(path)
    assert any("generic.md: expected skipped, got concept" in x for x in report["expectation_failures"])
    assert path.read_bytes() == before


def test_cli_exit_status_and_report_guard(tmp_path):
    output = tmp_path / "report.json"
    result = subprocess.run([sys.executable, "-m", "m0_harness", str(FIXTURES / "corpus.json"), "--output", str(output)], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(output.read_text(encoding="utf-8"))["sources_unchanged"]
    streamed = subprocess.run([sys.executable, "-m", "m0_harness", str(FIXTURES / "corpus.json")], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    assert streamed.returncode == 0
    assert json.loads(streamed.stdout)["expectation_failures"] == []
    result = subprocess.run([sys.executable, "-m", "m0_harness", str(FIXTURES / "corpus.json"), "--output", str(FIXTURES / "corpus.json")], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 2


def test_cli_mismatch_exits_nonzero(tmp_path):
    fixture = tmp_path / "fixtures"
    fixture.mkdir()
    manifest = json.loads((FIXTURES / "corpus.json").read_text(encoding="utf-8"))
    for entry in manifest["bundles"] + manifest["registration_attempts"]:
        entry["root"] = str(FIXTURES / entry["root"])
    manifest["bundles"][0]["expected_conformant"] = True
    path = fixture / "corpus.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    result = subprocess.run([sys.executable, "-m", "m0_harness", str(path), "--output", str(tmp_path / "failed.json")], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 1
    assert "unexpected format verdict" in result.stdout


def test_repository_documentation_remains_a_conformant_profile_bundle():
    bundles, diagnostics = scan([Registration("repository", ROOT, profile=True)], now=NOW)
    assert not diagnostics
    bundle = bundles["repository"]
    assert bundle.conformant, bundle.diagnostics
    assert not [d for d in bundle.diagnostics if d.category == "profile"]


def test_code_and_documented_baseline_match():
    text = (ROOT / "docs/compatibility/okf-v0.3-conformance.md").read_text(encoding="utf-8")
    assert BASELINE["commit"] in text
    assert BASELINE["spec_blob"] in text
    assert "/blob/main/SPEC.md" not in text
