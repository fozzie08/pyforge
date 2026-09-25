from content.dsl import case, challenge_problem, exercise, gen, lesson, module

# ---------------------------------------------------------------------------
# Lesson 1 · Classes & objects
# ---------------------------------------------------------------------------

CLASSES = lesson(
    "classes",
    "Classes & Objects",
    "Bundle data with the methods that use it, and design your own types.",
    minutes=25,
    body="""
    A **class** bundles data (attributes) with the functions that act on it (methods). Each object made from a class is an **instance** with its own data.

    ```python
    class Counter:
        def __init__(self, start=0):     # runs when you create an instance
            self.value = start           # self is the instance being set up

        def increment(self, by=1):
            self.value += by
            return self.value

    a = Counter()
    b = Counter(10)
    a.increment()
    a.increment()
    b.increment(5)
    print(a.value, b.value)
    ```

    `self` is how a method refers to its own instance. Writing `a.increment()` really means `Counter.increment(a)`.

    ## Printing objects nicely

    Define `__repr__` to control how an object is displayed:

    ```python
    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __repr__(self):
            return f"Point({self.x}, {self.y})"

        def distance_to(self, other):
            return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    p, q = Point(0, 0), Point(3, 4)
    print(p, q, p.distance_to(q))
    ```

    ## Special methods

    Methods with double underscores ("dunder" methods) let your objects work with Python's built-in syntax:

    ```python
    class Playlist:
        def __init__(self, songs):
            self.songs = list(songs)

        def __len__(self):
            return len(self.songs)

        def __contains__(self, song):
            return song in self.songs

        def __eq__(self, other):
            return isinstance(other, Playlist) and self.songs == other.songs

    mix = Playlist(["Intro", "Anthem"])
    print(len(mix), "Anthem" in mix, mix == Playlist(["Intro", "Anthem"]))
    ```

    ## Class attributes vs instance attributes

    ```python
    class Dog:
        species = "Canis familiaris"      # shared by every Dog

        def __init__(self, name):
            self.name = name              # different for each Dog

    rex, fido = Dog("Rex"), Dog("Fido")
    print(rex.species, fido.species, rex.name, fido.name)
    ```

    ## Objects that wrap data structures

    Most **design** problems are a class that wraps a list, dict or deque, with methods that keep it consistent:

    ```python
    from collections import deque

    class RecentHistory:
        def __init__(self, capacity):
            self.capacity = capacity
            self.items = deque()

        def visit(self, page):
            self.items.append(page)
            if len(self.items) > self.capacity:
                self.items.popleft()

        def recent(self):
            return list(self.items)

    h = RecentHistory(3)
    for page in ["home", "news", "sport", "weather"]:
        h.visit(page)
    print(h.recent())
    ```

    ## How design problems are tested

    LeetCode-style design problems test your class with two lists: the **operations** to call and their **arguments**. The first operation creates the object.

    ```text
    operations = ["RecentHistory", "visit", "visit", "recent"]
    arguments  = [[2],             ["a"],   ["b"],   []       ]
    output     = [None,            None,    None,    ["a", "b"]]
    ```

    That runs `h = RecentHistory(2)`, `h.visit("a")`, `h.visit("b")`, `h.recent()` and compares every return value. Methods that return nothing produce `None`.

    ## Inheritance

    A class can extend another, reusing its methods and overriding the ones that differ:

    ```python
    class Shape:
        def area(self):
            return 0

        def describe(self):
            return f"{type(self).__name__} with area {self.area():.1f}"

    class Circle(Shape):
        def __init__(self, r):
            self.r = r

        def area(self):
            return 3.14159 * self.r ** 2

    class Square(Shape):
        def __init__(self, side):
            self.side = side

        def area(self):
            return self.side ** 2

    for shape in [Circle(1), Square(3)]:
        print(shape.describe())
    ```

    > **Key idea:** a class keeps data and the operations on it together. `__init__` sets up the state, and methods read and update it through `self`.
    """,
    exercises=[
        exercise(
            "bank-account",
            "Bank Account",
            """
            Design a `BankAccount` class:

            - `BankAccount(balance)` opens an account with a starting `balance`.
            - `deposit(amount)` adds `amount` and **returns the new balance**.
            - `withdraw(amount)` removes `amount` if the balance is large enough and returns `True`. Otherwise it changes nothing and returns `False`.
            - `get_balance()` returns the current balance.
            """,
            """
            class BankAccount:
                def __init__(self, balance: int):
                    self.balance = balance

                def deposit(self, amount: int) -> int:
                    self.balance += amount
                    return self.balance

                def withdraw(self, amount: int) -> bool:
                    if amount > self.balance:
                        return False
                    self.balance -= amount
                    return True

                def get_balance(self) -> int:
                    return self.balance
            """,
            examples=[case(["BankAccount", "deposit", "withdraw", "withdraw", "get_balance"],
                           [[100], [50], [30], [500], []], out=[None, 150, True, False, 120],
                           why="Start at 100, deposit 50 (150), withdraw 30 (120). Withdrawing 500 fails, so the balance stays 120.")],
            tests=[case(["BankAccount", "get_balance"], [[0], []], out=[None, 0]),
                   case(["BankAccount", "withdraw", "withdraw", "get_balance"], [[10], [10], [1], []],
                        out=[None, True, False, 0]),
                   case(["BankAccount", "deposit", "deposit", "withdraw", "get_balance"], [[5], [0], [7], [12], []],
                        out=[None, 5, 12, True, 0])],
            constraints=["`0 <= balance, amount <= 10⁶`", "At most 1000 calls"],
            hints=["Store the balance on `self` in `__init__`.",
                   "`withdraw` must check before it subtracts."],
            explanation="""
            The object's only state is `self.balance`. Each method reads or updates it. `withdraw` checks the balance first so a failed withdrawal leaves the account unchanged. The operations/arguments format creates the object once and then calls methods on it in order.

            **Complexity:** O(1) per call.
            """,
        ),
        exercise(
            "moving-average",
            "Moving Average",
            """
            Design a `MovingAverage` class for a stream of numbers:

            - `MovingAverage(size)` sets the window size.
            - `next(val)` adds `val` to the stream and returns the average of the **last `size` values** (or of all values so far, if there are fewer than `size`).

            Each call should be O(1).
            """,
            """
            class MovingAverage:
                def __init__(self, size: int):
                    self.size = size
                    self.window = deque()
                    self.total = 0

                def next(self, val: int) -> float:
                    self.window.append(val)
                    self.total += val
                    if len(self.window) > self.size:
                        self.total -= self.window.popleft()
                    return self.total / len(self.window)
            """,
            examples=[case(["MovingAverage", "next", "next", "next", "next"], [[3], [1], [10], [3], [5]],
                           out=[None, 1.0, 5.5, 4.666666666666667, 6.0],
                           why="Averages of [1], [1, 10], [1, 10, 3], then [10, 3, 5] once the window is full.")],
            tests=[case(["MovingAverage", "next", "next"], [[1], [4], [-2]], out=[None, 4.0, -2.0]),
                   case(["MovingAverage", "next", "next", "next"], [[5], [0], [0], [9]], out=[None, 0.0, 0.0, 3.0]),
                   case(gen("['MovingAverage'] + ['next'] * 10**4"),
                        gen("[[1000]] + [[v] for v in rand_list(10**4, -1000, 1000, seed=51)]"))],
            constraints=["`1 <= size <= 1000`", "`-10⁵ <= val <= 10⁵`", "At most 10⁴ calls to `next`"],
            hints=["A `deque` makes a natural window: append on the right, popleft when it's too long.",
                   "Keep a running total instead of calling `sum` on every call."],
            explanation="""
            Store the window in a deque plus a running `total`. Each `next` adds the new value. If the window has grown past `size`, it pops the oldest value and subtracts it. The average is `total / len(window)`, so there's no re-summing.

            **Complexity:** O(1) per call, O(size) memory.
            """,
        ),
    ],
)

