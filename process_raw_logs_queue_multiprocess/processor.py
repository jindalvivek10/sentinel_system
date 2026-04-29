import multiprocessing

def alert_processor(raw_queue: multiprocessing.Queue, alert_queue: multiprocessing.Queue):
    """
    Listens to the raw_queue, performs bitwise logic, 
    and PUSHES critical alerts to the alert_queue.
    """
    while True:
        # PULL from queue (blocks until data is available)
        raw_log = raw_queue.get()
        
        if raw_log is None: break # Shutdown signal
        
        # Logic: Bridge_X or Traf_02 with 0x0003 are critical for this demo
        if "0x0003" in raw_log:
            print(f"  [Processor] ⚙️  CRITICAL logic detected in: {raw_log}")
            alert_queue.put(f"ALERT: {raw_log}")
        else:
            print(f"  [Processor] ✅ Log processed (Non-critical)")