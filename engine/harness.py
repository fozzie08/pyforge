"""PyForge judge: runs learner code against a problem's test cases.

This one file runs in two places:
  * in the browser, inside Pyodide (CPython compiled to WebAssembly), and
  * under your local Python when build.py validates every reference solution.

Keep it standard-library only and compatible with Python 3.9+.
"""

import builtins
import copy
import io
import json
import linecache
import math
import random
import sys
import time
import traceback
from collections import deque

USER_FILE = "solution.py"
MAX_STDOUT = 5000
MAX_REPR = 800
CASE_LIMIT_MS = 2000  # per-test time limit; problems can override with "time_limit_ms"

# Names every solution can use without importing, like on LeetCode.
PRELUDE = """
from typing import *
import collections, heapq, bisect, itertools, functools, math, string, re, random, operator
from collections import deque, defaultdict, Counter, OrderedDict
from heapq import heappush, heappop, heapify, heappushpop, heapreplace, nlargest, nsmallest
from bisect import bisect_left, bisect_right, insort
from functools import lru_cache, cache, reduce, cmp_to_key
from itertools import accumulate, combinations, permutations, product, chain, groupby, zip_longest
from math import inf, gcd, sqrt, ceil, floor, comb, factorial, isqrt
"""


# --------------------------------------------------------------------------
# Data structures shared with learner code
# --------------------------------------------------------------------------

class ListNode:
    """A node in a singly-linked list."""

    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

    def __repr__(self):
        parts, node = [], self
        while node is not None and len(parts) < 12:
            parts.append(repr(node.val))
            node = node.next
        if node is not None:
            parts.append("...")
        return "ListNode(" + " -> ".join(parts) + ")"


class TreeNode:
    """A node in a binary tree."""

    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

    def __repr__(self):
        return "TreeNode(%r)" % (self.val,)


def to_linked(values):
    dummy = tail = ListNode()
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next


def from_linked(node, limit=200000):
    out = []
    while node is not None:
        if len(out) >= limit:
            raise ValueError("the returned linked list never ends (is there a cycle?)")
        if not hasattr(node, "val") or not hasattr(node, "next"):
            raise TypeError("expected a ListNode but got %s" % type(node).__name__)
        out.append(node.val)
        node = node.next
    return out


def to_tree(values):
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    return root


def from_tree(root, limit=200000):
    out, queue = [], deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            out.append(None)
            continue
        if len(out) >= limit:
            raise ValueError("the returned tree is too large (is there a cycle?)")
        if not hasattr(node, "left") or not hasattr(node, "right"):
            raise TypeError("expected a TreeNode but got %s" % type(node).__name__)
        out.append(node.val)
        queue.append(node.left)
        queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


def dismantle(value, kind):
    """Cut the links inside node structures, iteratively.

    Freeing a long chain of nodes frees each node from inside the previous
    one. That recursion is harmless in native Python but overflows the much
    smaller WebAssembly stack in the browser (around 10,000 nodes), so the
    judge breaks structures apart once it has finished with them.
    """
    if kind == "plain" or value is None:
        return
    stack = list(value) if kind == "linked_list" and isinstance(value, list) else [value]
    seen = set()
    while stack:
        node = stack.pop()
        if node is None or id(node) in seen:
            continue
        seen.add(id(node))
        for attr in ("next", "left", "right"):
            child = getattr(node, attr, None)
            if child is not None and hasattr(child, "__dict__"):
                stack.append(child)
                try:
                    setattr(node, attr, None)
                except Exception:
                    pass


def kind_of(annotation):
    """Map a type annotation to how values are converted at the boundary."""
    a = (annotation or "").replace(" ", "")
    if a in ("ListNode", "Optional[ListNode]"):
        return "linked"
    if a in ("TreeNode", "Optional[TreeNode]"):
        return "tree"
    if a in ("List[ListNode]", "List[Optional[ListNode]]"):
        return "linked_list"
    return "plain"


def encode(value, kind):
    if kind == "linked":
        return to_linked(value)
    if kind == "tree":
        return to_tree(value)
    if kind == "linked_list":
        return [to_linked(v) for v in value]
    return value


def decode(value, kind):
    if kind == "linked":
        return from_linked(value)
    if kind == "tree":
        return from_tree(value)
    if kind == "linked_list":
        return [from_linked(v) for v in value]
    return normalize(value)


# --------------------------------------------------------------------------
# Helpers available inside test-case expressions
# --------------------------------------------------------------------------