# ---------------------------------------------------------------------------
# Lesson 2 · Linked lists
# ---------------------------------------------------------------------------

LINKED_LISTS = lesson(
    "linked-lists",
    "Linked Lists",
    "Chains of nodes: traversal, dummy heads and fast/slow pointers.",
    minutes=25,
    setup="""
    def from_list(values):
        dummy = tail = ListNode()
        for v in values:
            tail.next = ListNode(v)
            tail = tail.next
        return dummy.next

    def to_list(head):
        out = []
        while head:
            out.append(head.val)
            head = head.next
        return out
    """,
    body="""
    A **linked list** is a chain of nodes. Each node holds a value and a reference to the next node, and the last node points to `None`. You can only reach a node by following the chain from the **head**.

    ```python
    class ListNode:
        def __init__(self, val=0, next=None):
            self.val = val
            self.next = next

    head = ListNode(1, ListNode(2, ListNode(3)))       # 1 -> 2 -> 3
    print(head.val, head.next.val, head.next.next.val)
    print(head.next.next.next)                         # the end
    ```

    In exercises, `ListNode` is already defined for you, as on LeetCode. Test cases write a linked list as a Python list: `[1, 2, 3]` means `1 -> 2 -> 3`, and `[]` means an empty list (`None`).

    Every example in this lesson also has two helpers ready: `from_list(values)` builds a linked list and `to_list(head)` reads one back.

    ## Walking the chain

    ```python
    def length(head):
        count = 0
        node = head
        while node:              # stops after the last node
            count += 1
            node = node.next
        return count

    head = from_list([4, 8, 15, 16, 23])
    print(length(head), to_list(head))
    ```

    ## Linked lists vs Python lists

    | Operation | Python list | Linked list |
    |---|---|---|
    | read the i-th item | O(1) | O(n): walk there |
    | insert or delete at the front | O(n) | O(1) |
    | insert or delete after a node you hold | O(n) | O(1) |

    ## Inserting and deleting

    Changing a linked list means **re-pointing `next` references**. Draw boxes and arrows when in doubt.

    ```python
    head = from_list([1, 2, 4])
    two = head.next
    two.next = ListNode(3, two.next)      # insert 3 after 2
    print(to_list(head))

    head.next = head.next.next            # unlink the node after head
    print(to_list(head))
    ```

    ## The dummy node trick

    Deleting the head is usually a special case, because the head has no node before it. Put a **dummy** node in front and every real node has a predecessor:

    ```python
    def remove_all(head, target):
        dummy = ListNode(0, head)
        prev = dummy
        while prev.next:
            if prev.next.val == target:
                prev.next = prev.next.next    # skip over it
            else:
                prev = prev.next
        return dummy.next                     # the (possibly new) head

    print(to_list(remove_all(from_list([7, 7, 1, 7, 2]), 7)))
    ```

    ## Fast and slow pointers

    Move one pointer 1 step at a time and another 2 steps. On a list with a **cycle**, the fast pointer eventually laps the slow one. Otherwise it falls off the end.

    ```python
    def has_cycle(head):
        slow = fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            if slow is fast:
                return True
        return False

    a = from_list([1, 2, 3, 4])
    print(has_cycle(a))
    a.next.next.next.next = a.next        # point 4 back at 2
    print(has_cycle(a))
    ```

    When the fast pointer reaches the end, the slow pointer has gone half as far, which is handy for finding the middle.

    ## Before you re-point, save

    Overwriting `node.next` loses the rest of the chain unless you saved it first. Reversing a list (the first problem in this module's checkpoint) keeps three variables for exactly this reason: the previous node, the current node, and the saved next node.

    > **Key idea:** save `node.next` before you overwrite it, use a dummy node to avoid special cases at the head, and use fast/slow pointers to find middles and cycles.
    """,
    exercises=[
        exercise(
            "middle-node",
            "Middle of the Chain",
            """
            Given the `head` of a non-empty linked list, return the **middle node**. If there are two middle nodes, return the **second** one.

            The judge prints the list starting from the node you return.
            """,
            """
            def middle_node(head: Optional[ListNode]) -> Optional[ListNode]:
                slow = fast = head
                while fast and fast.next:
                    slow = slow.next
                    fast = fast.next.next
                return slow
            """,
            examples=[case([1, 2, 3, 4, 5], out=[3, 4, 5], why="The middle node holds 3."),
                      case([1, 2, 3, 4, 5, 6], out=[4, 5, 6], why="3 and 4 are both middles. Return the second.")],
            tests=[case([1], out=[1]), case([1, 2], out=[2]), case([1, 2, 3], out=[2, 3]),
                   case(gen("list(range(10**4))"))],
            constraints=["The list has between `1` and `10⁴` nodes"],
            hints=["Move a slow pointer one step and a fast pointer two steps at a time.",
                   "When the fast pointer can't move any more, where is the slow one?"],
            explanation="""
            The fast pointer moves twice as fast, so when it reaches the end the slow pointer is halfway. The loop condition `fast and fast.next` stops at the right moment for both odd and even lengths, landing on the second middle when there are two. This takes one pass and no counting.

            **Complexity:** O(n) time, O(1) space.
            """,
        ),
        exercise(
            "dedupe-sorted-list",
            "Remove Duplicates from a Sorted Chain",
            """
            The linked list starting at `head` is sorted in non-decreasing order. Delete nodes so that each value appears only **once**, and return the head of the result, which should still be sorted.
            """,
            """
            def delete_duplicates(head: Optional[ListNode]) -> Optional[ListNode]:
                node = head
                while node and node.next:
                    if node.next.val == node.val:
                        node.next = node.next.next
                    else:
                        node = node.next
                return head
            """,
            examples=[case([1, 1, 2], out=[1, 2]), case([1, 1, 2, 3, 3], out=[1, 2, 3])],
            tests=[case([], out=[]), case([1, 1, 1], out=[1]), case([1, 2, 3], out=[1, 2, 3]),
                   case([-1, 0, 0, 0, 5, 5], out=[-1, 0, 5]), case(gen("sorted(rand_list(5000, 0, 100, seed=52))"))],
            constraints=["The list has between `0` and `5000` nodes", "Values are sorted in non-decreasing order"],
            hints=["In a sorted list, duplicates sit next to each other.",
                   "If `node.next` has the same value, unlink it and stay put. Otherwise move on."],
            explanation="""
            Walk the list. Whenever the next node repeats the current value, skip it by re-pointing `node.next` past it, and **don't advance**, because the new next node might be another duplicate. Advance only when the next value differs.

            **Complexity:** O(n) time, O(1) space.
            """,
        ),
    ],
)

