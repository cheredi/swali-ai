"""
NeetCode Data Collector for Swali-AI

🎓 LEARNING NOTE: Curated Problem Lists
=======================================
NeetCode provides curated lists of the most important problems to study,
organized by pattern (e.g., NeetCode 150, Blind 75).

This is valuable because:
1. Problems are grouped by pattern (Two Pointers, Sliding Window, etc.)
2. Explanations focus on teaching the pattern, not just the solution
3. The curation saves time - these are the "must know" problems
"""

import json
from pathlib import Path
from typing import Any


class NeetCodeCollector:
    """
    Collects the NeetCode 150 problem list with pattern categorization.

    🎓 LEARNING NOTE: Pattern-Based Learning
    NeetCode organizes problems by algorithmic patterns:
    - Arrays & Hashing
    - Two Pointers
    - Sliding Window
    - Stack
    - Binary Search
    - Linked List
    - Trees
    - Tries
    - Heap / Priority Queue
    - Backtracking
    - Graphs
    - Dynamic Programming
    - Greedy
    - Intervals
    - Math & Geometry
    - Bit Manipulation

    This organization is GOLD for interview prep because
    patterns transfer across problems!
    """

    # NeetCode 150 organized by pattern
    # This is a curated list that represents the core problems
    NEETCODE_150 = {
        "arrays_hashing": [
            {"title": "Contains Duplicate", "leetcode_id": 217, "difficulty": "easy"},
            {"title": "Valid Anagram", "leetcode_id": 242, "difficulty": "easy"},
            {"title": "Two Sum", "leetcode_id": 1, "difficulty": "easy"},
            {"title": "Group Anagrams", "leetcode_id": 49, "difficulty": "medium"},
            {"title": "Top K Frequent Elements", "leetcode_id": 347, "difficulty": "medium"},
            {"title": "Product of Array Except Self", "leetcode_id": 238, "difficulty": "medium"},
            {"title": "Valid Sudoku", "leetcode_id": 36, "difficulty": "medium"},
            {"title": "Encode and Decode Strings", "leetcode_id": 271, "difficulty": "medium"},
            {"title": "Longest Consecutive Sequence", "leetcode_id": 128, "difficulty": "medium"},
        ],
        "two_pointers": [
            {"title": "Valid Palindrome", "leetcode_id": 125, "difficulty": "easy"},
            {"title": "Two Sum II", "leetcode_id": 167, "difficulty": "medium"},
            {"title": "3Sum", "leetcode_id": 15, "difficulty": "medium"},
            {"title": "Container With Most Water", "leetcode_id": 11, "difficulty": "medium"},
            {"title": "Trapping Rain Water", "leetcode_id": 42, "difficulty": "hard"},
        ],
        "sliding_window": [
            {"title": "Best Time to Buy and Sell Stock", "leetcode_id": 121, "difficulty": "easy"},
            {"title": "Longest Substring Without Repeating Characters", "leetcode_id": 3, "difficulty": "medium"},
            {"title": "Longest Repeating Character Replacement", "leetcode_id": 424, "difficulty": "medium"},
            {"title": "Permutation in String", "leetcode_id": 567, "difficulty": "medium"},
            {"title": "Minimum Window Substring", "leetcode_id": 76, "difficulty": "hard"},
            {"title": "Sliding Window Maximum", "leetcode_id": 239, "difficulty": "hard"},
        ],
        "stack": [
            {"title": "Valid Parentheses", "leetcode_id": 20, "difficulty": "easy"},
            {"title": "Min Stack", "leetcode_id": 155, "difficulty": "medium"},
            {"title": "Evaluate Reverse Polish Notation", "leetcode_id": 150, "difficulty": "medium"},
            {"title": "Generate Parentheses", "leetcode_id": 22, "difficulty": "medium"},
            {"title": "Daily Temperatures", "leetcode_id": 739, "difficulty": "medium"},
            {"title": "Car Fleet", "leetcode_id": 853, "difficulty": "medium"},
            {"title": "Largest Rectangle in Histogram", "leetcode_id": 84, "difficulty": "hard"},
        ],
        "binary_search": [
            {"title": "Binary Search", "leetcode_id": 704, "difficulty": "easy"},
            {"title": "Search a 2D Matrix", "leetcode_id": 74, "difficulty": "medium"},
            {"title": "Koko Eating Bananas", "leetcode_id": 875, "difficulty": "medium"},
            {"title": "Find Minimum in Rotated Sorted Array", "leetcode_id": 153, "difficulty": "medium"},
            {"title": "Search in Rotated Sorted Array", "leetcode_id": 33, "difficulty": "medium"},
            {"title": "Time Based Key-Value Store", "leetcode_id": 981, "difficulty": "medium"},
            {"title": "Median of Two Sorted Arrays", "leetcode_id": 4, "difficulty": "hard"},
        ],
        "linked_list": [
            {"title": "Reverse Linked List", "leetcode_id": 206, "difficulty": "easy"},
            {"title": "Merge Two Sorted Lists", "leetcode_id": 21, "difficulty": "easy"},
            {"title": "Linked List Cycle", "leetcode_id": 141, "difficulty": "easy"},
            {"title": "Reorder List", "leetcode_id": 143, "difficulty": "medium"},
            {"title": "Remove Nth Node From End of List", "leetcode_id": 19, "difficulty": "medium"},
            {"title": "Copy List with Random Pointer", "leetcode_id": 138, "difficulty": "medium"},
            {"title": "Add Two Numbers", "leetcode_id": 2, "difficulty": "medium"},
            {"title": "LRU Cache", "leetcode_id": 146, "difficulty": "medium"},
            {"title": "Merge K Sorted Lists", "leetcode_id": 23, "difficulty": "hard"},
            {"title": "Reverse Nodes in K-Group", "leetcode_id": 25, "difficulty": "hard"},
        ],
        "trees": [
            {"title": "Invert Binary Tree", "leetcode_id": 226, "difficulty": "easy"},
            {"title": "Maximum Depth of Binary Tree", "leetcode_id": 104, "difficulty": "easy"},
            {"title": "Diameter of Binary Tree", "leetcode_id": 543, "difficulty": "easy"},
            {"title": "Balanced Binary Tree", "leetcode_id": 110, "difficulty": "easy"},
            {"title": "Same Tree", "leetcode_id": 100, "difficulty": "easy"},
            {"title": "Subtree of Another Tree", "leetcode_id": 572, "difficulty": "easy"},
            {"title": "Lowest Common Ancestor of BST", "leetcode_id": 235, "difficulty": "medium"},
            {"title": "Binary Tree Level Order Traversal", "leetcode_id": 102, "difficulty": "medium"},
            {"title": "Binary Tree Right Side View", "leetcode_id": 199, "difficulty": "medium"},
            {"title": "Count Good Nodes in Binary Tree", "leetcode_id": 1448, "difficulty": "medium"},
            {"title": "Validate Binary Search Tree", "leetcode_id": 98, "difficulty": "medium"},
            {"title": "Kth Smallest Element in a BST", "leetcode_id": 230, "difficulty": "medium"},
            {"title": "Construct Binary Tree from Preorder and Inorder", "leetcode_id": 105, "difficulty": "medium"},
            {"title": "Binary Tree Maximum Path Sum", "leetcode_id": 124, "difficulty": "hard"},
            {"title": "Serialize and Deserialize Binary Tree", "leetcode_id": 297, "difficulty": "hard"},
        ],
        "heap": [
            {"title": "Kth Largest Element in a Stream", "leetcode_id": 703, "difficulty": "easy"},
            {"title": "Last Stone Weight", "leetcode_id": 1046, "difficulty": "easy"},
            {"title": "K Closest Points to Origin", "leetcode_id": 973, "difficulty": "medium"},
            {"title": "Kth Largest Element in an Array", "leetcode_id": 215, "difficulty": "medium"},
            {"title": "Task Scheduler", "leetcode_id": 621, "difficulty": "medium"},
            {"title": "Design Twitter", "leetcode_id": 355, "difficulty": "medium"},
            {"title": "Find Median from Data Stream", "leetcode_id": 295, "difficulty": "hard"},
        ],
        "backtracking": [
            {"title": "Subsets", "leetcode_id": 78, "difficulty": "medium"},
            {"title": "Combination Sum", "leetcode_id": 39, "difficulty": "medium"},
            {"title": "Permutations", "leetcode_id": 46, "difficulty": "medium"},
            {"title": "Subsets II", "leetcode_id": 90, "difficulty": "medium"},
            {"title": "Combination Sum II", "leetcode_id": 40, "difficulty": "medium"},
            {"title": "Word Search", "leetcode_id": 79, "difficulty": "medium"},
            {"title": "Palindrome Partitioning", "leetcode_id": 131, "difficulty": "medium"},
            {"title": "Letter Combinations of a Phone Number", "leetcode_id": 17, "difficulty": "medium"},
            {"title": "N-Queens", "leetcode_id": 51, "difficulty": "hard"},
        ],
        "graphs": [
            {"title": "Number of Islands", "leetcode_id": 200, "difficulty": "medium"},
            {"title": "Clone Graph", "leetcode_id": 133, "difficulty": "medium"},
            {"title": "Max Area of Island", "leetcode_id": 695, "difficulty": "medium"},
            {"title": "Pacific Atlantic Water Flow", "leetcode_id": 417, "difficulty": "medium"},
            {"title": "Surrounded Regions", "leetcode_id": 130, "difficulty": "medium"},
            {"title": "Rotting Oranges", "leetcode_id": 994, "difficulty": "medium"},
            {"title": "Course Schedule", "leetcode_id": 207, "difficulty": "medium"},
            {"title": "Course Schedule II", "leetcode_id": 210, "difficulty": "medium"},
            {"title": "Redundant Connection", "leetcode_id": 684, "difficulty": "medium"},
            {"title": "Number of Connected Components", "leetcode_id": 323, "difficulty": "medium"},
            {"title": "Graph Valid Tree", "leetcode_id": 261, "difficulty": "medium"},
            {"title": "Word Ladder", "leetcode_id": 127, "difficulty": "hard"},
        ],
        "dynamic_programming": [
            {"title": "Climbing Stairs", "leetcode_id": 70, "difficulty": "easy"},
            {"title": "Min Cost Climbing Stairs", "leetcode_id": 746, "difficulty": "easy"},
            {"title": "House Robber", "leetcode_id": 198, "difficulty": "medium"},
            {"title": "House Robber II", "leetcode_id": 213, "difficulty": "medium"},
            {"title": "Longest Palindromic Substring", "leetcode_id": 5, "difficulty": "medium"},
            {"title": "Palindromic Substrings", "leetcode_id": 647, "difficulty": "medium"},
            {"title": "Decode Ways", "leetcode_id": 91, "difficulty": "medium"},
            {"title": "Coin Change", "leetcode_id": 322, "difficulty": "medium"},
            {"title": "Maximum Product Subarray", "leetcode_id": 152, "difficulty": "medium"},
            {"title": "Word Break", "leetcode_id": 139, "difficulty": "medium"},
            {"title": "Longest Increasing Subsequence", "leetcode_id": 300, "difficulty": "medium"},
            {"title": "Partition Equal Subset Sum", "leetcode_id": 416, "difficulty": "medium"},
            {"title": "Unique Paths", "leetcode_id": 62, "difficulty": "medium"},
            {"title": "Longest Common Subsequence", "leetcode_id": 1143, "difficulty": "medium"},
            {"title": "Best Time to Buy and Sell Stock with Cooldown", "leetcode_id": 309, "difficulty": "medium"},
            {"title": "Coin Change II", "leetcode_id": 518, "difficulty": "medium"},
            {"title": "Target Sum", "leetcode_id": 494, "difficulty": "medium"},
            {"title": "Interleaving String", "leetcode_id": 97, "difficulty": "medium"},
            {"title": "Edit Distance", "leetcode_id": 72, "difficulty": "hard"},
            {"title": "Distinct Subsequences", "leetcode_id": 115, "difficulty": "hard"},
            {"title": "Burst Balloons", "leetcode_id": 312, "difficulty": "hard"},
            {"title": "Regular Expression Matching", "leetcode_id": 10, "difficulty": "hard"},
        ],
        "greedy": [
            {"title": "Maximum Subarray", "leetcode_id": 53, "difficulty": "medium"},
            {"title": "Jump Game", "leetcode_id": 55, "difficulty": "medium"},
            {"title": "Jump Game II", "leetcode_id": 45, "difficulty": "medium"},
            {"title": "Gas Station", "leetcode_id": 134, "difficulty": "medium"},
            {"title": "Hand of Straights", "leetcode_id": 846, "difficulty": "medium"},
            {"title": "Merge Triplets to Form Target", "leetcode_id": 1899, "difficulty": "medium"},
            {"title": "Partition Labels", "leetcode_id": 763, "difficulty": "medium"},
            {"title": "Valid Parenthesis String", "leetcode_id": 678, "difficulty": "medium"},
        ],
        "intervals": [
            {"title": "Insert Interval", "leetcode_id": 57, "difficulty": "medium"},
            {"title": "Merge Intervals", "leetcode_id": 56, "difficulty": "medium"},
            {"title": "Non-overlapping Intervals", "leetcode_id": 435, "difficulty": "medium"},
            {"title": "Meeting Rooms", "leetcode_id": 252, "difficulty": "easy"},
            {"title": "Meeting Rooms II", "leetcode_id": 253, "difficulty": "medium"},
            {"title": "Minimum Interval to Include Each Query", "leetcode_id": 1851, "difficulty": "hard"},
        ],
        "math_geometry": [
            {"title": "Rotate Image", "leetcode_id": 48, "difficulty": "medium"},
            {"title": "Spiral Matrix", "leetcode_id": 54, "difficulty": "medium"},
            {"title": "Set Matrix Zeroes", "leetcode_id": 73, "difficulty": "medium"},
            {"title": "Happy Number", "leetcode_id": 202, "difficulty": "easy"},
            {"title": "Plus One", "leetcode_id": 66, "difficulty": "easy"},
            {"title": "Pow(x, n)", "leetcode_id": 50, "difficulty": "medium"},
            {"title": "Multiply Strings", "leetcode_id": 43, "difficulty": "medium"},
            {"title": "Detect Squares", "leetcode_id": 2013, "difficulty": "medium"},
        ],
        "bit_manipulation": [
            {"title": "Single Number", "leetcode_id": 136, "difficulty": "easy"},
            {"title": "Number of 1 Bits", "leetcode_id": 191, "difficulty": "easy"},
            {"title": "Counting Bits", "leetcode_id": 338, "difficulty": "easy"},
            {"title": "Reverse Bits", "leetcode_id": 190, "difficulty": "easy"},
            {"title": "Missing Number", "leetcode_id": 268, "difficulty": "easy"},
            {"title": "Sum of Two Integers", "leetcode_id": 371, "difficulty": "medium"},
            {"title": "Reverse Integer", "leetcode_id": 7, "difficulty": "medium"},
        ],
    }

    def __init__(self, output_dir: str = "./data/raw/neetcode"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_pattern_descriptions(self) -> dict[str, str]:
        """
        Generate descriptions for each pattern.

        🎓 LEARNING NOTE: Pattern Descriptions
        These descriptions help users understand WHEN to apply each pattern.
        This is the key insight for interview prep!
        """
        return {
            "arrays_hashing": """
Use Arrays & Hashing patterns when:
- You need O(1) lookup/existence checks
- Counting frequencies of elements
- Finding duplicates or pairs
- Grouping elements by some property

Key techniques: Hash maps, sets, frequency counters
            """.strip(),

            "two_pointers": """
Use Two Pointers when:
- Working with sorted arrays/strings
- Finding pairs that satisfy a condition
- Partitioning arrays in-place
- Comparing elements from both ends

Key insight: Sorted input often enables two-pointer solutions
            """.strip(),

            "sliding_window": """
Use Sliding Window when:
- Finding subarrays/substrings with specific properties
- Optimizing from O(n²) brute force to O(n)
- The problem involves contiguous elements

Key insight: If moving one boundary, consider what that does to the window
            """.strip(),

            "stack": """
Use Stack when:
- Matching pairs (parentheses, tags)
- Tracking "most recent" elements
- Monotonic relationships needed
- Expression evaluation

Key insight: Stack for "nearest smaller/larger" problems
            """.strip(),

            "binary_search": """
Use Binary Search when:
- Input is sorted (or can be sorted)
- Search space can be halved each step
- Finding boundaries or insertion points
- Optimizing over a range (binary search on answer)

Key insight: Works on ANY monotonic function, not just sorted arrays!
            """.strip(),

            "linked_list": """
Use Linked List techniques when:
- Pointer manipulation required
- No random access needed
- In-place modifications needed

Key techniques: Two pointers, dummy nodes, reversing, finding cycles
            """.strip(),

            "trees": """
Use Tree patterns when:
- Hierarchical data structures
- Recursive problem decomposition
- Path-based problems

Key insight: Most tree problems reduce to: "What do I need from left subtree, right subtree, and current node?"
            """.strip(),

            "heap": """
Use Heap/Priority Queue when:
- Need min/max element repeatedly
- K largest/smallest problems
- Stream of data with ordering needs
- Merging sorted lists

Key insight: Heaps give O(log n) insert/delete vs O(n) for sorted lists
            """.strip(),

            "backtracking": """
Use Backtracking when:
- Generating all combinations/permutations
- Constraint satisfaction (valid solutions only)
- Decision tree exploration

Key insight: "Choose, Explore, Unchoose" - make a choice, recurse, undo the choice
            """.strip(),

            "graphs": """
Use Graph patterns when:
- Data has relationships (edges)
- Grid-based problems (cells are nodes)
- Finding paths or connected components
- Dependency ordering (topological sort)

Key techniques: DFS, BFS, Union-Find, Topological Sort
            """.strip(),

            "dynamic_programming": """
Use Dynamic Programming when:
- Overlapping subproblems
- Optimal substructure (optimal solution uses optimal sub-solutions)
- Counting or optimization problems

Key insight: "What state do I need to make a decision?" → That's your DP state
            """.strip(),

            "greedy": """
Use Greedy when:
- Local optimal leads to global optimal
- Problem has optimal substructure
- Choices don't affect future options

Key insight: Prove greedy works OR find counterexample. Don't assume!
            """.strip(),

            "intervals": """
Use Interval patterns when:
- Merging or comparing time ranges
- Scheduling problems
- Overlap detection

Key insight: Sort by start time (usually), then scan with careful logic
            """.strip(),

            "math_geometry": """
Use Math/Geometry patterns when:
- Matrix manipulation needed
- Number theory problems
- Coordinate geometry

Key techniques: Modular arithmetic, coordinate transforms, in-place matrix ops
            """.strip(),

            "bit_manipulation": """
Use Bit Manipulation when:
- Working with binary representations
- Space optimization needed
- XOR properties helpful (a ^ a = 0)
- Power of 2 operations

Key insight: XOR to find unique element, AND to check bits, shifts for powers of 2
            """.strip(),
        }

    def save_neetcode_150(self) -> None:
        """
        Save the NeetCode 150 problem list with pattern info.
        """
        patterns = self.generate_pattern_descriptions()

        output: dict[str, Any] = {
            "name": "NeetCode 150",
            "description": "Curated list of 150 LeetCode problems organized by pattern",
            "patterns": {}
        }

        for pattern_key, problems in self.NEETCODE_150.items():
            output["patterns"][pattern_key] = {
                "name": pattern_key.replace("_", " ").title(),
                "description": patterns.get(pattern_key, ""),
                "problems": problems
            }

        # Save to file
        output_file = self.output_dir / "neetcode_150.json"
        with open(output_file, "w") as f:
            json.dump(output, f, indent=2)

        print(f"✅ Saved NeetCode 150 to: {output_file}")
        print(f"   Total patterns: {len(output['patterns'])}")
        print(f"   Total problems: {sum(len(p) for p in self.NEETCODE_150.values())}")

    def get_problems_by_pattern(self, pattern: str) -> list[dict]:
        """Get all problems for a specific pattern."""
        return self.NEETCODE_150.get(pattern, [])

    def get_all_patterns(self) -> list[str]:
        """Get list of all pattern names."""
        return list(self.NEETCODE_150.keys())


if __name__ == "__main__":
    print("🧪 Testing NeetCode Collector\n")
    collector = NeetCodeCollector()

    # Save the NeetCode 150
    collector.save_neetcode_150()

    # Show pattern distribution
    print("\n📊 Pattern distribution:")
    for pattern, problems in collector.NEETCODE_150.items():
        print(f"   {pattern}: {len(problems)} problems")
