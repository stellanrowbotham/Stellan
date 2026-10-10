#!/usr/bin/env python3
"""Small helper CLI for the LLM Wiki (see CLAUDE.md §2, "tools/").

    python3 tools/wiki.py search "query terms" [-n 5]   BM25 search over wiki pages (--all: include index/log)
    python3 tools/wiki.py lint                          mechanical health check
    python3 tools/wiki.py stats                         page counts, hubs, link totals
    python3 tools/wiki.py graph [-o file.json]          nodes/edges JSON for visualisation

Standard library only. Meant to be good enough until qmd is worth installing.
"""
import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
RAW = ROOT / "raw"

LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
CODE_RE = re.compile(r"```.*?```|`[^`\n]*`", re.S)
FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
TOKEN_RE = re.compile(r"[a-z0-9]+")
REQUIRED_FM = {
    "source": ["type", "title", "created", "updated", "sources", "raw"],
    "entity": ["type", "kind", "title", "created", "updated", "sources"],
    "concept": ["type", "title", "created", "updated", "sources"],
    "analysis": ["type", "title", "created", "updated", "sources", "question"],
    "agent": ["type", "kind", "title", "created", "updated", "sources"],
    "overview": ["type", "title", "created", "updated"],
    "meta": ["type", "title", "created"],
}


def parse_frontmatter(text):
    m = FM_RE.match(text)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, val = line.split(":", 1)
            val = val.strip()
            if val.startswith("[") and val.endswith("]"):
                val = [v.strip().strip("\"'") for v in val[1:-1].split(",") if v.strip()]
            fm[key.strip()] = val
    return fm, text[m.end():]