# ---------------------------------------------------------------------------
# Lesson 3 · Binary trees
# ---------------------------------------------------------------------------

TREES = lesson(
    "binary-trees",
    "Binary Trees",
    "Recursive structures: depth-first and breadth-first traversal, BSTs.",
    minutes=30,
    setup="""
    def build_tree(values):
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
    """,
    body="""
    A **binary tree** is made of nodes that each hold a value and up to two children, `left` and `right`. The top node is the **root**. Nodes with no children are **leaves**.

    ```text
            3          ← root
           / \\
          9   20
             /  \\
            15   7     ← leaves: 9, 15 and 7
    ```

    ```python
    root = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
    print(root.val, root.left.val, root.right.left.val)
    print(root.left.left)        # a missing child is None
    ```

    Test cases write trees in **level order**: top to bottom, left to right, with `None` for missing children. The tree above is `[3, 9, 20, None, None, 15, 7]`. In this lesson's examples, `build_tree(values)` turns such a list into nodes for you.

    ## Recursion is natural for trees

    Every subtree is itself a tree, so most tree functions follow one shape: handle the empty tree (`None`), then combine the answers from the left and right subtrees.

    ```python
    def count_nodes(node):
        if node is None:
            return 0
        return 1 + count_nodes(node.left) + count_nodes(node.right)

    def height(node):
        if node is None:
            return 0
        return 1 + max(height(node.left), height(node.right))

    root = build_tree([3, 9, 20, None, None, 15, 7])
    print(count_nodes(root), height(root))
    ```

    ## Depth-first traversals

    The three classic orders differ only in **when** you record the current node:

    - **preorder**: the node, then its left subtree, then its right subtree
    - **inorder**: left subtree, then the node, then right subtree
    - **postorder**: left subtree, right subtree, then the node

    ```python
    def preorder(node, out):
        if node is None:
            return out
        out.append(node.val)        # record before visiting the children
        preorder(node.left, out)
        preorder(node.right, out)
        return out

    root = build_tree([1, 2, 3, 4, 5, None, 6])
    print(preorder(root, []))
    ```

    ## Breadth-first: level by level

    BFS with a queue visits the tree one level at a time:

    ```python
    from collections import deque

    def bfs_values(root):
        if root is None:
            return []
        out = []
        queue = deque([root])
        while queue:
            node = queue.popleft()
            out.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        return out

    print(bfs_values(build_tree([1, 2, 3, 4, 5, None, 6])))
    ```

    ## Binary search trees

    In a **binary search tree** (BST), every value in a node's left subtree is smaller than the node's value, and every value in its right subtree is larger. A search discards one whole side at each step, like binary search.

    ```python
    def bst_insert(node, val):
        if node is None:
            return TreeNode(val)
        if val < node.val:
            node.left = bst_insert(node.left, val)
        else:
            node.right = bst_insert(node.right, val)
        return node

    def bst_contains(node, val):
        while node:
            if val == node.val:
                return True
            node = node.left if val < node.val else node.right
        return False

    bst = None
    for v in [8, 3, 10, 1, 6, 14]:
        bst = bst_insert(bst, v)
    print(bst_contains(bst, 6), bst_contains(bst, 7))
    ```

    A balanced BST has height about log₂(n), so searches are O(log n). If values arrive already sorted, the tree becomes a long chain and searches degrade to O(n).

    > **Key idea:** most tree problems are "answer for `None`, then combine the left and right answers". Use a queue when the problem is about levels.
    """,
    exercises=[
        exercise(
            "count-leaves",
            "Count the Leaves",
            """
            Given the `root` of a binary tree, return how many **leaves** it has. A leaf is a node with no children.
            """,
            """
            def count_leaves(root: Optional[TreeNode]) -> int:
                if root is None:
                    return 0
                if root.left is None and root.right is None:
                    return 1
                return count_leaves(root.left) + count_leaves(root.right)
            """,
            examples=[case([3, 9, 20, None, None, 15, 7], out=3, why="The leaves are 9, 15 and 7."),
                      case([1], out=1), case([], out=0)],
            tests=[case([1, 2], out=1), case([1, 2, 3, 4, 5, 6, 7], out=4), case([1, None, 2, None, 3], out=1),
                   case([1, 2, 3, None, 4, 5], out=2), case(gen("list(range(1, 1024))"), out=512)],
            constraints=["The tree has between `0` and `2000` nodes"],
            hints=["An empty tree has 0 leaves. A node with no children is 1 leaf.",
                   "Otherwise, the leaves of a tree are the leaves of its left subtree plus those of its right."],
            explanation="""
            There are two base cases: `None` contributes 0, and a childless node contributes 1. Every other node's answer is the sum of its subtrees' answers. The leaf check must come before recursing, otherwise a leaf would report 0 + 0.

            **Complexity:** O(n) time, O(h) space for the recursion, where h is the tree height.
            """,
        ),
        exercise(
            "inorder-traversal",
            "Inorder Traversal",
            """
            Return the values of a binary tree in **inorder**: left subtree, then the node, then right subtree.

            For a binary search tree, inorder visits the values in sorted order.
            """,
            """
            def inorder(root: Optional[TreeNode]) -> List[int]:
                out = []

                def visit(node):
                    if node is None:
                        return
                    visit(node.left)
                    out.append(node.val)
                    visit(node.right)

                visit(root)
                return out
            """,
            examples=[case([1, None, 2, 3], out=[1, 3, 2]), case([], out=[]),
                      case([4, 2, 6, 1, 3, 5, 7], out=[1, 2, 3, 4, 5, 6, 7], why="A BST, so inorder is sorted.")],
            tests=[case([1], out=[1]), case([1, 2], out=[2, 1]), case([1, None, 2], out=[1, 2]),
                   case([5, 3, 8, 1, 4, 7, 9, None, 2]), case(gen("list(range(1, 1024))")),
                   case(gen("[1] + sum([[None, i] for i in range(2, 201)], [])"))],
            constraints=["The tree has between `0` and `1500` nodes", "The tree's height is at most 200"],
            hints=["Adapt the preorder function from the lesson. Only the position of the `append` changes.",
                   "A nested helper function can append to a list defined in the outer function."],
            explanation="""
            Recurse left, record the node, recurse right. A nested helper that appends to one shared list avoids building and joining many small lists. An iterative version uses an explicit stack: push left children as far as possible, pop one, record it, then move to its right child.

            **Complexity:** O(n) time, O(h) recursion depth.
            """,
        ),
    ],
)

