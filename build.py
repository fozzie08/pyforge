#!/usr/bin/env python3
"""Validate all PyForge content and compile it into the static site.

    python3 build.py            validate everything, write site/assets/content.js
                                and the single-file dist/pyforge.html
    python3 build.py --quiet    only print problems and the summary

The build fails (exit code 1) if any reference solution doesn't pass its own
tests, if a starter template already passes, or if a lesson example crashes.
"""

import ast
import hashlib
import importlib
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from content import MODULE_ORDER  # noqa: E402
from content.dsl import MISSING, gen  # noqa: E402
from engine import harness  # noqa: E402

SITE = ROOT / "site"
DIST = ROOT / "dist"
QUIET = "--quiet" in sys.argv
STORE_EXPECTED_LIMIT = 4000  # longer expected answers are computed in the browser
MAX_REFERENCE_CASE_MS = 400  # headroom under the judge's per-test limit (engine/harness.py)

LINKED_HEADER = """\
# Definition for singly-linked list (already defined for you):
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
"""
TREE_HEADER = """\
# Definition for a binary tree node (already defined for you):
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
"""


class ContentError(Exception):
    pass


def log(msg):
    if not QUIET:
        print(msg)


# --------------------------------------------------------------------------
# Reading a reference solution
# --------------------------------------------------------------------------

def _signature(fn):
    returns = " -> " + ast.unparse(fn.returns) if fn.returns else ""
    return "def %s(%s)%s:" % (fn.name, ast.unparse(fn.args), returns)


def _public_methods(cls):
    return [n for n in cls.body if isinstance(n, ast.FunctionDef)
            and (n.name == "__init__" or not n.name.startswith("_"))]


def analyze(prob):
    """Work out style, entry point, parameters and starter code from the solution."""
    tree = ast.parse(prob["solution"])
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name not in ("ListNode", "TreeNode")]
    funcs = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    solution_cls = next((c for c in classes if c.name == "Solution"), None)

    if solution_cls is not None:
        style = "class"
        methods = [m for m in _public_methods(solution_cls) if m.name != "__init__"]
        fn = next((m for m in methods if m.name == prob["entry"]), None) if prob["entry"] else methods[0]
        if fn is None:
            raise ContentError("no method %r on Solution" % prob["entry"])
        entry = fn.name
        params = [(a.arg, ast.unparse(a.annotation) if a.annotation else "") for a in fn.args.args[1:]]
        returns = ast.unparse(fn.returns) if fn.returns else ""
        body = "class Solution:\n    %s\n        pass\n" % _signature(fn)
    elif classes:
        style = "design"
        cls = next((c for c in classes if c.name == prob["entry"]), None) if prob["entry"] else classes[0]
        entry = cls.name
        params = [("operations", "List[str]"), ("arguments", "List[list]")]
        returns = "List"
        stubs = ["    %s\n        pass\n" % _signature(m) for m in _public_methods(cls)]
        body = "class %s:\n%s" % (entry, "\n".join(stubs))
    else:
        style = "function"
        fn = next((f for f in funcs if f.name == prob["entry"]), None) if prob["entry"] else funcs[0]
        if fn is None:
            raise ContentError("no function %r" % prob["entry"])
        entry = fn.name
        params = [(a.arg, ast.unparse(a.annotation) if a.annotation else "") for a in fn.args.args]
        returns = ast.unparse(fn.returns) if fn.returns else ""
        body = "%s\n    pass\n" % _signature(fn)

    header = ""
    if "ListNode" in prob["solution"]:
        header += LINKED_HEADER + "\n"
    if "TreeNode" in prob["solution"]:
        header += TREE_HEADER + "\n"
    starter = prob["starter"] or header + body

    return {
        "style": style,
        "entry": entry,
        "params": [{"name": n, "type": t, "kind": harness.kind_of(t)} for n, t in params],
        "return_type": returns,
        "return_kind": harness.kind_of(returns),
        "starter": starter,
    }


# --------------------------------------------------------------------------
# Test cases
# --------------------------------------------------------------------------

def to_expr(value):
    if isinstance(value, gen):
        return str(value), True
    text = repr(value)
    if eval(text) != value:  # noqa: S307 - our own content, checked at build time
        raise ContentError("value %r doesn't survive repr()" % (value,))
    return text, False


