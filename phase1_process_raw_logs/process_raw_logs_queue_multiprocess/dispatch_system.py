import multiprocessing
from typing import Any, Optional

def dispatch_consumer(alert_queue: multiprocessing.Queue) -> None:
    """
    PURPOSE: The 'Final Consumer' executing side-effects.
    
    ARGS:
        alert_queue: The queue containing critical SensorLog objects.
        
    RETURNS: None (Exits on Poison Pill).
    """
    print("[Dispatch] Dispatcher active. Monitoring for alerts...")
    
    while True:
        # log could be a SensorLog object or None
        log: Optional[Any] = alert_queue.get()
        
        # Check for Poison Pill
        if log is None:
            print("[Dispatch] Poison Pill received. Shutting down...")
            break
            
        # log is now guaranteed to be a SensorLog instance
        print(f"    [Dispatch] 🚨 EMERGENCY: {log.name} battery service required!")
        print(f"    [Dispatch]    -> Signal Strength: {log.signal_strength}/7")