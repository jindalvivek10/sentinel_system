import time
import random
import multiprocessing

def sensor_publisher(raw_queue: multiprocessing.Queue) -> None:
    """
    PURPOSE: Acts as the 'Producer' (Source). 
    
    ARGS:
        raw_queue: The multiprocessing.Queue used to push raw data 
                   to the downstream Processor service.
    
    RETURNS: None (Runs an infinite loop until terminated).
    """
    
    # Predefined telemetry strings consistent with GitHub repository.
    raw_telemetry_data: list[str] = [
        "Bridge_X:0x0003", 
        "Bridge_Y:0x0001", 
        "Bridge_Z:0x0003", 
        "Tunnel_A:0x001F",
        "Gate_B:0x0000"
    ]
    
    print("[Sensor] Service active. Streaming telemetry to Queue...")
    
    try:
        while True:
            # 1. Simulate the arrival frequency of sensor data (1.5 seconds)
            time.sleep(5) 
            
            # 2. Pick a log entry from our predefined list
            log_entry: str = random.choice(raw_telemetry_data)
            
            # 3. THE PUSH:
            # Serializes and sends the string through the OS pipe.
            raw_queue.put(log_entry)
            
            print(f"[Sensor] 📡 Telemetry Sent: {log_entry}")
            
    except Exception as e:
        print(f"[Sensor] ❌ Critical Failure: {e}")