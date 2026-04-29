import time
import random
import multiprocessing

def sensor_publisher(raw_queue: multiprocessing.Queue):
    """
    Simulates a separate service reading from hardware and 
    PUSHING data into a raw telemetry queue.
    """
    mock_data = ["Traf_01:0x0003", "Gate_99:0x0001", "Bridge_X:0x0003", "Traf_02:0x001F"]
    batch_count = 0
    
    try:
        while True:
            batch_count += 1
            # Simulate sensor frequency
            time.sleep(2) 
            
            raw_log = random.choice(mock_data)
            print(f"[Sensor] 📡 Generated: {raw_log} (Batch {batch_count})")
            
            # PUSH to queue
            raw_queue.put(raw_log)
    except KeyboardInterrupt:
        print("[Sensor] Stopping...")