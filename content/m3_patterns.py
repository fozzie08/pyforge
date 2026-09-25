from content.dsl import case, challenge_problem, exercise, gen, lesson, module

# ---------------------------------------------------------------------------
# Lesson 1 · Two pointers
# ---------------------------------------------------------------------------

TWO_POINTERS = lesson(
    "two-pointers",
    "Two Pointers",
    "Walk two indexes through the data to replace nested loops.",
    minutes=20,
    body="""
    Many list and string problems can be solved in a single pass by moving **two indexes** through the data instead of trying every pair. That turns O(n²) into O(n).

    ## Pattern 1: from both ends toward the middle

    ```python
    def is_palindrome(s):
        left, right = 0, len(s) - 1
        while left < right:
            if s[left] != s[right]:
                return False
            left += 1
            right -= 1
        return True

    print(is_palindrome("racecar"), is_palindrome("rocket"))
    ```

    Swapping the ends and moving inward also reverses a list without making a copy:

    ```python
    chars = list("hello")
    left, right = 0, len(chars) - 1
    while left < right:
        chars[left], chars[right] = chars[right], chars[left]
        left += 1
        right -= 1
    print(chars)
    ```

    ## Pair sums in a sorted list

    When the list is **sorted**, the sum of the two ends tells you which pointer to move:

    - sum too small: move `left` right, toward bigger numbers
    - sum too big: move `right` left, toward smaller numbers

    ```python
    def find_pair(nums, target):
        left, right = 0, len(nums) - 1
        steps = 0
        while left < right:
            steps += 1
            total = nums[left] + nums[right]
            if total == target:
                return nums[left], nums[right], f"{steps} steps"
            if total < target:
                left += 1
            else:
                right -= 1
        return None

    print(find_pair([1, 3, 4, 6, 8, 11, 15], 14))
    print(find_pair([1, 2, 3], 100))
    ```

    This is safe because, when the sum is too small, `nums[left]` can't be part of any answer. Even paired with the largest remaining number it falls short, so we can discard it.

    ## Pattern 2: a read pointer and a write pointer

    Walking a "read" index and a "write" index in the same direction filters a list **in place** without extra memory.

    ```python
    def remove_duplicates_sorted(nums):
        if not nums:
            return 0
        write = 1
        for read in range(1, len(nums)):
            if nums[read] != nums[read - 1]:
                nums[write] = nums[read]
                write += 1
        return write

    data = [1, 1, 2, 3, 3, 3, 7]
    k = remove_duplicates_sorted(data)
    print(k, data[:k])

    nums = [0, 1, 0, 3, 12]      # move zeroes to the end, keeping order
    write = 0
    for read in range(len(nums)):
        if nums[read] != 0:
            nums[write], nums[read] = nums[read], nums[write]
            write += 1
    print(nums)
    ```

    ## Pattern 3: one pointer per list

    Merging two sorted lists: compare the fronts and always take the smaller one.

    ```python
    def merge_sorted(a, b):
        i = j = 0
        out = []
        while i < len(a) and j < len(b):
            if a[i] <= b[j]:
                out.append(a[i])
                i += 1
            else:
                out.append(b[j])
                j += 1
        return out + a[i:] + b[j:]

    print(merge_sorted([1, 4, 9], [2, 3, 10, 11]))
    ```

    ## Modifying a list in place

    Some problems ask you to **change the input list in place** and return nothing. The judge then checks the list itself. Rebinding the parameter (`nums = ...`) doesn't touch the caller's list. You have to mutate it with index or slice assignment.

    ```python
    def double_all(nums):
        for i in range(len(nums)):
            nums[i] *= 2

    def broken(nums):
        nums = [x * 2 for x in nums]   # only rebinds the local name

    data = [1, 2, 3]
    double_all(data)
    print(data)
    broken(data)
    print(data)          # unchanged by broken()
    ```

    > **Key idea:** if brute force checks every pair, see whether sorted order or a read/write split lets two pointers do it in one pass.
    """,
    exercises=[
        exercise(
            "reverse-in-place",
            "Reverse In Place",
            """
            Reverse the list of characters `chars` **in place**: modify the list you're given and return nothing. Use only O(1) extra memory.

            The judge checks `chars` after your function returns, so `return chars[::-1]` won't count.
            """,
            """
            def reverse_in_place(chars: List[str]) -> None:
                left, right = 0, len(chars) - 1
                while left < right:
                    chars[left], chars[right] = chars[right], chars[left]
                    left += 1
                    right -= 1
            """,
            compare="inplace:0",
            examples=[case(["h", "e", "l", "l", "o"], out=["o", "l", "l", "e", "h"]),
                      case(["H", "a", "n", "n", "a", "h"], out=["h", "a", "n", "n", "a", "H"])],
            tests=[case(["a"], out=["a"]), case(["a", "b"], out=["b", "a"]), case(["x", "y", "z"], out=["z", "y", "x"]),
                   case(gen("list(rand_str(10**5, seed=1))"))],
            constraints=["`1 <= len(chars) <= 10⁵`"],
            hints=["Swap the first and last characters, then the second and second-to-last, and so on.",
                   "Python swaps in one line: `a[i], a[j] = a[j], a[i]`.",
                   "Stop when the pointers meet."],
            explanation="""
            Put one pointer at each end, swap the two characters, and step both inward until they meet. Each swap fixes two positions, so it takes n/2 swaps and no extra list. (`chars.reverse()` or `chars[:] = chars[::-1]` also mutate in place.)

            **Complexity:** O(n) time, O(1) extra space.
            """,
        ),
        exercise(
            "pair-sum-sorted",
            "Pair Sum in a Sorted List",
            """
            `nums` is sorted in non-decreasing order. Return the indices `[i, j]` with `i < j` such that `nums[i] + nums[j] == target`. Exactly one such pair exists.

            Aim for O(1) extra memory: no dicts or sets.
            """,
            """
            def pair_sum_sorted(nums: List[int], target: int) -> List[int]:
                left, right = 0, len(nums) - 1
                while left < right:
                    total = nums[left] + nums[right]
                    if total == target:
                        return [left, right]
                    if total < target:
                        left += 1
                    else:
                        right -= 1
                return []
            """,
            examples=[case([2, 7, 11, 15], 9, out=[0, 1]),
                      case([1, 3, 4, 6, 8, 11], 10, out=[2, 3], why="4 + 6 = 10"),
                      case([-3, -1, 0, 2, 6], 3, out=[0, 4])],
            tests=[case([1, 2], 3, out=[0, 1]), case([-5, -3, -1, 0], -8, out=[0, 1]), case([0, 0, 3, 4], 0, out=[0, 1]),
                   case([1, 2, 3, 4, 4, 9, 56, 90], 8, out=[3, 4]),
                   case(gen("list(range(0, 100000, 2)) + [10**9, 10**9 + 1]"), 2 * 10 ** 9 + 1, out=[50000, 50001])],
            constraints=["`2 <= len(nums) <= 10⁵`", "`nums` is sorted in non-decreasing order", "Exactly one answer exists"],
            hints=["Start with `left = 0` and `right = len(nums) - 1`.",
                   "If the sum is too small, which pointer should move to make it bigger?"],
            explanation="""
            Because the list is sorted, `nums[left] + nums[right]` tells us which way to go. Too small means `nums[left]` can't pair with anything remaining, so advance `left`. Too big means `nums[right]` is useless, so retreat `right`. Every step discards one candidate, so the pair is found in at most n steps.

            **Complexity:** O(n) time, O(1) space.
            """,
        ),
    ],
)

