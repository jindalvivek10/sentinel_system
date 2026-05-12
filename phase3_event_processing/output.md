--- [SENTINEL SYSTEM] Starting Phase 3 Naive Orchestrator ---
# Phase 3: Event Processing Simulation Logs

---
## 🧪 1. Naive Orchestrator Simulation
[PRODUCER] Ingesting: INT-101 at 45.0 mph
[PRODUCER] Ingesting: INT-202 at 2.0 mph
[PRODUCER] Ingesting: INT-303 at 15.0 mph
[PRODUCER] Ingesting: INT-404 at 55.0 mph
[PRODUCER] Ingesting: INT-999 at 1.0 mph

[ORCHESTRATOR] Starting SIMULATION Heartbeat (Batch Size: 3)...
=== len in batch = 1
=== len in batch = 2
=== len in batch = 3

--- ⚡ Processing Batch: 3 Events ---
[TRIGGER_AMBULANCE_DP] ID: INT-202 | Pri: 0 | Spd: 2.0
    -> [PHASE 2] Recalculating success map for INT-202...
[RECALCULATE_ROUTE] ID: INT-303 | Pri: 1 | Spd: 15.0
    -> [PHASE 2] Recalculating success map for INT-303...
[LOG_METRICS] ID: INT-101 | Pri: 2 | Spd: 45.0
=== len in batch = 1
=== len in batch = 2

--- ⚡ Processing Batch: 2 Events ---
[TRIGGER_AMBULANCE_DP] ID: INT-999 | Pri: 0 | Spd: 1.0
    -> [PHASE 2] Recalculating success map for INT-999...
[LOG_METRICS] ID: INT-404 | Pri: 2 | Spd: 55.0

[ORCHESTRATOR] Queue drained. Shutting down heartbeat.
**Status:** 🏁 [FINISHED] Naive Orchestrator Simulation Complete
---

---
## 🚀 2. Optimized Dual-Queue Orchestrator Simulation
--- Wave 1: Rapid Ingestion Into FIFO Buffer ---
[PRODUCER] Ingesting: INT-OLD-ROUTINE at 45.0 mph into FIFO
[PRODUCER] Ingesting: INT-OLD-URGENT at 5.0 mph into FIFO

[SYSTEM] Holding execution for 1.5s to accumulate wait time for buffered events...

--- Wave 2: New Influx Joins FIFO Buffer ---
[PRODUCER] Ingesting: INT-NEW-URGENT at 15.0 mph into FIFO

[ORCHESTRATOR] Beginning Processing Heartbeat...

--- ⚡ Processing Sorted Priority Queue: 3 Events ---
[TRIGGER_AMBULANCE_DP] ID: INT-OLD-URGENT  | Dynamic Priority Score:   0.01 | Total Buffer Wait Time: 1.5107s
[LOG_METRICS         ] ID: INT-OLD-ROUTINE | Dynamic Priority Score:   2.00 | Total Buffer Wait Time: 1.5209s
[RECALCULATE_ROUTE   ] ID: INT-NEW-URGENT  | Dynamic Priority Score:   2.52 | Total Buffer Wait Time: 0.0002s
**Status:** 🏁 [FINISHED] Optimized Orchestrator Simulation Complete
---