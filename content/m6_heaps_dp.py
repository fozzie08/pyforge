from content.dsl import case, challenge_problem, exercise, gen, lesson, module

# ---------------------------------------------------------------------------
# Lesson 1 · Heaps
# ---------------------------------------------------------------------------

HEAPS = lesson(
    "heaps",
    "Heaps & Priority Queues",
    "Always get the smallest (or largest) item fast with heapq.",
    minutes=20,
    body="""
    A **heap** gives you its smallest item in O(1) and lets you add or remove items in O(log n). It's the data structure behind **priority queues**, which always serve the most urgent item next. Python's `heapq` module maintains a plain list as a **min-heap**.

    ```python
    import heapq

    heap = []
    for x in [5, 1, 8, 3, 9, 2]:
        heapq.heappush(heap, x)
    print(heap[0])                    # the smallest is always at index 0
    print(heapq.heappop(heap), heapq.heappop(heap), heapq.heappop(heap))
    print(heap)                       # not fully sorted, just heap-ordered
    ```

    The list isn't sorted. It only guarantees that each parent is at most its children, which is enough to keep the smallest at the front.

    ## Building a heap in one go

    ```python
    import heapq

    nums = [9, 4, 7, 1, 8, 2]
    heapq.heapify(nums)               # O(n), in place
    print(nums[0], nums)
    ```

    ## Max-heaps by negation

    `heapq` only does min-heaps. For the largest item, push negated values and negate again when you pop:

    ```python
    import heapq

    max_heap = []
    for x in [5, 1, 8, 3]:
        heapq.heappush(max_heap, -x)
    print(-heapq.heappop(max_heap), -heapq.heappop(max_heap))
    ```

    ## Priorities with tuples

    Tuples compare element by element, so `(priority, item)` pairs pop in priority order:

    ```python
    import heapq

    tasks = []
    heapq.heappush(tasks, (2, "write tests"))
    heapq.heappush(tasks, (1, "fix outage"))
    heapq.heappush(tasks, (3, "refactor"))
    while tasks:
        priority, name = heapq.heappop(tasks)
        print(priority, name)
    ```

    If two priorities can tie and the items themselves can't be compared (nodes, dicts, custom objects), add a unique tie-breaker in the middle: `(priority, counter, item)`.

    ## Keeping the top k

    To keep the `k` largest items from a stream, hold a **min-heap of size k**. Its smallest element is the bar for entry. Every new item goes in, and whenever the heap grows past `k`, the smallest is pushed back out. That costs O(n log k) time and O(k) memory.

    ```python
    import heapq

    def k_largest(nums, k):
        heap = []
        for x in nums:
            heapq.heappush(heap, x)
            if len(heap) > k:
                heapq.heappop(heap)      # drop the smallest of the k + 1
        return sorted(heap, reverse=True)

    print(k_largest([5, 12, 3, 8, 20, 1, 15], 3))
    print(heapq.nlargest(3, [5, 12, 3, 8, 20, 1, 15]))   # built-in shortcut
    ```

    ## Merging sorted sequences

    ```python
    import heapq

    print(list(heapq.merge([1, 4, 9], [2, 3, 10], [0, 11])))
    ```

    | Operation | Cost |
    |---|---|
    | peek at `heap[0]` | O(1) |
    | `heappush`, `heappop` | O(log n) |
    | `heapify(list)` | O(n) |
    | `nlargest(k, items)` / `nsmallest` | O(n log k) |

    > **Key idea:** if you repeatedly need the smallest or largest item while new items keep arriving, use a heap.
    """,
    exercises=[
        exercise(
            "k-smallest",
            "K Smallest",
            """
            Return the `k` smallest values in `nums`, sorted in ascending order. Duplicates count separately.
            """,
            """
            def k_smallest(nums: List[int], k: int) -> List[int]:
                heap = []
                for x in nums:
                    heapq.heappush(heap, -x)
                    if len(heap) > k:
                        heapq.heappop(heap)
                return sorted(-x for x in heap)
            """,
            examples=[case([7, 10, 4, 3, 20, 15], 3, out=[3, 4, 7]), case([5, 5, 5], 2, out=[5, 5])],
            tests=[case([1], 1, out=[1]), case([-1, -2], 2, out=[-2, -1]), case([9, 8, 7, 6], 1, out=[6]),
                   case(gen("rand_list(10**5, -10**9, 10**9, seed=61)"), 10)],
            constraints=["`1 <= k <= len(nums) <= 10⁵`"],
            hints=["Sorting everything works. Can you do it while only ever keeping `k` values?",
                   "Keep the `k` smallest so far in a **max**-heap (negate the values), so the largest of them is easy to evict."],
            explanation="""
            Keep a max-heap (negated values) of the `k` smallest items seen so far. When it grows to `k + 1`, pop its largest. What's left at the end are the `k` smallest, which we sort for the answer. `heapq.nsmallest(k, nums)` does the same.

            **Complexity:** O(n log k) time, O(k) memory.
            """,
        ),
        exercise(
            "last-stone",
            "Last Stone",
            """
            You have stones with the given weights. Each turn, take the **two heaviest** stones, with weights `x <= y`, and smash them together:

            - if `x == y`, both stones are destroyed
            - otherwise the `x` stone is destroyed and the other becomes weight `y - x`

            Continue until at most one stone is left. Return its weight, or `0` if none remain.
            """,
            """
            def last_stone(stones: List[int]) -> int:
                heap = [-s for s in stones]
                heapq.heapify(heap)
                while len(heap) > 1:
                    y = -heapq.heappop(heap)
                    x = -heapq.heappop(heap)
                    if y != x:
                        heapq.heappush(heap, -(y - x))
                return -heap[0] if heap else 0
            """,
            examples=[case([2, 7, 4, 1, 8, 1], out=1, why="8 and 7 leave 1. Then 4 and 2 leave 2, 2 and 1 leave 1, and 1 and 1 cancel, leaving 1."),
                      case([1], out=1)],
            tests=[case([2, 2], out=0), case([10, 4, 2, 10], out=2), case([3, 7, 2], out=2), case([1, 1, 1], out=1),
                   case(gen("rand_list(3 * 10**4, 1, 1000, seed=62)"))],
            constraints=["`1 <= len(stones) <= 3 × 10⁴`", "`1 <= stones[i] <= 1000`"],
            hints=["You repeatedly need the two largest items, and new items keep arriving.",
                   "Use a max-heap: negate the weights with `heapq`."],
            explanation="""
            Store negated weights in a heap so `heappop` returns the heaviest. Each turn pops two and pushes the difference if it's non-zero. Re-sorting the list every turn would cost O(n log n) per turn, so O(n² log n) overall.

            **Complexity:** O(n log n) time.
            """,
        ),
    ],
)

