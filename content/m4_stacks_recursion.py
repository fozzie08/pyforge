from content.dsl import case, challenge_problem, exercise, gen, lesson, module

# ---------------------------------------------------------------------------
# Lesson 1 · Stacks
# ---------------------------------------------------------------------------

STACKS = lesson(
    "stacks",
    "Stacks",
    "Last in, first out: undo, matching pairs and monotonic stacks.",
    minutes=20,
    body="""
    A **stack** is last-in, first-out (LIFO), like a pile of plates: you only ever touch the top. A Python list makes a perfect stack. `append` pushes, `pop` removes the top, and `stack[-1]` peeks, all in O(1).

    ```python
    stack = []
    stack.append("a")
    stack.append("b")
    stack.append("c")
    print(stack, "top:", stack[-1])
    print(stack.pop(), stack.pop())
    print(stack, "empty?", not stack)
    ```

    Reach for a stack when the **most recent unfinished thing must be handled first**: undo history, the browser's back button, nested structures, and the function call stack itself.

    ## Undo and backspace

    ```python
    def apply_edits(keys):
        stack = []
        for ch in keys:
            if ch == "#":             # '#' means backspace
                if stack:
                    stack.pop()
            else:
                stack.append(ch)
        return "".join(stack)

    print(apply_edits("ab#c##d"))
    ```

    ## Matching pairs

    Each opener waits on the stack until its closer arrives, and the closer must match the **most recent** unmatched opener.

    ```python
    def tags_balanced(tags):
        stack = []
        for tag in tags:
            if not tag.startswith("/"):
                stack.append(tag)
            elif not stack or stack.pop() != tag[1:]:
                return False
        return not stack              # anything left open is an error too

    print(tags_balanced(["html", "body", "/body", "/html"]))
    print(tags_balanced(["b", "i", "/b", "/i"]))
    ```

    ## Evaluating expressions

    In postfix notation, `3 4 + 2 *` means `(3 + 4) * 2`. Numbers are pushed. An operator pops two values and pushes the result.

    ```python
    def eval_postfix(tokens):
        stack = []
        for tok in tokens:
            if tok in ("+", "-", "*"):
                b = stack.pop()
                a = stack.pop()
                if tok == "+":
                    stack.append(a + b)
                elif tok == "-":
                    stack.append(a - b)
                else:
                    stack.append(a * b)
            else:
                stack.append(int(tok))
        return stack[0]

    print(eval_postfix("3 4 + 2 *".split()))
    print(eval_postfix("5 1 2 + 4 * + 3 -".split()))
    ```

    ## Monotonic stacks

    A **monotonic stack** keeps its contents in sorted order by popping anything that would break the order before pushing. It answers "what's the nearest bigger (or smaller) element?" for **every** position in O(n) total.

    ```python
    def previous_smaller(nums):
        result = []
        stack = []          # increasing from bottom to top
        for x in nums:
            while stack and stack[-1] >= x:
                stack.pop()    # can never be the answer for anything after x
            result.append(stack[-1] if stack else None)
            stack.append(x)
        return result

    print(previous_smaller([4, 10, 5, 8, 20, 15, 3, 12]))
    ```

    It looks like a nested loop, but each value is pushed once and popped at most once, so the total work is O(n).

    > **Key idea:** a stack holds unfinished business in reverse order. A monotonic stack finds the next or previous greater or smaller element in O(n).
    """,
    exercises=[
        exercise(
            "remove-adjacent-pairs",
            "Remove Adjacent Pairs",
            """
            Given a string `s` of lower-case letters, repeatedly delete any two **adjacent, equal** letters until no such pair remains. Return the final string. The result is the same whatever order you delete pairs in.
            """,
            """
            def remove_pairs(s: str) -> str:
                stack = []
                for ch in s:
                    if stack and stack[-1] == ch:
                        stack.pop()
                    else:
                        stack.append(ch)
                return "".join(stack)
            """,
            examples=[case("abbaca", out="ca", why='Remove "bb" to get "aaca", then remove "aa" to get "ca".'),
                      case("azxxzy", out="ay")],
            tests=[case("a", out="a"), case("aa", out=""), case("aaa", out="a"), case("abccba", out=""),
                   case("abcd", out="abcd"), case(gen("rand_str(10**5, 'ab', seed=31)")),
                   case(gen("'ab' * 25000 + 'ba' * 25000"), out="")],
            constraints=["`1 <= len(s) <= 10⁵`", "`s` has lower-case English letters"],
            hints=["Process letters left to right, keeping the letters that survive so far on a stack.",
                   "If the new letter equals the top of the stack, the two cancel out."],
            explanation="""
            The stack holds the current reduced string. A new letter either cancels the top, when they're equal, or is pushed. Cancelling can expose an earlier letter that then matches the next one, which the stack handles automatically. Repeatedly scanning the string for pairs would be O(n²).

            **Complexity:** O(n) time and space.
            """,
        ),
        exercise(
            "next-greater",
            "Next Greater Element",
            """
            For every element of `nums`, find the first element to its **right** that is strictly greater. Return a list of those values, using `-1` where no greater element exists.
            """,
            """
            def next_greater(nums: List[int]) -> List[int]:
                result = [-1] * len(nums)
                stack = []
                for i, x in enumerate(nums):
                    while stack and nums[stack[-1]] < x:
                        result[stack.pop()] = x
                    stack.append(i)
                return result
            """,
            examples=[case([2, 1, 2, 4, 3], out=[4, 2, 4, -1, -1]), case([1, 2, 3], out=[2, 3, -1])],
            tests=[case([3, 2, 1], out=[-1, -1, -1]), case([5], out=[-1]), case([1, 1, 1], out=[-1, -1, -1]),
                   case([1, 3, 2, 4], out=[3, 4, 4, -1]), case(gen("list(range(10**5, 0, -1))")),
                   case(gen("rand_list(10**5, 0, 10**9, seed=32)"))],
            constraints=["`1 <= len(nums) <= 10⁵`", "`0 <= nums[i] <= 10⁹`"],
            hints=["Keep a stack of indexes that are still waiting for their next greater element.",
                   "When a new value arrives, it answers every waiting index whose value is smaller. Pop them."],
            explanation="""
            Scan left to right with a stack of indexes still waiting for an answer. Their values are non-increasing from bottom to top. A new value `x` pops, and answers, every waiting index with a smaller value, then waits itself. Each index is pushed and popped once, so it's O(n) instead of the O(n²) of scanning right from every element.

            **Complexity:** O(n) time and space.
            """,
        ),
    ],
)

