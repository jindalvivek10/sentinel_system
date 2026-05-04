"""
FILE: optimized_streaming_simulation.py

SYSTEM ROLE: 
A memory-efficient engine using the 'Running Balance' pattern.

PSEUDO-LOGIC:
1. INPUT: A dictionary (Event) from the input queue.
   Format: {"id": str, "speed": float}
2. STORAGE:
   - 'self.history': Dictionary mapping ID to a 'deque(maxlen=K)'.
   - 'self.running_sums': Dictionary mapping ID to a single float (the total sum).
3. WHY WE USE A RUNNING SUM DICT?
   - Instead of re-calculating the sum (which requires a loop), we update a 
     'balance sheet'. This turns an O(K) problem into an O(1) problem.
4. PROCESSING STEPS:
   - If 'history' (the deque) is already full, subtract the value at index 0 
     from the 'running_sum' (because it's about to be evicted).
   - Append the new speed to 'history' (auto-evicts the oldest).
   - Add the new speed to the 'running_sum'.
   - Average = running_sum / current_size_of_history.
5. OUTPUT: A dictionary sent to the output queue.
   Format: {"id": str, "avg": float, "memory_slots_used": int}

COMPLEXITY ANALYSIS:
- TIME: O(1) per update. No loops, just simple arithmetic.
- SPACE: O(I * K) + O(I). Memory is capped and predictable.
"""

from collections import deque
import queue
from typing import Dict

class OptimizedStreamingMonitor:
    def __init__(self, in_queue: queue.Queue, out_queue: queue.Queue, window_size: int = 5):
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.K = window_size
        # self.history uses deque(maxlen=K) to prevent memory leaks
        self.history: Dict[str, deque[float]] = {}
        # self.running_sums stores the current pre-calculated total for each ID
        self.running_sums: Dict[str, float] = {}

    def process_next(self):
        """Processes the next event using O(1) running-sum logic."""
        try:
            # 1. Pull the data packet
            item = self.in_queue.get_nowait()
            i_id, speed = item['id'], item['speed']

            # 2. Initialize state for new IDs
            if i_id not in self.history:
                self.history[i_id] = deque(maxlen=self.K)
                self.running_sums[i_id] = 0.0
            
            # Reference to our circular buffer (the sliding window)
            speeds_readings = self.history[i_id]
            
            # 3. The "Subtraction Phase"
            # If the window is full, the oldest value (index 0) will be kicked 
            # out by the next append. We subtract it from the sum NOW.
            if len(speeds_readings) == self.K:
                oldest_value = speeds_readings[0]
                self.running_sums[i_id] -= oldest_value
            
            # 4. The "Addition Phase"
            # Add to the deque (memory management) and the sum (calculation efficiency)
            speeds_readings.append(speed) 
            self.running_sums[i_id] += speed
            print(f"💾 [Internal RAM] History Dictionary : {self.history}")
            
            # 5. Calculate Average.
            # Use len(speeds_readings) to handle cases where we have fewer than K pings.
            avg = self.running_sums[i_id] / len(speeds_readings)

            # 6. Emit result
            self.out_queue.put({
                "id": i_id,
                "avg": round(avg, 2),
                "memory_slots_used": len(speeds_readings)
            })
            self.in_queue.task_done()
        except queue.Empty:
            pass

def simulate_optimized():
    """A test runner demonstrating O(1) performance and bounded memory."""
    in_pipe = queue.Queue()
    out_pipe = queue.Queue()
    monitor = OptimizedStreamingMonitor(in_pipe, out_pipe, window_size=3)

    print("--- [OPTIMIZED SYSTEM] Starting Simulation with 2 Intersections ---")
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
    # In Optimized, this dict will show deques of length 3 (Old data was evicted)
    print(f"Final Internal State (Capped Windows): {dict(monitor.history)}")
    print(f"Final Output Queue size: {out_pipe.qsize()} items.")

if __name__ == "__main__":
    simulate_optimized()