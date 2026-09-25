"""Small helpers for writing PyForge lessons, exercises and challenges.

Every problem is defined by a reference `solution`. build.py reads its
signature to generate starter code, runs it against every test, and refuses
to build if anything fails, so the content can't drift out of sync.
"""

import textwrap

MISSING = object()


class gen(str):
    """A test input written as Python source, evaluated when the tests run.

    Use it for large hidden inputs that would bloat the site if written out,
    e.g. gen("rand_list(10**5, -1000, 1000, seed=7)"). Helpers available:
    rand_list, rand_str, rand_grid, rand_sorted (see engine/harness.py).
    """


def case(*args, out=MISSING, why=None):
    """One test case: positional arguments plus the expected return value.

    Leave `out` off to have build.py compute it from the reference solution.
    `why` is shown as the explanation under an example.
    """
    return {"args": list(args), "out": out, "why": why}


def _clean(text):
    return textwrap.dedent(text).strip("\n")


def problem(id, title, description, solution, examples, tests=(), *, hints=(),
            constraints=(), explanation="", difficulty=None, tags=(),
            compare="exact", entry=None, starter=None, checker=None, time_limit_ms=None):
    """A problem. `compare` is one of:

    exact           output must equal the expected value
    unordered       output is a list whose order doesn't matter
    unordered_deep  a list of lists where neither level's order matters
    inplace:N       the function mutates argument N; that argument is checked
    """
    return {
        "id": id,
        "title": title,
        "description": _clean(description),
        "solution": _clean(solution) + "\n",
        "examples": list(examples),
        "tests": list(tests),
        "hints": [_clean(h) for h in hints],
        "constraints": list(constraints),
        "explanation": _clean(explanation),
        "difficulty": difficulty,
        "tags": list(tags),
        "compare": compare,
        "entry": entry,
        "starter": _clean(starter) + "\n" if starter else None,
        "checker": _clean(checker) + "\n" if checker else None,
        "time_limit_ms": time_limit_ms,
    }


def exercise(*args, **kwargs):
    kwargs.setdefault("difficulty", "Practice")
    return problem(*args, **kwargs)


def lesson(id, title, summary, body, exercises, minutes=15, setup=None):
    """A lesson. `setup` is helper code run silently before every example."""
    return {
        "id": id,
        "title": title,
        "summary": summary,
        "body": _clean(body),
        "exercises": list(exercises),
        "minutes": minutes,
        "setup": _clean(setup) + "\n" if setup else None,
    }


def module(id, title, blurb, lessons, challenges, challenge_title, challenge_blurb):
    return {
        "id": id,
        "title": title,
        "blurb": blurb,
        "lessons": list(lessons),
        "challenges": list(challenges),
        "challenge_title": challenge_title,
        "challenge_blurb": challenge_blurb,
    }


def challenge_problem(*args, **kwargs):
    """A checkpoint challenge; `difficulty` must be Easy, Medium or Hard."""
    return problem(*args, **kwargs)
