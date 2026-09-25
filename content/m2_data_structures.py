from content.dsl import case, challenge_problem, exercise, gen, lesson, module

# ---------------------------------------------------------------------------
# Lesson 1 · Lists
# ---------------------------------------------------------------------------

LISTS = lesson(
    "lists",
    "Lists",
    "Ordered, changeable sequences and what their operations cost.",
    minutes=20,
    body="""
    A **list** is an ordered, changeable collection. It can hold anything, including other lists.

    ```python
    primes = [2, 3, 5, 7, 11]
    mixed = [1, "two", 3.0, [4, 5]]
    print(len(primes), primes[0], primes[-1])
    print(primes[1:3], primes[::-1])
    print(7 in primes, 4 in primes)
    print(mixed[3][0])
    ```

    Indexing and slicing work exactly like strings. The difference is that lists are **mutable**: you can change them in place.

    ## Changing a list

    ```python
    nums = [3, 1, 4]
    nums.append(1)        # add to the end
    nums.extend([5, 9])   # add several
    nums.insert(0, 2)     # insert at index 0
    print(nums)
    last = nums.pop()     # remove and return the last item
    first = nums.pop(0)   # remove and return the item at index 0
    nums.remove(1)        # remove the first 1 (by value)
    nums[0] = 100         # replace by index
    print(nums, last, first)
    ```

    ## Sorting and aggregates

    ```python
    scores = [70, 95, 82, 61]
    print(sorted(scores))           # a NEW sorted list; scores is unchanged
    print(scores)
    scores.sort(reverse=True)       # sorts in place and returns None
    print(scores)
    print(sum(scores), min(scores), max(scores))
    ```

    ## Looping with enumerate and zip

    `enumerate` gives you the index alongside each item. `zip` walks several lists in step.

    ```python
    fruits = ["apple", "banana", "cherry"]
    for i, fruit in enumerate(fruits):
        print(i, fruit)

    prices = [1.2, 0.5, 3.0]
    for fruit, price in zip(fruits, prices):
        print(f"{fruit}: £{price:.2f}")
    ```

    ## Building a list in a loop

    ```python
    evens = []
    for n in range(10):
        if n % 2 == 0:
            evens.append(n)
    print(evens)

    running, total = [], 0
    for x in [3, 1, 4, 1, 5]:
        total += x
        running.append(total)
    print(running)
    ```

    ## Names are references

    Assigning a list to another name **doesn't copy it**. Both names point at the same list.

    ```python
    a = [1, 2, 3]
    b = a            # same list, two names
    b.append(4)
    print(a)         # [1, 2, 3, 4]
    c = a[:]         # a real copy (list(a) and a.copy() work too)
    c.append(5)
    print(a, c)
    ```

    This also applies to function arguments: a function that appends to a list parameter changes the caller's list.

    ## Grids: lists of lists

    ```python
    grid = [[0] * 3 for _ in range(2)]   # 2 rows × 3 columns, each row separate
    grid[0][1] = 7
    print(grid)

    bad = [[0] * 3] * 2                  # the SAME row object repeated twice
    bad[0][1] = 7
    print(bad)                           # both rows changed
    ```

    The first line uses a **comprehension**, which you'll learn properly at the end of this module.

    ## How fast are list operations?

    Big-O notation describes how running time grows with the input size `n`. With hidden tests of 100,000 elements, an O(n) step inside an O(n) loop means about 10¹⁰ operations, which is far too slow.

    | Operation | Cost |
    |---|---|
    | `nums[i]`, `nums[i] = x`, `len(nums)` | O(1) |
    | `nums.append(x)`, `nums.pop()` | O(1) |
    | `nums.insert(0, x)`, `nums.pop(0)` | O(n): every item shifts |
    | `x in nums`, `nums.index(x)`, `nums.remove(x)` | O(n): scans the list |
    | `nums[a:b]` | O(b − a): copies |
    | `sorted(nums)`, `nums.sort()` | O(n log n) |

    > **Key idea:** appending and indexing are cheap. Searching, inserting at the front, and slicing are not.
    """,
    exercises=[
        exercise(
            "running-sum",
            "Running Total",
            """
            Given a list `nums`, return a new list where the element at index `i` is the sum of `nums[0]` through `nums[i]`.

            The hidden tests include a list of 100,000 numbers, so avoid re-adding the whole prefix for every index.
            """,
            """
            def running_sum(nums: List[int]) -> List[int]:
                result = []
                total = 0
                for x in nums:
                    total += x
                    result.append(total)
                return result
            """,
            examples=[
                case([1, 2, 3, 4], out=[1, 3, 6, 10], why="[1, 1+2, 1+2+3, 1+2+3+4]"),
                case([3, 1, 2, 10, 1], out=[3, 4, 6, 16, 17]),
            ],
            tests=[case([5], out=[5]), case([-1, 1, -1, 1], out=[-1, 0, -1, 0]), case([0, 0, 0], out=[0, 0, 0]),
                   case([], out=[]), case(gen("rand_list(10**5, -1000, 1000, seed=2)"))],
            constraints=["`0 <= len(nums) <= 10⁵`", "`-1000 <= nums[i] <= 1000`"],
            hints=["Keep a running `total` as you loop and append it after each addition.",
                   "`sum(nums[:i + 1])` inside a loop is O(n²). Too slow for the big test."],
            explanation="""
            Carry the running total forward. Each new element needs one addition, not a fresh sum of everything before it. That turns an O(n²) approach into O(n).

            **Complexity:** O(n) time, O(n) for the output list.
            """,
        ),
        exercise(
            "rotate-right",
            "Rotate Right",
            """
            Return a **new list** containing the elements of `nums` rotated `k` steps to the right. Each step moves the last element to the front.

            `k` can be much larger than the list's length.
            """,
            """
            def rotate_right(nums: List[int], k: int) -> List[int]:
                if not nums:
                    return []
                k %= len(nums)
                cut = len(nums) - k
                return nums[cut:] + nums[:cut]
            """,
            examples=[
                case([1, 2, 3, 4, 5], 2, out=[4, 5, 1, 2, 3]),
                case([1, 2], 5, out=[2, 1], why="Rotating a 2-element list 5 times is the same as rotating it once."),
            ],
            tests=[case([], 3, out=[]), case([7], 0, out=[7]), case([1, 2, 3], 3, out=[1, 2, 3]),
                   case([1, 2, 3], 0, out=[1, 2, 3]), case([1, 2, 3, 4, 5, 6], 10 ** 9, out=[3, 4, 5, 6, 1, 2]),
                   case([9, 8], 1, out=[8, 9]), case(gen("rand_list(10**5, -10**9, 10**9, seed=8)"), 99999)],
            constraints=["`0 <= len(nums) <= 10⁵`", "`0 <= k <= 10⁹`"],
            hints=["Rotating by `len(nums)` gives back the original list, so only `k % len(nums)` matters.",
                   "After rotating, the last `k` elements are at the front: combine two slices.",
                   "Watch out for an empty list, since `k % 0` raises an error."],
            explanation="""
            Rotating by the list length is a no-op, so reduce `k` with `k %= len(nums)`. The result is then the last `k` elements followed by the rest, which is two slices joined with `+`. Guard the empty list first, because `% 0` raises `ZeroDivisionError`.

            **Complexity:** O(n) time and space, no matter how large `k` is.
            """,
        ),
    ],
)

