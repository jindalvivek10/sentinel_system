from sensor_stream import get_raw_telemetry_stream
from processor import SentinelProcessor
from dispatch_system import alert_emergency_units

def main():
    """
    SYSTEM ORCHESTRATOR: 
    This simulates the "wiring" of a message broker.
    It passes the output of one generator into the input of the next.
    """
    print("--- [SIMULATION START] ---")
    
    # 1. Initialize the raw stream (The 'Source')
    raw_telemetry = get_raw_telemetry_stream()
    
    # 2. Instantiate the processor logic
    processor = SentinelProcessor()
    
    # 3. 'Wire' the raw stream into the processor (The 'Pipe')
    # Nothing has executed yet; we are just building the pipeline.
    critical_pipeline = processor.filter_critical_alerts(raw_telemetry)
    
    # 4. 'Wire' the processor output into the dispatcher (The 'Sink')
    # The dispatcher's for-loop will now drive the entire lazy chain.
    try:
        alert_emergency_units(critical_pipeline)
    except KeyboardInterrupt:
        print("\n--- [SIMULATION TERMINATED BY USER] ---")

if __name__ == "__main__":
    main()