# ---------------------------------------------------------------------------
# Lesson 2 · Sliding window
# ---------------------------------------------------------------------------

SLIDING_WINDOW = lesson(
    "sliding-window",
    "Sliding Window",
    "Track the best contiguous range while scanning once.",
    minutes=25,
    body="""
    A **window** is a contiguous stretch of a list or string, such as `nums[left:right + 1]`. Sliding window problems ask for the best window: the largest sum of `k` elements, the longest substring with some property, and so on.

    Recomputing every window from scratch costs O(n·k). **Sliding** the window costs O(n): add the element that enters and remove the one that leaves.

    ## Fixed-size window

    ```python
    def max_sum_of_k(nums, k):
        window = sum(nums[:k])
        best = window
        for right in range(k, len(nums)):
            window += nums[right]        # element entering
            window -= nums[right - k]    # element leaving
            best = max(best, window)
        return best

    print(max_sum_of_k([2, 1, 5, 1, 3, 2], 3))
    ```

    ```text
    [2 1 5] 1 3 2    sum 8
     2 [1 5 1] 3 2   sum 7   (+1 −2)
     2 1 [5 1 3] 2   sum 9   (+3 −1)
     2 1 5 [1 3 2]   sum 6   (+2 −5)
    ```

    ## Variable-size window

    When the size isn't fixed, **grow** the window by advancing `right`, and **shrink** it from `left` whenever it breaks the rule. Each index enters once and leaves at most once, so the whole scan is O(n) even with the inner `while`.

    ```python
    def longest_with_sum_at_most(nums, limit):
        left = window = best = 0
        for right, x in enumerate(nums):
            window += x
            while window > limit:          # too big: shrink from the left
                window -= nums[left]
                left += 1
            best = max(best, right - left + 1)
        return best

    print(longest_with_sum_at_most([3, 1, 2, 1, 1, 4, 1], 5))
    ```

    ## Tracking what's inside with a dict

    To know *what's* in the window (distinct characters, counts), keep a dict updated as elements enter and leave:

    ```python
    def longest_with_k_distinct(s, k):
        counts = {}
        left = best = 0
        for right, ch in enumerate(s):
            counts[ch] = counts.get(ch, 0) + 1
            while len(counts) > k:
                gone = s[left]
                counts[gone] -= 1
                if counts[gone] == 0:
                    del counts[gone]
                left += 1
            best = max(best, right - left + 1)
        return best

    print(longest_with_k_distinct("eceba", 2))   # "ece"
    print(longest_with_k_distinct("aabbcc", 1))
    ```

    ## The template

    ```text
    left = 0
    for right in range(len(data)):
        add data[right] to the window
        while the window breaks the rule:
            remove data[left] from the window
            left += 1
        update the answer using the window data[left : right + 1]
    ```

    > **Key idea:** a problem about a *contiguous* subarray or substring that asks for the longest, shortest or best one is usually a sliding window.
    """,
    exercises=[
        exercise(
            "max-window-sum",
            "Best Window Sum",
            """
            Return the largest sum of any `k` **consecutive** elements of `nums`.
            """,
            """
            def max_window_sum(nums: List[int], k: int) -> int:
                window = sum(nums[:k])
                best = window
                for right in range(k, len(nums)):
                    window += nums[right] - nums[right - k]
                    best = max(best, window)
                return best
            """,
            examples=[case([2, 1, 5, 1, 3, 2], 3, out=9, why="5 + 1 + 3 = 9"), case([5], 1, out=5)],
            tests=[case([-1, -2, -3], 2, out=-3), case([1, 2, 3, 4], 4, out=10), case([4, -1, 2, 1], 2, out=3),
                   case([0, 0, 0, 7], 1, out=7), case(gen("rand_list(10**5, -10**4, 10**4, seed=4)"), 50000)],
            constraints=["`1 <= k <= len(nums) <= 10⁵`", "`-10⁴ <= nums[i] <= 10⁴`"],
            hints=["Compute the first window's sum once.",
                   "Moving the window one step adds `nums[right]` and removes `nums[right - k]`.",
                   "Sums can be negative, so start `best` from the first window rather than 0."],
            explanation="""
            Keep the current window's sum and update it in O(1) per step: add the entering element, subtract the leaving one. Re-summing each window would be O(n·k), about 2.5 × 10⁹ operations for the large test.

            **Complexity:** O(n) time, O(1) space.
            """,
        ),
        exercise(
            "shortest-subarray",
            "Shortest Subarray Reaching Target",
            """
            Given a list of **positive** integers `nums` and a positive integer `target`, return the length of the shortest contiguous subarray whose sum is **at least** `target`. If there is none, return `0`.
            """,
            """
            def shortest_subarray(nums: List[int], target: int) -> int:
                left = window = 0
                best = len(nums) + 1
                for right, x in enumerate(nums):
                    window += x
                    while window >= target:
                        best = min(best, right - left + 1)
                        window -= nums[left]
                        left += 1
                return best if best <= len(nums) else 0
            """,
            examples=[case([2, 3, 1, 2, 4, 3], 7, out=2, why="[4, 3] has sum 7 and length 2."),
                      case([1, 4, 4], 4, out=1), case([1, 1, 1, 1, 1, 1, 1, 1], 11, out=0)],
            tests=[case([1, 2, 3, 4, 5], 11, out=3), case([5], 5, out=1), case([1, 2, 3, 4, 5], 15, out=5),
                   case([10, 2, 3], 6, out=1), case(gen("[1] * 10**5"), 10 ** 5, out=100000),
                   case(gen("rand_list(10**5, 1, 10**4, seed=6)"), 10 ** 7)],
            constraints=["`1 <= len(nums) <= 10⁵`", "`1 <= nums[i] <= 10⁴`", "`1 <= target <= 10⁹`"],
            hints=["All numbers are positive, so growing the window always increases the sum and shrinking decreases it.",
                   "Once the window reaches the target, record its length, then shrink from the left while it still does."],
            explanation="""
            Extend `right` until the window sum reaches `target`, then shrink from `left` as far as possible, recording each valid length. Because every number is positive, shrinking only lowers the sum, so a window that stops being valid can't become valid again without adding elements. Each index enters and leaves once.

            **Complexity:** O(n) time, O(1) space.
            """,
        ),
    ],
)

