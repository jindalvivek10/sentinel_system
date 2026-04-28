# Sentinel System: Streaming Log Processor

This directory contains a high-performance, memory-efficient telemetry processing pipeline designed to handle real-time sensor data using Python's generator-based streaming architecture.

## Architecture Overview

The system follows a **Source -> Pipe -> Sink** pattern. Instead of processing data in large batches (which consumes significant memory), this implementation uses **Lazy Evaluation**. Data flows through the system one record at a time, keeping the memory footprint constant (O(1) space complexity relative to the stream size).

### 1. The Source (`sensor_stream.py`)
This module simulates a raw hardware feed or a network socket.
- **Function**: `get_raw_telemetry_stream()`
- **Output**: An `Iterator[str]` yielding hex-encoded telemetry strings (e.g., `Bridge_X:0x0003`).
- **Purpose**: Represents the entry point of data into the system.

### 2. The Pipe (`processor.py`)
This is the "Middleware" containing the business logic and data cleaning.
- **Function**: `filter_critical_alerts(stream)`
- **Logic**: 
    - Parses raw strings into immutable `SensorLog` (NamedTuple) objects.
    - Uses bitwise operations (`&` and `>>`) to extract status flags from 16-bit hex codes.
    - **Filtering**: It only yields logs where the sensor is both `Active` (Bit 0) and has a `Low Battery` (Bit 1).
- **Purpose**: Transforms and filters raw data into structured, actionable information.

### 3. The Sink (`dispatch_system.py`)
The final destination for processed alerts.
- **Function**: `alert_emergency_units(alert_stream)`
- **Logic**: Iterates over the incoming stream of critical logs and triggers external actions (simulated by console logging).
- **Purpose**: Executes side effects based on processed telemetry.

### 4. The Orchestrator (`orchestrator_pipeline.py`)
This acts as the system's "wiring" or "message broker simulation."

#### Step-by-Step Execution Flow:
1.  **Initialize Source**: Calls `get_raw_telemetry_stream()` to get a generator object. No data is fetched yet.
2.  **Instantiate Logic**: Creates the `SentinelProcessor`.
3.  **Construct Pipeline**: Passes the raw generator into `processor.filter_critical_alerts()`. This creates a *nested* generator. **Note:** At this point, no processing has occurred.
4.  **Trigger Execution**: The `alert_emergency_units()` function starts a `for` loop. This "pulls" the first item from the processor, which in turn "pulls" the first item from the sensor stream.
5.  **Streaming Loop**: Each log travels the full length of the pipeline (Raw -> Parsed -> Filtered -> Dispatched) before the next log is even read from the source.

## Why This Design?

| Feature | Benefit |
| :--- | :--- |
| **Generators** | Handles infinite data streams without crashing from memory exhaustion. |
| **Bitmasking** | Extremely fast status extraction compared to JSON or string parsing. |
| **NamedTuples** | Provides immutability and memory efficiency while maintaining readability. |
| **Decoupling** | Each service (Source, Pipe, Sink) is independent; you can swap the Source from a mock to a Kafka consumer without changing the Processor. |

## Data Format Detail
The status code is a 16-bit integer parsed from Hex:
- **Bit 0 (0x0001)**: Active Status (1 = True, 0 = False)
- **Bit 1 (0x0002)**: Low Battery (1 = True, 0 = False)
- **Bits 2-4 (0x001C)**: Signal Strength (Value 0-7)

A log is considered **CRITICAL** only if `(status_code & 0x0001)` and `(status_code & 0x0002)` are both truthy.

## How to Run
Execute the pipeline from the project root:
```bash
python3 orchestrator_pipeline.py
```
You will see logs being generated and processed in real-time. Use `Ctrl+C` to terminate the simulation.

---
*Developed as part of the Sentinel System Infrastructure.*