# ---------------------------------------------------------------------------
# Challenge section 5
# ---------------------------------------------------------------------------

CHALLENGES = [
    challenge_problem(
        "reverse-chain",
        "Reverse the Chain",
        """
        Given the `head` of a singly-linked list, reverse the list and return the new head.
        """,
        """
        class Solution:
            def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
                prev = None
                current = head
                while current:
                    nxt = current.next
                    current.next = prev
                    prev = current
                    current = nxt
                return prev
        """,
        difficulty="Easy",
        tags=["Linked List", "Loops", "Classes"],
        examples=[case([1, 2, 3, 4, 5], out=[5, 4, 3, 2, 1]), case([1, 2], out=[2, 1]), case([], out=[])],
        tests=[case([1], out=[1]), case([7, 7, 1], out=[1, 7, 7]), case([-1, 0, 1], out=[1, 0, -1]),
               case(gen("list(range(900))"))],
        constraints=["The list has between `0` and `900` nodes", "`-5000 <= Node.val <= 5000`"],
        hints=["Walk the list once, turning each `next` arrow around to point backwards.",
               "Before you overwrite `current.next`, save it, or you lose the rest of the list.",
               "Keep three variables: `prev`, `current` and `nxt`. What should the new head be at the end?"],
        explanation="""
        Walk the list, flipping each arrow. For each node, save `nxt = current.next`, point `current.next` back at `prev`, then advance: `prev = current` and `current = nxt`. When `current` becomes `None`, `prev` is the old tail, which is the new head.

        Recursive version: reverse the rest of the list, then set `head.next.next = head` and `head.next = None`. It uses O(n) stack space.

        **Complexity:** O(n) time, O(1) space.
        """,
    ),
    challenge_problem(
        "merge-sorted-chains",
        "Merge Sorted Chains",
        """
        You're given the heads of two linked lists, `list1` and `list2`, each sorted in non-decreasing order.

        Merge them into **one sorted list** by splicing their existing nodes together, and return its head.
        """,
        """
        class Solution:
            def mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
                dummy = tail = ListNode()
                while list1 and list2:
                    if list1.val <= list2.val:
                        tail.next, list1 = list1, list1.next
                    else:
                        tail.next, list2 = list2, list2.next
                    tail = tail.next
                tail.next = list1 or list2
                return dummy.next
        """,
        difficulty="Easy",
        tags=["Linked List", "Two Pointers", "Dummy Node"],
        examples=[case([1, 2, 4], [1, 3, 4], out=[1, 1, 2, 3, 4, 4]), case([], [], out=[]), case([], [0], out=[0])],
        tests=[case([5], [1, 2, 3], out=[1, 2, 3, 5]), case([1, 1], [1], out=[1, 1, 1]),
               case([-10, 0, 10], [-5, 5], out=[-10, -5, 0, 5, 10]), case([2], [], out=[2]),
               case(gen("sorted(rand_list(450, -100, 100, seed=53))"), gen("sorted(rand_list(450, -100, 100, seed=54))"))],
        constraints=["Each list has between `0` and `450` nodes", "Both lists are sorted in non-decreasing order"],
        hints=["This is the merge step from the two-pointers lesson, applied to linked lists.",
               "A dummy head node means you never need a special case for the first node.",
               "When one list runs out, attach whatever remains of the other in one step."],
        explanation="""
        Keep a `tail` pointer, starting at a dummy node. Repeatedly attach the smaller of the two front nodes and advance that list. When one list is empty, link the remainder of the other in a single assignment, since it's already sorted. Return `dummy.next`.

        **Complexity:** O(n + m) time, O(1) extra space, because the existing nodes are re-linked rather than copied.
        """,
    ),
    challenge_problem(
        "mirror-tree",
        "Mirror the Tree",
        """
        Given the `root` of a binary tree, turn it into its **mirror image** by swapping the left and right children of every node. Return the root.

        ```text
              4                 4
            /   \\             /   \\
           2     7    →      7     2
          / \\   / \\         / \\   / \\
         1   3 6   9       9   6 3   1
        ```
        """,
        """
        class Solution:
            def invertTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
                if root is None:
                    return None
                root.left, root.right = self.invertTree(root.right), self.invertTree(root.left)
                return root
        """,
        difficulty="Easy",
        tags=["Binary Tree", "Recursion", "Classes"],
        examples=[case([4, 2, 7, 1, 3, 6, 9], out=[4, 7, 2, 9, 6, 3, 1]), case([2, 1, 3], out=[2, 3, 1]), case([], out=[])],
        tests=[case([1], out=[1]), case([1, 2], out=[1, None, 2]), case([1, None, 2], out=[1, 2]),
               case([1, 2, 3, 4, None, None, 5], out=[1, 3, 2, 5, None, None, 4]), case(gen("list(range(1, 1024))"))],
        constraints=["The tree has between `0` and `1500` nodes"],
        hints=["Mirroring a tree means mirroring both subtrees and then swapping them.",
               "What's the mirror of an empty tree?"],
        explanation="""
        The mirror of a tree is its root with the **mirrored right subtree on the left** and the **mirrored left subtree on the right**. Python's tuple assignment evaluates both recursive calls before assigning, so the swap is safe in one line. An iterative BFS that swaps children at every node works too.

        **Complexity:** O(n) time, O(h) recursion depth.
        """,
    ),
    challenge_problem(
        "level-by-level",
        "Level by Level",
        """
        Given the `root` of a binary tree, return its values grouped **by level**, from top to bottom, with each level listed left to right.
        """,
        """
        class Solution:
            def levelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
                if root is None:
                    return []
                levels = []
                queue = deque([root])
                while queue:
                    level = []
                    for _ in range(len(queue)):
                        node = queue.popleft()
                        level.append(node.val)
                        if node.left:
                            queue.append(node.left)
                        if node.right:
                            queue.append(node.right)
                    levels.append(level)
                return levels
        """,
        difficulty="Medium",
        tags=["Binary Tree", "BFS", "Queues"],
        examples=[case([3, 9, 20, None, None, 15, 7], out=[[3], [9, 20], [15, 7]]), case([1], out=[[1]]), case([], out=[])],
        tests=[case([1, 2, 3, 4, 5, 6, 7], out=[[1], [2, 3], [4, 5, 6, 7]]), case([1, 2, None, 3, None, 4], out=[[1], [2], [3], [4]]),
               case([1, None, 2, None, 3], out=[[1], [2], [3]]), case(gen("list(range(1, 2048))")),
               case(gen("[i if i % 7 else None for i in range(1, 3000)]"))],
        constraints=["The tree has between `0` and `2000` nodes"],
        hints=["BFS visits nodes level by level, but you need to know where each level ends.",
               "At the start of each round, `len(queue)` is exactly the number of nodes on the current level."],
        explanation="""
        Run BFS, one level per round. When a round starts, the queue holds exactly the current level's nodes, so pop `len(queue)` of them into a list while queueing their children for the next round. A DFS that passes the depth along and appends to `levels[depth]` also works.

        **Complexity:** O(n) time, O(width) queue space.
        """,
    ),
    challenge_problem(
        "min-stack",
        "Min Stack",
        """
        Design a stack that can also report its **minimum element** in constant time.

        - `MinStack()` creates an empty stack.
        - `push(val)` pushes `val` onto the stack.
        - `pop()` removes the top element.
        - `top()` returns the top element.
        - `getMin()` returns the smallest element currently in the stack.

        **Every** method must run in O(1) time. `pop`, `top` and `getMin` are only called on a non-empty stack.
        """,
        """
        class MinStack:
            def __init__(self):
                self.stack = []

            def push(self, val: int) -> None:
                current_min = min(val, self.stack[-1][1]) if self.stack else val
                self.stack.append((val, current_min))

            def pop(self) -> None:
                self.stack.pop()

            def top(self) -> int:
                return self.stack[-1][0]

            def getMin(self) -> int:
                return self.stack[-1][1]
        """,
        difficulty="Medium",
        tags=["Design", "Stack", "Classes", "Tuples"],
        examples=[case(["MinStack", "push", "push", "push", "getMin", "pop", "top", "getMin"],
                       [[], [4], [7], [1], [], [], [], []], out=[None, None, None, None, 1, None, 7, 4],
                       why="After pushing 4, 7 and 1 the minimum is 1. Popping 1 leaves 7 on top and 4 as the minimum.")],
        tests=[case(["MinStack", "push", "push", "push", "pop", "pop", "getMin"], [[], [2], [2], [3], [], [], []],
                    out=[None, None, None, None, None, None, 2]),
               case(["MinStack", "push", "getMin", "top"], [[], [-5], [], []], out=[None, None, -5, -5]),
               case(["MinStack", "push", "push", "getMin", "pop", "getMin"], [[], [0], [-1], [], [], []],
                    out=[None, None, None, -1, None, 0]),
               case(gen("['MinStack'] + ['push'] * 20000 + ['getMin', 'pop'] * 10000"),
                    gen("[[]] + [[v] for v in rand_list(20000, -10**9, 10**9, seed=55)] + [[], []] * 10000"))],
        constraints=["`-2³¹ <= val <= 2³¹ - 1`", "At most `4 × 10⁴` calls in total"],
        hints=["Scanning the whole stack in `getMin` is O(n). Too slow.",
               "When an element is pushed, the minimum of the stack **at that moment** never changes until it's popped.",
               "Store that minimum alongside each element, for example as a `(value, min_so_far)` tuple."],
        explanation="""
        Each entry records `(value, minimum of everything at or below it)`. On push, the new minimum is `min(val, previous top's minimum)`. Popping removes the entry along with its minimum, which exposes the minimum from before it was pushed. Every operation is a single list operation.

        An alternative keeps a second stack of minimums and pushes to it only when `val <= current min`.

        **Complexity:** O(1) per operation, O(n) memory.
        """,
    ),
    challenge_problem(
        "lru-cache",
        "Least Recently Used Cache",
        """
        Design a cache with a fixed `capacity` that evicts the **least recently used** key when it's full.

        - `LRUCache(capacity)` creates the cache.
        - `get(key)` returns the value for `key`, or `-1` if it isn't present. Getting a key counts as **using** it.
        - `put(key, value)` inserts or updates `key`. This also counts as using it. If the insert makes the cache exceed `capacity`, evict the key that was used least recently.

        Both methods must run in **O(1)** average time.
        """,
        """
        class LRUCache:
            def __init__(self, capacity: int):
                self.capacity = capacity
                self.data = OrderedDict()

            def get(self, key: int) -> int:
                if key not in self.data:
                    return -1
                self.data.move_to_end(key)
                return self.data[key]

            def put(self, key: int, value: int) -> None:
                if key in self.data:
                    self.data.move_to_end(key)
                self.data[key] = value
                if len(self.data) > self.capacity:
                    self.data.popitem(last=False)
        """,
        difficulty="Medium",
        tags=["Design", "Hash Map", "Linked List", "Classes"],
        examples=[case(["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"],
                       [[2], [1, 10], [2, 20], [1], [3, 30], [2], [4, 40], [1], [3], [4]],
                       out=[None, None, None, 10, None, -1, None, -1, 30, 40],
                       why="get(1) makes key 2 the least recently used, so put(3, 30) evicts 2. Then put(4, 40) evicts 1.")],
        tests=[case(["LRUCache", "put", "get", "put", "get", "get"], [[1], [2, 1], [2], [3, 2], [2], [3]],
                    out=[None, None, 1, None, -1, 2]),
               case(["LRUCache", "put", "put", "put", "put", "get", "get"], [[2], [2, 1], [1, 1], [2, 3], [4, 1], [1], [2]],
                    out=[None, None, None, None, None, -1, 3]),
               case(["LRUCache", "get", "put", "get"], [[3], [5], [5, 55], [5]], out=[None, -1, None, 55]),
               case(gen("['LRUCache'] + ['get' if i % 3 == 0 else 'put' for i in range(30000)]"),
                    gen("[[500]] + [[k] if i % 3 == 0 else [k, i] for i, k in enumerate(rand_list(30000, 0, 1000, seed=56))]"))],
        constraints=["`1 <= capacity <= 3000`", "`0 <= key <= 10⁴`", "`0 <= value <= 10⁵`", "At most `3 × 10⁴` calls"],
        hints=["You need two things in O(1): look up a key, and find or refresh the least recently used key.",
               "A dict gives O(1) lookups. Python dicts also remember insertion order, so deleting and re-inserting a key moves it to the end.",
               "`collections.OrderedDict` has `move_to_end(key)` and `popitem(last=False)`. The classic interview answer is a dict plus a doubly-linked list."],
        explanation="""
        Keep the keys ordered by recency, least recent first, in a structure that also supports O(1) lookup. `OrderedDict` does both. `get` moves the key to the end, `put` inserts or updates at the end, and eviction pops from the front.

        Under the hood, that is a hash map pointing into a **doubly-linked list**, the answer interviewers usually want you to build. The map finds a node in O(1), and the list unlinks it and re-attaches it at the tail in O(1).

        **Complexity:** O(1) average per operation, O(capacity) memory.
        """,
    ),
]

MODULE = module(
    "linked-structures",
    "Objects, Linked Lists & Trees",
    "Design your own classes and work with node-based structures: linked lists and binary trees.",
    lessons=[CLASSES, LINKED_LISTS, TREES],
    challenges=CHALLENGES,
    challenge_title="Checkpoint 5 · Linked Structures",
    challenge_blurb="Pointer manipulation, tree recursion and BFS, plus two classic design questions that combine classes with hash maps.",
)
