"""
FILE: max_capacity_path_dynamic_bottomup.py

SYSTEM ROLE: 
Strategic pathfinder using Bottom-Up Dynamic Programming (Tabulation).
Unlike recursion, this "fills in a table" from the finish line back to the start.
Think of it as building a "Success Map" so that by the time you reach the start, 
you already know the best possible score for every single intersection.

INPUT EXAMPLE:
grid = [
    [10,  2,  1],
    [ 5, 20,  3],
    [ 1,  1, 10]
]

OUTPUT/RESULT:
Final DP Table (The "Success Map"):
[
    [48, 35, 14],  # Result is at [0][0]
    [38, 33, 13], 
    [12, 11, 10]
]
Final Result: 48

PSEUDO-LOGIC (The "Building Backwards" Strategy):
1. PREPARATION: Create a "Success Map" (DP Table) of the same size as our grid.
2. THE FOUNDATION: Start at the bottom-right corner (the Destination). 
   The max throughput there is just the capacity of that single cell.
3. THE "ONE-WAY" STREETS (The Edges):
   - On the VERY BOTTOM row, you can't go down. You can ONLY go right. 
     So, each cell's best score is: (My Capacity) + (The score to my Right).
   - On the FAR RIGHT column, you can't go right. You can ONLY go down. 
     So, each cell's best score is: (My Capacity) + (The score Below me).
4. THE DECISION ENGINE: For every other intersection, we have two choices: Right or Down.
   We look at our "Success Map" to see which path is already better and pick it.
   Score = (My Capacity) + MAX(Score Right, Score Down).
5. VICTORY: The answer for the entire journey is now stored in the top-left cell [0][0].

COMPLEXITY ANALYSIS:
- TIME: O(N * M) - "The Predictable Loop"
  * Explanation: We visit every intersection exactly once. If the grid is 100x100, 
    we do 10,000 steps. It doesn't matter how complex the paths are; the 
    workload is always exactly the size of the grid.
- SPACE: O(N * M) - "The Memory Map"
  * Explanation: We create a second grid (the DP table) to store our answers. 
    This uses memory proportional to the size of the city map.
- RELIABILITY: Unlike recursion, this doesn't use the "Call Stack," so it 
  can handle massive grids (e.g., 10,000 x 10,000) without crashing.
"""

from typing import List

def find_max_throughput_tabulated(grid: List[List[int]]) -> int:
    """
    Calculates maximum throughput using a bottom-up, table-filling approach.
    This avoids the 'Exponential Explosion' of the naive recursive method.
    """
    # 1. Validation: Handle empty or malformed maps immediately.
    if not grid or not grid[0]:
        return 0

    rows = len(grid)
    cols = len(grid[0])
    print(f"== rows={rows}, cols={cols}")

    # 2. Create the DP Table (initialized with 0s)
    dp = [ [0 for _ in range(0, cols)]  for _ in range(0, rows)]
    print(f"==  2. DP Table: {dp}")

    # 3. Base Case: The Finish Line
    # The journey ends here, so the best throughput is just the value of this cell.
    dp[rows-1][cols-1] = grid[rows-1][cols-1]
    print(f"==  3. DP Table: {dp}")

    # 4. Pre-fill the Bottom Row (Can only go Right)
    # Since there's no "Down" option, we simply add the current cell to the 
    # best score already calculated for the cell to its right.
    for c in range(cols-2, -1, -1):
        dp[rows-1][c] = grid[rows-1][c] + dp[rows-1][c+1]
    print(f"==  4. DP Table: {dp}")

    # 5. Pre-fill the Right Column (Can only go Down)
    # Since there's no "Right" option, we simply add the current cell to the 
    # best score already calculated for the cell below it.
    for r in range(rows-2, -1, -1): 
        dp[r][cols-1] = grid[r][cols-1] + dp[r+1][cols-1]
    print(f"==  5. DP Table: {dp}")

    # 6. Fill the rest of the Grid (Working backwards)
    # For these cells, we have a choice. We look at our pre-calculated answers 
    # for the Right and Down neighbors and pick the winner.
    for r in range( rows-2, -1, -1):
        for c in range(cols - 2, -1, -1):
            dp[r][c] = grid[r][c] + max( dp[r][c+1], dp[r+1][c] )
    print(f"==  6. DP Table: {dp}")

    # 7. The total maximum throughput is now stored at the start point
    return dp[0][0]


# ==========================================
# TEST SUITE: Validating the Iterative Brain
# ==========================================

def run_tests():
    print("--- [SENTINEL SYSTEM] Running Tabulated Pathfinder Tests ---\n")

    test_cases = [
        {
            "name": "Standard 3x3 Grid",
            "grid": [
                [10,  2,  1],
                [ 5, 20,  3],
                [ 1,  1, 10]
            ],
            "expected": 48
        },
        # {
        #     "name": "Deep 100x2 Grid (Would likely crash Naive recursion)",
        #     "grid": [[1, 1] for _ in range(100)],
        #     "expected": 101 # 100 rows + 1 right move
        # },
        # {
        #     "name": "Single Intersection",
        #     "grid": [[100]],
        #     "expected": 100
        # },
        # {
        #     "name": "Empty Grid Check",
        #     "grid": [],
        #     "expected": 0
        # }
    ]

    for case in test_cases:
        result = find_max_throughput_tabulated(case["grid"])
        status = "✅ PASS" if result == case["expected"] else "❌ FAIL"
        print(f"Test: {case['name']}")
        print(f"Result: {result} | Expected: {case['expected']} | {status}\n")

if __name__ == "__main__":
    run_tests()