# ---------------------------------------------------------------------------
# Lesson 2 · Queues & BFS
# ---------------------------------------------------------------------------

QUEUES = lesson(
    "queues-bfs",
    "Queues & Breadth-First Search",
    "First in, first out with deque, and exploring graphs layer by layer.",
    minutes=25,
    body="""
    A **queue** is first-in, first-out (FIFO), like a line at a shop. Use `collections.deque`: `append` adds to the back and `popleft` removes from the front, both O(1). A list's `pop(0)` is O(n) because every other item shifts along.

    ```python
    from collections import deque

    queue = deque()
    queue.append("first")
    queue.append("second")
    queue.append("third")
    print(queue.popleft(), queue.popleft())
    print(queue, len(queue))

    d = deque([1, 2, 3, 4, 5])
    d.appendleft(0)
    d.rotate(2)            # move the last 2 items to the front
    print(d)
    d.rotate(-3)           # move the first 3 items to the back
    print(d)
    ```

    ## Simulating a line

    Round-robin scheduling: each task gets up to 2 units of work, then goes to the back of the line.

    ```python
    from collections import deque

    tasks = deque([("A", 3), ("B", 5), ("C", 1)])
    time = 0
    while tasks:
        name, remaining = tasks.popleft()
        work = min(2, remaining)
        time += work
        if remaining > work:
            tasks.append((name, remaining - work))
        else:
            print(f"{name} finished at t={time}")
    ```

    ## Breadth-first search (BFS)

    BFS explores outward from a start in **layers**: everything 1 step away, then everything 2 steps away, and so on. A queue enforces that order, and a `visited` set prevents going round in circles. Because layers are processed in order, **the first time BFS reaches something is along a shortest path**, as long as every step costs the same.

    ```python
    from collections import deque

    friends = {
        "ana": ["ben", "cai"],
        "ben": ["ana", "dev"],
        "cai": ["ana", "dev"],
        "dev": ["ben", "cai", "eli"],
        "eli": ["dev"],
    }

    def degrees_apart(graph, start, goal):
        queue = deque([(start, 0)])
        visited = {start}
        while queue:
            person, dist = queue.popleft()
            if person == goal:
                return dist
            for friend in graph[person]:
                if friend not in visited:
                    visited.add(friend)
                    queue.append((friend, dist + 1))
        return -1

    print(degrees_apart(friends, "ana", "eli"))
    ```

    ## BFS on a grid

    A grid is a graph in disguise: each cell's neighbours are the cells above, below, left and right. A list of direction offsets keeps the code tidy.

    ```python
    from collections import deque

    grid = ["S.#.",
            "..#.",
            "...E"]
    rows, cols = len(grid), len(grid[0])
    DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    queue = deque([(0, 0, 0)])        # row, col, distance
    seen = {(0, 0)}
    while queue:
        r, c, d = queue.popleft()
        if grid[r][c] == "E":
            print("reached E in", d, "steps")
            break
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != "#" and (nr, nc) not in seen:
                seen.add((nr, nc))
                queue.append((nr, nc, d + 1))
    ```

    Mark a cell as visited **when you add it to the queue**, not when you pop it. Otherwise the same cell can be queued many times.

    ## Several starting points at once

    To measure distance from the *nearest* of several sources, put **all** of them in the queue at distance 0 before you begin. This is called multi-source BFS. The layers then spread from every source simultaneously.

    ```python
    from collections import deque

    line = [0, 0, 1, 0, 0, 0, 1, 0]          # 1 = a shop
    dist = [None] * len(line)
    queue = deque()
    for i, x in enumerate(line):
        if x == 1:
            dist[i] = 0
            queue.append(i)
    while queue:
        i = queue.popleft()
        for j in (i - 1, i + 1):
            if 0 <= j < len(line) and dist[j] is None:
                dist[j] = dist[i] + 1
                queue.append(j)
    print(dist)                               # distance to the nearest shop
    ```

    > **Key idea:** use `deque` for queues. BFS is a queue plus a visited set, and it finds shortest paths in unweighted graphs and grids.
    """,
    exercises=[
        exercise(
            "last-player",
            "Last Player Standing",
            """
            `n` players numbered `1` to `n` stand in a circle. Starting from player 1, count `k` players clockwise, including the one you start on. The `k`-th player leaves the circle, and counting starts again from the next player. This repeats until one player remains.

            Return the number of the last player.
            """,
            """
            def last_player(n: int, k: int) -> int:
                circle = deque(range(1, n + 1))
                while len(circle) > 1:
                    circle.rotate(-(k - 1))
                    circle.popleft()
                return circle[0]
            """,
            examples=[case(5, 2, out=3, why="Players leave in the order 2, 4, 1, 5, leaving player 3."),
                      case(6, 5, out=1)],
            tests=[case(1, 1, out=1), case(7, 3, out=4), case(10, 1, out=10), case(2, 2, out=1),
                   case(500, 500), case(500, 7)],
            constraints=["`1 <= k <= n <= 500`"],
            hints=["Put the players in a `deque`. The front of the deque is where counting starts.",
                   "Moving `k - 1` players from the front to the back puts the `k`-th player at the front.",
                   "`deque.rotate(-m)` moves `m` items from the front to the back."],
            explanation="""
            Model the circle as a deque whose front is the current counting position. Rotating left by `k - 1` moves the skipped players to the back, which brings the `k`-th player to the front, where `popleft` removes them. The next player is now at the front, ready for the next round.

            **Complexity:** O(n · k) time. There is also an O(n) mathematical recurrence, the Josephus problem.
            """,
        ),
        exercise(
            "minutes-to-spread",
            "Minutes to Spread",
            """
            A grid of cells holds:

            - `0`: an empty cell
            - `1`: a healthy plant
            - `2`: an infected plant

            Every minute, each infected plant infects the healthy plants directly above, below, left and right of it.

            Return the number of minutes until no healthy plants remain. If some healthy plant can never be reached, return `-1`.
            """,
            """
            def minutes_to_spread(grid: List[List[int]]) -> int:
                rows, cols = len(grid), len(grid[0])
                queue = deque()
                healthy = 0
                for r in range(rows):
                    for c in range(cols):
                        if grid[r][c] == 2:
                            queue.append((r, c, 0))
                        elif grid[r][c] == 1:
                            healthy += 1
                minutes = 0
                while queue:
                    r, c, t = queue.popleft()
                    minutes = max(minutes, t)
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                            grid[nr][nc] = 2
                            healthy -= 1
                            queue.append((nr, nc, t + 1))
                return minutes if healthy == 0 else -1
            """,
            examples=[
                case([[2, 1, 1], [1, 1, 0], [0, 1, 1]], out=4),
                case([[2, 1, 1], [0, 1, 1], [1, 0, 1]], out=-1, why="The plant in the bottom-left corner is cut off."),
                case([[0, 2]], out=0, why="There are no healthy plants to begin with."),
            ],
            tests=[case([[0]], out=0), case([[1]], out=-1), case([[2, 2], [1, 1]], out=1),
                   case([[1, 2, 1, 1, 2, 1, 1]], out=2), case([[2], [1], [1], [1], [1]], out=4),
                   case(gen("rand_grid(200, 200, [0, 1, 1, 1, 1, 2], seed=33)")),
                   case(gen("[[2] + [1] * 199] + [[1] * 200 for _ in range(199)]"), out=398)],
            constraints=["`1 <= rows, cols <= 200`", "`grid[r][c]` is 0, 1 or 2"],
            hints=["Every infected plant spreads at the same time. That's multi-source BFS.",
                   "Queue every `2` at time 0 and count the healthy plants.",
                   "Each time you infect a plant, decrease the healthy count. If it isn't 0 at the end, return -1."],
            explanation="""
            Start a BFS from **all** infected plants at once, with each queue entry carrying the minute it was infected. Infecting a neighbour marks it `2` immediately so it's never queued twice. The last minute processed is the answer, provided every healthy plant got infected, which the counter tracks.

            **Complexity:** O(rows × cols) time and space.
            """,
        ),
    ],
)

