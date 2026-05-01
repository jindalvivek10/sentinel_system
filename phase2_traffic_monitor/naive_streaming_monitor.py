"""
FILE: naive_streaming_simulation.py

PSEUDO-LOGIC:
1. INPUT: Receives a stream of (intersection_id, speed) from a queue.
2. STORAGE: Finds the list associated with the intersection_id. 
   - If it doesn't exist, create it.
   - Append the new speed to the end of the list.
3. CALCULATION (The 'Naive' part):
   - To get the average of the last 'K' items, we 'slice' the list: list[-K:].
   - We then iterate through those K items to sum them up.
   - Divide by the number of items retrieved.
4. OUTPUT: Push a dictionary containing the ID and the calculated average to an output queue.

STAFF-LEVEL CRITIQUE:
- MEMORY: The dictionary 'self.history' grows linearly with every sensor ping. 
  It never deletes old data. This is a "Memory Leak" by design.
- CPU: sum(history[-K:]) is an O(K) operation. As K (the window size) 
  increases, the time to process a single packet increases.
"""

import queue
import time
from typing import Dict, List

class NaiveStreamingMonitor:
    def __init__(self, in_queue: queue.Queue, out_queue: queue.Queue, window_size: int = 5):
        # The queue we read 'clean logs' from
        self.in_queue = in_queue
        # The queue where we send our calculated averages
        self.out_queue = out_queue
        # The number of recent samples we care about
        self.K = window_size
        
        # This dictionary stores EVERY speed ever recorded for every intersection.
        # Key: string (ID), Value: List of floats (All historical speeds)
        self.history: Dict[str, List[float]] = {}

    def process_next(self):
        """
        Attempts to process one single message from the input queue.
        Using 'get_nowait' allows us to run this in a loop without the 
        program hanging if the queue is empty.
        """
        try:
            # Step 1: Pull the latest data packet from the queue.
            # .get_nowait() raises queue.Empty if there is nothing to process.
            data = self.in_queue.get_nowait()

            intersection_id = data['id']
            speed = data['speed']

            # Step 2: Retrieve the history list for this specific intersection.
            # If this is the first time we see this ID, initialize an empty list.
            if intersection_id not in self.history:
                self.history[intersection_id] = []
            
            # Step 3: Record the speed.
            # WARNING: This list will grow until the computer runs out of RAM.
            self.history[intersection_id].append(speed)
            print(f"💾 [Internal RAM] History Dictionary : {self.history}")
            
            # Step 4: Calculate the average of the most recent K items.
            # 'history[-self.K:]' creates a NEW list (a copy) of the last K items.
            recent_readings = self.history[intersection_id][-self.K:]
            
            # 'sum()' must look at every item in 'recent_readings' one by one.
            # This is O(K) time complexity.
            avg_speed = sum(recent_readings) / len(recent_readings)
            
            output_event = {
                "id": intersection_id,
                "avg": round(avg_speed, 2),
                "total_records_stored": len(self.history[intersection_id])
            }
            print(f"📤 [Output Queue] Pushing result: {output_event}")
            self.out_queue.put(output_event)
            
            # Tell the queue that we have finished processing this specific item.
            self.in_queue.task_done()
            
        except queue.Empty:
            # If the queue was empty, we just exit the function gracefully.
            pass

def simulate_naive():
    """A test runner to demonstrate the Naive monitor in action."""
    # Create our communication 'pipes'
    in_pipe = queue.Queue()
    out_pipe = queue.Queue()
    
    # Initialize the monitor with a window size of 3
    monitor = NaiveStreamingMonitor(in_pipe, out_pipe, window_size=3)

    print("--- [NAIVE SYSTEM] Starting Simulation with 2 Intersections ---")
    # Interleaved data: 5 speed readings for INT-A and 5 for INT-B
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
        
        # We process immediately after putting to see the step-by-step growth
        # as requested, rather than buffering everything first.
        monitor.process_next()

    print("\n--- Simulation Complete ---")
    print(f"Final Internal State: {monitor.history}")

    # Final check of the output queue
    print(f"\nFinal Output Queue size: {out_pipe.qsize()} items.")

if __name__ == "__main__":
    simulate_naive()