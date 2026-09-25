from content.dsl import case, challenge_problem, exercise, gen, lesson, module

# ---------------------------------------------------------------------------
# Lesson 1 · Variables, numbers & operators
# ---------------------------------------------------------------------------

VARIABLES = lesson(
    "variables",
    "Variables, Numbers & Operators",
    "Store values in names, do arithmetic, and compare things.",
    minutes=15,
    body="""
    Every program works with **values**: numbers, text, true/false. A **variable** is a name that points at a value so you can use it again later.

    ```python
    language = "Python"
    year = 1991
    version = 3.13
    print(language, "first appeared in", year)
    print(type(year), type(version), type(language))
    ```

    Python works out the type from the value itself, so you never declare it. Press **Run** on any example to execute it, and edit it freely to experiment.

    ## Numbers and arithmetic

    Python has two everyday number types: `int` for whole numbers (with no size limit) and `float` for decimals.

    | Operator | Meaning | Example | Result |
    |---|---|---|---|
    | `+` `-` `*` | add, subtract, multiply | `7 * 3` | `21` |
    | `/` | true division, always gives a float | `7 / 2` | `3.5` |
    | `//` | floor division | `7 // 2` | `3` |
    | `%` | remainder (modulo) | `7 % 2` | `1` |
    | `**` | power | `2 ** 10` | `1024` |

    ```python
    print(7 / 2, 7 // 2, 7 % 2)
    print(2 ** 100)          # ints grow as big as you need
    print(-7 // 2, -7 % 2)   # floor division rounds DOWN, towards -infinity
    ```

    `//` and `%` work as a pair. For any `a` and positive `b`, `a == (a // b) * b + a % b`. Together they split a number into "how many whole groups" and "what's left over", which comes up constantly:

    ```python
    total_minutes = 135
    hours = total_minutes // 60
    minutes = total_minutes % 60
    print(hours, "h", minutes, "min")

    n = 4827
    print("last digit:", n % 10)
    print("without last digit:", n // 10)
    ```

    ## Updating variables

    ```python
    score = 10
    score += 5      # same as score = score + 5
    score *= 2
    print(score)

    a, b = 1, 2     # assign two names at once
    a, b = b, a     # swap without a temporary variable
    print(a, b)
    ```

    ## Comparisons and booleans

    Comparisons produce `True` or `False` (type `bool`). Combine them with `and`, `or` and `not`. Python lets you chain comparisons the way you would in maths.

    ```python
    x = 42
    print(x > 10, x == 42, x != 42)
    print(0 <= x < 100)              # chained: 0 <= x and x < 100
    print(x % 2 == 0 and x > 40)
    print(not (x > 50))
    ```

    `and` and `or` **short-circuit**: `and` stops at the first false value, `or` stops at the first true one. That lets you guard a risky check. `count > 0 and total / count > 5` never divides by zero.

    ## Converting between types

    ```python
    print(int("42") + 1)       # text to number
    print(str(42) + "!")       # number to text
    print(int(3.99))           # int() truncates toward zero
    print(round(3.567, 2))     # round to 2 decimal places
    print(abs(-8), min(4, 9, 2), max(4, 9, 2))
    ```

    ## How exercises work

    Each exercise gives you a **function** to complete. The function receives its inputs as parameters, and you `return` the answer rather than printing it. Functions get a full lesson later in this module; for now, write your code inside the indented block:

    ```python
    def area_of_rectangle(width, height):
        return width * height

    print(area_of_rectangle(3, 4))
    ```

    **Run** checks your code against the examples. **Submit** also runs the hidden tests, which include edge cases and large inputs.

    > **Key idea:** `//` gives the whole groups and `%` gives the leftover. Use them to pull numbers apart.
    """,
    exercises=[
        exercise(
            "split-time",
            "Digital Clock",
            """
            A stopwatch reports elapsed time as a single number of seconds, `total`. Convert it into hours, minutes and seconds.

            Return a list `[hours, minutes, seconds]` where `minutes` and `seconds` are each between `0` and `59`. Hours are not capped at 24.
            """,
            """
            def split_time(total: int) -> List[int]:
                hours = total // 3600
                minutes = total % 3600 // 60
                seconds = total % 60
                return [hours, minutes, seconds]
            """,
            examples=[
                case(3725, out=[1, 2, 5], why="3725 = 1 × 3600 + 2 × 60 + 5"),
                case(59, out=[0, 0, 59]),
            ],
            tests=[case(0, out=[0, 0, 0]), case(60, out=[0, 1, 0]), case(3600, out=[1, 0, 0]),
                   case(86399, out=[23, 59, 59]), case(90061, out=[25, 1, 1]), case(7322),
                   case(1000000, out=[277, 46, 40])],
            constraints=["`0 <= total <= 10⁶`"],
            hints=["There are 3600 seconds in an hour. `total // 3600` gives the hours.",
                   "`total % 3600` is what's left after removing the whole hours. Split that into minutes and seconds the same way."],
            explanation="""
            Floor division counts whole groups and the remainder keeps what's left over. `total // 3600` is the number of full hours. `total % 3600` is the leftover seconds, and dividing that by 60 gives minutes. The final seconds are simply `total % 60`, because every whole minute is 60 seconds.

            **Complexity:** O(1) time and space.
            """,
        ),
        exercise(
            "leap-year",
            "Leap Year",
            """
            In the Gregorian calendar a year is a **leap year** when:

            - it is divisible by 4,
            - **except** years divisible by 100 are not leap years,
            - **unless** they are also divisible by 400.

            Return `True` if `year` is a leap year and `False` otherwise.
            """,
            """
            def is_leap_year(year: int) -> bool:
                return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
            """,
            examples=[
                case(2024, out=True),
                case(1900, out=False, why="1900 is divisible by 100 but not by 400."),
                case(2000, out=True, why="2000 is divisible by 400."),
            ],
            tests=[case(2023, out=False), case(2100, out=False), case(2400, out=True), case(1, out=False),
                   case(4, out=True), case(1600, out=True), case(1996, out=True), case(1999, out=False),
                   case(1800, out=False), case(2012, out=True)],
            constraints=["`1 <= year <= 9999`"],
            hints=["`year % 4 == 0` tests divisibility by 4.",
                   "Combine the three rules with `and` / `or`. Parentheses make the exception clear."],
            explanation="""
            Translate the rules directly into a boolean expression: divisible by 4 **and** (not divisible by 100 **or** divisible by 400). The parentheses matter because `and` binds tighter than `or`.

            **Complexity:** O(1).
            """,
        ),
    ],
)

