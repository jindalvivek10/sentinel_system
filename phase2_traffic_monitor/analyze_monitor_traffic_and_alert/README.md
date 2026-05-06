# Sentinel System: Traffic Monitor Simulation

This directory explores algorithmic efficiency and memory management in the context of real-time streaming analytics. It focuses on the challenge of calculating **Sliding Window Averages** for high-frequency traffic data coming from multiple sensor points (intersections).

## Architecture Overview

The system simulates a stream of speed readings. We compare two distinct architectural patterns for managing historical state and performing calculations:

### 1. The Naive Monitor (`naive_streaming_monitor.py`)
A straightforward implementation that prioritizes code simplicity but fails to scale in production environments.
- **Logic**: Uses a standard Python `list` to store every historical reading for every intersection ID.
- **Processing**:
    - **Appends**: Every new data point is appended to an ever-growing list.
    - **Slicing**: To calculate the average, the system slices the list to retrieve the last `K` items.
    - **Summing**: It performs a `sum()` operation over the slice for every new event.
- **Drawback**: This creates a **Memory Leak** as the internal state grows indefinitely ($O(N)$ space) and consumes more CPU as the window size $K$ increases ($O(K)$ time).

### 2. The Optimized Monitor (`optimized_streaming_monitor.py`)
A memory-efficient, production-grade engine using the **"Running Balance"** pattern.
- **Logic**: Leverages `collections.deque(maxlen=K)` for automatic memory management and a dedicated dictionary for `running_sums`.
- **Processing**:
    - **Bounded Memory**: The `deque` automatically evicts the oldest record when the window is full, keeping memory usage constant.
    - **Subtraction Phase**: If the window is full, the system subtracts the value about to be evicted from the running sum.
    - **Addition Phase**: Adds the new speed to the running sum and the `deque` simultaneously.
- **Benefit**: Turns an $O(K)$ summation problem into an $O(1)$ arithmetic update, ensuring performance remains constant regardless of the window size.

## Why This Design?

| Feature | Naive (List Slicing) | Optimized (Running Balance) |
| :--- | :--- | :--- |
| **Time Complexity** | $O(K)$ per update | **$O(1)$ per update** |
| **Space Complexity** | $O(N)$ (Infinite growth) | **$O(I * K)$ (Capped)** |
| **Memory Safety** | Risk of RAM exhaustion | **Bounded and Predictable** |
| **Summation** | Iterative (loops through list) | **Arithmetic (Single subtraction/addition)** |

## Key Concepts

### The Running Balance Pattern
Instead of re-calculating the total sum from scratch every time a new event arrives, we maintain a "balance sheet." By knowing what value is leaving the window and what value is entering, we can update the total in two simple operations. This is critical for high-throughput systems where $K$ (the window size) might represent thousands of data points.

### Memory Management with Deques
Standard Python lists do not have a maximum size. Using `collections.deque(maxlen=K)` ensures that the Python interpreter handles the eviction of old data at the C-level, which is faster and more reliable than manual list management.

## Data Flow Detail
1. **Input**: A dictionary representing a sensor hit: `{"id": "INT-A", "speed": 45.5}`.
2. **State Lookup**: The monitor identifies the historical window for that specific `id`.
3. **Window Update**:
   - **Naive**: Append to list.
   - **Optimized**: Update running sum and push to deque.
4. **Output**: Emits the current average and a memory usage diagnostic to the output queue.

## How to Run

You can execute the simulations independently to compare the logs and observe the internal state growth:

**Run Naive Simulation (Watch the lists grow):**
```bash
python3 naive_streaming_monitor.py
```

**Run Optimized Simulation (Watch the deques stay capped):**
```bash
python3 optimized_streaming_monitor.py
```

## 🚀 Future Scalability

### 1. Persistence
In a real-world scenario, these internal dictionaries could be backed by an in-memory database like **Redis**. Redis supports "Sorted Sets" and "Streams" which can implement sliding windows natively.

### 2. Distributed Processing
The `id`-based partitioning used here (mapping histories to IDs) allows this logic to be easily shared across multiple worker nodes using a hashing algorithm (Consistent Hashing), enabling the system to monitor millions of intersections in parallel.

---
*Developed as part of the Sentinel System Infrastructure.*