# ---------------------------------------------------------------------------
# Lesson 3 · Recursion & backtracking
# ---------------------------------------------------------------------------

RECURSION = lesson(
    "recursion",
    "Recursion & Backtracking",
    "Solve problems in terms of smaller copies of themselves.",
    minutes=30,
    body="""
    A **recursive** function calls itself on a smaller version of the same problem. Every recursive function needs:

    1. a **base case** that is answered directly, and
    2. a **recursive case** that moves toward the base case.

    ```python
    def factorial(n):
        if n <= 1:                    # base case
            return 1
        return n * factorial(n - 1)   # smaller problem

    print(factorial(5))
    ```

    ## Trust the recursion

    Assume the recursive call already works for the smaller input, and think only about how to use its answer.

    ```python
    def total(nums):
        if not nums:
            return 0
        return nums[0] + total(nums[1:])

    def count_down(n):
        if n == 0:
            print("liftoff!")
            return
        print(n, end=" ")
        count_down(n - 1)

    print(total([4, 8, 15, 16, 23, 42]))
    count_down(5)
    ```

    ## The call stack

    Each call waits for the call it made to finish, and Python stacks them up. By default Python stops at around 1000 nested calls with a `RecursionError`. For very deep problems, a loop with your own stack or queue is safer.

    ```python
    def depth(n):
        if n == 0:
            return 0
        return 1 + depth(n - 1)

    print(depth(500))
    ```

    ## Halving the problem

    Fast exponentiation halves the exponent at each step, using `xⁿ = (x^(n/2))²`. That makes about log₂(n) calls instead of n.

    ```python
    def power(x, n):
        if n == 0:
            return 1
        half = power(x, n // 2)
        return half * half if n % 2 == 0 else half * half * x

    print(power(2, 10), power(3, 13))
    ```

    ## Nested data

    Recursion fits naturally when data contains smaller copies of itself:

    ```python
    def deep_sum(item):
        if isinstance(item, int):
            return item
        return sum(deep_sum(x) for x in item)

    print(deep_sum([1, [2, [3, 4]], [[5]]]))
    ```

    ## Backtracking

    **Backtracking** builds a candidate solution one choice at a time and **undoes** each choice after exploring it, so it systematically tries every possibility.

    ```text
    def backtrack(partial):
        if partial is complete:
            record a copy of it
            return
        for each available choice:
            make the choice          # e.g. current.append(x)
            backtrack(partial)       # explore
            undo the choice          # current.pop()
    ```

    Every ordering of some letters (permutations):

    ```python
    def orderings(letters):
        results, current = [], []
        used = [False] * len(letters)

        def backtrack():
            if len(current) == len(letters):
                results.append("".join(current))
                return
            for i, ch in enumerate(letters):
                if not used[i]:
                    used[i] = True
                    current.append(ch)
                    backtrack()
                    current.pop()
                    used[i] = False

        backtrack()
        return results

    print(orderings("abc"))
    ```

    Choosing `k` items (combinations). Each call only picks from index `start` onward, so items stay in order and no combination repeats:

    ```python
    def choose(items, k):
        results = []

        def backtrack(start, current):
            if len(current) == k:
                results.append(current[:])     # copy, because current keeps changing
                return
            for i in range(start, len(items)):
                current.append(items[i])
                backtrack(i + 1, current)
                current.pop()

        backtrack(0, [])
        return results

    print(choose([1, 2, 3, 4], 2))
    ```

    `results.append(current[:])` stores a **copy**. Appending `current` itself would store the same list object many times, and it's empty by the end.

    **Pruning** means abandoning a branch as soon as it can't lead to a valid answer. It's what makes backtracking fast enough in practice.

    > **Key idea:** recursion is a base case plus a call on a smaller input. Backtracking is choose, explore, un-choose.
    """,
    exercises=[
        exercise(
            "flatten",
            "Flatten a Nested List",
            """
            `nested` is a list whose items are either integers or other lists, which can themselves contain integers or lists, to any depth.

            Return a flat list of all the integers, in the order they appear.
            """,
            """
            def flatten(nested: list) -> List[int]:
                result = []
                for item in nested:
                    if isinstance(item, list):
                        result.extend(flatten(item))
                    else:
                        result.append(item)
                return result
            """,
            examples=[case([1, [2, [3, 4]], [[5]]], out=[1, 2, 3, 4, 5]), case([], out=[])],
            tests=[case([[[]]], out=[]), case([1, 2, 3], out=[1, 2, 3]), case([[1], [2], [[3]]], out=[1, 2, 3]),
                   case([[[[[[7]]]]]], out=[7]), case([0, [-1, [2]], [], [[-3, [4, []]]]], out=[0, -1, 2, -3, 4])],
            constraints=["Nesting depth is at most 50", "At most 10⁴ integers in total"],
            hints=["`isinstance(item, list)` tells you whether to recurse.",
                   "Flatten each inner list with a recursive call, then add its items to your result with `extend`."],
            explanation="""
            Integers go straight into the result. For a list, trust the recursion to flatten it and extend the result with whatever comes back. The base case is implicit: a list with no nested lists makes no recursive calls.

            **Complexity:** O(total items × depth) with this approach. Passing a single shared result list down through the calls brings it to O(total items).
            """,
        ),
        exercise(
            "no-adjacent-ones",
            "Binary Strings Without Adjacent Ones",
            """
            Return every binary string of length `n` (made of `'0'` and `'1'`) that never has two `'1'`s next to each other, in **lexicographic** (dictionary) order.
            """,
            """
            def no_adjacent_ones(n: int) -> List[str]:
                results = []

                def backtrack(current):
                    if len(current) == n:
                        results.append(current)
                        return
                    backtrack(current + "0")
                    if not current or current[-1] != "1":
                        backtrack(current + "1")

                backtrack("")
                return results
            """,
            examples=[case(1, out=["0", "1"]), case(3, out=["000", "001", "010", "100", "101"])],
            tests=[case(2, out=["00", "01", "10"]), case(4), case(10), case(16)],
            constraints=["`1 <= n <= 16`"],
            hints=["Build the string one character at a time with backtracking.",
                   "You can always add `'0'`. You can add `'1'` only if the last character isn't `'1'`.",
                   "Trying `'0'` before `'1'` produces the strings in lexicographic order automatically."],
            explanation="""
            Backtrack over positions. `'0'` is always allowed, and `'1'` only when the previous character isn't `'1'`. That check **prunes** invalid branches before they grow. Exploring `'0'` first yields results already sorted. The number of valid strings grows like the Fibonacci numbers (2584 for n = 16).

            **Complexity:** O(F(n) · n) where F is Fibonacci.
            """,
        ),
    ],
)

