--- [NAIVE SYSTEM] Starting Simulation with 2 Intersections ---

🎬 [Producer] Putting event into Input Queue: {'id': 'INT-A', 'speed': 10.0}
💾 [Internal RAM] History Dictionary : {'INT-A': [10.0]}
📤 [Output Queue] Pushing result: {'id': 'INT-A', 'avg': 10.0, 'total_records_stored': 1}

🎬 [Producer] Putting event into Input Queue: {'id': 'INT-B', 'speed': 100.0}
💾 [Internal RAM] History Dictionary : {'INT-A': [10.0], 'INT-B': [100.0]}
📤 [Output Queue] Pushing result: {'id': 'INT-B', 'avg': 100.0, 'total_records_stored': 1}

🎬 [Producer] Putting event into Input Queue: {'id': 'INT-A', 'speed': 20.0}
💾 [Internal RAM] History Dictionary : {'INT-A': [10.0, 20.0], 'INT-B': [100.0]}
📤 [Output Queue] Pushing result: {'id': 'INT-A', 'avg': 15.0, 'total_records_stored': 2}

🎬 [Producer] Putting event into Input Queue: {'id': 'INT-B', 'speed': 200.0}
💾 [Internal RAM] History Dictionary : {'INT-A': [10.0, 20.0], 'INT-B': [100.0, 200.0]}
📤 [Output Queue] Pushing result: {'id': 'INT-B', 'avg': 150.0, 'total_records_stored': 2}

🎬 [Producer] Putting event into Input Queue: {'id': 'INT-A', 'speed': 30.0}
💾 [Internal RAM] History Dictionary : {'INT-A': [10.0, 20.0, 30.0], 'INT-B': [100.0, 200.0]}
📤 [Output Queue] Pushing result: {'id': 'INT-A', 'avg': 20.0, 'total_records_stored': 3}

🎬 [Producer] Putting event into Input Queue: {'id': 'INT-B', 'speed': 300.0}
💾 [Internal RAM] History Dictionary : {'INT-A': [10.0, 20.0, 30.0], 'INT-B': [100.0, 200.0, 300.0]}
📤 [Output Queue] Pushing result: {'id': 'INT-B', 'avg': 200.0, 'total_records_stored': 3}

🎬 [Producer] Putting event into Input Queue: {'id': 'INT-A', 'speed': 40.0}
💾 [Internal RAM] History Dictionary : {'INT-A': [10.0, 20.0, 30.0, 40.0], 'INT-B': [100.0, 200.0, 300.0]}
📤 [Output Queue] Pushing result: {'id': 'INT-A', 'avg': 30.0, 'total_records_stored': 4}

🎬 [Producer] Putting event into Input Queue: {'id': 'INT-B', 'speed': 400.0}
💾 [Internal RAM] History Dictionary : {'INT-A': [10.0, 20.0, 30.0, 40.0], 'INT-B': [100.0, 200.0, 300.0, 400.0]}
📤 [Output Queue] Pushing result: {'id': 'INT-B', 'avg': 300.0, 'total_records_stored': 4}

🎬 [Producer] Putting event into Input Queue: {'id': 'INT-A', 'speed': 50.0}
💾 [Internal RAM] History Dictionary : {'INT-A': [10.0, 20.0, 30.0, 40.0, 50.0], 'INT-B': [100.0, 200.0, 300.0, 400.0]}
📤 [Output Queue] Pushing result: {'id': 'INT-A', 'avg': 40.0, 'total_records_stored': 5}

🎬 [Producer] Putting event into Input Queue: {'id': 'INT-B', 'speed': 500.0}
💾 [Internal RAM] History Dictionary : {'INT-A': [10.0, 20.0, 30.0, 40.0, 50.0], 'INT-B': [100.0, 200.0, 300.0, 400.0, 500.0]}
📤 [Output Queue] Pushing result: {'id': 'INT-B', 'avg': 400.0, 'total_records_stored': 5}

--- Simulation Complete ---
Final Internal State: {'INT-A': [10.0, 20.0, 30.0, 40.0, 50.0], 'INT-B': [100.0, 200.0, 300.0, 400.0, 500.0]}

Final Output Queue size: 10 items.









jindal_vivek10@cloudshell:~/projects/sentinel_system/phase2_traffic_monitor$ python optimized_streaming_monitor.py 
--- [OPTIMIZED SYSTEM] Starting Simulation with 2 Intersections ---

