"""
FILE: max_capacity_path_memory_optimized.py

SYSTEM ROLE: 
Strategic pathfinder calculating the maximum vehicle capacity route through 
a city grid using Top-Down Dynamic Programming (Memoization).

INPUT EXAMPLE:
grid = [                   # The "Map" of capacities
    [10,  2,  1],
    [ 5, 20,  3],
    [ 1,  1, 10]
]

EXPECTED OUTPUT:
Result: 48
Memory (The "Completed Notebook" visualized as a grid):
[
    [48, 35, 14],  # Max possible throughput starting from Row 0 to the end
    [38, 33, 13],  # Max possible throughput starting from Row 1 to the end
    [12, 11, 10]   # Max possible throughput starting from Row 2 to the end
]

PSEUDO-LOGIC (The "Notebook" Strategy):
1. START: We begin at (0, 0).
2. THE NOTEBOOK (Memory): 
   - Before we calculate anything, we look at our 'memory' dictionary. 
   - "Have we been to this intersection before?"
   - If YES: Just return the answer we already wrote down. No more work needed!
3. THE BOUNDARIES:
   - If we walk off the grid (Row or Col too big), we return -Infinity.
4. THE DESTINATION:
   - If we reach the bottom-right corner, the best path is just that cell's value.
5. EXPLORATION (Recursion):
   - We ask: "What's the best I can get if I go Right?" 
   - We ask: "What's the best I can get if I go Down?"
6. SAVING:
   - We take the current cell value + the better of the two options above.
   - WE WRITE THIS IN THE NOTEBOOK (memory) for the next time someone asks.

COMPLEXITY ANALYSIS (Why is it faster?):
- TIME: O(N * M) - "Only Do the Work Once"
  * THE PROBLEM: In a 100x100 grid, there are billions of ways to reach the same 
    intersection (e.g., Right-Down vs Down-Right). Without memory, we re-calculate 
    the rest of the journey every single time we arrive.
  * THE SOLUTION: When we reach an intersection, we ask: "Is the answer in the 
    notebook?" If yes, we stop and use that answer.
  * RESULT: Since there are only N * M intersections, we only ever do the 
    "actual math" N * M times. 
    - Naive: Trillions of operations (Exponential)
    - This Version: 10,000 operations (Linear to grid size)

- SPACE: O(N * M) - "The Storage Cost"
  * We need space to store the notebook entries for every cell in the grid.
"""

"""
COMPLEXITY ANALYSIS:
- TIME: O(N * M). We only calculate each intersection EXACTLY ONCE. 
  - Why? The 'memory' dictionary ensures that even if 10 different paths lead to 
    the same intersection, we only do the recursive work for the first one. 
  - Example: For a 100x100 grid, we perform roughly 10,000 calculations, 
    whereas the naive version would take trillions.
- SPACE: O(N * M). 
  - This includes the 'memory' dictionary which stores an answer for every 
    cell (N * M) and the 'recursion stack' (N + M) which tracks our current depth.
"""

import math
from typing import List

# 'memory' acts as our global "notebook" to store previously calculated 
# results for specific (row, column) coordinates.
memory = {}

def find_max_throughput(grid: List[List[int]], r: int, c: int) -> int:
    """
    Explores every path from (r, c) to the bottom-right corner.
    Returns the maximum sum of capacities found.
    """
    # 1. Validation for Staff-level robustness
    if not grid or not grid[0]:
        return 0

    # 2. Memoization Lookup: Check the "Notebook"
    # If we have already visited this coordinate, don't re-calculate.
    if (r, c) in memory:
        return memory[ (r, c) ]

    rows = len(grid)
    cols = len(grid[0])

    # 3. Base Case: Out of Bounds
    # We return negative infinity so the max() function in the caller 
    # will never choose this "dead end" path. Also we chose -math.inf instead of returning 0
    # because it handles negative numbers also
    if r >= rows or c >= cols:
        return -math.inf

    # 4. Base Case: The Finish Line
    # If we are at the destination, there are no more choices to make.
    if r == rows - 1 and c == cols - 1:
        return grid[r][c]

    # 5. The Recursive Steps (Exploring Options)
    # We ask: "What is the best I can do if I go Right? What about Down?"
    score_right = find_max_throughput(grid, r, c + 1)
    score_down = find_max_throughput(grid, r + 1, c)

    # 6. Aggregation and Storage
    # We take our current value and add the best of the future options.
    result = grid[r][c] + int(max(score_right, score_down))
    memory[ (r, c) ] = result  # Save result for future use (The Memoization part)
    return result


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
        memory.clear()  # Ensure results from previous grids don't pollute the current test
        result = find_max_throughput(case["grid"], 0, 0)
        status = "✅ PASS" if result == case["expected"] else "❌ FAIL"
        print(f"Test: {case['name']}")
        print(f"Result: {result} | Expected: {case['expected']} | {status}")
        print(f"Memory Contents: {memory}\n")

if __name__ == "__main__":
    run_tests()