def load_pages():
    pages = {}
    for path in sorted(WIKI.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        links = LINK_RE.findall(CODE_RE.sub("", body))
        pages[path.stem] = {
            "path": path,
            "fm": fm,
            "body": body,
            "links": [l.strip() for l in links],
        }
    return pages


def inbound(pages):
    inc = defaultdict(set)
    for name, p in pages.items():
        for l in p["links"]:
            if l != name:
                inc[l].add(name)
    return inc


# ---------------------------------------------------------------- search
def cmd_search(args):
    pages = load_pages()
    docs = {}
    for name, p in pages.items():
        if p["fm"].get("type") == "meta" and not args.all:
            continue  # index/log mention everything; they'd swamp real pages
        title = p["fm"].get("title", name)
        aliases = " ".join(p["fm"].get("aliases", []) or [])
        # title/aliases counted three times so they outweigh body mentions
        docs[name] = TOKEN_RE.findall(((title + " " + aliases + " ") * 3 + p["body"]).lower())
    N = len(docs)
    avgdl = sum(len(d) for d in docs.values()) / max(N, 1)
    df = Counter(t for d in docs.values() for t in set(d))
    q = TOKEN_RE.findall(args.query.lower())
    k1, b = 1.5, 0.75
    scores = []
    for name, d in docs.items():
        tf = Counter(d)
        s = 0.0
        for t in q:
            if t not in tf:
                continue
            idf = math.log(1 + (N - df[t] + 0.5) / (df[t] + 0.5))
            s += idf * tf[t] * (k1 + 1) / (tf[t] + k1 * (1 - b + b * len(d) / avgdl))
        if s > 0:
            scores.append((s, name))
    scores.sort(reverse=True)
    if not scores:
        print("no matches")
        return 0
    for s, name in scores[: args.n]:
        p = pages[name]
        body = re.sub(r"\s+", " ", p["body"])
        hit = next((m.start() for t in q for m in [re.search(re.escape(t), body, re.I)] if m), 0)
        snippet = body[max(0, hit - 60): hit + 100].strip()
        print(f"{s:6.2f}  [[{name}]]  ({p['path'].relative_to(ROOT)})\n        …{snippet}…")
    return 0


# ---------------------------------------------------------------- lint
def cmd_lint(args):
    pages = load_pages()
    names = set(pages)
    inc = inbound(pages)
    problems = defaultdict(list)

    for name, p in pages.items():
        for l in p["links"]:
            if l not in names:
                problems["broken link"].append(f"[[{name}]] → [[{l}]]")
        fm = p["fm"]
        ptype = fm.get("type")
        if not ptype:
            problems["frontmatter"].append(f"[[{name}]] has no `type`")
            continue
        for key in REQUIRED_FM.get(ptype, []):
            if key not in fm:
                problems["frontmatter"].append(f"[[{name}]] ({ptype}) missing `{key}`")
        if ptype == "source" and fm.get("raw") and not (ROOT / fm["raw"]).exists():
            problems["source"].append(f"[[{name}]] points at missing raw file {fm['raw']}")
        listed = set(fm.get("sources", []) or [])
        for s in listed:
            if s not in names:
                problems["frontmatter"].append(f"[[{name}]] lists unknown source `{s}`")
        cited = {l for l in p["links"] if l.startswith("src-")}
        if ptype in ("entity", "concept", "analysis", "agent") and cited - listed:
            problems["frontmatter"].append(
                f"[[{name}]] cites {sorted(cited - listed)} but they're not in `sources:`")

    special = {"index", "log", "overview"}
    for name in names - special:
        if not (inc[name] - {"index", "log"}):
            problems["orphan (only index/log link here)"].append(f"[[{name}]]")

    index_links = set(pages.get("index", {}).get("links", []))
    for name in names - {"index"}:
        if name not in index_links:
            problems["index drift"].append(f"[[{name}]] missing from index.md")

    index_body = pages.get("index", {}).get("body", "")
    for m in re.finditer(r"^- \[\[([^\]|]+)\]\].*· (\d+) sources?\s*$", index_body, re.M):
        name, n = m.group(1), int(m.group(2))
        actual = len(pages.get(name, {}).get("fm", {}).get("sources", []) or [])
        if name in pages and actual != n:
            problems["index drift"].append(f"[[{name}]] index says {n} sources, frontmatter has {actual}")

    raw_files = {p.relative_to(ROOT).as_posix() for p in RAW.rglob("*") if p.is_file() and p.name != ".gitkeep"}
    ingested = {p["fm"].get("raw") for p in pages.values() if p["fm"].get("type") == "source"}
    for r in sorted(raw_files - ingested):
        if not r.startswith("raw/assets/"):
            problems["not yet ingested"].append(r)

    if not problems:
        print(f"✓ clean: {len(pages)} pages, {sum(len(p['links']) for p in pages.values())} links")
        return 0
    for kind, items in problems.items():
        print(f"\n## {kind} ({len(items)})")
        for i in items:
            print(f"- {i}")
    return 1


# ---------------------------------------------------------------- stats / graph
def build_graph(pages):
    inc = inbound(pages)
    nodes = [{
        "id": n,
        "title": p["fm"].get("title", n),
        "type": p["fm"].get("type", "?"),
        "summary": next((l for l in p["body"].splitlines()[1:] if l.strip() and not l.startswith(("#", ">"))), "")[:200],
        "inbound": len(inc[n]),
        "sources": len(p["fm"].get("sources", []) or []),
    } for n, p in pages.items()]
    edges = sorted({(n, l) for n, p in pages.items() for l in p["links"] if l in pages and l != n})
    return {"nodes": nodes, "edges": [{"source": a, "target": b} for a, b in edges]}


def cmd_stats(args):
    pages = load_pages()
    g = build_graph(pages)
    by_type = Counter(n["type"] for n in g["nodes"])
    print("pages:", len(pages), dict(sorted(by_type.items())))
    print("unique links:", len(g["edges"]))
    print("raw sources:", len([p for p in RAW.rglob("*") if p.is_file() and p.name != ".gitkeep"]))
    print("\nhubs (most inbound links):")
    for n in sorted(g["nodes"], key=lambda n: -n["inbound"])[:8]:
        print(f"  {n['inbound']:3d}  [[{n['id']}]]")
    return 0


def cmd_graph(args):
    data = json.dumps(build_graph(load_pages()), indent=1, ensure_ascii=False)
    if args.o:
        Path(args.o).write_text(data, encoding="utf-8")
        print(f"wrote {args.o}")
    else:
        print(data)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("-n", type=int, default=5)
    s.add_argument("--all", action="store_true", help="also search meta pages (index, log)")
    s.set_defaults(func=cmd_search)
    sub.add_parser("lint").set_defaults(func=cmd_lint)
    sub.add_parser("stats").set_defaults(func=cmd_stats)
    g = sub.add_parser("graph"); g.add_argument("-o"); g.set_defaults(func=cmd_graph)
    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
