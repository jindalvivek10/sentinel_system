# Sentinel System: Multiprocess Queue Pipeline

This directory contains a high-throughput, parallel telemetry processing pipeline. Unlike the streaming implementation, this version leverages multi-core parallelism and Inter-Process Communication (IPC) to handle high-volume sensor data by bypassing Python's Global Interpreter Lock (GIL).

## Architecture Overview

The system utilizes a **Producer-Consumer** pattern distributed across isolated OS processes. Data is moved through the pipeline using `multiprocessing.Queue`, ensuring thread-safe communication and decoupling between stages.

### 1. The Logic Engine (`processor.py`)
This module acts as the primary worker process responsible for CPU-bound tasks.
- **Function**: `alert_processor(raw_queue, alert_queue)`
- **Logic**: 
    - **IPC**: Blocks on the `raw_queue` waiting for incoming hex strings.
    - **Parsing**: Transforms raw hex into structured `SensorLog` (NamedTuple) objects.
    - **Bitmasking**: Uses efficient bitwise operations to extract `is_active`, `low_battery`, and `signal_strength`.
    - **Filtering**: Identifies critical logs (Active + Low Battery) and pushes them to the next stage.
    - **Shutdown**: Implements a "Poison Pill" pattern—if it receives `None`, it gracefully shuts down.

### 2. The Dispatch System (`dispatch_system.py`)
The final consumer that executes side-effects (e.g., emergency alerts).
- **Function**: `dispatch_consumer(alert_queue)`
- **Logic**:
    - Listens on the `alert_queue` for critical objects provided by the processor.
    - Triggers simulated emergency protocols for sensors requiring battery service.
    - Handles its own shutdown upon receiving a `None` signal.

### 3. The Orchestrator (Implied)
The main process responsible for:
1. Initializing the shared `multiprocessing.Queue` instances.
2. Spawning the `Process` workers for the Logic Engine and Dispatcher.
3. Feeding raw data into the entry-point queue.
4. Cleaning up and joining processes after sending shutdown signals.

## Why This Design?

| Feature | Benefit |
| :--- | :--- |
| **Parallelism** | Executes parsing and dispatching on separate CPU cores simultaneously. |
| **GIL Bypass** | Since each worker is a separate process, Python's GIL does not bottleneck the pipeline. |
| **Queues** | Provides a memory-safe buffer. If the Dispatcher slows down, the Processor can continue working until the queue is full. |
| **Poison Pill** | A clean, deterministic way to signal shutdown across process boundaries without using forceful kills. |

## Data Format Detail
The status code is a 16-bit integer parsed from Hex:
- **Bit 0 (0x0001)**: Active Status (1 = True, 0 = False)
- **Bit 1 (0x0002)**: Low Battery (1 = True, 0 = False)
- **Bits 2-4 (0x001C)**: Signal Strength (Value 0-7)

## Graceful Shutdown
To ensure the system exits cleanly without leaving zombie processes, the pipeline uses a signaling mechanism:
1. The **Producer** sends `None` to the `raw_queue`.
2. The **Processor** sees `None`, sends `None` to the `alert_queue`, and exits.
3. The **Dispatcher** sees `None` and exits.

## How to Run
Execute the pipeline from the project root (ensure you have an orchestrator script that imports these functions):
```bash
python3 orchestrator.py
```

---

## 🛡️ Comparison: Streaming vs. Multiprocessing

### Streaming (Generators)
*   **Pros**: Extremely low memory footprint, simple single-threaded logic.
*   **Cons**: Bound by a single CPU core; if one stage is slow (like a slow API call), the entire pipeline stalls.
*   **Best for**: Moderate data rates where memory efficiency is the priority.

### Multiprocessing (Queues)
*   **Pros**: True parallel execution; high throughput; decoupled stages.
*   **Cons**: Higher memory overhead (multiple Python interpreters); complex IPC (Inter-Process Communication).
*   **Best for**: High-frequency data or heavy CPU-bound transformation logic.

## 🚀 Future Scalability

### Distributed Queuing
While `multiprocessing.Queue` works for a single machine, this architecture can be scaled horizontally by replacing the internal queues with **Redis** or **RabbitMQ**. This would allow the `processor.py` workers to run on different physical servers than the `dispatch_system.py`.

### Worker Pooling
For even higher loads, multiple `alert_processor` instances can be spawned to read from the same `raw_queue`, effectively load-balancing the parsing work across all available CPU cores.

---
*Developed as part of the Sentinel System Infrastructure.*