# ---------------------------------------------------------------------------
# Lesson 2 · Dynamic programming I
# ---------------------------------------------------------------------------

DP_1D = lesson(
    "dp-1d",
    "Dynamic Programming I",
    "Store answers to subproblems instead of recomputing them.",
    minutes=30,
    body="""
    **Dynamic programming** (DP) solves a problem by combining answers to smaller versions of it, and **stores** those answers so each is computed only once. It helps whenever the same smaller question would otherwise be asked again and again (**overlapping subproblems**).

    ## Why naive recursion is slow

    Fibonacci is defined by `fib(n) = fib(n - 1) + fib(n - 2)`. The direct recursion recomputes the same values an exponential number of times:

    ```python
    calls = 0

    def fib(n):
        global calls
        calls += 1
        if n < 2:
            return n
        return fib(n - 1) + fib(n - 2)

    print(fib(20), "took", calls, "calls")
    ```

    ## Fix 1: memoisation (top-down)

    Cache each answer the first time you compute it. `functools.lru_cache` does this in one line:

    ```python
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def fib(n):
        if n < 2:
            return n
        return fib(n - 1) + fib(n - 2)

    print(fib(90))
    ```

    Now each `fib(k)` is computed once, so it's O(n). It's still recursive, though, so very large `n` would hit the recursion limit.

    ## Fix 2: tabulation (bottom-up)

    Fill a table from the smallest subproblem upward, with no recursion at all:

    ```python
    def fib(n):
        if n < 2:
            return n
        dp = [0] * (n + 1)
        dp[1] = 1
        for i in range(2, n + 1):
            dp[i] = dp[i - 1] + dp[i - 2]
        return dp[n]

    print(fib(90))
    ```

    Each step only needs the previous two values, so two variables are enough:

    ```python
    def fib(n):
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a

    print(fib(90), fib(1000) % 1_000_000_007)
    ```

    ## The DP recipe

    1. **State:** say in words what `dp[i]` means, for example "the number of ways to reach step i".
    2. **Transition:** write how `dp[i]` is built from smaller states.
    3. **Base cases:** the smallest states, which you know directly.
    4. **Order:** compute states so everything `dp[i]` needs is already done.
    5. **Answer:** which state, or combination of states, answers the question.

    ## Worked example: climbing stairs

    You can climb 1 or 2 steps at a time. How many different ways reach step `n`?

    - State: `ways[i]` is the number of ways to reach step `i`.
    - Transition: the last move came from `i - 1` (a 1-step) or from `i - 2` (a 2-step), so `ways[i] = ways[i - 1] + ways[i - 2]`.
    - Base case: `ways[0] = 1`, the one way of standing still.

    ```python
    def climb(n):
        ways = [0] * (n + 1)
        ways[0] = 1
        for i in range(1, n + 1):
            ways[i] = ways[i - 1] + (ways[i - 2] if i >= 2 else 0)
        return ways[n]

    print([climb(n) for n in range(1, 11)])
    ```

    ## Choosing the best option

    Many DP problems take the best of several choices. Take the largest sum of a contiguous subarray. Let the state be "the best sum of a subarray **ending at** index i". At each element the choice is to extend the previous run or start fresh:

    ```python
    def max_subarray(nums):
        best_ending_here = best = nums[0]
        for x in nums[1:]:
            best_ending_here = max(x, best_ending_here + x)
            best = max(best, best_ending_here)
        return best

    print(max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]))   # 4 - 1 + 2 + 1
    ```

    States of the form "the best answer ending at position i" come up in DP problems again and again.

    > **Key idea:** define a state in words, write how it's built from smaller states, and fill the table in order. If a recursion recomputes things, memoise it.
    """,
    exercises=[
        exercise(
            "tribonacci",
            "Tribonacci",
            """
            The Tribonacci sequence is defined as `T(0) = 0`, `T(1) = 1`, `T(2) = 1`, and `T(n) = T(n - 1) + T(n - 2) + T(n - 3)` for `n >= 3`.

            Return `T(n)`.
            """,
            """
            def tribonacci(n: int) -> int:
                a, b, c = 0, 1, 1
                for _ in range(n):
                    a, b, c = b, c, a + b + c
                return a
            """,
            examples=[case(4, out=4, why="T(3) = 0 + 1 + 1 = 2, T(4) = 1 + 1 + 2 = 4"), case(25, out=1389537)],
            tests=[case(0, out=0), case(1, out=1), case(2, out=1), case(3, out=2), case(10, out=149),
                   case(37, out=2082876103)],
            constraints=["`0 <= n <= 37`"],
            hints=["Plain recursion makes about 3ⁿ calls. Far too many for n = 37.",
                   "Build the sequence upward, keeping only the last three values."],
            explanation="""
            Tabulate from the bottom, keeping a sliding set of three values. The tuple assignment `a, b, c = b, c, a + b + c` shifts the window in one step. Memoised recursion (`@lru_cache`) also works.

            **Complexity:** O(n) time, O(1) space.
            """,
        ),
        exercise(
            "cheapest-climb",
            "Cheapest Climb",
            """
            `cost[i]` is the price of stepping on stair `i`. Once you pay for a stair you can climb **one or two** stairs from it. You may start on stair `0` or stair `1` for free, meaning you haven't paid anything yet.

            Return the minimum total cost to reach the **top**, which is just past the last stair.
            """,
            """
            def min_cost_climb(cost: List[int]) -> int:
                two_back = one_back = 0
                for i in range(2, len(cost) + 1):
                    two_back, one_back = one_back, min(one_back + cost[i - 1], two_back + cost[i - 2])
                return one_back
            """,
            examples=[case([10, 15, 20], out=15, why="Start on stair 1, pay 15, and climb two stairs to the top."),
                      case([1, 100, 1, 1, 1, 100, 1, 1, 100, 1], out=6)],
            tests=[case([0, 0], out=0), case([5, 10], out=5), case([1, 2, 3], out=2), case([0, 1, 2, 2], out=2),
                   case(gen("rand_list(1000, 0, 999, seed=63)"))],
            constraints=["`2 <= len(cost) <= 1000`", "`0 <= cost[i] <= 999`"],
            hints=["Let `dp[i]` be the cheapest cost to **stand on** position `i` (not yet paid for). Then `dp[0] = dp[1] = 0`.",
                   "You arrive at `i` from `i - 1` (paying `cost[i - 1]`) or from `i - 2` (paying `cost[i - 2]`).",
                   "The top is position `len(cost)`."],
            explanation="""
            Let `dp[i]` be the minimum cost to arrive at position `i`. You got there by paying for stair `i - 1` or stair `i - 2`, so `dp[i] = min(dp[i - 1] + cost[i - 1], dp[i - 2] + cost[i - 2])`, with `dp[0] = dp[1] = 0` and the answer at `dp[n]`. Only the last two states are needed, so two variables replace the table.

            **Complexity:** O(n) time, O(1) space.
            """,
        ),
    ],
)

