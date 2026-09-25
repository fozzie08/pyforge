# PyForge

An interactive platform for learning Python, from first variables to dynamic programming.

1. **Learn:** each lesson explains a skill with examples you can run and edit in the page.
2. **Try it:** every lesson ends with practice exercises in a LeetCode-style editor.
3. **Prove it:** each module ends with a checkpoint of challenges that combine several skills from that module and earlier ones. The challenges are written in LeetCode's format and at its difficulty levels, and they're judged against hidden tests, including large inputs that catch slow solutions.

Everything runs in the browser. Python is [Pyodide](https://pyodide.org) (CPython compiled to WebAssembly), so there's no server, and nobody's code runs anywhere except on their own machine.

## Run it

```bash
cd pyforge
python3 -m http.server 8000 --directory site
```

Then open <http://localhost:8000>.

Or open **`dist/pyforge.html`** directly. It's a single self-contained file you can email or put on a USB stick. Either way, the first run needs an internet connection to download the Python runtime (about 10 MB, cached afterwards).

## What's inside

| Module | Lessons | Checkpoint |
|---|---|---|
| 1 · Python Foundations | Variables & operators, Strings, Conditionals & loops, Functions | 5 Easy |
| 2 · Core Data Structures | Lists, Dictionaries, Sets & tuples, Comprehensions & sorting | 3 Easy, 2 Medium |
| 3 · Algorithmic Patterns | Two pointers, Sliding window, Prefix sums, Binary search | 4 Medium, 1 Hard |
| 4 · Stacks, Queues & Recursion | Stacks, Queues & BFS, Recursion & backtracking | 1 Easy, 4 Medium |
| 5 · Objects, Linked Lists & Trees | Classes, Linked lists, Binary trees | 3 Easy, 3 Medium |
| 6 · Heaps & Dynamic Programming | Heaps, DP I, DP II | 5 Medium, 2 Hard |

That's 21 lessons with 120 runnable examples, 42 exercises, and 33 challenges (12 Easy, 18 Medium, 3 Hard). Challenge statements are original write-ups of classic interview problems.

## How judging works

- **Run** checks your code against the visible test cases. You can edit them or add your own in the Testcase tab. Expected answers for your own cases come from the reference solution.
- **Submit** runs every example plus the hidden tests and stops at the first failure, like LeetCode. The verdicts are `Accepted`, `Wrong Answer`, `Runtime Error` (showing only your own lines in the traceback), `Compile Error` and `Time Limit Exceeded`.
- **Time limits:** each test gets 2 seconds by default. The hidden tests include inputs of up to 100,000 elements, so an O(n²) solution to an O(n) problem times out. For example, the brute-force pair-sum solution times out on hidden test 8 of 9 after about 3.5 seconds.
- Starter code for challenges uses LeetCode's `class Solution:` format. `ListNode`, `TreeNode`, `List`, `Optional`, `deque`, `Counter`, `heapq` and the other names LeetCode provides are available without imports.
- Solutions unlock after you solve a problem. You can also reveal one early.

Progress, code and submissions are saved in your browser's local storage. Use **Progress → Export** to back them up or move them to another device.

## Adding lessons and problems

Content lives in `content/*.py` as plain Python. Each problem is defined by its **reference solution**. The build reads the solution's signature to generate starter code, runs the solution against every test, and refuses to build if anything fails.

```python
from content.dsl import case, challenge_problem, gen

challenge_problem(
    "max-profit",                       # unique id
    "Best Time to Sell",                # title
    """
    `prices[i]` is a stock's price on day `i`. Return the largest profit
    from buying on one day and selling on a later day, or `0`.
    """,
    """
    class Solution:
        def maxProfit(self, prices: List[int]) -> int:
            best, low = 0, float("inf")
            for p in prices:
                low = min(low, p)
                best = max(best, p - low)
            return best
    """,
    difficulty="Easy",                  # Easy / Medium / Hard
    tags=["Lists", "Loops"],            # skills it combines
    examples=[case([7, 1, 5, 3, 6, 4], out=5, why="Buy at 1, sell at 6.")],
    tests=[
        case([7, 6, 4, 3, 1], out=0),
        case(gen("rand_list(10**5, 0, 10**4, seed=1)")),   # expected computed from the solution
    ],
    constraints=["`1 <= len(prices) <= 10⁵`"],
    hints=["Track the lowest price seen so far."],
    explanation="One pass, remembering the minimum so far. **Complexity:** O(n).",
)
```

- `case(*args, out=..., why=...)` is one test. Leave out `out` to have it computed from the reference solution.
- `gen("...")` writes an input as a Python expression that's evaluated when the tests run. Use it for large inputs. The available helpers are `rand_list`, `rand_str`, `rand_grid` and `rand_sorted`.
- `compare=` can be `"unordered"` (any order), `"unordered_deep"` (a list of lists in any order), or `"inplace:0"` (the function mutates argument 0).
- Solutions can use plain functions (lesson exercises), `class Solution` (challenges), or any other class (design problems tested with `["Op", ...]` / `[[args], ...]` lists).
- Add a lesson with `lesson(...)` in a module file. Every ` ```python ` block in its markdown becomes a runnable example, and the build checks that each one runs.

Then rebuild:

```bash
python3 build.py
```

This validates everything under your local Python (3.9+) and writes `site/assets/content.js` and `dist/pyforge.html`.

## Project layout

```
pyforge/
├── build.py              validate content, then compile the site and single-file bundle
├── engine/harness.py     the judge; the same file runs in the browser and during the build
├── content/              curriculum: dsl.py helpers + one file per module
├── site/                 the static web app (index.html + assets/)
└── dist/pyforge.html     generated single-file version
```

## Sharing it

`site/` is a plain static website. To give other people a link, upload the folder to any static host, such as GitHub Pages, Netlify or Cloudflare Pages. No backend is needed. Or share `dist/pyforge.html` as a file.

## Credits

- [Pyodide](https://pyodide.org) (MPL-2.0) runs Python in the browser.
- [CodeMirror 5](https://codemirror.net/5/) (MIT) is the editor. Its base stylesheet is vendored in `site/assets/codemirror.css`.
- Fonts are Schibsted Grotesk, IBM Plex Sans and JetBrains Mono, via Google Fonts.
