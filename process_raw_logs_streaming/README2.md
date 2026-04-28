# 🏙️ Sentinel System: Phase 1 Architectural Deep-Dive

This document outlines the **Streaming Ingestion Architecture** for the Global Smart-City Sentinel System. Unlike traditional batch-processing scripts, this system is designed to handle infinite, high-velocity telemetry with a constant memory footprint using Python 3.12 generators.

---

## 🏗️ 1. The Plumbing: Orchestrator Setup
Before any data flows, the `orchestrator_pipeline.py` defines the "shape" of the system. This is done through **Functional Composition**, where we connect independent services without them "knowing" about each other.

1.  **The Source:** The orchestrator calls `get_raw_telemetry_stream()`. This returns a **Generator Object**. The "tap" is closed; no logs have been generated yet.
2.  **The Transformer:** The orchestrator passes that generator into `processor.filter_critical_alerts()`. We now have a "filter" attached to the "pipe."
3.  **The Sink:** Finally, the filtered generator is passed into `dispatch_system.alert_emergency_units()`. 

**Staff Insight:** At this stage, memory usage is near zero. We have built the machine, but we haven't turned the engine on.

---

## 🌊 2. The Data Flow: The "Pull" Mechanism
In this architecture, data is not "pushed" from the sensor; it is **"pulled"** from the bottom up by the Dispatcher.

1.  **Demand:** The Dispatcher's `for` loop asks for an alert (`next()`).
2.  **Request:** This request travels backward through the `Processor`. 
3.  **Extraction:** The `Processor` asks the `Sensor Stream` for a raw string. 
4.  **Generation:** Only now does the `Sensor Stream` wake up, finish its `time.sleep()`, and `yield` a hex string.
5.  **Validation (The Filter):** The `Processor` checks the bitmask.
    *   **If Critical:** It transforms the hex into a `SensorLog` and yields it to the Dispatcher.
    *   **If Not Critical:** It loops back *internally* to ask the Sensor Stream for another string. This is why you may see multiple "Batch" logs before a single alert appears.
6.  **Action:** The Dispatcher receives the object and executes the emergency logic.

---

## ⚖️ 3. Why This Approach? (Staff-Level Trade-offs)

We moved from **Batching** (Day 1) to **Streaming** (Today). Here is the technical justification:

### 🚀 Memory Efficiency: O(1) vs. O(N)
*   **The Old Way (Batch):** Storing 1,000,000 logs in a list requires O(N) memory. If the traffic spikes, the system crashes with an `OutOfMemory` (OOM) error.
*   **The New Way (Stream):** We only ever hold **one** log in memory at any given microsecond. The memory footprint is constant (O(1)), making the system infinitely scalable.

### ⏱️ Latency: Immediate vs. Blocked
*   **The Old Way (Batch):** You must wait for the entire list to finish processing before the first alert is sent.
*   **The New Way (Stream):** The moment a critical bit is detected, it is dispatched. There is zero "buffer wait" time.

### 🛑 Natural Backpressure
*   Because the `Sensor Stream` **pauses** at the `yield` statement, it cannot produce data faster than the `Dispatcher` can consume it. This prevents the "Buffer Bloat" that typically crashes high-volume distributed systems.

---

## 📂 Component Summary

*   **`orchestrator_pipeline.py`**: The Architect. Simulates a Message Broker (like Kafka/PubSub) by wiring the pipeline.
*   **`sensor_stream.py`**: The Hardware Interface. Produces raw telemetry strings.
*   **`processor.py`**: The Logic Core. Performs O(1) bitwise filtering and validation.
*   **`dispatch_system.py`**: The Action Layer. The "Pump" that drives the entire system loop.

---

### 🛠️ Execution
To start the end-to-end simulation:
```bash
python3 orchestrator_pipeline.py