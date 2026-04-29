import multiprocessing
from typing import NamedTuple, Optional

# Global data structure for structured telemetry
class SensorLog(NamedTuple):
    name: str
    status_code: int
    is_active: bool
    low_battery: bool
    signal_strength: int

def alert_processor(raw_queue: multiprocessing.Queue, alert_queue: multiprocessing.Queue) -> None:
    """
    PURPOSE: The 'Logic Engine' that transforms raw hex into structured objects.
    
    ARGS:
        raw_queue: The input queue containing raw hex strings.
        alert_queue: The output queue for critical SensorLog objects.
        
    RETURNS: None (Exits on Poison Pill).
    """
    print("[Processor] Logic Engine started. Waiting for logs...")
    
    while True:
        # PULL from the queue (BLOCKING)
        # Using Optional[str] logic because raw_msg could be None (Poison Pill)
        raw_msg: Optional[str] = raw_queue.get() 
        
        # Check for Shutdown Signal
        if raw_msg is None:
            print("[Processor] Poison Pill received. Shutting down...")
            break
            
        try:
            if ":" not in raw_msg: 
                continue

            # 1. Parsing
            sensor_name, hex_val = raw_msg.split(":")
            status_code: int = int(hex_val, 16)
            
            # 2. BITMASKING (Flags extraction)
            log = SensorLog(
                name=sensor_name,
                status_code=status_code,
                is_active=bool(status_code & 0x0001),
                low_battery=bool(status_code & 0x0002),
                signal_strength=(status_code & 0x001C) >> 2
            )

            # 3. Business Rule Filtering
            if log.is_active and log.low_battery:
                print(f"  [Processor] ⚠️  CRITICAL ALERT: {log.name}")
                # PUSH the entire object to the Dispatcher
                alert_queue.put(log)
            else:
                print(f"  [Processor] ✅ Normal: {log.name}")
                
        except Exception as e:
            print(f"  [Processor] ❌ Parsing Error: {e}")