def rand_list(n, lo, hi, seed=0):
    r = random.Random(seed)
    return [r.randint(lo, hi) for _ in range(n)]


def rand_str(n, alphabet="abcdefghijklmnopqrstuvwxyz", seed=0):
    r = random.Random(seed)
    return "".join(r.choice(alphabet) for _ in range(n))


def rand_grid(rows, cols, choices, seed=0):
    r = random.Random(seed)
    return [[r.choice(choices) for _ in range(cols)] for _ in range(rows)]


def rand_sorted(n, lo, hi, seed=0):
    """n distinct sorted integers from [lo, hi]."""
    r = random.Random(seed)
    return sorted(r.sample(range(lo, hi + 1), n))


def _case_env():
    # Test inputs are Python expressions (so hidden tests can build large
    # inputs like `rand_list(10**5, 0, 9)`). They come from the lesson content
    # or from the learner's own Testcase panel and are evaluated in the same
    # sandbox that already runs the learner's code, so eval adds no new risk.
    return {
        "__builtins__": builtins,
        "null": None, "true": True, "false": False,
        "rand_list": rand_list, "rand_str": rand_str,
        "rand_grid": rand_grid, "rand_sorted": rand_sorted,
    }


# --------------------------------------------------------------------------
# Comparing and showing values
# --------------------------------------------------------------------------

_ATOMIC = (int, float, str, bool, type(None))


def clone(value):
    """A fast deep copy for the plain data used in test cases."""
    t = type(value)
    if t is list:
        if all(type(x) in _ATOMIC for x in value):
            return value[:]
        return [clone(x) for x in value]
    if t in _ATOMIC:
        return value
    if t is dict:
        return {k: clone(v) for k, v in value.items()}
    if t is tuple:
        return tuple(clone(x) for x in value)
    if t is set:
        return set(value)
    return copy.deepcopy(value)


def normalize(value):
    """Treat tuples as lists so `return (a, b)` matches `[a, b]`."""
    if isinstance(value, (list, tuple)):
        if all(type(x) in _ATOMIC for x in value):
            return list(value)
        return [normalize(x) for x in value]
    return value


def same(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, float) or isinstance(b, float):
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return math.isclose(a, b, rel_tol=1e-6, abs_tol=1e-6)
        return False
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    return a == b


def _sorted_any(values):
    try:
        return sorted(values)
    except TypeError:
        return sorted(values, key=repr)


def matches(output, expected, mode, checker=None, args=None):
    if checker is not None:
        return bool(checker(output, expected, *args))
    if mode == "unordered":
        if not isinstance(output, list):
            return False
        return same(_sorted_any(output), _sorted_any(expected))
    if mode == "unordered_deep":
        if not isinstance(output, list) or not all(isinstance(x, list) for x in output):
            return False
        norm = lambda rows: _sorted_any([_sorted_any(r) for r in rows])
        return same(norm(output), norm(expected))
    return same(output, expected)


def show(value):
    try:
        text = repr(value)
    except Exception as exc:  # a learner's __repr__ can fail
        text = "<unprintable: %s>" % type(exc).__name__
    if len(text) > MAX_REPR:
        text = text[:MAX_REPR] + " … (%d characters)" % len(text)
    return text


# --------------------------------------------------------------------------
# Running learner code
# --------------------------------------------------------------------------

class _Capture(io.TextIOBase):
    """Collects printed output, keeping only the first MAX_STDOUT characters."""

    def __init__(self):
        self.parts = []
        self.size = 0

    def writable(self):
        return True

    def write(self, s):
        if self.size < MAX_STDOUT:
            self.parts.append(s[: MAX_STDOUT - self.size])
        self.size += len(s)
        return len(s)

    def getvalue(self):
        text = "".join(self.parts)
        if self.size > MAX_STDOUT:
            text += "\n… (output truncated)"
        return text


class _Redirect:
    def __init__(self, capture):
        self.capture = capture

    def __enter__(self):
        self.saved = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = self.capture

    def __exit__(self, *exc):
        sys.stdout, sys.stderr = self.saved
        return False


def _no_input(prompt=""):
    raise RuntimeError("input() isn't available here. Put your test values straight into the code instead.")


def make_namespace():
    ns = {"__name__": "__main__", "ListNode": ListNode, "TreeNode": TreeNode}
    exec(PRELUDE, ns)
    ns["input"] = _no_input
    return ns


