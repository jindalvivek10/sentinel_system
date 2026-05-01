import multiprocessing
import time
from sensor_stream import sensor_publisher
from processor import alert_processor
from dispatch_system import dispatch_consumer

if __name__ == "__main__":
    # 1. SETUP SHARED CHANNELS (OS Pipes)
    # maxsize handles 'Backpressure' to prevent memory overflow
    # By using a bounded queue, we force Backpressure. We tell the Sensor: 
    # "Hey, the Processor is struggling. You need to slow down or stop until we catch up."
    raw_topic: multiprocessing.Queue = multiprocessing.Queue(maxsize=50)

    alert_topic: multiprocessing.Queue = multiprocessing.Queue(maxsize=50)

    # 2. DEFINE ISOLATED SERVICES
    # Each runs in a separate process with its own memory and GIL.
    p1: multiprocessing.Process = multiprocessing.Process(
        target=sensor_publisher,  
        args=(raw_topic,)
    )
    p2: multiprocessing.Process = multiprocessing.Process(
        target=alert_processor, 
        args=(raw_topic, alert_topic)
    )
    p3: multiprocessing.Process = multiprocessing.Process(
        target=dispatch_consumer, 
        args=(alert_topic,)
    )

    # 3. TRIGGER EXECUTION
    p1.start()
    p2.start()
    p3.start()

    try:
        # Keep the Main process alive to monitor the children
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[Orchestrator] 🛑 Shutting down system...")
        
        # A. Stop the producer (Sensor) immediately
        p1.terminate() 
        
        # B. Send Graceful Shutdown signals (Poison Pills) to workers
        raw_topic.put(None)
        alert_topic.put(None)
        
        # C. Ensure all OS processes are cleaned up and resources released
        p1.join()
        p2.join()
        p3.join()
        
        print("[Orchestrator] Clean exit. System offline.")