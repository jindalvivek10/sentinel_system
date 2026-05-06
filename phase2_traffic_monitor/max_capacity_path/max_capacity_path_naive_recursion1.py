"""
FILE: max_capacity_path_naive_recursion1.py

SYSTEM ROLE: 
Strategic pathfinder calculating the maximum vehicle capacity route through 
a city grid using top-down recursion (Brute Force / Naive approach).

PSEUDO-LOGIC:
1. INPUT & START: 
   - 'grid': A 2D List (the city map) where each cell has a "capacity" (throughput).
   - 'r', 'c': The current Row and Column coordinates (starts at 0, 0).
2. BASE CASE - THE FINISH LINE (Destination):
   - If the current (r, c) is the bottom-right corner, we've reached the end. 
     Return that cell's capacity.
3. BASE CASE - THE BOUNDARIES (The Safety Net):
   - If 'r' or 'c' move outside the grid, return negative infinity (-inf). 
   - This tells the "decision maker" that this path is a dead end and should be ignored.
4. THE RECURSIVE "FORK" (Exploring All Options):
   - At each intersection, we don't know if going Right or Down is better.
   - So, we ask the algorithm to explore BOTH branches:
     a) score_right = find_max_throughput(grid, r, c + 1)
     b) score_down = find_max_throughput(grid, r + 1, c)
5. THE AGGREGATION (Combining Results):
   - The total capacity for this block is: 
     (Current Cell Capacity) + (The Maximum of the two future paths).

INPUT EXAMPLE:
grid = [
    [10,  2,  1],
    [ 5, 20,  3],
    [ 1,  1, 10]
]

OUTPUT/RESULT:
- The algorithm evaluates paths like: 10 -> 2 -> 1 -> 3 -> 10 (sum: 26)
- It finds the optimal path: 10 -> 5 -> 20 -> 3 -> 10 (sum: 48)
- FINAL RESULT: 48

COMPLEXITY ANALYSIS:
- TIME: O(2^(N+M)) - "The Exponential Explosion"
  * Explanation: Every time the function is called, it splits into TWO more calls (Right and Down). 
    Think of it like a family tree where every person has 2 children; it grows huge very quickly.
  * Problem: It has "No Memory." It recalculates the max throughput for the same intersections 
    thousands of times if they are reached via different paths.
- SPACE: O(N+M) - "The Call Stack Depth" at a given time
  * Explanation: This represents the maximum number of function calls the computer keeps 
    "on hold" while waiting to reach the finish line. 
  * In a grid, the longest path is (Rows + Columns), so that's the maximum stack height.
"""

import math
from typing import List

def find_max_throughput(grid: List[List[int]], r: int, c: int) -> int:
    """
    Recursively explores every possible path from (r, c) to the bottom-right corner.
    Returns the maximum combined sum of capacities found along the way.
    """
    # 1. Validation for Robustness: Ensures we don't crash on empty input.
    if not grid or not grid[0]:
        return 0

    rows = len(grid)
    cols = len(grid[0])

    # 2. Base Case: Out of Bounds (The Safety Rails)
    # We return negative infinity so the max() function in Step 5 will never 
    # accidentally pick this "path to nowhere." We use -math.inf because it 
    # correctly handles grids that might contain negative numbers.
    if r >= rows or c >= cols:
        return -math.inf

    # 3. Base Case: The Finish Line (The Destination)
    # If we are at the bottom-right corner, we have completed a path. 
    # There are no more moves to make, so we just return this cell's capacity.
    if r == rows - 1 and c == cols - 1:
        return grid[r][c]

    # 4. The Recursive Steps (The Branching Decision)
    # This is the core "Choice": Should we go Right or Down?
    # This doubling effect at every cell is what creates the exponential time complexity.
    score_right = find_max_throughput(grid, r, c + 1)
    score_down = find_max_throughput(grid, r + 1, c)

    # 5. The Aggregation: Result = Current value + the best of the next steps.
    # We look at the results from our "Future Self" (the recursive calls) 
    # and pick the highest one to add to our current intersection's capacity.
    return grid[r][c] + max(score_right, score_down)


# ==========================================
# TEST SUITE: Validating the Strategic Brain
# ==========================================

def run_tests():
    print("--- [SENTINEL SYSTEM] Running Naive Pathfinder Tests ---\n")

    test_cases = [
        {
            "name": "Standard 3x3 Grid (The Example)",
            "grid": [
                [10,  2,  1],
                [ 5, 20,  3],
                [ 1,  1, 10]
            ],
            "expected": 48
        },
        {
            "name": "Single Row (Only Right Move Possible)",
            "grid": [[5, 10, 2]],
            "expected": 17
        },
        {
            "name": "Single Column (Only Down Move Possible)",
            "grid": [[5], [10], [2]],
            "expected": 17
        },
        {
            "name": "Small 2x2 Grid",
            "grid": [
                [1, 10],
                [1,  1]
            ],
            "expected": 12
        },
        {
            "name": "Single Intersection (Start is Finish)",
            "grid": [[100]],
            "expected": 100
        }
    ]

    for case in test_cases:
        result = find_max_throughput(case["grid"], 0, 0)
        status = "✅ PASS" if result == case["expected"] else "❌ FAIL"
        print(f"Test: {case['name']}")
        print(f"Result: {result} | Expected: {case['expected']} | {status}\n")

if __name__ == "__main__":
    run_tests()