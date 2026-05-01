import random
import time
from typing import Iterator

def get_raw_telemetry_stream() -> Iterator[str]:
    """
    UPSTREAM: Simulates the raw hardware feed.
    In production, this would be replaced by a Kafka Consumer or Socket.recv()
    """
    mock_data = [
        "Traf_01:0x0001", # Binary: ...0001 (Active=True, LowBat=False) -> Not Critical
        "Bridge_X:0x0003", # Binary: ...0011 (Active=True, LowBat=True)  -> ** CRITICAL **
        "Traf_02:0x001F", # Binary: ...11111 (Active=True, LowBat=True, Signal=7) -> ** CRITICAL **
        "Sensor_7:0x0001", # Binary: ...0001 (Active=True, LowBat=False) -> Not Critical
        "Gate_99:0x0002", # Binary: ...0010 (Active=False, LowBat=True) -> Not Critical
        "Invalid_Data", # Malformed string -> Ignored by processor (no hex value)
    ]
    log_count = 0
    while True:
        # Simulate network delay of data arrival
        # time.sleep(0.5)
        time.sleep(10)
        log_count += 1
        raw_data_choice = random.choice(mock_data)
        print(f"====sending log_count = {log_count} for raw raw_data_choice = {raw_data_choice}====")
        yield raw_data_choice
