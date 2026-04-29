import multiprocessing

def dispatch_consumer(alert_queue: multiprocessing.Queue):
    """
    Listens to the alert_queue and dispatches emergency units.
    """
    while True:
        alert = alert_queue.get()
        if alert is None: break # Shutdown signal
        
        print(f"    [Dispatch] 🚨 ACTION TAKEN: {alert}")