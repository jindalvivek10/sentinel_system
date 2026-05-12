# Sentinel System: High-Concurrency Event Orchestrator

This directory implements the core "Nervous System" of the Sentinel municipal operating system. It handles high-frequency telemetry streams from city-wide sensors, prioritizes emergency patterns, and safely dispatches events to the heavy computational pathfinding engines (Phase 2 DP Brain) without locking up the system.

---

## 🏛️ Architecture Overview (The ER Analogy)

* **The Naive Orchestrator**: Functions like an Emergency Room receptionist who forces the front doors closed until exactly 3 patients are waiting. The receptionist then freezes all new intakes, sorts those 3 patients by trauma severity, and blocks the entry lane until doctors finish treating all 3. If a patient requires a slow 2-hour procedure, the whole facility locks out incoming life-critical emergencies.
* **The Optimized Orchestrator**: Functions like an advanced dual-stage triage center. Arriving patients are instantly dropped into a rapid intake buffer without waiting. A triage handler constantly streams patients out of this buffer, measures exactly how long they have been waiting relative to their condition, dynamically updates their priority score, and routes them through a self-sorting queue. Older routine cases steadily move forward so they aren't completely starved of care by minor new arrivals.

---

## 1. The Naive Orchestrator (`naive_event_orchestrator.py`)

A batch-processing engine that groups events into lists and sorts them repeatedly.

### 🔄 Core Workflow

1. **Ingestion**: Receives telemetry data and pushes raw inputs into a standard thread-safe `queue.Queue`.
2. **Batch Collection**: Blocks for up to 2 seconds per item to accumulate a fixed slice of records (`batch_size = 3`).
3. **Enrichment**: Extracts events from the buffer and assigns static priority values based on raw speed (0 for Critical, 1 for Urgent, 2 for Routine).
4. **Timsort Pass**: Executes an explicit `list.sort()` operation over the local batch based on `(priority, timestamp)`.
5. **Synchronous Dispatch**: Loops through the batch sequentially, invoking the pathfinder code while blocking all entry tasks.

### 🛑 Architectural Bottlenecks

* **Batch-Local Blindness**: Priority is only observed within the immediate batch of 3. A Critical event arriving late must wait in line behind an entire batch of earlier routine items.
* **The $O(N \log N)$ Sorting Tax**: Sorting an array repeatedly introduces high CPU consumption as volume grows.
* **Priority Starvation**: Routine events are consistently forced behind critical ones inside every batch, preventing them from being processed during high-volume spikes.
* **Latency-Inducing Timeouts**: If sensor data traffic slows down, the loop freezes for several seconds trying to fulfill its minimum batch size, stalling ready events.

---

## 2. The Optimized Orchestrator (`optimized_event_orchestrator.py`)

A production-grade, dual-stage streaming pipeline that decouples physical ingestion from scheduling math.

### 🔄 Core Workflow

* **Stage 1: The Rapid Buffer (FIFO Ingestion)**
Sensors drop raw event payloads into an instantaneous, $O(1)$ constant-time `queue.Queue`. No threshold checks or scheduling math happen here, completely eliminating ingestion backpressure.
* **Stage 2: Dynamic Prioritization & Triage (Min-Heap Population)**
During the processing cycle, the engine drains the FIFO queue entirely. It tracks the exact timestamp when the event hit the system boundaries and maps it against a stable anchor time using an addition-based aging engine.
* **Stage 3: Streaming Execution**
The engine pops items from a `queue.PriorityQueue` one-by-one. It handles tasks in exact global urgency order without needing to hold or block for batch construction.

### ⚙️ The Mathematical Addition-Aging Engine

To avoid negative priority scores and ensure clean system diagnostics, the orchestrator calculates sorting priorities using absolute timeline tracking:

$$\text{Priority Score} = \text{Base Priority} + (\text{Elapsed Seconds Since Epoch} \times \text{Aging Factor})$$

Because Python's underlying priority queue acts as a **Min-Heap**, the item with the smallest numerical score is popped first. Older events have an earlier arrival time, yielding a smaller value for elapsed seconds. When added to the base priority, their score remains low, allowing long-waiting routine events to bubble up ahead of brand-new incoming urgent cases.

### 🛡️ Tuple Crash Defense

Python's priority queue throws a terminal `TypeError` if it attempts to compare dictionary payloads when sorting scores are identical. To defend against this, the orchestrator wraps events inside a 4-element tuple containing a lock-protected, auto-incrementing integer:

$$\text{Heap Structure} = (\text{Effective Priority}, \text{Arrival Timestamp}, \text{Sequence ID}, \text{Payload})$$

The `Sequence ID` acts as an absolute tie-breaker, guaranteeing that Python never compares the raw data dictionaries.

---

## 🚀 Simulation Mechanics & Verification

The included simulation run explicitly tests the dynamic aging mechanism in a single-threaded environment to clearly illustrate priority changes without concurrent logging clutter:

1. **Wave 1 Intake**: Pushes an old routine item (`INT-OLD-ROUTINE`) followed immediately by an old urgent item (`INT-OLD-URGENT`).
2. **Pipeline Stall**: The main thread sleeps for 1.5 seconds, allowing Wave 1 events to accrue substantial buffer wait time.
3. **Wave 2 Intake**: Pushes a brand-new urgent item (`INT-NEW-URGENT`).
4. **The Heartbeat Execution**: The optimized engine processes the queue. Because of the aging offset, the calculated scores sort the old routine item **ahead** of the new urgent item, demonstrating zero starvation under heavy load.