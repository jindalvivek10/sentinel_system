"""
FILE: naive_streaming_simulation.py

SYSTEM ROLE: 
Analyzes traffic data using a simple list-append approach.

PSEUDO-LOGIC:
1. INPUT: A dictionary (Event) from the input queue.
   Format: {"id": str, "speed": float}
2. STORAGE: 
   - A dictionary 'self.history' where the Key is the Intersection ID.
   - The Value is a Python List that stores EVERY speed reading forever.
3. WHY WE STORE SUMS/LISTS:
   - We need to group readings by ID so INT-A doesn't affect INT-B's average.
4. PROCESSING STEPS:
   - Append the new speed to the historical list.
   - Slice the list to get the last 'K' items.
   - Calculate average: sum(slice) / count(slice).
5. WHY len() vs K?
   - During the "Warm-up" (e.g., only 1 or 2 pings received), we divide by the 
     actual number of items present to avoid mathematically incorrect averages.
6. OUTPUT: A dictionary sent to the output queue.
   Format: {"id": str, "avg": float, "total_records_stored": int}

COMPLEXITY ANALYSIS:
- TIME: O(K) per update. Python must iterate through K items to sum them.
- SPACE: O(N) where N is total pings. The lists grow infinitely (Memory Leak).
"""

import queue
from typing import Dict, List

class NaiveStreamingMonitor:
    def __init__(self, in_queue: queue.Queue, out_queue: queue.Queue, window_size: int = 5):
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.K = window_size
        # State: Dictionary mapping ID to an ever-growing list
        self.history: Dict[str, List[float]] = {}

    def process_next(self):
        """Processes the next event from the queue using list-slicing."""
        try:
            # 1. Pull the raw data dictionary from the queue
            data = self.in_queue.get_nowait()
            i_id, speed = data['id'], data['speed']

            # 2. Ensure a list exists for this intersection
            if i_id not in self.history:
                self.history[i_id] = []
            
            # 3. Append the speed (The memory leak: this list never shrinks)
            self.history[i_id].append(speed)
            print(f"💾 [Internal RAM] History Dictionary : {self.history}")
            
            # 4. Grab the most recent K items (The CPU bottleneck: O(K) slicing)
            recent_readings = self.history[i_id][-self.K:]
            
            # 5. Calculate average. We use len() to handle the 'warm-up' phase 
            # where the list size is still smaller than K.
            avg_speed = sum(recent_readings) / len(recent_readings)

            # 6. Emit results to the next system phase
            self.out_queue.put({
                "id": i_id,
                "avg": round(avg_speed, 2),
                "total_records_stored": len(self.history[i_id])
            })
            self.in_queue.task_done()
        except queue.Empty:
            pass

def simulate_naive():
    """A test runner showing interleaved data and infinite memory growth."""
    in_pipe = queue.Queue()
    out_pipe = queue.Queue()
    monitor = NaiveStreamingMonitor(in_pipe, out_pipe, window_size=3)

    print("--- [NAIVE SYSTEM] Starting Simulation with 2 Intersections ---")
    test_events = [
        {"id": "INT-A", "speed": 10.0}, {"id": "INT-B", "speed": 100.0},
        {"id": "INT-A", "speed": 20.0}, {"id": "INT-B", "speed": 200.0},
        {"id": "INT-A", "speed": 30.0}, {"id": "INT-B", "speed": 300.0},
        {"id": "INT-A", "speed": 40.0}, {"id": "INT-B", "speed": 400.0},
        {"id": "INT-A", "speed": 50.0}, {"id": "INT-B", "speed": 500.0},
    ]
    
    for event in test_events:
        print(f"🎬 [Producer] Putting event: {event}")
        in_pipe.put(event)
        monitor.process_next()

    print("\n--- Simulation Complete ---")
    # In Naive, this dict will show lists of length 5 (all data kept)
    print(f"Final Internal State (Infinite History): {dict(monitor.history)}")
    print(f"Final Output Queue size: {out_pipe.qsize()} items.")

if __name__ == "__main__":
    simulate_naive()