# ---------------------------------------------------------------------------
# Lesson 2 · Strings
# ---------------------------------------------------------------------------

STRINGS = lesson(
    "strings",
    "Strings",
    "Index, slice, search and format text.",
    minutes=20,
    body="""
    A **string** is a sequence of characters. Use single or double quotes; they behave identically.

    ## Indexing and slicing

    Each character has a position, starting at `0`. Negative indexes count from the end.

    ```text
     p   y   t   h   o   n
     0   1   2   3   4   5
    -6  -5  -4  -3  -2  -1
    ```

    ```python
    word = "python"
    print(len(word))
    print(word[0], word[-1])      # first and last characters
    print(word[1:4])              # 'yth': start included, stop excluded
    print(word[:2], word[2:])     # omit start or stop to go to the edge
    print(word[::-1])             # step -1 reverses
    print(word[::2])              # every second character
    ```

    A slice `s[start:stop:step]` never raises an error for out-of-range bounds; it just clips. Indexing a single position that doesn't exist does raise `IndexError`.

    ## Strings are immutable

    You can't change a character in place. Build a new string instead:

    ```python
    word = "python"
    # word[0] = "P" would raise TypeError
    word = "P" + word[1:]
    print(word)
    ```

    ## Useful methods

    | Method | What it does |
    |---|---|
    | `s.lower()`, `s.upper()`, `s.capitalize()` | change case |
    | `s.strip()` | remove whitespace from both ends |
    | `s.split()` / `s.split(sep)` | break into a list of pieces |
    | `sep.join(pieces)` | glue pieces together with `sep` between them |
    | `s.replace(old, new)` | replace every occurrence |
    | `s.find(sub)` | index of the first match, or `-1` |
    | `s.count(sub)` | number of non-overlapping matches |
    | `s.startswith(p)`, `s.endswith(p)` | prefix / suffix tests |
    | `s.isdigit()`, `s.isalpha()`, `s.isalnum()` | character-class tests |

    ```python
    line = "   Hello, World!  "
    clean = line.strip()
    print(clean.lower(), clean.upper())
    print(clean.split(", "))
    print("-".join(["2026", "09", "25"]))
    print(clean.replace("World", "Python"))
    print(clean.find("World"), clean.find("xyz"))
    print("banana".count("a"), "42".isdigit(), "abc1".isalpha())
    ```

    `split()` with no argument splits on any run of whitespace and ignores leading and trailing spaces, which is usually what you want for messy input:

    ```python
    print("  too    many   spaces ".split())
    ```

    ## f-strings

    Put `f` before the quotes and write expressions inside `{}`. A format spec after `:` controls the layout.

    ```python
    name, score = "Ada", 93.456
    print(f"{name} scored {score:.1f}%")
    print(f"[{name:>8}]")      # right-align in 8 characters
    print(f"{7:03d}")           # pad with zeros
    print(f"{2 + 3 = }")        # '=' shows the expression too, handy for debugging
    ```

    ## Characters and codes

    `in` tests for a substring. `ord()` turns a character into its code number and `chr()` goes back. Looping over a string (next lesson) visits one character at a time.

    ```python
    print("py" in "python", "z" not in "python")
    print(ord("a"), ord("b"), ord("A"))
    print(chr(ord("a") + 2))
    print(ord("e") - ord("a"))    # position in the alphabet, from 0
    ```

    > **Key idea:** `s[::-1]` reverses, `split()`/`join()` convert between strings and lists, and f-strings handle formatting.
    """,
    exercises=[
        exercise(
            "palindrome-word",
            "Palindrome Word",
            """
            A **palindrome** reads the same forwards and backwards. Given a `word` made only of letters, return `True` if it's a palindrome **ignoring upper/lower case**, and `False` otherwise.
            """,
            """
            def is_palindrome(word: str) -> bool:
                lowered = word.lower()
                return lowered == lowered[::-1]
            """,
            examples=[
                case("Racecar", out=True, why="Lowercased, 'racecar' reversed is still 'racecar'."),
                case("Python", out=False),
            ],
            tests=[case("a", out=True), case("Aa", out=True), case("ab", out=False), case("Noon", out=True),
                   case("abcba", out=True), case("abca", out=False), case("LeveL", out=True),
                   case("xyzzyX", out=True), case("abcdefgfedcbaZ", out=False)],
            constraints=["`1 <= len(word) <= 1000`", "`word` contains only English letters"],
            hints=["Make the case consistent first with `.lower()`.", "`s[::-1]` is the reversed string."],
            explanation="""
            Lowercase the word so `R` and `r` compare equal, then compare it with its reverse, `lowered[::-1]`.

            **Complexity:** O(n) time and O(n) extra space for the copies.
            """,
        ),
        exercise(
            "format-name",
            "Tidy Name",
            """
            A sign-up form stores names messily: random capitalisation and extra spaces. Given `full_name`, which contains **exactly two words** (a first name then a last name) separated by one or more spaces, return it formatted as `"Last, First"` with each name capitalised (first letter upper case, the rest lower case).
            """,
            """
            def format_name(full_name: str) -> str:
                first, last = full_name.split()
                return f"{last.capitalize()}, {first.capitalize()}"
            """,
            examples=[
                case("ada lovelace", out="Lovelace, Ada"),
                case("  GRACE   hopper ", out="Hopper, Grace", why="Extra spaces are ignored and the case is fixed."),
            ],
            tests=[case("alan turing", out="Turing, Alan"), case("a b", out="B, A"),
                   case("LINUS TORVALDS", out="Torvalds, Linus"), case(" guido    van ", out="Van, Guido"),
                   case("mArGaReT hAmIlToN", out="Hamilton, Margaret"), case("x   Y")],
            constraints=["`full_name` contains exactly two words of English letters", "`1 <= len(full_name) <= 100`"],
            hints=["`split()` with no argument handles any amount of whitespace.",
                   "You can unpack the two words directly: `first, last = full_name.split()`.",
                   "`str.capitalize()` upper-cases the first letter and lower-cases the rest."],
            explanation="""
            `split()` with no arguments discards leading, trailing and repeated spaces and returns exactly two words here, which we unpack into `first` and `last`. `capitalize()` fixes the case, and an f-string assembles the result.

            **Complexity:** O(n).
            """,
        ),
    ],
)

