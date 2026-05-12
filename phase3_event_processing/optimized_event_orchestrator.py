"""
FILE: optimized_event_orchestrator.py

EXAMPLE Real Analogy
The Optimized Orchestrator (New Code): The ER receptionist drops every single arriving patient into a rapid intake buffer 
without stopping to interview them. A dedicated triage nurse constantly pulls people from this buffer, calculates exactly 
how long they have been waiting relative to their condition, assigns them a dynamic priority score, and places them into 
a self-sorting priority line. If a routine patient has been waiting for an exceptionally long time, their priority score decreases 
gradually so they aren't starved of care by minor incoming urgent cases.

SYSTEM ROLE: 
The high-performance "Autonomic Nervous System" of Sentinel. It decouples high-speed telemetry 
ingestion from prioritization using two distinct sequential queue layers: a standard FIFO 
Ingestion Queue (queue.Queue) and a self-sorting Priority Queue (queue.PriorityQueue).
Priority calculations are explicitly deferred to processing time.

REAL-WORLD CONNECTION:
By calculating priority at processing time rather than ingestion time, we capture the true 
latency an event experienced while sitting in the city's ingestion buffer. This allows us 
to implement an aging mechanism: if a routine traffic log sits in the queue too long under 
heavy emergency workloads, its wait time forces it to bubble up, preventing data starvation.

PSEUDO-LOGIC (The "Ingest-Buffer, Prioritize-at-Processing" Strategy - Detailed Flow):
1. STAGE 1: RAW INGESTION (The Rapid Buffer)
   - Mechanism: Sensors drop raw JSON payloads into a standard FIFO `queue.Queue`.
   - Optimization: Zero logic occurs here. We prioritize ingestion speed to prevent 
     backpressure on the sensors. Every event is timestamped the moment it arrives.

2. STAGE 2: DYNAMIC PRIORITIZATION & AGING (The Triage)
   - Mechanism: The orchestrator drains the FIFO buffer into a `queue.PriorityQueue` (Min-Heap).
   - The Aging Formula: 
     `effective_priority = base_priority + ((arrival_time - system_epoch) * aging_factor)`
   - Logic: Newer events have larger timestamps. By adding time to the base priority, 
     older events maintain smaller total scores. Since Python's Heap is a Min-Heap, 
     smaller scores stay at the front.

3. STAGE 3: ACTION DISPATCH (The Execution)
   - Mechanism: The orchestrator pops the item with the absolute lowest `effective_priority` 
     score from the heap.
   - Result: This allows an "Old Routine" event to eventually jump ahead of a 
     "Brand New Urgent" event if it has been waiting long enough.

SOLVING THE NAIVE BOTTLENECKS:
1. FIXES BATCH-LOCAL PRIORITY: Unlike the Naive version which only sorts 3 items 
   at a time, this system considers the ENTIRE buffer. A Critical event can jump 
   to the front of the entire line immediately.
2. FIXES SORTING OVERHEAD: Replaces the O(N log N) `list.sort()` with O(log N) 
   heap insertions, providing consistent performance as the queue grows.
3. FIXES DATA STARVATION: The `aging_factor` ensures that even low-priority 
   logs are eventually processed during heavy traffic spikes.
4. THE TUPLE CRASH DEFENSE:
   - Elements are stored in the heap as: (effective_priority, arrival_time, sequence_id, payload)
   - The auto-incrementing `sequence_id` prevents comparison crashes on dictionary payloads.

4. STAGE 3: ACTION DISPATCH (Execution)
   - The orchestrator drains the priority queue one-by-one, popping the absolute most urgent item, 
     demonstrating how old routine items can jump ahead of brand-new urgent ones.

COMPLEXITY ANALYSIS:
- TIME: 
  * Ingestion Stage: O(1) constant time per incoming sensor ping.
  * Sorting Stage: O(log N) per event to push into and pop from the Min-Heap.
- SPACE: O(N) linear memory footprint across both queue layers combined.
- CORRECTNESS: Solves the priority starvation, sorting overhead, and ingestion latency issues of the naive version.
"""