def load(code, filename):
    linecache.cache[filename] = (len(code), None, code.splitlines(True), filename)
    ns = make_namespace()
    exec(compile(code, filename, "exec"), ns)
    return ns


def format_syntax_error(exc):
    text = "".join(traceback.format_exception_only(type(exc), exc))
    return text.replace('File "%s", line' % USER_FILE, "Line").rstrip()


def format_error(exc):
    frames = [f for f in traceback.extract_tb(exc.__traceback__) if f.filename == USER_FILE]
    lines = ["Traceback (most recent call last):"] if frames else []
    shown = frames
    hidden = 0
    if len(frames) > 8:  # deep recursion: keep the ends, drop the middle
        shown = frames[:3] + frames[-3:]
        hidden = len(frames) - 6
    for n, f in enumerate(shown):
        if hidden and n == 3:
            lines.append("  … %d more calls …" % hidden)
        lines.append("  Line %d, in %s" % (f.lineno, f.name))
        if f.line:
            lines.append("    " + f.line.strip())
    message = str(exc)
    lines.append("%s: %s" % (type(exc).__name__, message) if message else type(exc).__name__)
    return "\n".join(lines)


def _find_target(ns, problem):
    style, entry = problem["style"], problem["entry"]
    if style == "class":
        cls = ns.get("Solution")
        if not isinstance(cls, type):
            raise LookupError("Couldn't find `class Solution`. Keep the class name from the starter code.")
        method = getattr(cls(), entry, None)
        if method is None:
            raise LookupError("`Solution` has no method called `%s`. Keep the method name from the starter code." % entry)
        return method
    if style == "design":
        cls = ns.get(entry)
        if not isinstance(cls, type):
            raise LookupError("Couldn't find `class %s`. Keep the class name from the starter code." % entry)
        return cls
    fn = ns.get(entry)
    if not callable(fn):
        raise LookupError("Couldn't find a function called `%s`. Keep the name from the starter code." % entry)
    return fn


def _invoke(target, problem, args):
    """Call the learner's code on one case. Returns (comparable value, milliseconds)."""
    if problem["style"] == "design":
        operations, arguments = args
        if not operations or len(operations) != len(arguments):
            raise ValueError("a design test needs one argument list per operation")
        t0 = time.perf_counter()
        obj = target(*clone(arguments[0]))
        outputs = [None]
        for op, op_args in zip(operations[1:], arguments[1:]):
            method = getattr(obj, op, None)
            if method is None:
                raise AttributeError("'%s' object has no method '%s'" % (problem["entry"], op))
            outputs.append(normalize(method(*clone(op_args))))
        return outputs, (time.perf_counter() - t0) * 1000

    params = problem["params"]
    call_args = [encode(clone(a), p["kind"]) for a, p in zip(args, params)]
    returned = None
    try:
        t0 = time.perf_counter()
        returned = target(*call_args)
        ms = (time.perf_counter() - t0) * 1000
        compare = problem.get("compare", "exact")
        if compare.startswith("inplace:"):
            idx = int(compare.split(":", 1)[1])
            return decode(call_args[idx], params[idx]["kind"]), ms
        return decode(returned, problem["return_kind"]), ms
    finally:
        dismantle(returned, problem["return_kind"])
        for a, p in zip(call_args, params):
            dismantle(a, p["kind"])


def _describe_inputs(problem, args):
    return [{"name": p["name"], "value": show(a)} for p, a in zip(problem["params"], args)]