def compile_cases(spec, raw_cases, ref_target, is_example):
    out = []
    for n, c in enumerate(raw_cases):
        exprs, has_gen = [], False
        for a in c["args"]:
            e, g = to_expr(a)
            exprs.append(e)
            has_gen = has_gen or g
        if len(exprs) != len(spec["params"]):
            raise ContentError("case %d has %d args; expected %d" % (n + 1, len(exprs), len(spec["params"])))
        expected = None
        if c["out"] is not MISSING:
            expected = repr(c["out"])
        elif not has_gen or is_example:
            env = harness._case_env()
            args = [eval(e, env) for e in exprs]  # noqa: S307
            value, _ = harness._invoke(ref_target, spec, args)
            text = repr(value)
            if is_example or len(text) <= STORE_EXPECTED_LIMIT:
                expected = text
        item = {"args": exprs, "expected": expected}
        if is_example:
            item["why"] = c["why"]
        out.append(item)
    return out


# --------------------------------------------------------------------------
# Building problems and lessons
# --------------------------------------------------------------------------

def build_problem(prob, kind, extra):
    try:
        spec = analyze(prob)
        spec["compare"] = prob["compare"]
        spec["reference"] = prob["solution"]
        spec["checker"] = prob["checker"]
        spec["time_limit_ms"] = prob["time_limit_ms"] or harness.CASE_LIMIT_MS
        ref_target = harness._find_target(harness.load(prob["solution"], "reference.py"), spec)
        spec["examples"] = compile_cases(spec, prob["examples"], ref_target, True)
        spec["tests"] = compile_cases(spec, prob["tests"], ref_target, False)
    except ContentError as exc:
        raise ContentError("%s: %s" % (prob["id"], exc))

    if not prob["examples"]:
        raise ContentError("%s: needs at least one example" % prob["id"])

    t0 = time.perf_counter()
    verdict = harness.judge(spec, prob["solution"], "submit")
    elapsed = time.perf_counter() - t0
    if verdict["status"] != "Accepted":
        detail = verdict["error"] or json.dumps(verdict["cases"], indent=2)
        raise ContentError("%s: reference solution got %s\n%s" % (prob["id"], verdict["status"], detail))

    starter_verdict = harness.judge(spec, spec["starter"], "submit")
    if starter_verdict["status"] in ("Accepted", "Compile Error"):
        raise ContentError("%s: starter code got %s" % (prob["id"], starter_verdict["status"]))

    if verdict["slowest_ms"] > MAX_REFERENCE_CASE_MS:
        raise ContentError("%s: the reference solution took %.0f ms on one test; keep every test under %d ms "
                           "so learners on slower devices stay well inside the %d ms limit"
                           % (prob["id"], verdict["slowest_ms"], MAX_REFERENCE_CASE_MS, verdict["limit_ms"]))
    log("  ✓ %-38s %2d tests  %6.0f ms total  %5.0f ms slowest"
        % (prob["id"], verdict["total"], elapsed * 1000, verdict["slowest_ms"]))

    record = {
        "id": prob["id"],
        "kind": kind,
        "title": prob["title"],
        "difficulty": prob["difficulty"],
        "tags": prob["tags"],
        "description": prob["description"],
        "constraints": prob["constraints"],
        "hints": prob["hints"],
        "explanation": prob["explanation"],
    }
    record.update(spec)
    record.update(extra)
    return record


def check_lesson_examples(lesson):
    """Every ```python block in a lesson must run without error."""
    blocks = re.findall(r"```python\n(.*?)```", lesson["body"], re.S)
    for n, code in enumerate(blocks):
        result = harness.run_script(code, lesson["setup"])
        if result["error"] and "# error expected" not in code:
            raise ContentError("lesson %s, example %d failed:\n%s\n%s" % (lesson["id"], n + 1, code, result["error"]))
    return len(blocks)