# ---------------------------------------------------------------------------
# Lesson 3 · Dynamic programming II
# ---------------------------------------------------------------------------

DP_2D = lesson(
    "dp-2d",
    "Dynamic Programming II",
    "Two-dimensional states: grids, pairs of strings and knapsacks.",
    minutes=30,
    body="""
    Some problems need a **2-D state**: a position in a grid, or a position in each of two strings.

    ## Counting grid paths

    A robot starts at the top-left of an `m × n` grid and can only move **right** or **down**. How many routes reach the bottom-right corner? Every cell is entered from above or from the left:

    `paths[r][c] = paths[r - 1][c] + paths[r][c - 1]`

    ```python
    m, n = 4, 5
    paths = [[1] * n for _ in range(m)]     # top row and left column: one way each
    for r in range(1, m):
        for c in range(1, n):
            paths[r][c] = paths[r - 1][c] + paths[r][c - 1]
    for row in paths:
        print(" ".join(f"{v:3}" for v in row))
    ```

    ## Cheapest path

    Same shape, but take the cheaper of the two ways in:

    ```python
    grid = [[1, 3, 1],
            [1, 5, 1],
            [4, 2, 1]]
    rows, cols = len(grid), len(grid[0])
    cost = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if r == 0 and c == 0:
                cost[r][c] = grid[r][c]
            elif r == 0:
                cost[r][c] = cost[r][c - 1] + grid[r][c]
            elif c == 0:
                cost[r][c] = cost[r - 1][c] + grid[r][c]
            else:
                cost[r][c] = min(cost[r - 1][c], cost[r][c - 1]) + grid[r][c]
    print(cost[-1][-1])       # 1 → 3 → 1 → 1 → 1
    ```

    ## Two strings: the prefix table

    To compare strings `a` and `b`, let `dp[i][j]` describe the first `i` characters of `a` and the first `j` characters of `b`. The table gets one extra row and column for the empty prefixes.

    For example, the longest **common substring** (contiguous). Let `dp[i][j]` be the length of the common run that ends exactly at `a[i - 1]` and `b[j - 1]`:

    ```python
    def longest_common_substring(a, b):
        dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
        best = 0
        for i in range(1, len(a) + 1):
            for j in range(1, len(b) + 1):
                if a[i - 1] == b[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                    best = max(best, dp[i][j])
        return best

    print(longest_common_substring("abcdxyz", "xyzabcd"))   # "abcd"
    ```

    When characters differ, the run is broken, so the cell stays `0`. For **subsequences**, which don't need to be contiguous, a mismatch would instead carry forward the best answer from dropping a character from one string or the other.

    ## Knapsack-style choices

    Each item is either taken or not. Can some of these numbers add up to exactly `target`? Let `can[s]` mean "sum `s` is reachable". For each number, update the sums **from high to low** so the same number isn't used twice:

    ```python
    def subset_sum(nums, target):
        can = [False] * (target + 1)
        can[0] = True
        for x in nums:
            for s in range(target, x - 1, -1):     # downward: each x used at most once
                if can[s - x]:
                    can[s] = True
        return can[target]

    print(subset_sum([3, 34, 4, 12, 5, 2], 9), subset_sum([3, 34, 4, 12, 5, 2], 30))
    ```

    Looping **upward** instead would let each item be reused any number of times. That's the right choice when supplies are unlimited, like coins.

    > **Key idea:** in a grid, `dp[r][c]` comes from the cell above and the cell to the left. For two strings, `dp[i][j]` describes the prefixes `a[:i]` and `b[:j]`.
    """,
    exercises=[
        exercise(
            "paths-with-obstacles",
            "Paths Around Obstacles",
            """
            A robot starts at the top-left of `grid` and wants to reach the bottom-right, moving only **right** or **down**. Cells containing `1` are obstacles, and `0` cells are free.

            Return the number of distinct routes. If the start or the end is blocked, the answer is `0`.
            """,
            """
            def paths_with_obstacles(grid: List[List[int]]) -> int:
                cols = len(grid[0])
                row = [0] * cols
                row[0] = 1
                for r in range(len(grid)):
                    for c in range(cols):
                        if grid[r][c] == 1:
                            row[c] = 0
                        elif c > 0:
                            row[c] += row[c - 1]
                return row[-1]
            """,
            examples=[case([[0, 0, 0], [0, 1, 0], [0, 0, 0]], out=2, why="Go around the centre obstacle either clockwise or anticlockwise."),
                      case([[0, 1], [0, 0]], out=1)],
            tests=[case([[1]], out=0), case([[0]], out=1), case([[0, 0], [0, 1]], out=0), case([[0, 0, 0, 0]], out=1),
                   case([[0], [1], [0]], out=0), case([[0, 0], [1, 0], [0, 0]], out=1),
                   case(gen("[[0] * 60 for _ in range(60)]")), case(gen("rand_grid(80, 80, [0, 0, 0, 0, 0, 0, 0, 1], seed=64)"))],
            constraints=["`1 <= rows, cols <= 100`", "`grid[r][c]` is 0 or 1"],
            hints=["Same recurrence as the lesson: paths into a cell come from above plus from the left.",
                   "An obstacle cell has 0 paths into it.",
                   "Careful with the first row and column: once blocked, everything after is unreachable."],
            explanation="""
            `paths[r][c] = paths[r - 1][c] + paths[r][c - 1]`, except obstacles are forced to 0. Starting with a single 1 at the origin and treating out-of-grid cells as 0 handles the first row and column automatically, including blocked edges. Each row depends only on the row above, so one list updated in place is enough: `row[c]` still holds the value from above when we add `row[c - 1]`, which is the value from the left.

            **Complexity:** O(rows × cols) time, O(cols) space.
            """,
        ),
        exercise(
            "lcs-length",
            "Longest Common Subsequence",
            """
            A **subsequence** keeps some characters of a string, in their original order, but not necessarily next to each other. For example, `"ace"` is a subsequence of `"abcde"`.

            Return the length of the longest subsequence that `a` and `b` have in common.
            """,
            """
            def lcs_length(a: str, b: str) -> int:
                prev = [0] * (len(b) + 1)
                for i in range(1, len(a) + 1):
                    cur = [0] * (len(b) + 1)
                    for j in range(1, len(b) + 1):
                        if a[i - 1] == b[j - 1]:
                            cur[j] = prev[j - 1] + 1
                        else:
                            cur[j] = max(prev[j], cur[j - 1])
                    prev = cur
                return prev[-1]
            """,
            examples=[case("abcde", "ace", out=3, why='"ace" appears in both.'), case("abc", "abc", out=3),
                      case("abc", "def", out=0)],
            tests=[case("a", "a", out=1), case("bsbininm", "jmjkbkjkv", out=1), case("oxcpqrsvwf", "shmtulqrypy", out=2),
                   case("ezupkr", "ubmrapg", out=2), case("pythonista", "typhoon"),
                   case(gen("rand_str(800, 'abcd', seed=65)"), gen("rand_str(800, 'abcd', seed=66)"))],
            constraints=["`1 <= len(a), len(b) <= 800`", "Both strings contain lower-case English letters"],
            hints=["Let `dp[i][j]` be the LCS length of `a[:i]` and `b[:j]`.",
                   "If `a[i - 1] == b[j - 1]`, that character extends the LCS of the shorter prefixes: `dp[i - 1][j - 1] + 1`.",
                   "Otherwise, drop the last character of one string or the other: `max(dp[i - 1][j], dp[i][j - 1])`."],
            explanation="""
            `dp[i][j]` is the LCS of the prefixes `a[:i]` and `b[:j]`. A match extends the diagonal, `dp[i - 1][j - 1] + 1`. A mismatch means one of the two last characters isn't used, so take the better of skipping either one. Each row only reads the previous row, so two rows are enough.

            **Complexity:** O(m × n) time, O(n) space.
            """,
        ),
    ],
)

