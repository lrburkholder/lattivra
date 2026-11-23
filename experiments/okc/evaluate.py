"""Run the pinned OKC CLI against disposable copies of the M0 corpus."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import sqlite3
import subprocess
import tempfile


REPO = Path(__file__).resolve().parents[2]
CORPUS = REPO / "tests/fixtures/corpus.json"
WINDOWS_SHA256 = "e9910ba8b53dbd336f7d6fa55efb9d7e3902fde0e97e62a5f9121572942bc76d"
QUERIES = ("decision", "latfirstmarker", "latsecondmarker", "latobserver")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(root):
    return {p.relative_to(root).as_posix(): digest(p) for p in root.rglob("*") if p.is_file()}


def save(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def logical_index(db):
    # Compare stored documents by path and value. Local row IDs, mtimes, timing
    # and ranking have no meaning across two independently created databases.
    queries = {
        "documents": "SELECT path, title, type, description, parse_status, body_text FROM documents",
        "metadata": "SELECT path, key, value FROM metadata_fields JOIN documents ON document_id=id",
        "tags": "SELECT path, tag FROM document_tags JOIN documents ON document_id=id",
        "links": """SELECT path, target_path, target_anchor, external_url, exists_in_repository
                    FROM links JOIN documents ON source_document_id=id""",
        "errors": "SELECT path, stage, message, line FROM scan_errors",
    }
    result = {}
    with sqlite3.connect(db.as_uri() + "?mode=ro", uri=True) as conn:
        for key, sql in queries.items():
            rows = list(conn.execute(sql))
            if key == "metadata":
                rows = [(p, k, json.loads(v)) for p, k, v in rows]
            result[key] = sorted(rows, key=lambda row: json.dumps(row, sort_keys=True))
    return result


class Catalog:
    def __init__(self, exe, run, name, roots):
        self.exe = exe
        self.run = run
        self.db = run / (name + ".db")
        self.config = run / (name + ".toml")
        self.config.write_text(
            "roots = " + json.dumps([p.as_posix() for p in roots], ensure_ascii=False)
            + "\ndb_path = " + json.dumps(self.db.as_posix(), ensure_ascii=False)
            + "\nfollow_symlinks = false\n", encoding="utf-8"
        )
        self.calls = []

    def call(self, *args, allowed=(0,)):
        sources = self.run / "sources"
        before = hashes(sources)
        proc = subprocess.run(
            [self.exe, "--config", self.config, *args], cwd=self.run,
            env={k: v for k, v in os.environ.items() if not k.upper().startswith("OKC_")},
            capture_output=True, encoding="utf-8", errors="replace", timeout=90,
        )
        self.calls.append(dict(args=args, code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr))
        save(self.config.with_suffix(".commands.json"), self.calls)
        if hashes(sources) != before:
            raise RuntimeError(f"Source bytes changed during {args}. Evidence: {self.run}")
        if proc.returncode not in allowed:
            raise RuntimeError(f"{args} exited {proc.returncode}: {proc.stderr}")
        return proc.stdout

    def snapshot(self, label):
        result = logical_index(self.db)
        validation = json.loads(self.call("validate", "--json", allowed=(0, 1)))
        result["diagnostics"] = sorted(validation["issues"], key=lambda v: json.dumps(v, sort_keys=True))
        result["search"] = {}
        for query in QUERIES:
            output = self.call("search", query)
            paths = re.findall(r"^  (.+?) \[.*?\] - score:", output, re.MULTILINE)
            count = re.search(r"Total matches: (\d+)", output)
            if not count or len(paths) != int(count[1]):
                raise ValueError(f"Unexpected or truncated search output: {output}")
            result["search"][query] = sorted(paths)
        save(self.run / f"{self.config.stem}-{label}.json", result)
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    exe = parser.parse_args().binary.resolve(strict=True)
    binary_hash = digest(exe)
    if os.name == "nt" and binary_hash != WINDOWS_SHA256:
        raise ValueError(f"Unexpected Windows release binary: sha256={binary_hash}")
    version = subprocess.check_output([exe, "--version"], text=True).strip()
    if version != "okc 0.1.0":
        raise ValueError(f"Unexpected OKC version: {version}")

    artifacts = REPO / "artifacts"
    artifacts.mkdir(exist_ok=True)
    # Dot-prefixed experiment directories are outside the repository's OKF scan.
    run = Path(tempfile.mkdtemp(prefix=".okc-run-", dir=artifacts))
    print(run, flush=True)
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    roots = {}
    for bundle in corpus["bundles"]:
        name = bundle["id"]
        roots[name] = run / "sources" / name / "bundle"
        shutil.copytree(CORPUS.parent / bundle["root"], roots[name])
    initial = hashes(run / "sources")
    save(run / "inputs.json", dict(platform=platform.platform(), version=version,
                                   binary_sha256=binary_hash, corpus_sha256=digest(CORPUS), files=initial))
    all_roots = list(roots.values())
    combined = Catalog(exe, run, "combined", all_roots)
    combined.call("scan")
    combined.snapshot("baseline")
    combined.call("metadata", "--filter", "type=Decision")
    combined.call("search", "decision", "--types", "Decision")
    shared = str(Path("decisions/shared.md"))
    for name, root in roots.items():
        single = Catalog(exe, run, name, [root])
        single.call("scan")
        single.snapshot("baseline")
        if name in ("alpha", "beta"):
            single.call("get", shared, "--include", "metadata,body")
            single.call("backlinks", shared)
        if name == "alpha":
            for path in ("specifications/native.md", "specifications/projected.md", "unknown.md"):
                single.call("get", str(Path(path)), "--include", "metadata,custom,body")
                single.call("links", str(Path(path)))

    for attempt in corpus["registration_attempts"]:
        source = (CORPUS.parent / attempt["root"]).resolve()
        parent = next(b for b in corpus["bundles"] if source.is_relative_to(
            (CORPUS.parent / b["root"]).resolve()))
        extra = roots[parent["id"]] / source.relative_to((CORPUS.parent / parent["root"]).resolve())
        conflict = Catalog(exe, run, attempt["id"], [*all_roots, extra])
        conflict.call("scan", allowed=(0, 1))

    # Exercise optional-field cases separately so the baseline corpus counts
    # and registration configuration stay comparable across refreshes.
    optional = run / "sources" / "optional"
    optional.mkdir()
    for name, value in (("null", "null"), ("empty-string", "''"), ("empty-list", "[]")):
        (optional / f"{name}.md").write_text(
            f"---\ntype: Reference\nstatus: {value}\nstale_after: {value}\nverified: {value}\n---\n",
            encoding="utf-8",
        )
    (optional / "incomplete.md").write_text(
        "---\ntype: Reference\nstatus: mystery\nstale_after: someday\n"
        "sources: [{id: incomplete}, {resource: /valid.md}]\n---\n", encoding="utf-8"
    )
    fields = Catalog(exe, run, "optional", [optional])
    fields.call("scan")
    fields.snapshot("fields")

    # Keep a live inbound link after deletion. Use root-level targets to
    # distinguish refresh behavior from nested path separator handling.
    probe = roots["alpha"] / "probe.md"
    observer = roots["alpha"] / "observer.md"
    observer.write_text("---\ntype: Reference\n---\nlatobserver [probe](probe.md)\n", encoding="utf-8")
    for phase in ("added", "edited", "deleted"):
        if phase == "deleted":
            probe.unlink()
        else:
            term, target = ("latfirstmarker", "generic.md") if phase == "added" else ("latsecondmarker", "unknown.md")
            probe.write_text(f"---\ntype: Reference\ntitle: {phase}\n---\n{term} [link]({target})\n",
                             encoding="utf-8")
        combined.call("scan")
        state = combined.snapshot(phase)
        for target in ("generic.md", "unknown.md", "probe.md"):
            combined.call("backlinks", target, allowed=(0, 1))
        combined.call("links", "observer.md")

    fresh = Catalog(exe, run, "fresh", all_roots)
    fresh.call("scan")
    rebuilt = fresh.snapshot("rebuilt")
    comparison = {key: state[key] == rebuilt[key] for key in state}
    save(run / "equivalence.json", comparison)
    print(json.dumps(comparison, indent=2))


if __name__ == "__main__":
    main()