# ---------------------------------------------------------------------------
# Lesson 2 · Dictionaries
# ---------------------------------------------------------------------------

DICTS = lesson(
    "dictionaries",
    "Dictionaries",
    "Key-value lookups in O(1): counting, grouping and remembering.",
    minutes=20,
    body="""
    A **dictionary** (`dict`) maps **keys** to **values**. Looking up a key takes O(1) time on average, however big the dictionary is. That makes dicts the most important tool for writing fast algorithms.

    ```python
    ages = {"ada": 36, "alan": 41}
    ages["grace"] = 85            # add or update
    print(ages["ada"])
    print(len(ages), "alan" in ages, "linus" in ages)
    del ages["alan"]
    print(ages)
    ```

    ## Safe lookups

    `d[key]` raises `KeyError` if the key is missing. `d.get(key, default)` returns the default instead.

    ```python
    stock = {"apples": 3}
    print(stock.get("apples", 0), stock.get("pears", 0))
    ```

    ## Looping

    Dicts remember insertion order.

    ```python
    capitals = {"France": "Paris", "Japan": "Tokyo", "Kenya": "Nairobi"}
    for country in capitals:              # loops over keys
        print(country, end=" ")
    print()
    print(list(capitals.values()))
    for country, city in capitals.items():
        print(f"{city} is the capital of {country}")
    ```

    ## Counting: the classic dict pattern

    ```python
    counts = {}
    for ch in "mississippi":
        counts[ch] = counts.get(ch, 0) + 1
    print(counts)
    ```

    The `collections` module has shortcuts for counting and grouping:

    ```python
    from collections import Counter, defaultdict

    c = Counter("mississippi")
    print(c)
    print(c.most_common(2))
    print(c["s"], c["z"])               # missing keys count as 0

    groups = defaultdict(list)          # missing keys start as an empty list
    for word in ["ant", "bee", "asp", "cow", "bat"]:
        groups[word[0]].append(word)
    print(dict(groups))
    ```

    ## Remembering what you've seen

    A dict can record *where* or *when* you saw each value. That turns a search inside a loop into a single pass:

    ```python
    nums = [4, 9, 1, 9, 4, 7]
    first_seen = {}
    for i, x in enumerate(nums):
        if x not in first_seen:
            first_seen[x] = i
    print(first_seen)
    ```

    ## Keys must be hashable

    Keys must be **immutable**: strings, numbers, booleans, or tuples of those. A list can't be a key (`TypeError: unhashable type: 'list'`), so convert it with `tuple(...)` first. Values can be anything.

    ```python
    board = {}
    board[(0, 0)] = "X"          # a tuple key works
    board[tuple([1, 2])] = "O"
    print(board)
    ```

    > **Key idea:** whenever you're about to search a list inside a loop, ask whether a dict could answer the question in O(1).
    """,
    exercises=[
        exercise(
            "word-count",
            "Word Count",
            """
            Given a `sentence`, return a dictionary mapping each word to how many times it appears. Words are separated by one or more spaces and should be counted **case-insensitively**, using the lower-case form as the key.
            """,
            """
            def word_count(sentence: str) -> Dict[str, int]:
                counts = {}
                for word in sentence.lower().split():
                    counts[word] = counts.get(word, 0) + 1
                return counts
            """,
            examples=[
                case("the cat and the hat", out={"the": 2, "cat": 1, "and": 1, "hat": 1}),
                case("Go go GO", out={"go": 3}),
            ],
            tests=[case("a", out={"a": 1}), case("  spaced   out  ", out={"spaced": 1, "out": 1}), case("", out={}),
                   case("One two Two three THREE three"), case(gen("rand_str(10**5, 'ab ', seed=3)"))],
            constraints=["`0 <= len(sentence) <= 10⁵`", "`sentence` has English letters and spaces"],
            hints=["`sentence.lower().split()` gives you clean, lower-case words.",
                   "`counts.get(word, 0) + 1` handles words you haven't seen yet."],
            explanation="""
            Lower-case the sentence once, split on whitespace, and count with `dict.get(word, 0) + 1`. `Counter(sentence.lower().split())` does the same thing in one line.

            **Complexity:** O(n) time.
            """,
        ),
        exercise(
            "group-by-length",
            "Group by Length",
            """
            Given a list of `words`, return a dictionary that maps each word length to the list of words with that length. Words in each list must keep the order they had in the input.
            """,
            """
            def group_by_length(words: List[str]) -> Dict[int, List[str]]:
                groups = {}
                for word in words:
                    groups.setdefault(len(word), []).append(word)
                return groups
            """,
            examples=[
                case(["hi", "sun", "ok", "moon", "sea"], out={2: ["hi", "ok"], 3: ["sun", "sea"], 4: ["moon"]}),
                case([], out={}),
            ],
            tests=[case(["a"], out={1: ["a"]}), case(["same", "same"], out={4: ["same", "same"]}),
                   case(["", "a", ""], out={0: ["", ""], 1: ["a"]}),
                   case(["python", "is", "fun", "and", "useful"])],
            constraints=["`0 <= len(words) <= 10⁴`"],
            hints=["Start each group as an empty list the first time you see that length.",
                   "`d.setdefault(key, [])` or `collections.defaultdict(list)` does that for you."],
            explanation="""
            `setdefault(len(word), [])` returns the existing list for that length, or inserts and returns a new empty one. Either way we can `.append(word)` straight away. Appending in input order preserves the required ordering.

            **Complexity:** O(n) time.
            """,
        ),
    ],
)

