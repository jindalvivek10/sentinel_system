"""
FILE: naive_event_orchestrator.py

SYSTEM ROLE: 
The "Nervous System" of Sentinel. It receives raw telemetry (speed) from intersections, 
determines the urgency (Priority), and organizes the data for the DP Brain.

REAL-WORLD CONNECTION:
If a sensor reports 2mph in a 50mph zone, that is a 'Critical' event (Potential Accident).
The Orchestrator must recognize this instantly, bump it to the front of the line, 
and trigger the Phase 2 "Relief Route" calculation.

PSEUDO-LOGIC (The "Batch, Validate, & Sort" Strategy):
1. INGESTION: Intersections drop raw JSON-like data into a thread-safe Queue.
2. VALIDATION (The Action Map): 
   - Pull events from the queue.
   - Look at the 'speed' value. 
   - Assign a Priority: 0 (Critical), 1 (Urgent), 2 (Routine).
3. THE TIE-BREAKER: 
   - We store events as (Priority, Timestamp). 
   - If two Ambulances (Priority 0) arrive, the one with the earlier timestamp goes first.
4. BATCH PROCESSING:
   - To be efficient, we don't sort after every single ping. We collect a "wave" 
     of data, sort the entire wave by Priority, and then execute.
5. HAND-OFF: 
   - High-priority events trigger the Phase 2 DP pathfinder.
PSEUDO-LOGIC (The "Batch, Validate, & Sort" Strategy - Detailed Flow):
1. INGESTION: Telemetry Reception
   - Mechanism: Raw sensor data, typically in a JSON-like format containing `intersection_id` and `speed`, is pushed into a `queue.Queue` instance. This queue is designed to be thread-safe, allowing multiple sensor producers to feed data concurrently without race conditions.
   - Purpose: Acts as the initial buffer for all incoming events, decoupling the data producers from the processing logic.

2. COLLECTION: Batch Formation
   - Goal: The orchestrator attempts to gather a fixed number of events (`batch_size`) from the `ingestion_queue` to process them together. This batching strategy aims to amortize the overhead of sorting.
   - Process: Events are continuously pulled from the queue using a blocking `get()` call with a `timeout`. This timeout is crucial for responsiveness, allowing the orchestrator to periodically check for termination conditions or to process a partial batch if the incoming data rate is low.

3. ENRICHMENT: Priority Assignment & Action Mapping
   - Transformation: As each raw event is pulled from the queue, it undergoes an enrichment step. The `_assign_priority` method evaluates the `speed` value against predefined, hard-coded thresholds.
   - Priority Levels:
     - `0` (CRITICAL): Assigned for very low speeds (e.g., <= 5.0 mph), indicating potential accidents or gridlock. These events trigger immediate, high-priority actions.
     - `1` (URGENT): Assigned for speeds below a configurable `speed_threshold` (e.g., <= 30.0 mph), suggesting heavy traffic or congestion. These require route recalculations.
     - `2` (ROUTINE): Assigned for speeds above the `speed_threshold`, indicating free-flowing traffic. These are typically logged for metrics.
   - Metadata Addition: The assigned `priority` and a corresponding `action` string (e.g., "TRIGGER_AMBULANCE_DP") are added as new fields to the event dictionary.

4. SORTING: Prioritization within the Batch
   - Algorithm: Once the collection phase is complete (either `batch_size` is met or the queue is empty), the `active_batch` (a standard Python list) is sorted. Python's built-in Timsort algorithm is used, which is efficient for partially sorted data.
   - Sorting Keys:
     - Primary Key: `priority` (ascending order). Events with lower priority numbers (e.g., 0 for Critical) will appear first in the sorted batch.
     - Secondary Key: `timestamp` (ascending order). For events with identical priority, the one that arrived earlier (smaller timestamp) will be processed first, ensuring a FIFO (First-In, First-Out) order within the same priority level.

5. DISPATCH: Action Execution
   - Iteration: The orchestrator iterates through the now sorted `active_batch`, processing events one by one.
   - Conditional Action: For events with `priority` less than `2` (i.e., Critical or Urgent), the `_run_phase2_strategic_pathfinder` method is invoked. This simulates a call to a downstream system responsible for more complex analysis or action.
   - Blocking Call: This dispatch step is currently synchronous and blocking. If the `_run_phase2_strategic_pathfinder` call takes a significant amount of time, the entire orchestrator loop pauses, preventing further event ingestion or processing.

6. REPEAT: Cycle Restart
   - Cleanup: After all events in the `active_batch` have been dispatched, the `active_batch` list is cleared to prepare for the next cycle.
   - Loop Continuation: The orchestrator then returns to the `COLLECTION` phase, attempting to pull new events from the `ingestion_queue`.
   - Termination (Simulation Mode): If `continuous` mode is `False` and the `ingestion_queue` is empty, the loop terminates, allowing the simulation to conclude.
   - Idle Sleep (Continuous Mode): In `continuous` mode, a small `time.sleep()` is introduced when the queue is idle to prevent the orchestrator from consuming 100% CPU cycles in a busy-wait loop.

COMPLEXITY ANALYSIS:
- TIME: O(N log N) per batch.
  * Explanation: Sorting the batch of N events by priority and timestamp takes logarithmic time.
- SPACE: O(N) 
  * Explanation: We store N events in the queue and then N events in the processing list.
- LIMITATION: This is "Blocking." If the DP calculation takes 2 seconds, 
  the whole system stops and waits. (We will fix this in the Optimized version).

BOTTLENECKS & ISSUES (Why this is "Naive"):
1. BATCH-LOCAL PRIORITY: Priority is only respected WITHIN the batch. If a 
   'Critical' event arrives while a 'Routine' batch is processing, it must 
   wait. A true priority system should allow 'Critical' events to "jump" the 
   entire ingestion queue.
2. SYNCHRONOUS BLOCKING: The processing loop is serial. If a Phase 2 pathfinder 
   execution is slow, it blocks the orchestrator from collecting or sorting 
   new incoming data.
3. COLLECTION LATENCY: The 'while' loop for collection can be inefficient.
   It waits for a timeout (2s) for every single missing item in a batch, 
   potentially stalling processing of existing events if sensor input is slow.
4. SORTING OVERHEAD: Sorting an entire list for every batch is more expensive 
   than maintaining a self-sorting structure like a Min-Heap.
"""