# ---------------------------------------------------------------------------
# Lesson 3 · Prefix sums
# ---------------------------------------------------------------------------

PREFIX_SUMS = lesson(
    "prefix-sums",
    "Prefix Sums",
    "Precompute running totals so every range sum is O(1).",
    minutes=20,
    body="""
    A **prefix sum** list stores running totals: `prefix[i]` is the sum of the first `i` elements. Building it takes O(n). After that, the sum of any range is one subtraction, which is O(1).

    ```python
    from itertools import accumulate

    nums = [3, 1, 4, 1, 5, 9, 2]
    prefix = [0]
    for x in nums:
        prefix.append(prefix[-1] + x)
    print(prefix)

    # sum of nums[i..j] (inclusive) = prefix[j + 1] - prefix[i]
    i, j = 2, 5
    print(sum(nums[i:j + 1]), prefix[j + 1] - prefix[i])

    print(list(accumulate(nums, initial=0)))    # the same, built in
    ```

    Starting with `prefix[0] = 0`, one element longer than `nums`, removes the special case for ranges that begin at index 0.

    ```text
    nums     =    3  1  4  1   5   9   2
    prefix   = 0  3  4  8  9  14  23  25
    sum(nums[2..5]) = prefix[6] - prefix[2] = 23 - 4 = 19
    ```

    Answering `q` range questions directly costs O(n·q). With a prefix list it's O(n + q).

    ## Left side vs right side

    A running total plus the overall total tells you the sums on both sides of any position in one pass:

    ```python
    nums = [2, 3, -1, 8, 4]
    total = sum(nums)
    left = 0
    for i, x in enumerate(nums):
        right = total - left - x
        print(f"index {i}: left sum {left}, right sum {right}")
        left += x
    ```

    ## Prefix sums + a set: finding a range with a given total

    If the same running total appears twice, the elements between those two points must sum to **zero**. More generally, the range between two prefixes sums to `current - earlier`. Remembering earlier prefixes in a set or dict lets you find such ranges in a single pass:

    ```python
    def has_zero_sum_range(nums):
        seen = {0}
        running = 0
        for x in nums:
            running += x
            if running in seen:
                return True
            seen.add(running)
        return False

    print(has_zero_sum_range([4, 2, -3, 1, 6]))   # 2 + (-3) + 1 = 0
    print(has_zero_sum_range([1, 2, 3]))
    ```

    This works with negative numbers, unlike a sliding window, which needs every value positive so that growing the window always increases the sum.

    > **Key idea:** pay O(n) once for running totals and every range sum becomes O(1). Store earlier prefixes in a set or dict to find ranges with a particular total.
    """,
    exercises=[
        exercise(
            "range-sums",
            "Range Sum Queries",
            """
            You're given a list `nums` and a list of `queries`, where each query `[left, right]` asks for the sum of `nums[left]` through `nums[right]` inclusive.

            Return a list with the answer to each query, in order. There can be as many queries as elements, so answer each one in O(1).
            """,
            """
            def range_sums(nums: List[int], queries: List[List[int]]) -> List[int]:
                prefix = [0]
                for x in nums:
                    prefix.append(prefix[-1] + x)
                return [prefix[r + 1] - prefix[l] for l, r in queries]
            """,
            examples=[case([3, 1, 4, 1, 5, 9, 2], [[0, 2], [2, 5], [6, 6]], out=[8, 19, 2])],
            tests=[case([5], [[0, 0]], out=[5]), case([-1, 2, -3], [[0, 2], [1, 1], [0, 1]], out=[-2, 2, 1]),
                   case([1, 2, 3, 4], [], out=[]),
                   case(gen("rand_list(10**5, -10**4, 10**4, seed=12)"), gen("[[0, 99999]] * 10**5")),
                   case(gen("rand_list(10**5, -10**4, 10**4, seed=13)"),
                        gen("[sorted(p) for p in rand_grid(10**5, 2, range(10**5), seed=14)]"))],
            constraints=["`1 <= len(nums) <= 10⁵`", "`0 <= len(queries) <= 10⁵`", "`0 <= left <= right < len(nums)`"],
            hints=["Build `prefix` with `prefix[0] = 0` and `prefix[i + 1] = prefix[i] + nums[i]`.",
                   "The sum of `nums[l..r]` is `prefix[r + 1] - prefix[l]`."],
            explanation="""
            Build the prefix list once in O(n). Each query is then a single subtraction, `prefix[r + 1] - prefix[l]`. Summing each range directly could cost 10⁵ × 10⁵ = 10¹⁰ additions in the worst case.

            **Complexity:** O(n + q) time, O(n) extra space.
            """,
        ),
        exercise(
            "balance-index",
            "Balance Index",
            """
            The **balance index** of `nums` is an index where the sum of all elements strictly to its left equals the sum of all elements strictly to its right. (At the edges, the empty side sums to `0`.)

            Return the **leftmost** balance index, or `-1` if there is none.
            """,
            """
            def balance_index(nums: List[int]) -> int:
                total = sum(nums)
                left = 0
                for i, x in enumerate(nums):
                    if left == total - left - x:
                        return i
                    left += x
                return -1
            """,
            examples=[case([1, 7, 3, 6, 5, 6], out=3, why="Left of index 3: 1 + 7 + 3 = 11. Right: 5 + 6 = 11."),
                      case([1, 2, 3], out=-1),
                      case([2, 1, -1], out=0, why="Left of index 0 is empty (0). Right: 1 + (-1) = 0.")],
            tests=[case([0], out=0), case([1], out=0), case([-1, -1, -1, 0, 1, 1], out=0), case([1, -1], out=-1),
                   case([0, 0, 0], out=0), case([3, 1, 2], out=-1), case([1, 2, 3, 4, 6], out=3),
                   case(gen("rand_list(10**5, -1000, 1000, seed=17)"))],
            constraints=["`1 <= len(nums) <= 10⁵`", "`-1000 <= nums[i] <= 1000`"],
            hints=["Compute the total once.", "Right sum = total − left sum − nums[i]."],
            explanation="""
            With the total known, the right-hand sum at index `i` is `total - left - nums[i]`, so one pass keeping a running `left` sum checks every index in O(1). Recomputing both sides for every index would be O(n²).

            **Complexity:** O(n) time, O(1) space.
            """,
        ),
    ],
)