# ---------------------------------------------------------------------------
# Lesson 3 · Sets & tuples
# ---------------------------------------------------------------------------

SETS = lesson(
    "sets-tuples",
    "Sets & Tuples",
    "Unique collections with fast membership, and immutable records.",
    minutes=15,
    body="""
    ## Tuples

    A **tuple** is like a list that can't be changed. Use one for a fixed group of values such as a coordinate, a pair or a record.

    ```python
    point = (3, 4)
    x, y = point                 # unpacking
    print(x, y, point[0], len(point))
    single = (5,)                # a one-element tuple needs the trailing comma
    print(type(single), type((5)))
    ```

    Tuples are hashable, so they can be dict keys and set members. They compare element by element, which is useful for sorting:

    ```python
    distances = {(0, 0): 0, (1, 2): 3}
    print(distances[(1, 2)])
    print((1, 5) < (2, 0), (1, 5) < (1, 9))
    ```

    ## Sets

    A **set** is an unordered collection of **unique** items with O(1) membership tests.

    ```python
    colours = {"red", "green"}
    colours.add("blue")
    colours.add("red")            # already present: nothing happens
    print(len(colours), "red" in colours)
    colours.discard("green")      # remove if present, no error if missing
    print(sorted(colours))        # sets have no order; sort to display
    print(set([3, 1, 3, 2, 1]))   # de-duplicate a list
    empty = set()                 # careful: {} is an empty dict
    print(type(empty), type({}))
    ```

    ## Set algebra

    ```python
    a = {1, 2, 3, 4}
    b = {3, 4, 5}
    print(a | b)         # union: in either
    print(a & b)         # intersection: in both
    print(a - b)         # difference: in a but not b
    print(a ^ b)         # in exactly one
    print({1, 2} <= a)   # subset test
    ```

    ## "Have I seen this before?"

    ```python
    def first_repeat(items):
        seen = set()
        for item in items:
            if item in seen:
                return item
            seen.add(item)
        return None

    print(first_repeat(["a", "b", "c", "b", "a"]))
    print(first_repeat([1, 2, 3]))
    ```

    `item in seen` is O(1) for a set and O(n) for a list. On 100,000 items that's the difference between instant and minutes.

    ## Which collection should I use?

    | You need | Use |
    |---|---|
    | an ordered sequence you can change | `list` |
    | a fixed record, or a compound dict key | `tuple` |
    | fast "is it in there?" checks or uniqueness | `set` |
    | to look up a value by a key | `dict` |

    > **Key idea:** convert to a set when you only care *whether* something is present, and use tuples when you need a list-like value as a key.
    """,
    exercises=[
        exercise(
            "common-elements",
            "Common Elements",
            """
            Given two lists of integers `a` and `b`, return a **sorted** list of the distinct values that appear in both.
            """,
            """
            def common_elements(a: List[int], b: List[int]) -> List[int]:
                return sorted(set(a) & set(b))
            """,
            examples=[case([1, 2, 2, 3], [2, 3, 4], out=[2, 3]),
                      case([1, 1], [2], out=[])],
            tests=[case([], [1], out=[]), case([5, 4, 3], [3, 4, 5], out=[3, 4, 5]), case([-1, 0], [0, -1, -1], out=[-1, 0]),
                   case(gen("rand_list(10**5, 0, 10**6, seed=1)"), gen("rand_list(10**5, 0, 10**6, seed=2)"))],
            constraints=["`0 <= len(a), len(b) <= 10⁵`", "`-10⁹ <= a[i], b[i] <= 10⁹`"],
            hints=["`&` gives the intersection of two sets.", "`sorted()` accepts a set and returns a list."],
            explanation="""
            Converting each list to a set removes duplicates and makes membership checks O(1). Set intersection `&` keeps values present in both, and `sorted` returns the ordered list. A double loop with `in` on lists would be O(n·m), about 10¹⁰ operations for the large test.

            **Complexity:** O(n + m + k log k) where k is the size of the result.
            """,
        ),
        exercise(
            "unique-points",
            "Distinct Points",
            """
            You're given a list of 2-D `points`, each written as `[x, y]`. Return how many **distinct** points there are.
            """,
            """
            def unique_points(points: List[List[int]]) -> int:
                return len({(x, y) for x, y in points})
            """,
            examples=[case([[1, 2], [3, 4], [1, 2]], out=2), case([[0, 0]], out=1)],
            tests=[case([[1, 2], [2, 1]], out=2), case([], out=0), case([[5, 5], [5, 5], [5, 5]], out=1),
                   case(gen("rand_grid(10**5, 2, list(range(100)), seed=5)"))],
            constraints=["`0 <= len(points) <= 10⁵`", "`-10⁴ <= x, y <= 10⁴`"],
            hints=["A set removes duplicates, but lists can't go in a set.", "Convert each point to a tuple first."],
            explanation="""
            Lists are unhashable, so `set(points)` fails. Converting each point to a tuple makes it hashable. The set keeps one copy of each distinct point, and its length is the answer.

            **Complexity:** O(n) time and space.
            """,
        ),
    ],
)

