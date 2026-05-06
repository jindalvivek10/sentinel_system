# Sentinel System: Dynamic Programming Pathfinder

This document outlines the architectural evolution of our traffic throughput pathfinding algorithm. We explore the transition from a naive brute-force approach to a production-grade Bottom-Up Dynamic Programming (DP) solution.

## The Objective
Given a city grid where each cell represents a traffic capacity (throughput), find the path from the **Top-Left (0,0)** to the **Bottom-Right (N,M)** that yields the maximum total capacity. Movement is restricted to **Right** and **Down**.

---

## Phase 1: Naive Recursion (The "Explorer")
**File:** `naive_recursive_max_capacity_path.py`

The simplest way to solve this is to explore every possible branch. At every intersection, the algorithm asks: "Should I go Right or Down?" and recursively calculates the score for both.

### The Logic
1. **Base Case**: If at the finish line, return the cell value.
2. **Recursive Step**: `Current + Max(Recursive_Right, Recursive_Down)`.

### The Issues
*   **Exponential Explosion ($O(2^{N+M})$)**: Without memory, the algorithm recalculates the best path for the same intersection millions of times if reached via different routes.
*   **Performance**: Even a 20x20 grid can take seconds, and a 100x100 grid would take years to complete.

---

## Phase 2: Top-Down Memoization (The "Notebook")
**File:** `max_paths_with_memory_optimized.py`

To fix the efficiency issue, we introduce **Memoization**. We use a "notebook" (a dictionary) to store the result of an intersection the first time we calculate it.

### The Logic
*   Before performing any math, the function checks: "Is this coordinate in my notebook?"
*   If yes, it returns the stored value immediately.
*   If no, it calculates it once and saves it.

### The Improvement
*   **Time Complexity**: Reduced to $O(N \times M)$. We only perform "actual math" once per cell.

### The Remaining Issue
*   **Recursion Depth**: Python has a limit on how deep the "call stack" can go. For massive grids (e.g., 10,000x10,000), this approach will trigger a `RecursionError` (Stack Overflow), crashing the system.

---

## Phase 3: Bottom-Up Tabulation (The "Success Map")
**File:** `max_paths_dynamic.py`

This is the final, production-grade evolution. Instead of starting at the beginning and looking forward, we start at the **Destination** and build a "Success Map" backwards.

### The Strategy
1.  **The Foundation**: The max throughput at the destination is just the destination's value.
2.  **The Edges**:
    *   On the bottom row, you can only go Right.
    *   On the rightmost column, you can only go Down.
3.  **The Decision Engine**: For all other cells, we fill the table by looking at the already-calculated cells to the Right and Below:
    `DP[r][c] = Grid[r][c] + Max(DP[r+1][c], DP[r][c+1])`

### Why This Wins
*   **Iterative, Not Recursive**: It uses standard loops. There is no risk of hitting recursion limits.
*   **Predictable Performance**: It visits every cell exactly once. A 100x100 grid takes exactly 10,000 operations every time.
*   **Memory Safety**: The memory usage is bounded exactly to the size of the grid.

---

## Comparison Summary

| Metric | Naive Recursion | Top-Down (Memoization) | Bottom-Up (Tabulation) |
| :--- | :--- | :--- | :--- |
| **Time Complexity** | $O(2^{N+M})$ (Terrible) | $O(N \times M)$ (Great) | $O(N \times M)$ (Great) |
| **Space Complexity** | $O(N+M)$ (Stack) | $O(N \times M)$ (Dict + Stack) | $O(N \times M)$ (Table) |
| **Large Grid Safety**| ❌ Crashingly Slow | ❌ `RecursionError` | ✅ **Safe & Stable** |
| **Logic Flow** | Forward-looking | Forward-looking | Backward-building |

## Implementation Note
In the `Sentinel System`, we utilize the **Bottom-Up** approach. In high-throughput traffic monitoring, grid sizes can be unpredictable, and system stability is paramount. Avoiding the Python recursion stack ensures that our pathfinder remains robust regardless of the city's scale.

---
*Developed for Phase 2 of the Sentinel System Infrastructure.*