# ---------------------------------------------------------------------------
# Lesson 4 · Binary search
# ---------------------------------------------------------------------------

BINARY_SEARCH = lesson(
    "binary-search",
    "Binary Search",
    "Halve the search space each step: O(log n).",
    minutes=25,
    body="""
    **Binary search** finds a target in a *sorted* list by repeatedly halving the range that could contain it. Each step throws away half the candidates, so a million items need only about 20 steps. That's O(log n).

    ```python
    def binary_search(nums, target):
        lo, hi = 0, len(nums) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if nums[mid] == target:
                return mid
            if nums[mid] < target:
                lo = mid + 1         # target can only be to the right
            else:
                hi = mid - 1         # target can only be to the left
        return -1

    data = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
    print(binary_search(data, 23), binary_search(data, 7))
    ```

    ```text
    target 23 in [2 5 8 12 16 23 38 56 72 91]
    lo=0 hi=9 mid=4 → 16 < 23, go right
    lo=5 hi=9 mid=7 → 56 > 23, go left
    lo=5 hi=6 mid=5 → 23 found at index 5
    ```

    ## Finding a boundary

    Often you want the **first position** where something becomes true, for example the first index with `nums[i] >= target`. That is also where `target` would be inserted to keep the list sorted.

    ```python
    def lower_bound(nums, target):
        lo, hi = 0, len(nums)        # hi = len(nums) means "insert at the end"
        while lo < hi:
            mid = (lo + hi) // 2
            if nums[mid] < target:
                lo = mid + 1
            else:
                hi = mid             # mid might be the answer, so keep it
        return lo

    data = [1, 3, 3, 3, 5, 8]
    print(lower_bound(data, 3), lower_bound(data, 4), lower_bound(data, 100))
    ```

    The `bisect` module has these built in:

    ```python
    from bisect import bisect_left, bisect_right, insort

    data = [1, 3, 3, 3, 5, 8]
    print(bisect_left(data, 3))    # first index with value >= 3
    print(bisect_right(data, 3))   # first index with value > 3
    print(bisect_right(data, 3) - bisect_left(data, 3), "copies of 3")
    insort(data, 4)                # insert and keep it sorted
    print(data)
    ```

    ## Binary search on the answer

    Binary search works on any **yes/no question whose answer flips once**, not just lists. If "is `x` big enough?" goes no, no, no, yes, yes as `x` grows, you can binary search for the first yes.

    ```python
    def cube_root_ceil(n):
        lo, hi = 0, n
        while lo < hi:
            mid = (lo + hi) // 2
            if mid ** 3 >= n:
                hi = mid
            else:
                lo = mid + 1
        return lo

    print(cube_root_ceil(27), cube_root_ceil(28), cube_root_ceil(10 ** 18))
    ```

    ## Avoiding off-by-one bugs

    - Decide whether `hi` is inclusive or exclusive and keep it consistent.
    - Every iteration must shrink the range, or the loop never ends. With `while lo < hi`, write `lo = mid + 1`, never `lo = mid`.
    - Test lists of length 0, 1 and 2, and targets smaller and larger than everything.

    > **Key idea:** sorted data, or a yes/no question that flips exactly once, means binary search in O(log n).
    """,
    exercises=[
        exercise(
            "insert-positions",
            "Insert Positions",
            """
            `nums` is sorted in non-decreasing order. For each value in `queries`, find the index where it would be inserted to keep `nums` sorted. If equal values already exist, use the position **before** them (the leftmost).

            Return the list of positions. There can be 10⁵ queries, so each one needs to be O(log n).
            """,
            """
            def insert_positions(nums: List[int], queries: List[int]) -> List[int]:
                def lower_bound(target):
                    lo, hi = 0, len(nums)
                    while lo < hi:
                        mid = (lo + hi) // 2
                        if nums[mid] < target:
                            lo = mid + 1
                        else:
                            hi = mid
                    return lo
                return [lower_bound(q) for q in queries]
            """,
            examples=[case([1, 3, 5, 6], [5, 2, 7, 0], out=[2, 1, 4, 0],
                           why="5 is already at index 2. 2 goes between 1 and 3. 7 goes at the end. 0 goes at the start.")],
            tests=[case([], [3], out=[0]), case([2, 2, 2], [2, 1, 3], out=[0, 0, 3]), case([1], [1, 0, 2], out=[0, 0, 1]),
                   case([-5, 0, 5], [-5, -4, 4, 5, 6], out=[0, 1, 2, 2, 3]),
                   case(gen("sorted(rand_list(10**5, -10**6, 10**6, seed=15))"),
                        gen("rand_list(10**5, -10**6 - 10, 10**6 + 10, seed=16)"))],
            constraints=["`0 <= len(nums), len(queries) <= 10⁵`", "`nums` is sorted in non-decreasing order"],
            hints=["This is the lower bound search from the lesson.",
                   "Use `hi = len(nums)` so a query larger than everything returns `len(nums)`.",
                   "`bisect.bisect_left` does exactly this, but try writing the loop yourself first."],
            explanation="""
            Each query is a lower bound search: the first index whose value is `>= q`. Keeping `hi` exclusive (starting at `len(nums)`) naturally handles queries bigger than every element. A linear scan per query would be O(n·q), about 10¹⁰ steps on the large test.

            **Complexity:** O(q log n).
            """,
        ),
        exercise(
            "integer-sqrt",
            "Integer Square Root",
            """
            Given a non-negative integer `x`, return the largest integer `r` with `r * r <= x`, which is √x rounded down.

            Don't use `**`, `math.sqrt` or `math.isqrt`. Floating-point square roots also give wrong answers for very large `x`.
            """,
            """
            def integer_sqrt(x: int) -> int:
                lo, hi = 0, x
                while lo < hi:
                    mid = (lo + hi + 1) // 2
                    if mid * mid <= x:
                        lo = mid
                    else:
                        hi = mid - 1
                return lo
            """,
            examples=[case(4, out=2), case(8, out=2, why="√8 ≈ 2.83, which rounds down to 2.")],
            tests=[case(0, out=0), case(1, out=1), case(2, out=1), case(15, out=3), case(16, out=4),
                   case(2147395599, out=46339), case(2 ** 31 - 1, out=46340), case(10 ** 18, out=10 ** 9),
                   case(10 ** 18 - 1, out=999999999)],
            constraints=["`0 <= x <= 10¹⁸`"],
            hints=["Is `mid * mid <= x` a yes/no question that flips once as `mid` grows?",
                   "You're looking for the **last** yes. Round `mid` up with `(lo + hi + 1) // 2` so `lo = mid` always makes progress."],
            explanation="""
            `r * r <= x` is true for small `r` and false beyond the answer, so binary search for the last true. When the update is `lo = mid`, compute `mid` rounding **up**. Otherwise `lo = mid` can repeat forever once `hi = lo + 1`.

            Why not `int(x ** 0.5)`? Floats carry about 16 significant digits, and for `x = 10¹⁸ − 1` the float square root rounds to exactly `1e9`, which is one too big. Integer arithmetic is always exact.

            **Complexity:** O(log x), about 60 iterations for x ≤ 10¹⁸.
            """,
        ),
    ],
)