# ---------------------------------------------------------------------------
# Lesson 3 · Control flow
# ---------------------------------------------------------------------------

CONTROL_FLOW = lesson(
    "control-flow",
    "Conditionals & Loops",
    "Make decisions with if, and repeat work with for and while.",
    minutes=20,
    body="""
    ## if / elif / else

    Python uses **indentation** (4 spaces) to mark which lines belong to a block. The first condition that's true wins, and the rest are skipped.

    ```python
    temperature = 23
    if temperature > 30:
        print("hot")
    elif temperature > 15:
        print("pleasant")
    else:
        print("cold")
    ```

    Any value can be used as a condition. `0`, `0.0`, `""` (empty string), `None` and empty collections are **falsy**; almost everything else is **truthy**.

    ```python
    name = ""
    if name:
        print("Hello,", name)
    else:
        print("No name given")
    ```

    ## for loops and range

    `for` visits each item of a sequence in turn. `range(stop)`, `range(start, stop)` and `range(start, stop, step)` produce integers, and `stop` is **never included**.

    ```python
    for i in range(5):
        print(i, end=" ")
    print()
    for i in range(2, 11, 2):
        print(i, end=" ")
    print()
    for i in range(5, 0, -1):
        print(i, end=" ")
    print()
    for ch in "hey":
        print(ch.upper(), end="")
    ```

    ## The accumulator pattern

    Start a variable at a neutral value, then update it inside the loop. This single pattern solves a huge number of problems.

    ```python
    total = 0
    for n in range(1, 101):
        total += n
    print("1 + 2 + ... + 100 =", total)

    vowels = 0
    for ch in "programming in python":
        if ch in "aeiou":
            vowels += 1
    print("vowels:", vowels)

    longest_run = run = 0
    for ch in "aabbbbcdd":
        run = run + 1 if ch == "b" else 0
        longest_run = max(longest_run, run)
    print("longest run of b:", longest_run)
    ```

    ## while loops

    Use `while` when you don't know in advance how many steps you need. Make sure something inside changes so the condition eventually becomes false, otherwise the loop never ends. (PyForge stops code that runs too long with **Time Limit Exceeded**.)

    ```python
    n = 1
    while n < 1000:
        n *= 2
    print(n)   # first power of two that is >= 1000

    n = 90210
    digits = 0
    while n > 0:
        n //= 10       # chop off the last digit
        digits += 1
    print("digits:", digits)
    ```

    ## break and continue

    `break` leaves the loop immediately. `continue` skips to the next iteration.

    ```python
    for n in range(2, 50):
        if n % 7 == 0:
            print("first multiple of 7:", n)
            break

    for n in range(10):
        if n % 3 == 0:
            continue
        print(n, end=" ")
    ```

    ## Nested loops

    A loop inside a loop runs the inner loop fully for **each** outer iteration. That's `rows × cols` steps in total, and this multiplication is where slow code usually comes from.

    ```python
    for row in range(1, 4):
        line = ""
        for col in range(1, 5):
            line += f"{row * col:4}"
        print(line)
    ```

    > **Key idea:** most loop problems are "walk through the input once, updating one or two variables as you go".
    """,
    exercises=[
        exercise(
            "digit-sum",
            "Sum of Digits",
            """
            Given a non-negative integer `n`, return the sum of its decimal digits.

            Try solving it with `//` and `%` in a `while` loop rather than converting to a string.
            """,
            """
            def digit_sum(n: int) -> int:
                total = 0
                while n > 0:
                    total += n % 10
                    n //= 10
                return total
            """,
            examples=[case(4827, out=21, why="4 + 8 + 2 + 7 = 21"), case(0, out=0)],
            tests=[case(9, out=9), case(10, out=1), case(999999999, out=81), case(1000000, out=1),
                   case(123456789, out=45), case(10 ** 18, out=1), case(10 ** 18 - 1, out=162)],
            constraints=["`0 <= n <= 10¹⁸`"],
            hints=["`n % 10` is the last digit and `n // 10` removes it.",
                   "Keep going while `n > 0`, adding each last digit to a running total."],
            explanation="""
            Repeatedly peel off the last digit with `n % 10`, add it to a total, then drop it with `n //= 10`. The loop ends when no digits remain. For `n = 0` the loop never runs and the answer is `0`.

            **Complexity:** O(d) where d is the number of digits.
            """,
        ),
        exercise(
            "collatz-steps",
            "Collatz Steps",
            """
            Start with a positive integer `n` and repeat:

            - if `n` is even, replace it with `n / 2`
            - if `n` is odd, replace it with `3n + 1`

            Return the number of steps needed to reach `1`.
            """,
            """
            def collatz_steps(n: int) -> int:
                steps = 0
                while n != 1:
                    if n % 2 == 0:
                        n //= 2
                    else:
                        n = 3 * n + 1
                    steps += 1
                return steps
            """,
            examples=[
                case(6, out=8, why="6 → 3 → 10 → 5 → 16 → 8 → 4 → 2 → 1 takes 8 steps."),
                case(1, out=0, why="Already at 1."),
            ],
            tests=[case(2, out=1), case(3, out=7), case(7, out=16), case(27, out=111), case(97, out=118),
                   case(871, out=178), case(1000000), case(837799)],
            constraints=["`1 <= n <= 10⁶`"],
            hints=["Use a `while n != 1` loop and count iterations.",
                   "Use `//` for halving so `n` stays an integer."],
            explanation="""
            Simulate the process with a `while` loop, counting iterations. Use `n //= 2` rather than `n /= 2`: `/` produces floats, which get less precise as numbers grow.

            **Complexity:** proportional to the number of steps (a few hundred for n ≤ 10⁶).
            """,
        ),
    ],
)