import queue
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

class OptimizedEventOrchestrator:
    """
    Staff-Level Optimized Orchestrator.
    Postpones priority calculation to processing time, utilizing a dual-queue structure
    with an addition-based aging formula to prevent starvation.
    """

    def __init__(self, speed_threshold: float = 30.0, aging_factor: float = 1.0):
        # Stage 1: Fast FIFO buffer for raw incoming telemetry
        self.ingestion_queue: queue.Queue = queue.Queue()
        
        # Stage 2: Self-sorting Min-Heap for priority scheduling
        self.priority_queue: queue.PriorityQueue = queue.PriorityQueue()
        
        self.speed_threshold = speed_threshold
        self.aging_factor = aging_factor
        
        # Anchor timestamp to track elapsed time without precision loss
        self.system_epoch: float = datetime.now().timestamp()
        
        # Unique counter to prevent tuple comparison crashes on payload dicts
        self.sequence_id = 0

    def _calculate_effective_priority(self, speed: float, arrival_time: float) -> float:
        """
        Dynamic Processing-Time Aging Engine.
        Formula: Score = Base_Priority + (Elapsed_Seconds_Since_Epoch * Aging_Factor)
        
        Newer events have larger 'arrival_time' values. Adding this to the base priority
        creates a higher score, pushing them deeper into the Min-Heap (behind older events).
        """
        # Determine Base Priority (0 = Critical, 1 = Urgent, 2 = Routine)
        if speed <= 5.0:
            base_priority = 0.0  # CRITICAL: Potential Accident
        elif speed <= self.speed_threshold:
            base_priority = 1.0  # URGENT: Heavy Congestion
        else:
            base_priority = 2.0  # ROUTINE: Normal Flow

        # Calculate time elapsed from system startup to the event's original arrival
        elapsed_seconds = arrival_time - self.system_epoch
        
        # User-Preferred Addition Logic: Older items stay smaller (higher priority in Min-Heap)
        effective_priority = base_priority + (elapsed_seconds * self.aging_factor)
        return effective_priority

    def process_live_queue(self) -> None:
        """
        Optimized Two-Step Pipeline:
        1. TRIAGE: Empties the FIFO buffer, calculates dynamic priorities with aging, 
           and populates the global Min-Heap.
        2. EXECUTION: Drains the priority heap sequentially, ensuring the absolute 
           most urgent (or oldest-waiting) tasks are handled first.
        """
        print(f"\n[ORCHESTRATOR] Beginning Processing Heartbeat...")

        # ------------------------------------------------------------------
        # STEP 1: DRAIN FIFO AND POPULATE SELF-SORTING PRIORITY QUEUE (O(log N))
        # ------------------------------------------------------------------
        # We move items from the raw buffer to the "smart" priority heap.
        while not self.ingestion_queue.empty():
            raw_event = self.ingestion_queue.get()
            
            # Calculate dynamic priority score at this exact execution moment using arrival time
            effective_prio = self._calculate_effective_priority(raw_event["speed"], raw_event["timestamp"])
            
            self.sequence_id += 1
            
            # Tuple Structure: (Effective Priority, Arrival Time, Sequence ID, Payload)
            heap_item = (effective_prio, raw_event["timestamp"], self.sequence_id, raw_event)
            
            # Insert into Min-Heap in O(log N) time
            self.priority_queue.put(heap_item)

        # ------------------------------------------------------------------
        # STEP 2: DRAIN PRIORITY QUEUE AND DISPATCH ACTIONS (O(log N))
        # ------------------------------------------------------------------
        # The Min-Heap guarantees that .get() always returns the most urgent item.
        print(f"\n--- ⚡ Processing Sorted Priority Queue: {self.priority_queue.qsize()} Events ---")
        
        while not self.priority_queue.empty():
            effective_prio, arrival_time, seq, event = self.priority_queue.get()
            
            speed = event["speed"]
            # Map the priority to a specific system action
            if speed <= 5.0:
                action = "TRIGGER_AMBULANCE_DP"
            elif speed <= self.speed_threshold:
                action = "RECALCULATE_ROUTE"
            else:
                action = "LOG_METRICS"
                
            actual_wait_time = datetime.now().timestamp() - arrival_time
            
            print(f"[{action:20s}] ID: {event['intersection_id']:15s} | "
                  f"Dynamic Priority Score: {effective_prio:6.2f} | "
                  f"Total Buffer Wait Time: {actual_wait_time:6.4f}s")
            
            # Simulated hand-off to the Phase 2 DP pathfinder engine
            if speed <= self.speed_threshold:
                self._run_phase2_strategic_pathfinder(event["intersection_id"])

    def _run_phase2_strategic_pathfinder(self, intersection_id: str) -> None:
        """
        Simulated link to the Phase 2 DP code.
        """
        pass


