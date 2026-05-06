--- [NAIVE SYSTEM] Starting Simulation with 2 Intersections ---
# Sentinel System: Traffic Monitor Simulation Logs

## 1. Naive System Simulation
*   **Logic:** List-append (Infinite history growth)
*   **Time Complexity:** O(K) per update (Slicing/Summing)

### Event Logs
```text
🎬 [Producer] Putting event: {'id': 'INT-A', 'speed': 10.0}
💾 [Internal RAM] History Dictionary : {'INT-A': [10.0]}
🎬 [Producer] Putting event: {'id': 'INT-B', 'speed': 100.0}
💾 [Internal RAM] History Dictionary : {'INT-A': [10.0], 'INT-B': [100.0]}
🎬 [Producer] Putting event: {'id': 'INT-A', 'speed': 20.0}
💾 [Internal RAM] History Dictionary : {'INT-A': [10.0, 20.0], 'INT-B': [100.0]}
🎬 [Producer] Putting event: {'id': 'INT-B', 'speed': 200.0}
💾 [Internal RAM] History Dictionary : {'INT-A': [10.0, 20.0], 'INT-B': [100.0, 200.0]}
🎬 [Producer] Putting event: {'id': 'INT-A', 'speed': 30.0}
💾 [Internal RAM] History Dictionary : {'INT-A': [10.0, 20.0, 30.0], 'INT-B': [100.0, 200.0]}
🎬 [Producer] Putting event: {'id': 'INT-B', 'speed': 300.0}
💾 [Internal RAM] History Dictionary : {'INT-A': [10.0, 20.0, 30.0], 'INT-B': [100.0, 200.0, 300.0]}
🎬 [Producer] Putting event: {'id': 'INT-A', 'speed': 40.0}
💾 [Internal RAM] History Dictionary : {'INT-A': [10.0, 20.0, 30.0, 40.0], 'INT-B': [100.0, 200.0, 300.0]}
🎬 [Producer] Putting event: {'id': 'INT-B', 'speed': 400.0}
💾 [Internal RAM] History Dictionary : {'INT-A': [10.0, 20.0, 30.0, 40.0], 'INT-B': [100.0, 200.0, 300.0, 400.0]}
🎬 [Producer] Putting event: {'id': 'INT-A', 'speed': 50.0}
💾 [Internal RAM] History Dictionary : {'INT-A': [10.0, 20.0, 30.0, 40.0, 50.0], 'INT-B': [100.0, 200.0, 300.0, 400.0]}
🎬 [Producer] Putting event: {'id': 'INT-B', 'speed': 500.0}
💾 [Internal RAM] History Dictionary : {'INT-A': [10.0, 20.0, 30.0, 40.0, 50.0], 'INT-B': [100.0, 200.0, 300.0, 400.0, 500.0]}
```

**Simulation Results:**
*   **Final Internal State (Infinite History):** `{'INT-A': [10.0, 20.0, 30.0, 40.0, 50.0], 'INT-B': [100.0, 200.0, 300.0, 400.0, 500.0]}`
*   **Final Output Queue size:** 10 items.

---

## 2. Optimized System Simulation
*   **Logic:** `deque(maxlen=K)` with Running Balance
*   **Time Complexity:** O(1) per update

### Event Logs
```text
🎬 [Producer] Putting event: {'id': 'INT-A', 'speed': 10.0}
💾 [Internal RAM] History Dictionary : {'INT-A': deque([10.0], maxlen=3)}
🎬 [Producer] Putting event: {'id': 'INT-B', 'speed': 100.0}
💾 [Internal RAM] History Dictionary : {'INT-A': deque([10.0], maxlen=3), 'INT-B': deque([100.0], maxlen=3)}
🎬 [Producer] Putting event: {'id': 'INT-A', 'speed': 20.0}
💾 [Internal RAM] History Dictionary : {'INT-A': deque([10.0, 20.0], maxlen=3), 'INT-B': deque([100.0], maxlen=3)}
🎬 [Producer] Putting event: {'id': 'INT-B', 'speed': 200.0}
💾 [Internal RAM] History Dictionary : {'INT-A': deque([10.0, 20.0], maxlen=3), 'INT-B': deque([100.0, 200.0], maxlen=3)}
🎬 [Producer] Putting event: {'id': 'INT-A', 'speed': 30.0}
💾 [Internal RAM] History Dictionary : {'INT-A': deque([10.0, 20.0, 30.0], maxlen=3), 'INT-B': deque([100.0, 200.0], maxlen=3)}
🎬 [Producer] Putting event: {'id': 'INT-B', 'speed': 300.0}
💾 [Internal RAM] History Dictionary : {'INT-A': deque([10.0, 20.0, 30.0], maxlen=3), 'INT-B': deque([100.0, 200.0, 300.0], maxlen=3)}
🎬 [Producer] Putting event: {'id': 'INT-A', 'speed': 40.0}
💾 [Internal RAM] History Dictionary : {'INT-A': deque([20.0, 30.0, 40.0], maxlen=3), 'INT-B': deque([100.0, 200.0, 300.0], maxlen=3)}
🎬 [Producer] Putting event: {'id': 'INT-B', 'speed': 400.0}
💾 [Internal RAM] History Dictionary : {'INT-A': deque([20.0, 30.0, 40.0], maxlen=3), 'INT-B': deque([200.0, 300.0, 400.0], maxlen=3)}
🎬 [Producer] Putting event: {'id': 'INT-A', 'speed': 50.0}
💾 [Internal RAM] History Dictionary : {'INT-A': deque([30.0, 40.0, 50.0], maxlen=3), 'INT-B': deque([200.0, 300.0, 400.0], maxlen=3)}
🎬 [Producer] Putting event: {'id': 'INT-B', 'speed': 500.0}
💾 [Internal RAM] History Dictionary : {'INT-A': deque([30.0, 40.0, 50.0], maxlen=3), 'INT-B': deque([300.0, 400.0, 500.0], maxlen=3)}
```

**Simulation Results:**
*   **Final Internal State (Capped Windows):** `{'INT-A': deque([30.0, 40.0, 50.0], maxlen=3), 'INT-B': deque([300.0, 400.0, 500.0], maxlen=3)}`
*   **Final Output Queue size:** 10 items.