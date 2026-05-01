"""
FILE: optimized_streaming_simulation.py

PSEUDO-LOGIC:
1. INPUT: Receives a stream of (intersection_id, speed) from a queue.
2. STORAGE (The 'Fixed-Bucket' Trick):
   - Use a 'deque' (Double-Ended Queue) with a 'maxlen'. 
   - When the deque reaches maxlen, the oldest item is automatically deleted 
     when a new one is added. This keeps memory usage constant (O(K)).
3. CALCULATION (The 'Running Balance' Trick):
   - Instead of summing the list every time, we keep a single number: 'running_sum'.
   - IF the deque is full: Subtract the value that is about to be deleted 
     from the 'running_sum'.
   - ADD the new speed to the 'running_sum'.
   - Average = running_sum / current_size_of_deque.
4. OUTPUT: Push the result to the output queue.

STAFF-LEVEL ADVANTAGES:
- TIME: O(1) per update. The speed of the system does not depend on window size.
- SPACE: O(K) per intersection. Memory usage is predictable and bounded.
"""

from collections import deque
import queue
import time
from typing import Dict

class OptimizedStreamingMonitor:
    def __init__(self, in_queue: queue.Queue, out_queue: queue.Queue, window_size: int = 5):
        # Communication channels
        self.in_queue = in_queue
        self.out_queue = out_queue
        # Fixed window size for analytics
        self.K = window_size
        
        # Stores only the last K readings. Memory is capped at K items per ID.
        # Key: ID (str), Value: deque of floats (maxlen=K)
        self.windows: Dict[str, deque[float]] = {}
        
        # Stores the sum of the values currently inside the deque.
        # This allows us to avoid the 'sum()' function loop.
        # Key: ID (str), Value: float
        self.running_sums: Dict[str, float] = {}

    def process_next(self):
        """
        Processes one item from the queue with high-efficiency O(1) logic.
        """
        try:
            # Step 1: Pull the latest data packet from the queue.
            data = self.in_queue.get_nowait()
            intersection_id = data['id']
            speed = data['speed']

            # Step 2: Initialize state for new intersections.
            if intersection_id not in self.windows:
                # deque(maxlen=K) is the 'secret sauce' for sliding windows.
                self.windows[intersection_id] = deque(maxlen=self.K)
                self.running_sums[intersection_id] = 0.0
            
            # Pointer to the specific window we are updating
            window = self.windows[intersection_id]
            
            # Step 3: Maintain the 'Running Balance'.
            # If the window is already at max capacity, the oldest value (index 0)
            # is about to be deleted. We must subtract its value from our sum
            # before we lose track of it.
            if len(window) == self.K:
                evicted_value = window[0] # The 'tail' of the window
                self.running_sums[intersection_id] -= evicted_value
            
            # Step 4: Add the new speed to both the storage and the sum.
            window.append(speed) # Automatically removes oldest item if full
            self.running_sums[intersection_id] += speed
            print(f"💾 [Internal RAM] Active Windows (Max {self.K}): {dict(self.windows)}")
            
            # Step 5: Calculate Average.
            # This is O(1) because it's just one division operation.
            avg_speed = self.running_sums[intersection_id] / len(window)

            # Step 6: Push the result to the output queue.
            output_event = {
                "id": intersection_id,
                "avg": round(avg_speed, 2),
                "window_slots_used": len(window)
            }
            print(f"📤 [Output Queue] Pushing result: {output_event}")
            self.out_queue.put(output_event)
            
            # Cleanup for the queue
            self.in_queue.task_done()
            
        except queue.Empty:
            pass

def simulate_optimized():
    """A test runner to demonstrate the Optimized monitor in action."""
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
        print(f"\n🎬 [Producer] Putting event into Input Queue: {event}")
        in_pipe.put(event)
        monitor.process_next()

    print("\n--- Simulation Complete ---")
    print(f"Final Internal State (Capped Windows): {dict(monitor.windows)}")
    print(f"Final Output Queue size: {out_pipe.qsize()} items.")

if __name__ == "__main__":
    simulate_optimized()