# ==========================================
# SIMULATION: Verifying Starvation Resolution
# ==========================================

def run_simulation():
    print("--- [SENTINEL SYSTEM] Starting Phase 3 Optimized Dual-Queue Orchestrator ---\n")
    
    # Initialize the optimized orchestrator with an Aging Factor of 1.0
    orchestrator = OptimizedEventOrchestrator(speed_threshold=30.0, aging_factor=1.0)

    # ------------------------------------------------------------------
    # WAVE 1: Initial Influx of City Traffic
    # ------------------------------------------------------------------
    print("--- Wave 1: Rapid Ingestion Into FIFO Buffer ---")
    
    wave_1 = [
        ("INT-OLD-ROUTINE", 45.0), # Base Priority 2.0 (Routine)
        ("INT-OLD-URGENT", 5.0),  # Base Priority 1.0 (Urgent)
    ]
    
    for intersection_id, speed in wave_1:
        payload = {
            "intersection_id": intersection_id,
            "speed": speed,
            "timestamp": datetime.now().timestamp()
        }
        print(f"[PRODUCER] Ingesting: {intersection_id} at {speed} mph into FIFO")
        orchestrator.ingestion_queue.put(payload)
        time.sleep(0.01) # Small delay to preserve precise, distinct timestamps

    # SIMULATION TWIST: We force the program to sleep for 1.5 seconds.
    # This simulates a backpressure scenario where Wave 1 waits in the FIFO pipeline.
    print(f"\n[SYSTEM] Holding execution for 1.5s to accumulate wait time for buffered events...\n")
    time.sleep(1.5)

    # ------------------------------------------------------------------
    # WAVE 2: New Events Arrive After the Delay
    # ------------------------------------------------------------------
    print("--- Wave 2: New Influx Joins FIFO Buffer ---")
    
    wave_2 = [
        ("INT-NEW-URGENT", 15.0),  # Base Priority 1.0 (Urgent, but brand-new)
    ]
    
    for intersection_id, speed in wave_2:
        payload = {
            "intersection_id": intersection_id,
            "speed": speed,
            "timestamp": datetime.now().timestamp()
        }
        print(f"[PRODUCER] Ingesting: {intersection_id} at {speed} mph into FIFO")
        orchestrator.ingestion_queue.put(payload)

    # ------------------------------------------------------------------
    # RUN PROCESSOR ENGINE
    # ------------------------------------------------------------------
    # Tracing the Math with Addition:
    # 1. INT-OLD-URGENT  -> Base 1.0 + (0.00s elapsed * 1) = 1.00
    # 2. INT-OLD-ROUTINE -> Base 2.0 + (0.01s elapsed * 1) = 2.01
    # 3. INT-NEW-URGENT  -> Base 1.0 + (1.51s elapsed * 1) = 2.51
    #
    # Expected execution order popped from Min-Heap:
    # First:  1.00 (INT-OLD-URGENT)
    # Second: 2.01 (INT-OLD-ROUTINE) -> Aged successfully ahead of new urgent traffic!
    # Third:  2.51 (INT-NEW-URGENT)
    orchestrator.process_live_queue()

if __name__ == "__main__":
    run_simulation()