import queue
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

class NaiveEventOrchestrator:
    """
    A Production-Grade Naive Orchestrator.
    Handles data validation, priority assignment, and batch sorting.
    """

    def __init__(self, speed_threshold: float = 25.0):
        # Thread-safe FIFO queue for incoming sensor data
        self.ingestion_queue: queue.Queue = queue.Queue()
        self.speed_threshold = speed_threshold
        
        # Internal list to hold the current batch being sorted/processed
        self.active_batch: List[Dict[str, Any]] = []

    def _assign_priority(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        The 'Action Engine'. Maps raw speed to a system priority.
        Staff Principle: Lower numbers = Higher priority (Standard convention).
        """
        # NAIVE: Fixed thresholds. A more robust system would use relative 
        # speed (delta from speed limit) or dynamic thresholds.
        speed = event["speed"]
        
        if speed <= 5.0:
            event["priority"] = 0  # CRITICAL: Accident/Gridlock
            event["action"] = "TRIGGER_AMBULANCE_DP"
        elif speed <= self.speed_threshold:
            event["priority"] = 1  # URGENT: Heavy Traffic
            event["action"] = "RECALCULATE_ROUTE"
        else:
            event["priority"] = 2  # ROUTINE: Free flow
            event["action"] = "LOG_METRICS"
            
        return event

    def process_live_queue(self, batch_size: int = 3, continuous: bool = False) -> None:
        """
        The core heartbeat loop. 
        - continuous=True: Runs forever (Production behavior).
        - continuous=False: Exits when queue is empty (Simulation behavior).
        """
        mode = "CONTINUOUS" if continuous else "SIMULATION"
        print(f"\n[ORCHESTRATOR] Starting {mode} Heartbeat (Batch Size: {batch_size})...")

        while True:
            # 1. COLLECTION PHASE (Naive): Fill the batch as much as possible.
            while len(self.active_batch) < batch_size:
                try:
                    # If the queue is empty, `get` will block for `timeout` seconds.
                    raw_data = self.ingestion_queue.get(block=True, timeout=2)
                    validated_data = self._assign_priority(raw_data)
                    self.active_batch.append(validated_data)
                    print(f"=== len in batch = {len(self.active_batch)}")

                except queue.Empty:
                    # If queue is empty, stop filling this batch and process what we have
                    break

            # 2. Processing Phase: Only run if we actually collected data.
            # 2. PROCESSING PHASE (Naive): Sequential execution.
            if self.active_batch:
                # Sort by Priority (Low number first), then Timestamp - O(N log N)
                # BOTTLENECK: Sorting the entire list is less efficient than using a Priority Queue.
                self.active_batch.sort(key=lambda x: (x['priority'], x['timestamp']))

                print(f"\n--- ⚡ Processing Batch: {len(self.active_batch)} Events ---")
                for event in self.active_batch:
                    print(f"[{event['action']}] ID: {event['intersection_id']} | "
                          f"Pri: {event['priority']} | Spd: {event['speed']}")
                                        
                    # BOTTLENECK: This call is BLOCKING. If Phase 2 takes time, we 
                    # cannot process the next event in the batch or ingest new ones.
                    if event["priority"] < 2:
                        self._run_phase2_strategic_pathfinder(event["intersection_id"])
                
                # Clear memory for next batch cycle
                self.active_batch.clear()

            # 3. TERMINATION PHASE
            # If simulation mode and queue is drained, we exit so the script can finish.
            if not continuous and self.ingestion_queue.empty():
                print("\n[ORCHESTRATOR] Queue drained. Shutting down heartbeat.")
                break
            
            # Small sleep to prevent 100% CPU usage when the queue is idle.
            if continuous:
                time.sleep(2)

    def _run_phase2_strategic_pathfinder(self, intersection_id: str):
        """
        Simulated link to the Phase 2 DP code.
        In a real system, this would instantiate the grid and find the max throughput.
        """
        # This is a placeholder for a more complex, potentially time-consuming, Phase 2 operation.
        print(f"    -> [PHASE 2] Recalculating success map for {intersection_id}...")
        pass

# ==========================================
# SIMULATION: The Smart-City "Rush Hour"
# ==========================================

def run_simulation():
    print("--- [SENTINEL SYSTEM] Starting Phase 3 Naive Orchestrator ---\n")
    
    # Initialize with a 30mph urgency threshold
    orchestrator = NaiveEventOrchestrator(speed_threshold=30.0)

    # 1. Simulate a wave of incoming data
    # Note: We send them out of order (Routine first, then Critical)
    sensor_data_stream = [
        ("INT-101", 45.0),  # Routine
        ("INT-202", 2.0),   # CRITICAL (Accident)
        ("INT-303", 15.0),  # URGENT (Congestion)
        ("INT-404", 55.0),  # Routine
        ("INT-999", 1.0),   # CRITICAL (Accident - Arrived slightly later)
    ]

    for intersection_id, speed in sensor_data_stream:
        # Directly creating the payload and putting it in the queue to reduce redundancy
        payload = {
            "intersection_id": intersection_id,
            "speed": speed,
            "timestamp": datetime.now().timestamp()
        }
        print(f"[PRODUCER] Ingesting: {intersection_id} at {speed} mph")
        orchestrator.ingestion_queue.put(payload)
        time.sleep(0.01)  # Ensure unique timestamps

    # 2. Trigger the automated processing heartbeat
    # This will now internally loop and process batches until the queue is empty.
    orchestrator.process_live_queue(batch_size=3)

if __name__ == "__main__":
    run_simulation()