# ---------------------------------------------------------------------------
# Challenge section 4
# ---------------------------------------------------------------------------

CHALLENGES = [
    challenge_problem(
        "balanced-brackets",
        "Balanced Brackets",
        """
        Given a string `s` containing only the characters `'('`, `')'`, `'['`, `']'`, `'{'` and `'}'`, decide whether it is **balanced**:

        - every opening bracket is closed by the same type of bracket,
        - brackets close in the correct order, and
        - every closing bracket has a matching opening bracket before it.
        """,
        """
        class Solution:
            def isValid(self, s: str) -> bool:
                pairs = {")": "(", "]": "[", "}": "{"}
                stack = []
                for ch in s:
                    if ch in pairs:
                        if not stack or stack.pop() != pairs[ch]:
                            return False
                    else:
                        stack.append(ch)
                return not stack
        """,
        difficulty="Easy",
        tags=["Stack", "Hash Map", "Strings"],
        examples=[case("()", out=True), case("()[]{}", out=True), case("(]", out=False), case("([])", out=True)],
        tests=[case("(", out=False), case(")", out=False), case("([)]", out=False), case("{[]}", out=True),
               case("((", out=False), case("){", out=False), case("[({})]", out=True), case("]", out=False),
               case(gen("'(' * 50000 + ')' * 50000"), out=True), case(gen("'()' * 50000 + '('"), out=False),
               case(gen("'([{' * 20000 + '}])' * 20000"), out=True)],
        constraints=["`1 <= len(s) <= 10⁵`", "`s` contains only `()[]{}`"],
        hints=["The most recently opened bracket must be closed first. Which data structure gives you the most recent item?",
               "A dict mapping each closer to its opener keeps the check short.",
               "Don't forget brackets left open at the end."],
        explanation="""
        Push every opening bracket onto a stack. For a closing bracket, the top of the stack must be its partner. If the stack is empty or the top doesn't match, the string is unbalanced. At the end the stack must be empty, otherwise something was never closed.

        **Complexity:** O(n) time, O(n) space.
        """,
    ),
    challenge_problem(
        "warmer-days-ahead",
        "Warmer Days Ahead",
        """
        `temperatures[i]` is the temperature on day `i`. Return a list `answer` where `answer[i]` is the number of days you have to wait after day `i` for a **strictly warmer** day. If no warmer day comes, `answer[i]` is `0`.
        """,
        """
        class Solution:
            def dailyTemperatures(self, temperatures: List[int]) -> List[int]:
                answer = [0] * len(temperatures)
                stack = []
                for i, t in enumerate(temperatures):
                    while stack and temperatures[stack[-1]] < t:
                        j = stack.pop()
                        answer[j] = i - j
                    stack.append(i)
                return answer
        """,
        difficulty="Medium",
        tags=["Monotonic Stack", "Lists", "enumerate"],
        examples=[case([73, 74, 75, 71, 69, 72, 76, 73], out=[1, 1, 4, 2, 1, 1, 0, 0]),
                  case([30, 40, 50, 60], out=[1, 1, 1, 0]), case([30, 60, 90], out=[1, 1, 0])],
        tests=[case([50], out=[0]), case([70, 70, 70], out=[0, 0, 0]), case([90, 80, 70, 100], out=[3, 2, 1, 0]),
               case([55, 38, 53, 81, 61, 93, 97, 32, 43, 78]),
               case(gen("[99] * 99999 + [100]")), case(gen("rand_list(10**5, 30, 100, seed=34)"))],
        constraints=["`1 <= len(temperatures) <= 10⁵`", "`30 <= temperatures[i] <= 100`"],
        hints=["For each day, you want the next greater element to its right, and how far away it is.",
               "Keep a stack of days still waiting for a warmer day. Store indexes, not temperatures, so you can compute distances.",
               "When a warmer day arrives, pop every waiting day it satisfies."],
        explanation="""
        This is "next greater element", recording the distance instead of the value. Keep a stack of indexes whose warmer day hasn't arrived yet. Their temperatures are non-increasing from bottom to top. Each new day pops every colder waiting day and fills in `i - j`. Days never popped keep the default `0`.

        **Complexity:** O(n) time, because each index is pushed and popped at most once. O(n) space.
        """,
    ),
    challenge_problem(
        "every-subset",
        "Every Subset",
        """
        Given a list of **distinct** integers `nums`, return all possible **subsets** (the power set), including the empty set and `nums` itself.

        The result must not contain duplicate subsets. Return them in any order.
        """,
        """
        class Solution:
            def subsets(self, nums: List[int]) -> List[List[int]]:
                result = []
                current = []

                def backtrack(start):
                    result.append(current[:])
                    for i in range(start, len(nums)):
                        current.append(nums[i])
                        backtrack(i + 1)
                        current.pop()

                backtrack(0)
                return result
        """,
        difficulty="Medium",
        tags=["Backtracking", "Recursion", "Lists"],
        compare="unordered_deep",
        examples=[case([1, 2, 3], out=[[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]),
                  case([0], out=[[], [0]])],
        tests=[case([5, -5], out=[[], [5], [-5], [5, -5]]), case([-1, 0, 1, 2]),
               case([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]), case([9, 4, 7, 1, 8, 3, 2, 6, 5, 0])],
        constraints=["`1 <= len(nums) <= 10`", "`-10 <= nums[i] <= 10`", "All values in `nums` are distinct"],
        hints=["Each element is either in a subset or not, so there are 2ⁿ subsets.",
               "With backtracking, record the current subset at **every** call, not just at the leaves.",
               "Only choose elements at or after `start`, so each subset is built in one order and never repeats."],
        explanation="""
        Backtrack as in the "choose k" example, but record `current[:]` on **every** call, because every partial selection is itself a valid subset. Picking only from index `start` onward means each subset is generated exactly once, in increasing index order.

        A loop-based alternative starts from `[[]]` and, for each number, appends a copy of every existing subset with that number added.

        **Complexity:** O(n · 2ⁿ) time and output space.
        """,
    ),
    challenge_problem(
        "island-count",
        "Island Count",
        """
        You're given a map `grid` of `"1"` (land) and `"0"` (water). An **island** is a group of land cells connected horizontally or vertically. Diagonals don't count. Everything outside the grid is water.

        Return the number of islands.
        """,
        """
        class Solution:
            def numIslands(self, grid: List[List[str]]) -> int:
                rows, cols = len(grid), len(grid[0])
                count = 0
                for r in range(rows):
                    for c in range(cols):
                        if grid[r][c] == "1":
                            count += 1
                            grid[r][c] = "0"
                            queue = deque([(r, c)])
                            while queue:
                                cr, cc = queue.popleft()
                                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                                    nr, nc = cr + dr, cc + dc
                                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == "1":
                                        grid[nr][nc] = "0"
                                        queue.append((nr, nc))
                return count
        """,
        difficulty="Medium",
        tags=["BFS", "Grids", "Sets"],
        examples=[
            case([["1", "1", "0", "0"], ["1", "0", "0", "1"], ["0", "0", "1", "1"], ["0", "0", "0", "0"]], out=2),
            case([["1", "0", "1", "0", "1"], ["0", "1", "0", "1", "0"]], out=5, why="Diagonal neighbours aren't connected."),
            case([["0"]], out=0),
        ],
        tests=[case([["1"]], out=1), case([["1", "1"], ["1", "1"]], out=1), case([["1", "0", "1"]], out=2),
               case([["1"], ["0"], ["1"], ["1"]], out=2),
               case([["1", "1", "1"], ["0", "1", "0"], ["1", "1", "1"]], out=1),
               case(gen("rand_grid(120, 120, ['0', '0', '0', '1', '1'], seed=35)")),
               case(gen("[['1'] * 30 for _ in range(30)]"), out=1),
               case(gen("[[str((r + c) % 2) for c in range(100)] for r in range(100)]"), out=5000)],
        constraints=["`1 <= rows, cols <= 120`", "`grid[r][c]` is `\"0\"` or `\"1\"`"],
        hints=["Scan every cell. Each time you find unvisited land, you've found a new island.",
               "From that cell, BFS (or DFS) to every connected land cell and mark them visited, for example by setting them to `\"0\"`.",
               "The number of times you start a new search is the answer."],
        explanation="""
        Scan the grid. Each unvisited `"1"` starts a new island, so count it, then flood-fill the whole island with BFS, turning its cells to `"0"` so they're never counted again. The number of flood fills equals the number of islands.

        A recursive DFS also works, but on large islands it can exceed Python's recursion limit (about 1000 nested calls). BFS with a queue has no such limit.

        **Complexity:** O(rows × cols) time. O(rows × cols) space in the worst case for the queue.
        """,
    ),
    challenge_problem(
        "bracket-builder",
        "Bracket Builder",
        """
        Given `n`, return every string of `n` pairs of parentheses that is **well-formed**: every `'('` is closed by a later `')'` and no `')'` appears without a matching `'('` before it.

        Return the strings in any order.
        """,
        """
        class Solution:
            def generateParenthesis(self, n: int) -> List[str]:
                result = []

                def backtrack(current, opened, closed):
                    if len(current) == 2 * n:
                        result.append(current)
                        return
                    if opened < n:
                        backtrack(current + "(", opened + 1, closed)
                    if closed < opened:
                        backtrack(current + ")", opened, closed + 1)

                backtrack("", 0, 0)
                return result
        """,
        difficulty="Medium",
        tags=["Backtracking", "Recursion", "Strings"],
        compare="unordered",
        examples=[case(3, out=["((()))", "(()())", "(())()", "()(())", "()()()"]), case(1, out=["()"])],
        tests=[case(2, out=["(())", "()()"]), case(4), case(6), case(8)],
        constraints=["`1 <= n <= 8`"],
        hints=["Generating all 2²ⁿ strings and filtering works for small n, but you can do better by never building an invalid prefix.",
               "At any point you may add `'('` if you've used fewer than `n`, and `')'` if there are unmatched `'('`s.",
               "Track how many of each you've placed."],
        explanation="""
        Backtrack while keeping counts of opened and closed brackets. `'('` is allowed while `opened < n`. `')'` is allowed while `closed < opened`, so a closer never lacks a partner. Every complete string built this way is well-formed, and no time is wasted on invalid prefixes.

        The number of results is the n-th **Catalan number**: 1, 2, 5, 14, 42, … (1430 for n = 8).

        **Complexity:** O(Cₙ · n) time, where Cₙ is the Catalan number.
        """,
    ),
]

MODULE = module(
    "stacks-recursion",
    "Stacks, Queues & Recursion",
    "Process things in the right order with stacks and queues, and break problems into smaller copies of themselves.",
    lessons=[STACKS, QUEUES, RECURSION],
    challenges=CHALLENGES,
    challenge_title="Checkpoint 4 · Stacks & Recursion",
    challenge_blurb="Stacks, BFS on grids and backtracking, each paired with hash maps, strings or lists.",
)