# ---------------------------------------------------------------------------
# Lesson 4 · Comprehensions & sorting
# ---------------------------------------------------------------------------

COMPREHENSIONS = lesson(
    "comprehensions",
    "Comprehensions & Sorting",
    "Build collections in one expression and sort by any rule.",
    minutes=20,
    body="""
    ## List comprehensions

    A comprehension builds a list in one expression: `[expression for item in iterable if condition]`.

    ```python
    squares = [n * n for n in range(6)]
    evens = [n for n in range(20) if n % 2 == 0]
    lowered = [w.lower() for w in ["Hello", "World"]]
    print(squares, evens, lowered)
    ```

    It's shorthand for the familiar loop:

    ```python
    evens = []
    for n in range(20):
        if n % 2 == 0:
            evens.append(n)
    print(evens)
    ```

    Comprehensions can nest, and the `for` clauses read left to right like nested loops:

    ```python
    pairs = [(x, y) for x in range(3) for y in range(3) if x < y]
    print(pairs)
    grid = [[r * 3 + c for c in range(3)] for r in range(3)]
    print(grid)
    flat = [v for row in grid for v in row]
    print(flat)
    labels = ["even" if n % 2 == 0 else "odd" for n in range(5)]
    print(labels)
    ```

    ## Dict and set comprehensions

    ```python
    words = ["apple", "fig", "banana"]
    lengths = {w: len(w) for w in words}
    first_letters = {w[0] for w in words}
    print(lengths, first_letters)
    inverted = {v: k for k, v in {"a": 1, "b": 2}.items()}
    print(inverted)
    ```

    ## Generator expressions

    Inside a function call you can drop the brackets. Python then streams the values instead of building a list:

    ```python
    nums = [3, 8, 12, 5]
    print(sum(n * n for n in nums))
    print(any(n > 10 for n in nums), all(n > 0 for n in nums))
    print(max(len(w) for w in ["a", "abc", "ab"]))
    ```

    ## Sorting with a key

    `sorted(items, key=f)` compares `f(item)` instead of the item itself.

    ```python
    words = ["banana", "Fig", "apple", "cherry", "date"]
    print(sorted(words))                  # capital letters sort first
    print(sorted(words, key=str.lower))
    print(sorted(words, key=len))
    print(sorted(words, key=len, reverse=True))
    ```

    For several criteria, return a **tuple** from the key. To reverse one numeric criterion, negate it:

    ```python
    people = [("Ada", 36), ("Alan", 41), ("Grace", 36), ("Bob", 41)]
    print(sorted(people, key=lambda p: (p[1], p[0])))    # age, then name
    print(sorted(people, key=lambda p: (-p[1], p[0])))   # oldest first, then name
    ```

    Python's sort is **stable**: items with equal keys keep their original order. `min` and `max` accept a `key` too:

    ```python
    scores = {"ada": 91, "alan": 78, "grace": 99}
    print(max(scores, key=scores.get))
    print(min(["pear", "fig", "banana"], key=len))
    ```

    > **Key idea:** a comprehension replaces a build-a-list loop, and `key=lambda x: (a, b)` sorts by several rules at once.
    """,
    exercises=[
        exercise(
            "even-squares",
            "Even Squares",
            """
            Return a list of the squares of the **even** numbers in `nums`, sorted in ascending order. Try writing it as a single comprehension.
            """,
            """
            def even_squares(nums: List[int]) -> List[int]:
                return sorted(n * n for n in nums if n % 2 == 0)
            """,
            examples=[case([1, 2, 3, 4], out=[4, 16]),
                      case([-4, 3, -2], out=[4, 16], why="(-4)² = 16 and (-2)² = 4, sorted ascending.")],
            tests=[case([], out=[]), case([1, 3, 5], out=[]), case([0], out=[0]), case([10, -10], out=[100, 100]),
                   case(gen("rand_list(10**5, -10**4, 10**4, seed=9)"))],
            constraints=["`0 <= len(nums) <= 10⁵`", "`-10⁴ <= nums[i] <= 10⁴`"],
            hints=["Filter with `if n % 2 == 0` at the end of the comprehension.",
                   "Negative numbers square to positives, so sort after squaring."],
            explanation="""
            One expression does everything: filter the evens, square them, then sort. `sorted()` accepts a generator expression directly. Sorting must happen after squaring because negative inputs change order.

            **Complexity:** O(n log n).
            """,
        ),
        exercise(
            "sort-words",
            "Sort by Length",
            """
            Sort `words` by length, shortest first. Words of the same length should be in alphabetical order. Return the sorted list.
            """,
            """
            def sort_words(words: List[str]) -> List[str]:
                return sorted(words, key=lambda w: (len(w), w))
            """,
            examples=[case(["banana", "kiwi", "apple", "fig", "date"], out=["fig", "date", "kiwi", "apple", "banana"])],
            tests=[case(["b", "a", "c"], out=["a", "b", "c"]), case(["bb", "a", "ab", "b"], out=["a", "b", "ab", "bb"]),
                   case([], out=[]), case(["same", "same"], out=["same", "same"]),
                   case(["python", "java", "c", "go", "rust", "ruby"])],
            constraints=["`0 <= len(words) <= 10⁴`", "Words contain lower-case English letters"],
            hints=["`key=` can return a tuple, and tuples compare element by element.",
                   "`(len(w), w)` compares by length first, then alphabetically."],
            explanation="""
            A tuple key sorts by its first element and uses later elements only to break ties. `(len(w), w)` therefore orders by length and then alphabetically.

            **Complexity:** O(n log n) comparisons.
            """,
        ),
    ],
)