🎬 [Producer] Putting event into Input Queue: {'id': 'INT-A', 'speed': 10.0}
💾 [Internal RAM] Active Windows (Max 3): {'INT-A': deque([10.0], maxlen=3)}
📤 [Output Queue] Pushing result: {'id': 'INT-A', 'avg': 10.0, 'window_slots_used': 1}

🎬 [Producer] Putting event into Input Queue: {'id': 'INT-B', 'speed': 100.0}
💾 [Internal RAM] Active Windows (Max 3): {'INT-A': deque([10.0], maxlen=3), 'INT-B': deque([100.0], maxlen=3)}
📤 [Output Queue] Pushing result: {'id': 'INT-B', 'avg': 100.0, 'window_slots_used': 1}

🎬 [Producer] Putting event into Input Queue: {'id': 'INT-A', 'speed': 20.0}
💾 [Internal RAM] Active Windows (Max 3): {'INT-A': deque([10.0, 20.0], maxlen=3), 'INT-B': deque([100.0], maxlen=3)}
📤 [Output Queue] Pushing result: {'id': 'INT-A', 'avg': 15.0, 'window_slots_used': 2}

🎬 [Producer] Putting event into Input Queue: {'id': 'INT-B', 'speed': 200.0}
💾 [Internal RAM] Active Windows (Max 3): {'INT-A': deque([10.0, 20.0], maxlen=3), 'INT-B': deque([100.0, 200.0], maxlen=3)}
📤 [Output Queue] Pushing result: {'id': 'INT-B', 'avg': 150.0, 'window_slots_used': 2}

🎬 [Producer] Putting event into Input Queue: {'id': 'INT-A', 'speed': 30.0}
💾 [Internal RAM] Active Windows (Max 3): {'INT-A': deque([10.0, 20.0, 30.0], maxlen=3), 'INT-B': deque([100.0, 200.0], maxlen=3)}
📤 [Output Queue] Pushing result: {'id': 'INT-A', 'avg': 20.0, 'window_slots_used': 3}

🎬 [Producer] Putting event into Input Queue: {'id': 'INT-B', 'speed': 300.0}
💾 [Internal RAM] Active Windows (Max 3): {'INT-A': deque([10.0, 20.0, 30.0], maxlen=3), 'INT-B': deque([100.0, 200.0, 300.0], maxlen=3)}
📤 [Output Queue] Pushing result: {'id': 'INT-B', 'avg': 200.0, 'window_slots_used': 3}

🎬 [Producer] Putting event into Input Queue: {'id': 'INT-A', 'speed': 40.0}
💾 [Internal RAM] Active Windows (Max 3): {'INT-A': deque([20.0, 30.0, 40.0], maxlen=3), 'INT-B': deque([100.0, 200.0, 300.0], maxlen=3)}
📤 [Output Queue] Pushing result: {'id': 'INT-A', 'avg': 30.0, 'window_slots_used': 3}

🎬 [Producer] Putting event into Input Queue: {'id': 'INT-B', 'speed': 400.0}
💾 [Internal RAM] Active Windows (Max 3): {'INT-A': deque([20.0, 30.0, 40.0], maxlen=3), 'INT-B': deque([200.0, 300.0, 400.0], maxlen=3)}
📤 [Output Queue] Pushing result: {'id': 'INT-B', 'avg': 300.0, 'window_slots_used': 3}

🎬 [Producer] Putting event into Input Queue: {'id': 'INT-A', 'speed': 50.0}
💾 [Internal RAM] Active Windows (Max 3): {'INT-A': deque([30.0, 40.0, 50.0], maxlen=3), 'INT-B': deque([200.0, 300.0, 400.0], maxlen=3)}
📤 [Output Queue] Pushing result: {'id': 'INT-A', 'avg': 40.0, 'window_slots_used': 3}

🎬 [Producer] Putting event into Input Queue: {'id': 'INT-B', 'speed': 500.0}
💾 [Internal RAM] Active Windows (Max 3): {'INT-A': deque([30.0, 40.0, 50.0], maxlen=3), 'INT-B': deque([300.0, 400.0, 500.0], maxlen=3)}
📤 [Output Queue] Pushing result: {'id': 'INT-B', 'avg': 400.0, 'window_slots_used': 3}

--- Simulation Complete ---
Final Internal State (Capped Windows): {'INT-A': deque([30.0, 40.0, 50.0], maxlen=3), 'INT-B': deque([300.0, 400.0, 500.0], maxlen=3)}
Final Output Queue size: 10 items.