def judge(problem, code, mode="submit", cases=None, progress=None):
    """Judge `code` against a problem.

    mode="run":    run `cases` (default: the examples); expected answers come
                   from the reference solution, so edited inputs work too.
    mode="submit": run every example and hidden test, stopping at the first
                   failure, like a real judge.
    """
    if mode == "run":
        case_list = cases if cases is not None else problem["examples"]
    else:
        case_list = problem["examples"] + problem["tests"]
    compare = problem.get("compare", "exact")
    limit_ms = problem.get("time_limit_ms") or CASE_LIMIT_MS
    result = {
        "status": None, "mode": mode, "passed": 0, "total": len(case_list),
        "runtime_ms": 0.0, "slowest_ms": 0.0, "limit_ms": limit_ms,
        "cases": [], "error": None, "last_input": None,
    }

    # progress(i, total) is called just before the learner's code runs, so the
    # browser can time each test and stop the worker if one runs too long.
    # i = -1 covers loading the module (top-level code).
    if progress is not None:
        progress(-1, len(case_list))
    setup_out = _Capture()
    try:
        with _Redirect(setup_out):
            user_ns = load(code, USER_FILE)
        target = _find_target(user_ns, problem)
    except SyntaxError as exc:
        result.update(status="Compile Error", error=format_syntax_error(exc))
        return result
    except LookupError as exc:
        result.update(status="Runtime Error", error=str(exc))
        return result
    except BaseException as exc:
        result.update(status="Runtime Error", error=format_error(exc))
        return result

    ref_ns = load(problem["reference"], "reference.py")
    ref_target = _find_target(ref_ns, problem)
    checker = None
    if problem.get("checker"):
        checker_ns = load(problem["checker"], "checker.py")
        checker = checker_ns["check"]

    env = _case_env()
    for i, case in enumerate(case_list):
        try:
            args = [eval(expr, env) for expr in case["args"]]
        except Exception as exc:
            result.update(status="Invalid Testcase",
                          error="Couldn't read the input for case %d: %s: %s" % (i + 1, type(exc).__name__, exc))
            return result
        if len(args) != len(problem["params"]):
            result.update(status="Invalid Testcase",
                          error="Case %d has %d inputs but the function takes %d." % (i + 1, len(args), len(problem["params"])))
            return result
        inputs = _describe_inputs(problem, args)
        result["last_input"] = inputs

        expected_error = None
        if mode == "submit" and case.get("expected") is not None:
            expected = eval(case["expected"], env)
        else:
            try:
                with _Redirect(_Capture()):
                    expected, _ = _invoke(ref_target, problem, args)
            except Exception as exc:
                expected = None
                expected_error = "The reference solution couldn't handle this input (%s). Check that it follows the constraints." % type(exc).__name__

        out = _Capture()
        if i == 0:
            out.write(setup_out.getvalue())
        if progress is not None:
            progress(i, len(case_list))
        try:
            with _Redirect(out):
                output, ms = _invoke(target, problem, args)
        except BaseException as exc:  # includes RecursionError and SystemExit
            result.update(status="Runtime Error", error=format_error(exc))
            result["cases"].append({"index": i, "input": inputs, "stdout": out.getvalue(),
                                    "output": None, "expected": show(expected), "passed": False})
            return result

        result["runtime_ms"] += ms
        result["slowest_ms"] = max(result["slowest_ms"], round(ms, 2))
        if ms > limit_ms:
            result["status"] = "Time Limit Exceeded"
            result["cases"].append({"index": i, "input": inputs, "stdout": out.getvalue(), "ms": round(ms, 1),
                                    "output": None, "expected": None, "passed": False})
            result["runtime_ms"] = round(result["runtime_ms"], 2)
            return result
        ok = expected_error is None and matches(output, expected, compare, checker, args)
        entry = {"index": i, "input": inputs, "output": show(output),
                 "expected": expected_error or show(expected), "stdout": out.getvalue(),
                 "passed": ok, "ms": round(ms, 2)}
        if ok:
            result["passed"] += 1
            if mode == "run":
                result["cases"].append(entry)
        else:
            result["cases"].append(entry)
            if mode == "submit":
                result["status"] = "Wrong Answer"
                return result

    if mode == "run":
        result["status"] = "Accepted" if result["passed"] == len(case_list) else "Wrong Answer"
    else:
        result["status"] = "Accepted"
    result["runtime_ms"] = round(result["runtime_ms"], 2)
    return result


def run_script(code, setup=None):
    """Run a free-form snippet (lesson examples) and capture what it prints.

    `setup` is optional lesson code (helper functions) run silently first.
    """
    out = _Capture()
    error = None
    try:
        with _Redirect(out):
            ns = make_namespace()
            if setup:
                exec(compile(setup, "lesson_setup.py", "exec"), ns)
            linecache.cache[USER_FILE] = (len(code), None, code.splitlines(True), USER_FILE)
            exec(compile(code, USER_FILE, "exec"), ns)
    except SyntaxError as exc:
        error = format_syntax_error(exc)
    except BaseException as exc:
        error = format_error(exc)
    return {"stdout": out.getvalue(), "error": error}


def handle(request_json, progress=None):
    """Entry point used by the browser worker."""
    request = json.loads(request_json)
    if request["action"] == "script":
        response = run_script(request["code"], request.get("setup"))
    else:
        response = judge(request["problem"], request["code"], request.get("mode", "submit"),
                         request.get("cases"), progress)
    return json.dumps(response)