# ---------------------------------------------------------------------------
# Lesson 4 · Functions
# ---------------------------------------------------------------------------

FUNCTIONS = lesson(
    "functions",
    "Functions",
    "Package logic into reusable, testable pieces.",
    minutes=20,
    body="""
    A **function** takes inputs (parameters), does some work, and `return`s a result. Defining one with `def` doesn't run it; calling it does.

    ```python
    def greet(name, greeting="Hello"):
        return f"{greeting}, {name}!"

    print(greet("Ada"))
    print(greet("Grace", greeting="Welcome"))   # keyword argument
    ```

    `greeting="Hello"` is a **default value**: callers can leave it out.

    ## return vs print

    `return` hands a value back to the caller so it can be used in more code. `print` only shows text on screen. A function with no `return` gives back `None`.

    ```python
    def add(a, b):
        return a + b

    def shout(text):
        print(text.upper())

    result = add(2, 3) * 10
    print(result)
    print(shout("hi"))    # prints HI, then None
    ```

    ## Returning several values

    Return several values separated by commas. The caller can **unpack** them into separate names.

    ```python
    def min_max(a, b, c):
        return min(a, b, c), max(a, b, c)

    low, high = min_max(7, 2, 9)
    print(low, high)
    ```

    ## Scope

    Variables assigned inside a function are **local**: they exist only while the function runs and don't affect names outside it.

    ```python
    count = 0

    def bump():
        count = 99        # a new local variable; the outer count is untouched
        return count

    print(bump(), count)
    ```

    ## Type hints

    Starter code in PyForge (and on LeetCode) uses **type hints** to document what goes in and out. Python doesn't enforce them.

    ```python
    from typing import List

    def average(nums: List[int]) -> float:
        return sum(nums) / len(nums)

    print(average([3, 4, 8]))
    ```

    `List[int]` means "a list of ints", `Optional[int]` means "an int or None", and `-> bool` says the function returns a bool.

    ## Functions are values

    You can pass a function to another function. `lambda` writes a small one-expression function inline, and it's often used as a `key` for sorting.

    ```python
    def apply_twice(f, x):
        return f(f(x))

    print(apply_twice(lambda n: n * 3, 2))

    words = ["kiwi", "fig", "banana"]
    print(sorted(words, key=len))
    ```

    ## A classic trap: mutable defaults

    A default value is created **once**, when the function is defined. A list used as a default is shared between calls:

    ```python
    def add_item(item, basket=[]):
        basket.append(item)
        return basket

    print(add_item("apple"))
    print(add_item("pear"))            # surprise: ['apple', 'pear']

    def add_item_fixed(item, basket=None):
        if basket is None:
            basket = []
        basket.append(item)
        return basket

    print(add_item_fixed("apple"), add_item_fixed("pear"))
    ```

    ## Break problems into helpers

    Small functions with clear names make code easier to read and test.

    ```python
    def is_vowel(ch):
        return ch.lower() in "aeiou"

    def count_vowels(text):
        total = 0
        for ch in text:
            if is_vowel(ch):
                total += 1
        return total

    print(count_vowels("Functions Keep Code Tidy"))
    ```

    > **Key idea:** a function should do one job, take everything it needs as parameters, and return its result.
    """,
    exercises=[
        exercise(
            "is-prime",
            "Prime Check",
            """
            Return `True` if `n` is a **prime number**, meaning it's greater than 1 and its only divisors are 1 and itself. Otherwise return `False`.

            The hidden tests include numbers around two billion, so checking every possible divisor up to `n` will be too slow.
            """,
            """
            def is_prime(n: int) -> bool:
                if n < 2:
                    return False
                d = 2
                while d * d <= n:
                    if n % d == 0:
                        return False
                    d += 1
                return True
            """,
            examples=[case(7, out=True), case(1, out=False, why="1 is not prime by definition."),
                      case(9, out=False, why="9 = 3 × 3")],
            tests=[case(2, out=True), case(0, out=False), case(97, out=True), case(100, out=False),
                   case(7919, out=True), case(25, out=False), case(49, out=False),
                   case(2147483647, out=True), case(1000000007, out=True), case(999999999, out=False),
                   case(1999999973, out=True)],
            constraints=["`0 <= n <= 2 × 10⁹`"],
            hints=["If `n` has a divisor bigger than √n, it must also have one smaller than √n.",
                   "So you only need to test divisors `d` while `d * d <= n`.",
                   "Return `False` as soon as you find a divisor. Returning early is fine."],
            explanation="""
            Divisors come in pairs `d × (n // d)`, and one of each pair is at most √n. So if no `d` with `d * d <= n` divides `n`, nothing does. Testing `d * d <= n` avoids floating-point square roots.

            **Complexity:** O(√n) time, which is about 45,000 checks for n ≈ 2 × 10⁹ instead of two billion.
            """,
        ),
        exercise(
            "nth-prime",
            "The n-th Prime",
            """
            Return the `n`-th prime number, counting from 1: the 1st prime is `2`, the 2nd is `3`, the 3rd is `5`, and so on.

            A helper function is a great idea here.
            """,
            """
            def is_prime(k: int) -> bool:
                if k < 2:
                    return False
                d = 2
                while d * d <= k:
                    if k % d == 0:
                        return False
                    d += 1
                return True

            def nth_prime(n: int) -> int:
                count = 0
                candidate = 1
                while count < n:
                    candidate += 1
                    if is_prime(candidate):
                        count += 1
                return candidate
            """,
            entry="nth_prime",
            starter="""
            def is_prime(k: int) -> bool:
                # Optional helper: reuse your code from the previous exercise.
                pass

            def nth_prime(n: int) -> int:
                pass
            """,
            examples=[case(1, out=2), case(6, out=13, why="The primes are 2, 3, 5, 7, 11, 13, ...")],
            tests=[case(2, out=3), case(3, out=5), case(10, out=29), case(100, out=541), case(1000, out=7919),
                   case(2000, out=17389)],
            constraints=["`1 <= n <= 2000`"],
            hints=["Write `is_prime(k)` first, then count upward from 2 until you've seen `n` primes.",
                   "Keep two variables: the candidate number and how many primes you've found."],
            explanation="""
            Split the problem in two. `is_prime` answers one question well, and `nth_prime` just counts candidates that pass it. Keeping the logic separate makes each piece easy to check on its own.

            **Complexity:** roughly O(p√p) where p is the answer, which is fast enough for n ≤ 2000. The Sieve of Eratosthenes is faster when you need many primes.
            """,
        ),
    ],
)