def build():
    modules, problems = [], {}
    challenge_no = 0
    seen_ids = set()

    for index, name in enumerate(MODULE_ORDER, start=1):
        mod = importlib.import_module("content." + name).MODULE
        log("\nModule %d · %s" % (index, mod["title"]))
        lesson_records = []
        for lesson in mod["lessons"]:
            examples = check_lesson_examples(lesson)
            log(" %s (%d runnable examples)" % (lesson["title"], examples))
            ex_ids = []
            for ex in lesson["exercises"]:
                if ex["id"] in seen_ids:
                    raise ContentError("duplicate id %s" % ex["id"])
                seen_ids.add(ex["id"])
                problems[ex["id"]] = build_problem(ex, "exercise", {"lesson": lesson["id"], "module": mod["id"]})
                ex_ids.append(ex["id"])
            lesson_records.append({
                "id": lesson["id"], "title": lesson["title"], "summary": lesson["summary"],
                "body": lesson["body"], "minutes": lesson["minutes"], "exercises": ex_ids,
                "setup": lesson["setup"],
            })

        log(" %s" % mod["challenge_title"])
        ch_ids = []
        for ch in mod["challenges"]:
            if ch["id"] in seen_ids:
                raise ContentError("duplicate id %s" % ch["id"])
            if ch["difficulty"] not in ("Easy", "Medium", "Hard"):
                raise ContentError("%s: challenge difficulty must be Easy, Medium or Hard" % ch["id"])
            seen_ids.add(ch["id"])
            challenge_no += 1
            problems[ch["id"]] = build_problem(ch, "challenge", {"module": mod["id"], "number": challenge_no})
            ch_ids.append(ch["id"])

        modules.append({
            "id": mod["id"], "number": index, "title": mod["title"], "blurb": mod["blurb"],
            "lessons": lesson_records, "challenges": ch_ids,
            "challenge_title": mod["challenge_title"], "challenge_blurb": mod["challenge_blurb"],
        })

    return {"modules": modules, "problems": problems}


def stamp_asset_versions():
    """Add ?v=<content hash> to asset links in index.html.

    Static hosts like GitHub Pages let browsers cache files for a while; the
    hash changes whenever a file does, so a new deploy never mixes fresh and
    stale assets.
    """
    index = SITE / "index.html"

    def stamp(match):
        path = match.group(2)
        digest = hashlib.sha256((SITE / path).read_bytes()).hexdigest()[:10]
        return '%s="%s?v=%s"' % (match.group(1), path, digest)

    html = re.sub(r'(href|src)="(assets/[^"?]+)(?:\?v=\w+)?"', stamp, index.read_text())
    index.write_text(html)


def write_outputs(data):
    harness_src = (ROOT / "engine" / "harness.py").read_text()
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    js = ("// Generated by build.py. Edit the files in content/ and rebuild instead.\n"
          "window.PYFORGE_CONTENT = %s;\nwindow.PYFORGE_HARNESS = %s;\n"
          % (payload, json.dumps(harness_src)))
    (SITE / "assets" / "content.js").write_text(js)
    stamp_asset_versions()

    # One self-contained HTML file that works when opened straight from disk.
    html = (SITE / "index.html").read_text()

    def inline_css(match):
        return "<style>\n%s\n</style>" % (SITE / match.group(1)).read_text()

    def inline_js(match):
        src = (SITE / match.group(1)).read_text().replace("</script", "<\\/script")
        return "<script>\n%s\n</script>" % src

    html = re.sub(r'<link rel="stylesheet" href="(assets/[^"?]+)(?:\?v=\w+)?">', inline_css, html)
    html = re.sub(r'<script src="(assets/[^"?]+)(?:\?v=\w+)?"></script>', inline_js, html)
    DIST.mkdir(exist_ok=True)
    (DIST / "pyforge.html").write_text(html)
    return len(js), len(html)


def main():
    t0 = time.perf_counter()
    try:
        data = build()
    except ContentError as exc:
        print("\n✗ Build failed: %s" % exc)
        return 1
    js_size, html_size = write_outputs(data)
    probs = data["problems"].values()
    n_ex = sum(1 for p in probs if p["kind"] == "exercise")
    by_diff = {}
    for p in probs:
        if p["kind"] == "challenge":
            by_diff[p["difficulty"]] = by_diff.get(p["difficulty"], 0) + 1
    n_lessons = sum(len(m["lessons"]) for m in data["modules"])
    print("\n✓ Built %d modules, %d lessons, %d exercises, %d challenges (%s) in %.1fs"
          % (len(data["modules"]), n_lessons, n_ex, sum(by_diff.values()),
             ", ".join("%d %s" % (by_diff.get(d, 0), d) for d in ("Easy", "Medium", "Hard")),
             time.perf_counter() - t0))
    print("  site/assets/content.js  %6.0f KB" % (js_size / 1024))
    print("  dist/pyforge.html       %6.0f KB" % (html_size / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