# ---------------------------------------------------------------------------
# Challenge section 6
# ---------------------------------------------------------------------------

CHALLENGES = [
    challenge_problem(
        "neighbourhood-heist",
        "Neighbourhood Heist",
        """
        A row of houses holds `nums[i]` in valuables each. Neighbouring houses share an alarm system, so taking from **two adjacent houses** on the same night triggers it.

        Return the most you can collect without triggering an alarm.
        """,
        """
        class Solution:
            def rob(self, nums: List[int]) -> int:
                take, skip = 0, 0
                for x in nums:
                    take, skip = skip + x, max(take, skip)
                return max(take, skip)
        """,
        difficulty="Medium",
        tags=["Dynamic Programming", "Lists", "Tuples"],
        examples=[case([1, 2, 3, 1], out=4, why="Take houses 0 and 2: 1 + 3 = 4."),
                  case([2, 7, 9, 3, 1], out=12, why="Take houses 0, 2 and 4: 2 + 9 + 1 = 12.")],
        tests=[case([5], out=5), case([2, 1, 1, 2], out=4), case([0, 0], out=0), case([100, 1, 1, 100], out=200),
               case([1, 3, 1], out=3), case(gen("rand_list(10**4, 0, 400, seed=71)"))],
        constraints=["`1 <= len(nums) <= 10⁴`", "`0 <= nums[i] <= 400`"],
        hints=["At each house there are two choices: take it (so you skipped the previous one) or skip it.",
               "Let `best[i]` be the most you can collect from the first `i` houses. How does it relate to `best[i - 1]` and `best[i - 2]`?",
               "You only ever need the last two values."],
        explanation="""
        `best[i] = max(best[i - 1], best[i - 2] + nums[i])`: either skip house `i`, or take it on top of the best haul that ends two houses back. The solution tracks this as two running values. `take` is the best total if the current house is robbed, and `skip` is the best if it isn't.

        Trying every subset is O(2ⁿ). Memoised recursion or tabulation brings it to linear time.

        **Complexity:** O(n) time, O(1) space.
        """,
    ),
    challenge_problem(
        "fewest-coins",
        "Fewest Coins",
        """
        You have unlimited coins of each denomination in `coins`. Return the **fewest coins** needed to make exactly `amount`, or `-1` if it can't be done.
        """,
        """
        class Solution:
            def coinChange(self, coins: List[int], amount: int) -> int:
                INF = amount + 1
                dp = [0] + [INF] * amount
                for s in range(1, amount + 1):
                    for c in coins:
                        if c <= s and dp[s - c] + 1 < dp[s]:
                            dp[s] = dp[s - c] + 1
                return dp[amount] if dp[amount] != INF else -1
        """,
        difficulty="Medium",
        tags=["Dynamic Programming", "Lists", "Loops"],
        examples=[case([1, 2, 5], 11, out=3, why="11 = 5 + 5 + 1"), case([2], 3, out=-1), case([1], 0, out=0)],
        tests=[case([1], 1, out=1), case([2, 5, 10, 1], 27, out=4), case([186, 419, 83, 408], 6249, out=20),
               case([3, 7], 5, out=-1), case([1, 3, 4], 6, out=2), case([5, 10], 3, out=-1),
               case([1, 7, 23, 49], 10 ** 4), case([7, 13, 29, 101, 257], 9999)],
        constraints=["`1 <= len(coins) <= 12`", "`1 <= coins[i] <= 2³¹ - 1`", "`0 <= amount <= 10⁴`"],
        hints=["Greedy (always take the biggest coin) fails. Try coins `[1, 3, 4]` and amount 6.",
               "Let `dp[s]` be the fewest coins that make `s`. The last coin used was some `c`, leaving `s - c`.",
               "`dp[s] = 1 + min(dp[s - c])` over all coins `c <= s`, with `dp[0] = 0`."],
        explanation="""
        Build `dp[s]`, the fewest coins that make `s`, for every `s` from 0 up to `amount`. The last coin used is some `c`, so `dp[s] = 1 + min(dp[s - c])`. Unreachable amounts stay at the sentinel `amount + 1`, which is more coins than any real answer could need. Going upward means each coin can be reused, matching the unlimited supply.

        **Complexity:** O(amount × len(coins)) time, O(amount) space.
        """,
    ),
    challenge_problem(
        "closest-to-origin",
        "Closest to the Origin",
        """
        Given a list of `points` on a plane, where each point is `[x, y]`, and an integer `k`, return the `k` points closest to the origin `(0, 0)` by straight-line (Euclidean) distance.

        The answer is unique. Return the points in any order.
        """,
        """
        class Solution:
            def kClosest(self, points: List[List[int]], k: int) -> List[List[int]]:
                return heapq.nsmallest(k, points, key=lambda p: p[0] * p[0] + p[1] * p[1])
        """,
        difficulty="Medium",
        tags=["Heap", "Sorting", "Lambdas", "Math"],
        compare="unordered",
        examples=[case([[1, 3], [-2, 2], [4, 0]], 1, out=[[-2, 2]],
                       why="Squared distances are 10, 8 and 16. (-2, 2) is closest."),
                  case([[3, 3], [5, -1], [-2, 4], [0, 1]], 2, out=[[0, 1], [3, 3]])],
        tests=[case([[0, 0]], 1, out=[[0, 0]]), case([[1, 1], [2, 2], [3, 3]], 3, out=[[1, 1], [2, 2], [3, 3]]),
               case([[-5, 4], [4, 6], [2, -1]], 2, out=[[2, -1], [-5, 4]]),
               case(gen("[[i, 0] for i in range(50000, 0, -1)]"), 100),
               case(gen("[[i, -i] for i in range(10**4, 0, -1)]"), 5, out=[[5, -5], [4, -4], [3, -3], [2, -2], [1, -1]])],
        constraints=["`1 <= k <= len(points) <= 5 × 10⁴`", "`-10⁴ <= x, y <= 10⁴`"],
        hints=["You don't need the actual square root: comparing `x² + y²` gives the same order.",
               "Sorting by distance with a `key` works in O(n log n).",
               "A heap of size `k` (or `heapq.nsmallest`) does it in O(n log k)."],
        explanation="""
        Rank points by squared distance `x² + y²`. The square root doesn't change the order, and skipping it avoids floating-point error. Then take the `k` smallest: `sorted(points, key=...)[:k]` is O(n log n), and `heapq.nsmallest(k, points, key=...)` keeps only `k` candidates, which is O(n log k). Quickselect gives O(n) on average.

        **Complexity:** O(n log k) time, O(k) extra space.
        """,
    ),
    challenge_problem(
        "word-split",
        "Word Split",
        """
        Given a string `s` and a list of dictionary words `wordDict`, return `True` if `s` can be split into a sequence of one or more dictionary words, with no letters left over. Words may be reused any number of times.
        """,
        """
        class Solution:
            def wordBreak(self, s: str, wordDict: List[str]) -> bool:
                words = set(wordDict)
                lengths = {len(w) for w in words}
                ok = [True] + [False] * len(s)
                for i in range(1, len(s) + 1):
                    for size in lengths:
                        if size <= i and ok[i - size] and s[i - size:i] in words:
                            ok[i] = True
                            break
                return ok[len(s)]
        """,
        difficulty="Medium",
        tags=["Dynamic Programming", "Hash Set", "Strings"],
        examples=[case("sunflowerpot", ["sun", "flower", "pot", "flow"], out=True, why='"sun" + "flower" + "pot"'),
                  case("carpetsale", ["car", "pet", "sale", "carp", "ets"], out=True),
                  case("doghouses", ["dog", "house", "hou"], out=False, why='The final "s" can never be matched.')],
        tests=[case("a", ["a"], out=True), case("aaaaaaa", ["aaaa", "aaa"], out=True), case("abcd", ["a", "abc", "b", "cd"], out=True),
               case("cars", ["car", "ca", "rs"], out=True), case("ab", ["a"], out=False), case("goalspecial", ["go", "goal", "goals", "special"], out=True),
               case(gen("'a' * 150 + 'b'"), gen("['a' * i for i in range(1, 11)]"), out=False),
               case(gen("'ab' * 150"), gen("['a', 'b', 'ab', 'ba', 'aba', 'bab']"), out=True)],
        constraints=["`1 <= len(s) <= 300`", "`1 <= len(wordDict) <= 1000`", "`1 <= len(wordDict[i]) <= 20`"],
        hints=["Trying every split recursively explodes on inputs like `\"aaaa…ab\"`.",
               "Let `ok[i]` mean \"the first `i` characters can be split\". Then `ok[0]` is `True`.",
               "`ok[i]` is true if some dictionary word ends at `i` and `ok[i - len(word)]` is true. Use a set for O(1) word lookups."],
        explanation="""
        `ok[i]` is `True` when `s[:i]` splits into dictionary words. It holds if some word `w` matches the last `len(w)` characters of that prefix and `ok[i - len(w)]` is true. A set makes each substring check O(1) (plus slicing), and only word lengths that actually occur need trying. Plain recursion re-explores the same prefixes exponentially often, which the `"aaa…ab"` test exposes.

        **Complexity:** O(n × L × w) time, where L is the number of distinct word lengths and w is the longest word (for slicing). O(n) space.
        """,
    ),
    challenge_problem(
        "fewest-edits",
        "Fewest Edits",
        """
        Given two strings `word1` and `word2`, return the minimum number of single-character operations needed to turn `word1` into `word2`. The allowed operations are:

        - **insert** a character
        - **delete** a character
        - **replace** a character with another
        """,
        """
        class Solution:
            def minDistance(self, word1: str, word2: str) -> int:
                m, n = len(word1), len(word2)
                prev = list(range(n + 1))
                for i in range(1, m + 1):
                    cur = [i] + [0] * n
                    for j in range(1, n + 1):
                        if word1[i - 1] == word2[j - 1]:
                            cur[j] = prev[j - 1]
                        else:
                            cur[j] = 1 + min(prev[j], cur[j - 1], prev[j - 1])
                    prev = cur
                return prev[n]
        """,
        difficulty="Medium",
        tags=["Dynamic Programming", "Strings", "2-D Tables"],
        examples=[case("kitten", "sitting", out=3, why="Replace k→s, replace e→i, insert g."),
                  case("sunday", "saturday", out=3), case("", "abc", out=3)],
        tests=[case("a", "a", out=0), case("abc", "", out=3), case("intention", "execution", out=5), case("flaw", "lawn", out=2),
               case("python", "pythons", out=1), case("abcdef", "azced", out=3),
               case(gen("rand_str(300, 'abc', seed=72)"), gen("rand_str(280, 'abc', seed=73)"))],
        constraints=["`0 <= len(word1), len(word2) <= 300`", "Both strings contain lower-case English letters"],
        hints=["Let `dp[i][j]` be the edits needed to turn `word1[:i]` into `word2[:j]`.",
               "Base cases: turning a prefix into the empty string takes `i` deletions, and building `word2[:j]` from nothing takes `j` insertions.",
               "If the last characters match, `dp[i][j] = dp[i - 1][j - 1]`. Otherwise it's 1 plus the best of delete `dp[i - 1][j]`, insert `dp[i][j - 1]` and replace `dp[i - 1][j - 1]`."],
        explanation="""
        This is the classic **Levenshtein distance**. `dp[i][j]` is the answer for the prefixes `word1[:i]` and `word2[:j]`. When the last characters match, they cost nothing, so take `dp[i - 1][j - 1]`. Otherwise the last operation was one of three:

        - delete `word1[i - 1]`, costing `dp[i - 1][j] + 1`
        - insert `word2[j - 1]`, costing `dp[i][j - 1] + 1`
        - replace one with the other, costing `dp[i - 1][j - 1] + 1`

        The first row and column are `0, 1, 2, …`. Keeping only the previous row reduces memory to O(n).

        **Complexity:** O(m × n) time, O(n) space.
        """,
    ),
    challenge_problem(
        "merge-k-chains",
        "Merge K Sorted Chains",
        """
        You're given a list `lists` of `k` linked lists, each sorted in non-decreasing order. Merge them all into **one sorted linked list** and return its head.
        """,
        """
        class Solution:
            def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
                heap = []
                for i, node in enumerate(lists):
                    if node:
                        heapq.heappush(heap, (node.val, i, node))
                dummy = tail = ListNode()
                while heap:
                    _, i, node = heapq.heappop(heap)
                    tail.next = node
                    tail = node
                    if node.next:
                        heapq.heappush(heap, (node.next.val, i, node.next))
                return dummy.next
        """,
        difficulty="Hard",
        tags=["Heap", "Linked List", "Tuples", "Dummy Node"],
        examples=[case([[2, 5, 9], [1, 6], [3, 4, 10]], out=[1, 2, 3, 4, 5, 6, 9, 10]), case([], out=[]), case([[]], out=[])],
        tests=[case([[1], [0]], out=[0, 1]), case([[], [1, 1], []], out=[1, 1]), case([[-3, -1], [-2, 0, 2], []], out=[-3, -2, -1, 0, 2]),
               case([[5, 5], [5], [5, 5, 5]], out=[5, 5, 5, 5, 5, 5]),
               case(gen("[sorted(rand_list(20, -10**4, 10**4, seed=i)) for i in range(500)]")),
               case(gen("[sorted(rand_list(5, -10**4, 10**4, seed=1000 + i)) for i in range(2000)]"))],
        constraints=["`0 <= k <= 10⁴`", "Each list has at most 500 nodes, and there are at most 10⁴ nodes in total",
                     "Each list is sorted in non-decreasing order"],
        hints=["Repeatedly scanning all `k` list heads for the smallest costs O(k) per node.",
               "A min-heap of the current heads gives the smallest in O(log k).",
               "`ListNode`s can't be compared, so push `(value, list_index, node)`. The index breaks ties."],
        explanation="""
        Keep a min-heap holding the current head of every non-empty list. Pop the smallest, append it to the result, and push that node's successor. The heap never holds more than `k` entries, so each of the N nodes costs O(log k).

        Ties matter here. Python compares tuples element by element, and when two values are equal it would try to compare `ListNode`s, raising `TypeError`. A unique middle element, the list index, prevents that.

        An alternative is divide and conquer: merge the lists in pairs, as in merge sort. That's also O(N log k).

        **Complexity:** O(N log k) time, O(k) heap space.
        """,
    ),
    challenge_problem(
        "running-median",
        "Running Median",
        """
        Design a structure that receives numbers one at a time and can report the **median** of everything received so far.

        - `MedianFinder()` creates an empty structure.
        - `addNum(num)` adds a number.
        - `findMedian()` returns the median as a float. For an even count, that's the mean of the two middle values.

        `findMedian` is only called after at least one number has been added.
        """,
        """
        class MedianFinder:
            def __init__(self):
                self.low = []     # max-heap (negated) holding the smaller half
                self.high = []    # min-heap holding the larger half

            def addNum(self, num: int) -> None:
                heapq.heappush(self.low, -num)
                heapq.heappush(self.high, -heapq.heappop(self.low))
                if len(self.high) > len(self.low):
                    heapq.heappush(self.low, -heapq.heappop(self.high))

            def findMedian(self) -> float:
                if len(self.low) > len(self.high):
                    return float(-self.low[0])
                return (-self.low[0] + self.high[0]) / 2
        """,
        difficulty="Hard",
        tags=["Design", "Heap", "Classes"],
        examples=[case(["MedianFinder", "addNum", "addNum", "findMedian", "addNum", "findMedian", "addNum", "findMedian"],
                       [[], [5], [15], [], [1], [], [3], []], out=[None, None, None, 10.0, None, 5.0, None, 4.0],
                       why="Medians of [5, 15], [1, 5, 15] and [1, 3, 5, 15].")],
        tests=[case(["MedianFinder", "addNum", "findMedian"], [[], [-7], []], out=[None, None, -7.0]),
               case(["MedianFinder", "addNum", "addNum", "addNum", "findMedian"], [[], [2], [2], [2], []],
                    out=[None, None, None, None, 2.0]),
               case(["MedianFinder", "addNum", "addNum", "findMedian"], [[], [1], [2], []], out=[None, None, None, 1.5]),
               case(gen("['MedianFinder'] + ['addNum', 'findMedian'] * 20000"),
                    gen("[[]] + [x for v in rand_list(20000, -10**5, 10**5, seed=74) for x in ([v], [])]"))],
        constraints=["`-10⁵ <= num <= 10⁵`", "At most `4 × 10⁴` calls in total"],
        hints=["Sorting on every `findMedian` is O(n log n) per call. Too slow when calls alternate.",
               "Split the numbers into a lower half and an upper half. The median sits where they meet.",
               "Keep the lower half in a max-heap and the upper half in a min-heap, with sizes differing by at most one."],
        explanation="""
        Maintain two heaps: `low`, a max-heap of the smaller half (stored negated), and `high`, a min-heap of the larger half. Every element of `low` is at most every element of `high`, and `low` holds the same number of elements or one more.

        To add a number, push it into `low`, move `low`'s largest across to `high` (which restores the ordering), and if `high` is now bigger, move its smallest back. The median is `low`'s top when the total count is odd, or the mean of both tops when it's even.

        **Complexity:** O(log n) per `addNum`, O(1) per `findMedian`.
        """,
    ),
]

MODULE = module(
    "heaps-dp",
    "Heaps & Dynamic Programming",
    "Priority queues for always-the-best-next problems, and dynamic programming for problems built from overlapping subproblems.",
    lessons=[HEAPS, DP_1D, DP_2D],
    challenges=CHALLENGES,
    challenge_title="Grand Checkpoint · Everything Together",
    challenge_blurb="The final set: DP on lists and strings, heaps with linked lists, and a two-heap design problem. Each one draws on several modules.",
)