# ---------------------------------------------------------------------------
# Challenge section 1
# ---------------------------------------------------------------------------

CHALLENGES = [
    challenge_problem(
        "digit-mirror",
        "Digit Mirror",
        """
        You're given an integer `x` that fits in a signed 32-bit range. Return the integer formed by writing the digits of `x` in reverse order, keeping its sign. Zeros that end up at the front disappear, so `120` becomes `21`.

        If the reversed value falls outside the signed 32-bit range `[-2³¹, 2³¹ - 1]`, return `0` instead.
        """,
        """
        class Solution:
            def reverse(self, x: int) -> int:
                sign = -1 if x < 0 else 1
                x = abs(x)
                result = 0
                while x > 0:
                    result = result * 10 + x % 10
                    x //= 10
                result *= sign
                if result < -2 ** 31 or result > 2 ** 31 - 1:
                    return 0
                return result
        """,
        difficulty="Easy",
        tags=["Math", "Loops", "Operators"],
        examples=[case(123, out=321), case(-123, out=-321), case(120, out=21)],
        tests=[case(0, out=0), case(1534236469, out=0), case(-2147483648, out=0), case(1463847412, out=2147483641),
               case(-2147483412, out=-2143847412), case(10, out=1), case(-1, out=-1), case(1000000003, out=0),
               case(2147483647, out=0), case(-10200, out=-201)],
        constraints=["`-2³¹ <= x <= 2³¹ - 1`"],
        hints=["Handle the sign separately: work with `abs(x)` and put the sign back at the end.",
               "Build the answer digit by digit: `result = result * 10 + x % 10`.",
               "Compare against `2 ** 31 - 1` and `-2 ** 31` at the end."],
        explanation="""
        Strip the sign, then pop digits off the end of `x` with `% 10` and push them onto `result` with `* 10 +`. This builds the reversed number without any string conversion. Reapply the sign and check the 32-bit bounds.

        Python ints never overflow, so a range check at the end is enough. In languages with fixed-size integers you'd have to check before each multiply.

        **Complexity:** O(log |x|) time (one step per digit), O(1) space.
        """,
    ),
    challenge_problem(
        "clean-palindrome",
        "Clean Palindrome",
        """
        A phrase is a **clean palindrome** if, after converting every upper-case letter to lower case and removing everything that isn't a letter or a digit, it reads the same forwards and backwards.

        Given a string `s`, return `True` if it's a clean palindrome and `False` otherwise.
        """,
        """
        class Solution:
            def isPalindrome(self, s: str) -> bool:
                cleaned = ""
                for ch in s:
                    if ch.isalnum():
                        cleaned += ch.lower()
                return cleaned == cleaned[::-1]
        """,
        difficulty="Easy",
        tags=["Strings", "Loops", "Conditionals"],
        examples=[
            case("A man, a plan, a canal: Panama", out=True, why='Cleaned, it becomes "amanaplanacanalpanama".'),
            case("race a car", out=False, why='"raceacar" is not a palindrome.'),
            case(" ", out=True, why="Nothing is left after cleaning. An empty string is a palindrome."),
        ],
        tests=[case("0P", out=False), case("ab_a", out=True), case("Was it a car or a cat I saw?", out=True),
               case("No 'x' in Nixon", out=True), case("abc", out=False), case(".,", out=True), case("1a2", out=False),
               case("a", out=True), case("Madam, I'm Adam.", out=True), case("12321", out=True), case("123abc321", out=False),
               case(gen("rand_str(50000, seed=11) + rand_str(50000, seed=11)[::-1]"), out=True),
               case(gen("rand_str(60000, 'ab ,.', seed=4) + 'x'"))],
        constraints=["`1 <= len(s) <= 2 × 10⁵`", "`s` contains printable ASCII characters"],
        hints=["`ch.isalnum()` is `True` for letters and digits.",
               "Build a cleaned, lower-cased version of `s`, then compare it with its reverse.",
               "Watch out: digits count, so `\"0P\"` is not a palindrome."],
        explanation="""
        Filter and normalise in one pass: keep characters where `ch.isalnum()` is true, lower-cased. Then compare the cleaned string with `cleaned[::-1]`.

        You can also avoid building the cleaned string by walking two indexes inward from both ends and skipping non-alphanumeric characters. You'll meet that **two pointers** technique in Module 3.

        **Complexity:** O(n) time, O(n) space (O(1) with two pointers).
        """,
    ),
    challenge_problem(
        "spreadsheet-column",
        "Spreadsheet Column Number",
        """
        Spreadsheet columns are labelled `A, B, ..., Z, AA, AB, ..., AZ, BA, ..., ZZ, AAA, ...`.

        Given a column label `columnTitle`, return its column number, where `A` is 1.
        """,
        """
        class Solution:
            def titleToNumber(self, columnTitle: str) -> int:
                result = 0
                for ch in columnTitle:
                    result = result * 26 + (ord(ch) - ord("A") + 1)
                return result
        """,
        difficulty="Easy",
        tags=["Strings", "Math", "Loops"],
        examples=[case("A", out=1), case("AB", out=28, why="A = 1, then 1 × 26 + 2 = 28."), case("ZY", out=701)],
        tests=[case("Z", out=26), case("AA", out=27), case("AZ", out=52), case("BA", out=53), case("ZZ", out=702),
               case("AAA", out=703), case("FXSHRXW", out=2147483647), case("PYTHON")],
        constraints=["`1 <= len(columnTitle) <= 7`", "`columnTitle` contains only upper-case English letters",
                     "The answer fits in `[1, 2³¹ - 1]`"],
        hints=["`ord(ch) - ord('A') + 1` maps A→1 ... Z→26.",
               "It's like reading a number in base 26: multiply the running total by 26 before adding each letter."],
        explanation="""
        Treat the label as a base-26 number whose digits run from 1 to 26 instead of 0 to 25. Read left to right, shifting the running total one "place" (`× 26`) before adding each letter's value, the same way you'd read `"123"` as `((1 × 10) + 2) × 10 + 3`.

        **Complexity:** O(n) time, O(1) space.
        """,
    ),
    challenge_problem(
        "humble-number",
        "Humble Number",
        """
        A **humble number** is a positive integer whose prime factors are limited to `2`, `3` and `5`. By convention, `1` is humble because it has no prime factors at all.

        Given an integer `n`, return `True` if `n` is humble.
        """,
        """
        class Solution:
            def isHumble(self, n: int) -> bool:
                if n <= 0:
                    return False
                for p in (2, 3, 5):
                    while n % p == 0:
                        n //= p
                return n == 1
        """,
        difficulty="Easy",
        tags=["Math", "Loops", "Functions"],
        examples=[case(6, out=True, why="6 = 2 × 3"), case(1, out=True),
                  case(14, out=False, why="14 = 2 × 7, and 7 is not allowed.")],
        tests=[case(0, out=False), case(-6, out=False), case(8, out=True), case(30, out=True), case(49, out=False),
               case(2147483647, out=False), case(-2147483648, out=False), case(1000000000, out=True),
               case(7, out=False), case(1073741824, out=True), case(905391974)],
        constraints=["`-2³¹ <= n <= 2³¹ - 1`"],
        hints=["Negative numbers and zero are never humble.",
               "Divide out every factor of 2, then 3, then 5. What must be left?"],
        explanation="""
        Divide `n` by 2 as long as it divides evenly, then by 3, then by 5. If only those primes were present, nothing but `1` remains. Any leftover value greater than 1 contains some other prime factor. Zero and negatives are rejected first, which also stops `0 % 2 == 0` from looping forever.

        **Complexity:** O(log n) time, since each division at least halves `n`.
        """,
    ),
    challenge_problem(
        "capital-usage",
        "Capital Usage",
        """
        A word uses capitals **correctly** when one of these is true:

        - every letter is upper case, like `"NASA"`
        - every letter is lower case, like `"python"`
        - only the first letter is upper case, like `"Guido"`

        Given a `word`, return `True` if its capital usage is correct.
        """,
        """
        class Solution:
            def detectCapitalUse(self, word: str) -> bool:
                if word.isupper() or word.islower():
                    return True
                return word[0].isupper() and word[1:].islower()
        """,
        difficulty="Easy",
        tags=["Strings", "Conditionals"],
        examples=[case("NASA", out=True), case("FlaG", out=False), case("Guido", out=True)],
        tests=[case("g", out=True), case("G", out=True), case("ffffffffffffffffffffF", out=False), case("mL", out=False),
               case("Ab", out=True), case("aB", out=False), case("ABc", out=False), case("abc", out=True),
               case("PyForge", out=False), case("ZZZZz", out=False)],
        constraints=["`1 <= len(word) <= 100`", "`word` contains only English letters"],
        hints=["Python has `str.isupper()` and `str.islower()`.",
               "Check the three allowed shapes one by one. The last one is about `word[0]` and `word[1:]`."],
        explanation="""
        Check each allowed pattern with the built-in case tests. `isupper()` and `islower()` cover the first two. For the third, the first character must be upper case and the rest, `word[1:]`, lower case. A one-letter word is caught by the first two checks, which matters because `"".islower()` is `False`.

        **Complexity:** O(n).
        """,
    ),
]

MODULE = module(
    "foundations",
    "Python Foundations",
    "Variables, strings, loops and functions: the building blocks of every program.",
    lessons=[VARIABLES, STRINGS, CONTROL_FLOW, FUNCTIONS],
    challenges=CHALLENGES,
    challenge_title="Checkpoint 1 · Foundations",
    challenge_blurb="Five Easy problems that mix arithmetic, string handling, loops and functions.",
)