# ---------------------------------------------------------------------------
# Challenge section 2
# ---------------------------------------------------------------------------

CHALLENGES = [
    challenge_problem(
        "pair-target-sum",
        "Pair With Target Sum",
        """
        Given a list of integers `nums` and an integer `target`, return the **indices** of the two numbers that add up to `target`.

        Each input has **exactly one** solution, and you can't use the same element twice. You can return the two indices in any order.
        """,
        """
        class Solution:
            def twoSum(self, nums: List[int], target: int) -> List[int]:
                seen = {}
                for i, x in enumerate(nums):
                    if target - x in seen:
                        return [seen[target - x], i]
                    seen[x] = i
                return []
        """,
        difficulty="Easy",
        tags=["Hash Map", "Lists", "enumerate"],
        compare="unordered",
        examples=[
            case([2, 7, 11, 15], 9, out=[0, 1], why="nums[0] + nums[1] == 9, so return [0, 1]."),
            case([3, 2, 4], 6, out=[1, 2]),
            case([3, 3], 6, out=[0, 1]),
        ],
        tests=[case([1, 4, 9, -3], 6, out=[2, 3]), case([0, 4, 3, 0], 0, out=[0, 3]),
               case([-1, -2, -3, -4, -5], -8, out=[2, 4]), case([5, 75, 25], 100, out=[1, 2]),
               case(gen("list(range(1, 20001))"), 39999, out=[19998, 19999]),
               case(gen("rand_sorted(20000, -10**9, -1, seed=3) + [10**9 - 1, 10**9]"), 2 * 10 ** 9 - 1, out=[20000, 20001])],
        constraints=["`2 <= len(nums) <= 2 × 10⁴`",
                     "`-10⁹ <= nums[i], target <= 10⁹`", "Exactly one valid answer exists"],
        hints=["The brute-force way checks every pair, which is O(n²). Can you avoid the inner loop?",
               "For each `x`, the number you need is `target - x`. How can you check whether you've already seen it in O(1)?",
               "Store each value's index in a dict as you go."],
        explanation="""
        Walk through the list once. For each `x`, its partner must be `target - x`. If that partner is already in the `seen` dictionary, we have the answer. Otherwise record `x`'s index and move on. Checking before inserting stops an element from pairing with itself, and it still handles duplicates such as `[3, 3]`.

        **Complexity:** O(n) time, O(n) extra space, compared with O(n²) for trying every pair. On the 20,000-element hidden tests that's 20,000 steps instead of 200 million.
        """,
    ),
    challenge_problem(
        "roman-numeral-value",
        "Roman Numeral Value",
        """
        Roman numerals use seven symbols:

        | Symbol | I | V | X | L | C | D | M |
        |---|---|---|---|---|---|---|---|
        | Value | 1 | 5 | 10 | 50 | 100 | 500 | 1000 |

        Symbols are usually written largest to smallest and added up: `XXVII` is `10 + 10 + 5 + 1 + 1 = 27`. Six cases use subtraction instead: when a smaller symbol comes **before** a larger one, it is subtracted (`IV` = 4, `IX` = 9, `XL` = 40, `XC` = 90, `CD` = 400, `CM` = 900).

        Given a valid Roman numeral `s`, return its integer value.
        """,
        """
        class Solution:
            def romanToInt(self, s: str) -> int:
                values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
                total = 0
                for i, ch in enumerate(s):
                    if i + 1 < len(s) and values[ch] < values[s[i + 1]]:
                        total -= values[ch]
                    else:
                        total += values[ch]
                return total
        """,
        difficulty="Easy",
        tags=["Hash Map", "Strings", "Loops"],
        examples=[case("III", out=3), case("LVIII", out=58, why="L = 50, V = 5, III = 3."),
                  case("MCMXCIV", out=1994, why="M = 1000, CM = 900, XC = 90 and IV = 4.")],
        tests=[case("IV", out=4), case("IX", out=9), case("XL", out=40), case("XC", out=90), case("CD", out=400),
               case("CM", out=900), case("MMMCMXCIX", out=3999), case("I", out=1), case("MMXXVI", out=2026),
               case("DCCCXC", out=890), case("CDXLIV", out=444)],
        constraints=["`1 <= len(s) <= 15`", "`s` is a valid Roman numeral in the range `[1, 3999]`"],
        hints=["Store the symbol values in a dict.",
               "A symbol is subtracted exactly when the symbol after it is larger."],
        explanation="""
        Map each symbol to its value with a dict. Scan left to right: if the next symbol is larger, the current one is part of a subtractive pair, so subtract it. Otherwise add it. `MCMXCIV` becomes `+1000 −100 +1000 −10 +100 −1 +5 = 1994`.

        **Complexity:** O(n) time, O(1) space.
        """,
    ),
    challenge_problem(
        "joyful-number",
        "Joyful Number",
        """
        Start with a positive integer `n`. Replace it with the **sum of the squares of its digits**, and repeat.

        Either the process eventually reaches `1` and stays there, or it loops forever in a cycle that never includes `1`. A number is **joyful** if the process reaches `1`.

        Return `True` if `n` is joyful.
        """,
        """
        class Solution:
            def isHappy(self, n: int) -> bool:
                seen = set()
                while n != 1 and n not in seen:
                    seen.add(n)
                    n = sum(int(d) ** 2 for d in str(n))
                return n == 1
        """,
        difficulty="Easy",
        tags=["Hash Set", "Math", "Loops"],
        examples=[
            case(19, out=True, why="1² + 9² = 82 → 8² + 2² = 68 → 6² + 8² = 100 → 1² + 0² + 0² = 1"),
            case(2, out=False, why="2 → 4 → 16 → 37 → 58 → 89 → 145 → 42 → 20 → 4 → … repeats forever."),
        ],
        tests=[case(1, out=True), case(7, out=True), case(4, out=False), case(100, out=True), case(1111111, out=True),
               case(2147483647), case(116), case(3, out=False), case(10, out=True), case(999999999)],
        constraints=["`1 <= n <= 2³¹ - 1`"],
        hints=["How do you know you're stuck in a loop? You've seen the same number before.",
               "Keep a set of every number you've visited."],
        explanation="""
        Simulate the process and remember every value in a set. If we reach `1`, the number is joyful. If we meet a value we've already seen, the sequence is in a cycle that doesn't include `1`, so we stop.

        The sequence always drops quickly below a few hundred, so the set stays tiny. The same idea works without extra memory using a "slow" and a "fast" pointer (Floyd's cycle detection), which you'll use on linked lists in Module 5.

        **Complexity:** O(log n) per step, with a small bounded number of steps.
        """,
    ),
    challenge_problem(
        "anagram-groups",
        "Anagram Groups",
        """
        Given a list of strings `strs`, group the words that are **anagrams** of each other: words that use exactly the same letters, the same number of times, in any order.

        Return the groups in any order, with the words inside each group in any order.
        """,
        """
        class Solution:
            def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
                groups = defaultdict(list)
                for word in strs:
                    groups[tuple(sorted(word))].append(word)
                return list(groups.values())
        """,
        difficulty="Medium",
        tags=["Hash Map", "Sorting", "Tuples"],
        compare="unordered_deep",
        examples=[
            case(["eat", "tea", "tan", "ate", "nat", "bat"], out=[["bat"], ["nat", "tan"], ["ate", "eat", "tea"]]),
            case([""], out=[[""]]),
            case(["a"], out=[["a"]]),
        ],
        tests=[case(["ab", "ba", "abc", "cab", "bca", "xyz"], out=[["ab", "ba"], ["abc", "cab", "bca"], ["xyz"]]),
               case(["", ""], out=[["", ""]]), case(["listen", "silent", "enlist", "google", "gogole", "cat"]),
               case(["aab", "aba", "abb"], out=[["aab", "aba"], ["abb"]]),
               case(gen("[rand_str(6, 'abcdef', seed=i) for i in range(20000)]"))],
        constraints=["`1 <= len(strs) <= 2 × 10⁴`", "`0 <= len(strs[i]) <= 100`",
                     "`strs[i]` contains lower-case English letters"],
        hints=["Two words are anagrams exactly when their sorted letters match.",
               "Use that sorted form as a dict key. It has to be hashable, so a `tuple` or a `str`.",
               "`collections.defaultdict(list)` saves you from checking whether a key exists."],
        explanation="""
        Give every word a **canonical key** that is identical for all its anagrams: its letters sorted, e.g. `"tea"` → `('a', 'e', 't')`. Group words by that key in a dict of lists, then return the dict's values.

        Sorting each word costs O(k log k). A counting key works too, such as a tuple of 26 letter counts, which costs O(k) per word.

        **Complexity:** O(n · k log k) time for n words of length up to k; O(n · k) space.
        """,
    ),
    challenge_problem(
        "most-frequent-k",
        "Most Frequent K",
        """
        Given an integer list `nums` and an integer `k`, return the `k` values that appear **most often**. You can return them in any order.

        The answer is guaranteed to be unique, so there is never a tie at the cut-off.
        """,
        """
        class Solution:
            def topKFrequent(self, nums: List[int], k: int) -> List[int]:
                counts = Counter(nums)
                return [x for x, _ in counts.most_common(k)]
        """,
        difficulty="Medium",
        tags=["Hash Map", "Sorting", "Comprehensions"],
        compare="unordered",
        examples=[case([1, 1, 1, 2, 2, 3], 2, out=[1, 2]), case([1], 1, out=[1])],
        tests=[case([4, 4, 4, 5, 5, 6, 6, 6, 6], 2, out=[6, 4]), case([-1, -1, 2], 1, out=[-1]),
               case([1, 2], 2, out=[1, 2]), case([5, 3, 5, 3, 5, 9], 1, out=[5]),
               case(gen("[i % 1000 for i in range(100000)] + [7] * 50 + [3] * 40"), 2, out=[7, 3])],
        constraints=["`1 <= len(nums) <= 10⁵`", "`-10⁴ <= nums[i] <= 10⁴`",
                     "`k` is between 1 and the number of distinct values"],
        hints=["First count how often each value appears.",
               "Then sort the distinct values by their count, highest first, and take `k`.",
               "`Counter.most_common(k)` does both steps."],
        explanation="""
        Count occurrences with a dict (or `Counter`), then pick the `k` values with the highest counts, either by sorting the distinct values by count or with `most_common(k)`.

        To beat O(n log n), use **bucket sort**: make a list where index `c` holds the values that appear `c` times, then walk it from the highest count down until you've collected `k`. That's O(n).

        **Complexity:** O(n + d log d) with sorting, where d is the number of distinct values.
        """,
    ),
]

MODULE = module(
    "data-structures",
    "Core Data Structures",
    "Lists, dictionaries, sets and tuples, plus the comprehensions and sorting that tie them together.",
    lessons=[LISTS, DICTS, SETS, COMPREHENSIONS],
    challenges=CHALLENGES,
    challenge_title="Checkpoint 2 · Data Structures",
    challenge_blurb="Hash maps meet strings, sets and sorting. Includes two classic Medium interview questions.",
)
