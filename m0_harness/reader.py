"""A small OKF reader with independent format, profile, and diagnostic results."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
from pathlib import Path, PurePosixPath
import posixpath
import re
from typing import Any
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError


BASELINE = {
    "repository": "https://github.com/open-knowledge-format/open-knowledge-format",
    "commit": "527e81aff55992be21507e97004286789126f88c",
    "spec_blob": "0dc3f7aa0fc710e588ba918eb115935d41eb2943",
    "version": "0.3",
}
PROFILE_HEADINGS = {
    "Specification": ("Context", "Requirements", "Acceptance Criteria"),
    "Decision": ("Context", "Decision", "Rationale", "Consequences"),
    "Implementation Plan": ("Objective", "Tasks", "Verification"),
}
MARKDOWN = MarkdownIt("commonmark", {"html": False}).enable("table").use(footnote_plugin)


@dataclass
class Diagnostic:
    category: str
    code: str
    file: str
    field: str = ""
    line: int | None = None


@dataclass
class Document:
    path: str
    kind: str
    raw: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    body: str = ""
    profile: str = "not_applied"
    state: dict = field(default_factory=dict)
    references: list[dict] = field(default_factory=list)


@dataclass
class Registration:
    id: str
    root: Path
    profile: bool = False
    legacy_paths: bool = False


@dataclass
class Bundle:
    id: str
    root: Path
    metadata: dict = field(default_factory=dict)
    documents: dict[str, Document] = field(default_factory=dict)
    assets: list[str] = field(default_factory=list)
    diagnostics: list[Diagnostic] = field(default_factory=list)

    @property
    def conformant(self) -> bool:
        return not any(d.category == "format" for d in self.diagnostics)

    @property
    def concepts(self) -> dict[str, Document]:
        return {p[:-3]: d for p, d in self.documents.items() if d.kind == "concept"}

    @property
    def edges(self) -> list[dict]:
        return [
            {"source": f"{self.id}:{concept_id}", "target": ref["concept"], "field": ref["field"]}
            for concept_id, doc in self.concepts.items() for ref in doc.references
            if "concept" in ref and ref["field"] != "image"
        ]


def absent(value: Any) -> bool:
    return value is None or value == "" or value == []


def timestamp(value: Any) -> datetime | None:
    """Only offset date-times and full dates; normalize to UTC for comparisons."""
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc) if value.tzinfo else None
    if isinstance(value, date):
        return datetime.combine(value, time(), timezone.utc)
    if not isinstance(value, str):
        return None
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            return datetime.combine(date.fromisoformat(value), time(), timezone.utc)
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})", value):
            return datetime.fromisoformat(value.upper().replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        pass
    return None


def parse(text: str) -> tuple[dict, str, str | None, int | None]:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        return {}, text, None, None
    end = next((i for i in range(1, len(lines)) if lines[i].rstrip("\r\n") == "---"), None)
    if end is None:
        return {}, "", "UNCLOSED_FRONTMATTER", 1
    yaml = YAML(typ="safe", pure=True)
    yaml.version = (1, 2)
    yaml.allow_duplicate_keys = False
    try:
        raw = yaml.load("".join(lines[1:end]))
        if not isinstance(raw, dict):
            return {}, "", "FRONTMATTER_NOT_MAPPING", 2
        # Cyclic YAML aliases cannot be represented in the JSON experiment report.
        def acyclic(value, parents):
            if isinstance(value, (dict, list)):
                if id(value) in parents:
                    raise ValueError("recursive YAML alias")
                children = value.values() if isinstance(value, dict) else value
                for child in children:
                    acyclic(child, parents | {id(value)})
        acyclic(raw, set())
        if yaml.version != (1, 2):
            return {}, "", "UNSUPPORTED_YAML", 2
        return raw, "".join(lines[end + 1:]), None, None
    except (YAMLError, ValueError, TypeError, RecursionError) as exc:
        mark = getattr(exc, "problem_mark", None)
        line = mark.line + 2 if mark else 2
        code = "DUPLICATE_KEY" if type(exc).__name__ == "DuplicateKeyError" else "INVALID_YAML"
        if isinstance(exc, (ValueError, RecursionError)) or type(exc).__name__ == "ConstructorError":
            code = "UNSUPPORTED_YAML"
        return {}, "", code, line


def consume(raw: dict, add) -> dict:
    metadata = deepcopy(raw)
    for key in tuple(metadata):
        if key != "type" and absent(metadata[key]):
            del metadata[key]
    for key, required in (("tags", ()), ("sources", ("resource",)),
                          ("verified", ("by", "at")), ("parameters", ("name", "type"))):
        if key not in metadata:
            continue
        values = metadata[key] if isinstance(metadata[key], list) else [metadata[key]]
        kept = []
        for i, value in enumerate(values):
            if required and (not isinstance(value, dict) or any(absent(value.get(k)) for k in required)):
                add("metadata", "INCOMPLETE_ENTRY", f"{key}[{i}]")
            else:
                if key == "parameters" and absent(value.get("required")):
                    value["required"] = False
                kept.append(value)
        metadata[key] = kept
    if "generated" in metadata:
        generated = metadata["generated"]
        if not isinstance(generated, dict) or absent(generated.get("by")):
            add("metadata", "INCOMPLETE_ENTRY", "generated")
            del metadata["generated"]
    return metadata


def state(metadata: dict, now: datetime, add) -> dict:
    status = metadata.get("status", "stable")
    if status not in ("draft", "stable", "deprecated"):
        add("metadata", "UNKNOWN_STATUS", "status")
    deadline = metadata.get("stale_after")
    parsed_deadline = timestamp(deadline)
    freshness = "unspecified"
    if deadline is not None:
        freshness = "malformed" if parsed_deadline is None else ("stale" if now >= parsed_deadline else "fresh")
        if parsed_deadline is None:
            add("metadata", "INVALID_STALE_AFTER", "stale_after")
    generated = metadata.get("generated")
    generation_time = timestamp(generated.get("at")) if isinstance(generated, dict) else None
    comparable = generated is None or generation_time is not None
    if not comparable:
        add("compatibility", "GENERATION_TIME_UNRESOLVED", "generated.at")
    current = []
    for i, event in enumerate(metadata.get("verified", [])):
        at = timestamp(event.get("at"))
        if at is None:
            add("metadata", "INVALID_VERIFICATION_TIME", f"verified[{i}].at")
        elif comparable and (generation_time is None or at >= generation_time):
            current.append(event)
    trust = "unverified"
    if current:
        trust = "human-reviewed" if any(str(e["by"]).startswith("human:") for e in current) else "machine-confirmed"
    return {"status": status, "current": status in ("draft", "stable"), "freshness": freshness, "trust": trust}


def headings(tokens, levels=("h1", "h2")) -> set[str]:
    return {"".join(c.content for c in tokens[i + 1].children or [] if c.type in ("text", "code_inline"))
            for i, t in enumerate(tokens[:-1]) if t.type == "heading_open" and t.tag in levels}


def path_fields(metadata: dict):
    for key in ("resource", "computation", "superseded_by"):
        if isinstance(metadata.get(key), str):
            yield key, metadata[key]
    for key in ("executor", "attester"):
        value = metadata.get(key)
        if isinstance(value, dict) and isinstance(value.get("resource"), str):
            yield key + ".resource", value["resource"]
    for i, value in enumerate(metadata.get("sources", [])):
        resource = value.get("resource")
        if isinstance(resource, str):
            yield f"sources[{i}].resource", resource


def computation(metadata: dict, tokens) -> str | None:
    if "computation" in metadata:
        return None  # Resolved in the second pass; the path takes precedence.
    level = None
    for i, token in enumerate(tokens):
        if token.type == "heading_open":
            if level is not None and int(token.tag[1:]) <= level:
                return None
            if level is None and token.markup.startswith("#") and tokens[i + 1].content == "Computation":
                level = int(token.tag[1:])
        if level is not None and token.type == "fence":
            return token.content
    return None


def read_document(bundle: Bundle, path: str, text: str, profile: bool, now: datetime):
    def add(category, code, field="", line=None):
        bundle.diagnostics.append(Diagnostic(category, code, path, field, line))
    raw, body, error, line = parse(text)
    if error:
        category = "compatibility" if error == "UNSUPPORTED_YAML" else "format"
        add(category, error, line=line)
        return Document(path, "invalid" if category == "format" else "unsupported")
    name = PurePosixPath(path).name
    if name in ("index.md", "log.md"):
        if text.startswith("---\n") or text.startswith("---\r\n"):
            if name == "log.md" or path != "index.md":
                add("format", "RESERVED_FRONTMATTER")
        if name == "log.md":
            dates = re.findall(r"^## (.+)$", body, re.M)
            if any(not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) or timestamp(d) is None for d in dates):
                add("format", "INVALID_LOG_DATE")
            elif dates != sorted(dates, reverse=True):
                add("format", "LOG_DATE_ORDER")
        if path == "index.md":
            bundle.metadata = raw
        return Document(path, "reserved", raw=raw, body=body)
    concept_type = raw.get("type")
    if absent(concept_type):
        add("discovery", "NON_CONCEPT")
        return Document(path, "skipped", raw=raw, body=body)
    if not isinstance(concept_type, str) or not concept_type.strip():
        add("compatibility", "TYPE_UNRESOLVED", "type")
        return Document(path, "unresolved", raw=raw, body=body)
    metadata = consume(raw, add)
    tokens = MARKDOWN.parse(body)
    doc = Document(path, "concept", raw=raw, metadata=metadata, body=body)
    doc.state = state(metadata, now, add)
    if profile and concept_type in PROFILE_HEADINGS:
        doc.profile = "passed"
        for heading in PROFILE_HEADINGS[concept_type]:
            if heading not in headings(tokens):
                add("profile", "MISSING_HEADING", heading)
                doc.profile = "failed"
        if metadata.get("status", "stable") not in ("draft", "stable", "deprecated"):
            add("profile", "INVALID_STATUS", "status")
            doc.profile = "failed"
        if sum(source.get("id") == "authoritative-source" for source in metadata.get("sources", [])) > 1:
            add("profile", "COMPETING_AUTHORITIES", "sources")
            doc.profile = "failed"
        for i, source in enumerate(metadata.get("sources", [])):
            if "x-lattivra-revision" in source and (not isinstance(source["x-lattivra-revision"], str) or not source["x-lattivra-revision"].strip()):
                add("profile", "INVALID_REVISION", f"sources[{i}].x-lattivra-revision")
                doc.profile = "failed"
    for token in tokens:
        for child in token.children or []:
            if child.type == "link_open" and child.markup != "autolink":
                doc.references.append({"field": "body", "target": child.attrGet("href")})
            elif child.type == "image":
                doc.references.append({"field": "image", "target": child.attrGet("src")})
    doc.references.extend({"field": key, "target": value} for key, value in path_fields(metadata))
    if concept_type == "Attested Computation":
        if absent(metadata.get("runtime")):
            add("contract", "MISSING_RUNTIME", "runtime")
        doc.state["attested"] = False  # A file is never evidence of a successful run.
        doc.state["computation_available"] = computation(metadata, tokens) is not None
    return doc


def within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def walk(bundle: Bundle):
    """Inspect aliases before opening targets; in-root directory aliases are skipped."""
    def visit(directory):
        try:
            entries = sorted(directory.iterdir())
        except OSError:
            bundle.diagnostics.append(Diagnostic("access", "UNREADABLE", directory.relative_to(bundle.root).as_posix()))
            return
        for entry in entries:
            if entry.name.startswith("."):
                continue
            relative = entry.relative_to(bundle.root).as_posix()
            try:
                resolved = entry.resolve()
                if not within(resolved, bundle.root):
                    bundle.diagnostics.append(Diagnostic("access", "OUTSIDE_ROOT", relative))
                    continue
                alias = entry.is_symlink() or entry.is_junction()
                if alias:
                    bundle.diagnostics.append(Diagnostic("compatibility", "INTERNAL_ALIAS_UNSUPPORTED", relative))
                elif entry.is_dir():
                    yield from visit(entry)
                elif entry.is_file():
                    yield entry
            except (OSError, RuntimeError):
                bundle.diagnostics.append(Diagnostic("access", "UNREADABLE", relative))
    yield from visit(bundle.root)


def resolve(bundle: Bundle, doc: Document, reference: dict, legacy: bool) -> dict:
    target = reference["target"]
    field_name = reference["field"]
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("//"):
        return {"state": "external"}
    # Explicitly provisional scope-descriptor heuristic (checklist U-03).
    if field_name.startswith("sources[") and re.search(r"\s", target):
        return {"state": "descriptor"}
    parsed = urlsplit(target)
    path = unquote(parsed.path)
    if "\\" in path or "\x00" in path or re.search(r"%(?![0-9a-fA-F]{2})", parsed.path):
        return {"state": "unsupported"}
    if not path:
        path = doc.path
    elif path.startswith("/"):
        path = path.lstrip("/")
    else:
        path = posixpath.join(posixpath.dirname(doc.path), path)
    path = posixpath.normpath(path)
    if path == ".." or path.startswith("../"):
        return {"state": "blocked"}
    if any(part.startswith(".") for part in PurePosixPath(path).parts if part != "."):
        return {"state": "excluded"}
    try:
        if not within((bundle.root / path).resolve(), bundle.root):
            return {"state": "blocked"}
    except (OSError, RuntimeError):
        return {"state": "blocked"}
    known = set(bundle.documents) | set(bundle.assets)
    version = bundle.metadata.get("okf_version")
    old = absent(version) or bool(re.fullmatch(r"0\.[0-2]", str(version)))
    if path not in known and legacy and old and field_name not in ("body", "image") and not parsed.path.startswith("/"):
        candidate = posixpath.normpath(unquote(parsed.path))
        if candidate in known:
            path = candidate
    if path in bundle.documents:
        result = {"state": bundle.documents[path].kind, "path": path}
        if result["state"] == "concept":
            result["concept"] = f"{bundle.id}:{path[:-3]}"
        return result
    if path in bundle.assets:
        return {"state": "asset", "path": path}
    # Infer directories only from scanned inputs, without reading new targets.
    if path == "." or any(p.startswith(path.rstrip("/") + "/") for p in known):
        return {"state": "directory", "path": path}
    return {"state": "unresolved", "path": path}


def scan(registrations: list[Registration], *, now: datetime, mappings: dict | None = None):
    if now.tzinfo is None:
        raise ValueError("evaluation clock must include a UTC offset")
    bundles: dict[str, Bundle] = {}
    diagnostics: list[Diagnostic] = []
    accepted = []
    for registration in registrations:
        root = registration.root.resolve()
        conflict = next((b for b in bundles.values() if b.id == registration.id or within(root, b.root) or within(b.root, root)), None)
        if conflict:
            diagnostics.append(Diagnostic("configuration", "REGISTRATION_CONFLICT", registration.id, f"{root} overlaps {conflict.id}: {conflict.root}"))
            continue
        if not root.is_dir():
            diagnostics.append(Diagnostic("access", "ROOT_UNREADABLE", registration.id))
            continue
        bundle = Bundle(registration.id, root)
        bundles[bundle.id] = bundle
        accepted.append(registration)
        for file in walk(bundle):
            relative = file.relative_to(root).as_posix()
            if not file.name.endswith(".md"):
                bundle.assets.append(relative)
                continue
            try:
                text = file.read_bytes().decode("utf-8")
                bundle.documents[relative] = read_document(bundle, relative, text, registration.profile, now)
            except UnicodeError:
                bundle.diagnostics.append(Diagnostic("format", "INVALID_UTF8", relative))
                bundle.documents[relative] = Document(relative, "invalid")
            except OSError:
                bundle.diagnostics.append(Diagnostic("access", "UNREADABLE", relative))
        version = bundle.metadata.get("okf_version")
        if not absent(version) and str(version) not in ("0.1", "0.2", "0.3"):
            bundle.diagnostics.append(Diagnostic("compatibility", "UNSUPPORTED_VERSION", "index.md", "okf_version"))
    for registration in accepted:
        bundle = bundles[registration.id]
        for doc in bundle.documents.values():
            for reference in doc.references:
                try:
                    result = resolve(bundle, doc, reference, registration.legacy_paths)
                except ValueError:
                    result = {"state": "unsupported"}
                if result["state"] == "external":
                    matches = (mappings or {}).get(reference["target"], [])
                    if len(matches) > 1:
                        result = {"state": "ambiguous"}
                    elif len(matches) == 1:
                        match = matches[0]
                        target_bundle = bundles.get(match["bundle"])
                        if target_bundle and match["concept"] in target_bundle.concepts:
                            result = {"state": "mapped", "concept": f"{match['bundle']}:{match['concept']}"}
                        else:
                            result = {"state": "unresolved"}
                reference.update(result)
                category = "access" if result["state"] == "blocked" else "reference"
                if result["state"] in ("blocked", "unresolved", "ambiguous", "unsupported"):
                    bundle.diagnostics.append(Diagnostic(category, result["state"].upper(), doc.path, reference["field"]))
            if doc.metadata.get("type") == "Attested Computation" and "computation" in doc.metadata:
                doc.state["computation_available"] = any(r["field"] == "computation" and r["state"] in ("asset", "concept", "skipped", "reserved") for r in doc.references)
    return bundles, diagnostics