# ---------------------------------------------------------------------------
# Challenge section 3
# ---------------------------------------------------------------------------

CHALLENGES = [
    challenge_problem(
        "longest-unique-run",
        "Longest Unique Run",
        """
        Given a string `s`, return the length of the longest **substring** (a contiguous run of characters) that contains no repeated characters.
        """,
        """
        class Solution:
            def lengthOfLongestSubstring(self, s: str) -> int:
                last = {}
                left = best = 0
                for right, ch in enumerate(s):
                    if ch in last and last[ch] >= left:
                        left = last[ch] + 1
                    last[ch] = right
                    best = max(best, right - left + 1)
                return best
        """,
        difficulty="Medium",
        tags=["Sliding Window", "Hash Map", "Strings"],
        examples=[case("abcabcbb", out=3, why='"abc" is the longest run without repeats.'),
                  case("bbbbb", out=1), case("pwwkew", out=3, why='"wke". Note that "pwke" is not contiguous.')],
        tests=[case("", out=0), case(" ", out=1), case("au", out=2), case("dvdf", out=3), case("abba", out=2),
               case("tmmzuxt", out=5), case("abcdefg", out=7),
               case(gen("rand_str(10**5, 'abcdefghijklmnopqrstuvwxyz0123456789', seed=21)")),
               case(gen("''.join(chr(33 + i % 94) for i in range(10**5))"), out=94)],
        constraints=["`0 <= len(s) <= 10⁵`", "`s` contains letters, digits, symbols and spaces"],
        hints=["Use a sliding window `s[left:right + 1]` that never contains a repeat.",
               "When `s[right]` is already in the window, move `left` past its previous occurrence.",
               "A dict from character to its last index lets you jump `left` in one step. Make sure `left` never moves backwards."],
        explanation="""
        Slide a window whose invariant is "no repeated characters". Store each character's most recent index in a dict. When `s[right]` was last seen **inside** the window (`last[ch] >= left`), jump `left` just past that occurrence. The check matters: in `"abba"`, the second `a` was last seen before `left`, so `left` must not jump back.

        **Complexity:** O(n) time. Space is O(min(n, alphabet size)).
        """,
    ),
    challenge_problem(
        "subarrays-summing-to-k",
        "Subarrays Summing to K",
        """
        Given an integer list `nums` (which may contain negative numbers) and an integer `k`, return how many **contiguous, non-empty subarrays** have a sum equal to `k`.
        """,
        """
        class Solution:
            def subarraySum(self, nums: List[int], k: int) -> int:
                seen = {0: 1}
                running = count = 0
                for x in nums:
                    running += x
                    count += seen.get(running - k, 0)
                    seen[running] = seen.get(running, 0) + 1
                return count
        """,
        difficulty="Medium",
        tags=["Prefix Sums", "Hash Map", "Lists"],
        examples=[case([1, 1, 1], 2, out=2, why="[1, 1] starting at index 0 and [1, 1] starting at index 1."),
                  case([1, 2, 3], 3, out=2, why="[1, 2] and [3].")],
        tests=[case([1], 0, out=0), case([0, 0, 0], 0, out=6), case([1, -1, 0], 0, out=3), case([-1, -1, 1], 0, out=1),
               case([3, 4, 7, 2, -3, 1, 4, 2], 7, out=4), case([5], 5, out=1),
               case(gen("rand_list(2 * 10**4, -1000, 1000, seed=22)"), 0),
               case(gen("rand_list(2 * 10**4, -5, 10, seed=23)"), 50)],
        constraints=["`1 <= len(nums) <= 2 × 10⁴`", "`-1000 <= nums[i] <= 1000`", "`-10⁷ <= k <= 10⁷`"],
        hints=["Negative numbers break the sliding window idea. Why?",
               "The sum of `nums[i..j]` is `prefix[j + 1] - prefix[i]`. For a fixed end, how many starts give exactly `k`?",
               "Count how many times each prefix sum has appeared so far, in a dict. Remember the empty prefix, 0."],
        explanation="""
        A subarray ending at the current position sums to `k` exactly when some earlier prefix sum equals `running - k`. So keep a dict counting how often each prefix sum has occurred, starting with `{0: 1}` for the empty prefix, and add `seen[running - k]` at every step before recording the current prefix.

        Negative numbers mean a window's sum can go up or down as it grows, which is why sliding windows fail here and prefix sums work.

        **Complexity:** O(n) time, O(n) space, compared with O(n²) for trying all subarrays.
        """,
    ),
    challenge_problem(
        "zero-sum-triplets",
        "Zero-Sum Triplets",
        """
        Given an integer list `nums`, return every **distinct** triplet `[a, b, c]` of values taken from three different positions such that `a + b + c == 0`.

        No triplet may appear twice, regardless of order. Return the triplets in any order, with the numbers in each triplet in any order.
        """,
        """
        class Solution:
            def threeSum(self, nums: List[int]) -> List[List[int]]:
                nums.sort()
                result = []
                for i in range(len(nums) - 2):
                    if nums[i] > 0:
                        break
                    if i > 0 and nums[i] == nums[i - 1]:
                        continue
                    left, right = i + 1, len(nums) - 1
                    while left < right:
                        total = nums[i] + nums[left] + nums[right]
                        if total < 0:
                            left += 1
                        elif total > 0:
                            right -= 1
                        else:
                            result.append([nums[i], nums[left], nums[right]])
                            left += 1
                            right -= 1
                            while left < right and nums[left] == nums[left - 1]:
                                left += 1
                return result
        """,
        difficulty="Medium",
        tags=["Two Pointers", "Sorting", "Lists"],
        compare="unordered_deep",
        examples=[
            case([-1, 0, 1, 2, -1, -4], out=[[-1, -1, 2], [-1, 0, 1]],
                 why="(-1) + 0 + 1 = 0 and (-1) + (-1) + 2 = 0. The two -1s make [-1, 0, 1] possible in two ways, but it's listed once."),
            case([0, 1, 1], out=[]),
            case([0, 0, 0], out=[[0, 0, 0]]),
        ],
        tests=[case([-2, 0, 1, 1, 2], out=[[-2, 0, 2], [-2, 1, 1]]), case([1, 2, -2, -1], out=[]),
               case([0, 0, 0, 0], out=[[0, 0, 0]]), case([-4, -2, -2, -2, 0, 1, 2, 2, 2, 3, 3, 4, 4, 6, 6]),
               case([3, -2, 1, 0], out=[]), case([-1, 0, 1, 0], out=[[-1, 0, 1]]),
               case(gen("rand_list(1500, -10**4, 10**4, seed=24)")), case(gen("[0] * 1500"), out=[[0, 0, 0]])],
        constraints=["`3 <= len(nums) <= 1500`", "`-10⁵ <= nums[i] <= 10⁵`"],
        hints=["Trying all triples is O(n³). Too slow for 1500 numbers.",
               "Sort first. Then fix the first number and look for a pair summing to `-nums[i]`. That's the two-pointer pair search.",
               "To avoid duplicate triplets, skip values equal to the previous one, both for the fixed number and after finding a match."],
        explanation="""
        Sort the list, then for each index `i` treat `nums[i]` as the smallest element and run the sorted two-pointer pair search on the rest for a pair summing to `-nums[i]`. That's O(n) per `i`, so O(n²) in total.

        Sorting also makes duplicates adjacent. Skip `i` if `nums[i] == nums[i - 1]`, and after recording a triplet advance `left` past equal values. Once `nums[i] > 0`, no triplet can sum to zero, so stop early.

        **Complexity:** O(n²) time. Extra space beyond the output is O(1), apart from what the sort uses.
        """,
    ),
    challenge_problem(
        "rotated-search",
        "Search a Rotated List",
        """
        A list of **distinct** integers was sorted in ascending order and then **rotated** at an unknown point. For example, `[0, 1, 2, 4, 5, 6, 7]` might have become `[4, 5, 6, 7, 0, 1, 2]`.

        Given the rotated list `nums` and an integer `target`, return the index of `target`, or `-1` if it's not present. Your algorithm must run in **O(log n)** time.
        """,
        """
        class Solution:
            def search(self, nums: List[int], target: int) -> int:
                lo, hi = 0, len(nums) - 1
                while lo <= hi:
                    mid = (lo + hi) // 2
                    if nums[mid] == target:
                        return mid
                    if nums[lo] <= nums[mid]:
                        if nums[lo] <= target < nums[mid]:
                            hi = mid - 1
                        else:
                            lo = mid + 1
                    else:
                        if nums[mid] < target <= nums[hi]:
                            lo = mid + 1
                        else:
                            hi = mid - 1
                return -1
        """,
        difficulty="Medium",
        tags=["Binary Search", "Lists", "Conditionals"],
        examples=[case([4, 5, 6, 7, 0, 1, 2], 0, out=4), case([4, 5, 6, 7, 0, 1, 2], 3, out=-1), case([1], 0, out=-1)],
        tests=[case([1], 1, out=0), case([3, 1], 1, out=1), case([5, 1, 3], 5, out=0), case([1, 3], 3, out=1),
               case([4, 5, 6, 7, 8, 1, 2, 3], 8, out=4), case([6, 7, 1, 2, 3, 4, 5], 6, out=0),
               case([3, 4, 5, 6, 1, 2], 2, out=5), case([5, 1, 2, 3, 4], 1, out=1),
               case(gen("list(range(50000, 100000)) + list(range(50000))"), 49999, out=99999),
               case(gen("list(range(50000, 100000)) + list(range(50000))"), -7, out=-1)],
        constraints=["`1 <= len(nums) <= 10⁵`", "All values in `nums` are distinct",
                     "`nums` is an ascending list rotated at some pivot"],
        hints=["Pick a middle index. At least one of the halves `[lo..mid]` or `[mid..hi]` is sorted normally.",
               "You can tell which half is sorted by comparing `nums[lo]` with `nums[mid]`.",
               "If the target lies within the sorted half's range, search there. Otherwise search the other half."],
        explanation="""
        Split at `mid`. Rotation breaks the order at only one point, so at least one side is fully sorted: the left side if `nums[lo] <= nums[mid]`, otherwise the right. For the sorted side we can check in O(1) whether `target` falls inside its range. If it does, search that side. If not, the target can only be in the other side. Each step still halves the range.

        **Complexity:** O(log n) time, O(1) space.
        """,
    ),
    challenge_problem(
        "rainwater-between-walls",
        "Rainwater Between Walls",
        """
        `height[i]` is the height of a wall of width 1 at position `i`. After heavy rain, water collects in the dips between walls.

        Return the total number of units of water trapped.

        ```text
                       █
               █ ≈ ≈ ≈ █ █ ≈ █
           █ ≈ █ █ ≈ █ █ █ █ █ █
         0 1 0 2 1 0 1 3 2 1 2 1   ← heights; ≈ is water (6 units)
        ```
        """,
        """
        class Solution:
            def trap(self, height: List[int]) -> int:
                left, right = 0, len(height) - 1
                left_max = right_max = 0
                water = 0
                while left < right:
                    if height[left] < height[right]:
                        left_max = max(left_max, height[left])
                        water += left_max - height[left]
                        left += 1
                    else:
                        right_max = max(right_max, height[right])
                        water += right_max - height[right]
                        right -= 1
                return water
        """,
        difficulty="Hard",
        tags=["Two Pointers", "Prefix Sums", "Lists"],
        examples=[case([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1], out=6), case([4, 2, 0, 3, 2, 5], out=9)],
        tests=[case([1], out=0), case([2, 0, 2], out=2), case([3, 0, 0, 2, 0, 4], out=10), case([5, 4, 3, 2, 1], out=0),
               case([1, 2, 3], out=0), case([5, 0, 5, 0, 5], out=10), case([0, 0, 0], out=0), case([2, 1, 0, 1, 2], out=4),
               case(gen("rand_list(2 * 10**4, 0, 10**5, seed=25)")),
               case(gen("list(range(10**4)) + list(range(10**4, -1, -1))"), out=0)],
        constraints=["`1 <= len(height) <= 2 × 10⁴`", "`0 <= height[i] <= 10⁵`"],
        hints=["The water above position `i` is `min(tallest wall to its left, tallest wall to its right) - height[i]`.",
               "Computing those maxima from scratch for every `i` is O(n²). Precompute them with a running max from each side (prefix maxima).",
               "For O(1) space, use two pointers: whichever side has the smaller wall so far is the limiting side."],
        explanation="""
        The water at position `i` is bounded by the shorter of the tallest walls on each side: `min(max_left[i], max_right[i]) - height[i]`. Precomputing both running-max lists (prefix and suffix maxima) gives an O(n) time, O(n) space solution.

        The two-pointer version removes the extra lists. Move inward from both ends. If `height[left] < height[right]`, the right side is guaranteed to have a wall at least as tall as `height[right]`, so the water at `left` is limited only by `left_max`. Add `left_max - height[left]` and advance. The mirror case applies to the right.

        **Complexity:** O(n) time, O(1) space.
        """,
    ),
]

MODULE = module(
    "patterns",
    "Algorithmic Patterns",
    "Two pointers, sliding windows, prefix sums and binary search: the patterns behind most array and string problems.",
    lessons=[TWO_POINTERS, SLIDING_WINDOW, PREFIX_SUMS, BINARY_SEARCH],
    challenges=CHALLENGES,
    challenge_title="Checkpoint 3 · Patterns",
    challenge_blurb="Interview-grade Medium problems plus your first Hard. Each one needs a pattern and a data structure together.",
)
