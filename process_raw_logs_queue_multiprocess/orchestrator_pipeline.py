import multiprocessing
import time

if __name__ == "__main__":
    # 1. Create the 'Topics' (Queues)
    # maxsize prevents the Sensor from overwhelming the system RAM
    raw_data_topic = multiprocessing.Queue(maxsize=100)
    alert_topic = multiprocessing.Queue(maxsize=100)

    # 2. Initialize the Services as separate Processes
    sensor_proc = multiprocessing.Process(
        target=__import__('sensor_stream').sensor_publisher, 
        args=(raw_data_topic,)
    )
    
    processor_proc = multiprocessing.Process(
        target=__import__('processor').alert_processor, 
        args=(raw_data_topic, alert_topic)
    )
    
    dispatch_proc = multiprocessing.Process(
        target=__import__('dispatch_system').dispatch_consumer, 
        args=(alert_topic,)
    )

    print("--- [STARTING DISTRIBUTED QUEUE SYSTEM] ---")
    processor_proc.start()
    dispatch_proc.start()
    sensor_proc.start()

    try:
        # Let it run until user interrupts
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n--- [TERMINATING SERVICES] ---")
        sensor_proc.terminate()
        # Send Poison Pills to workers for graceful exit
        raw_data_topic.put(None)
        alert_topic.put(None)
        
        processor_proc.join()
        dispatch_proc.join()
        print("--- [SYSTEM OFFLINE] ---")