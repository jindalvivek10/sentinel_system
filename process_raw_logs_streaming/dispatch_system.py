from typing import Iterable
from processor import SensorLog

def alert_emergency_units(alert_stream: Iterable[SensorLog]) -> None:
    """
    DOWNSTREAM: Final action execution.
    """
    print("[Dispatch] 🚔 Emergency System Online. Monitoring alerts...")
    for alert in alert_stream:
        # In reality, this would trigger an API call to a dispatch center
        print(f"==== [Dispatch] 🚨 ALERT: Sensor {alert.id} is CRITICAL (Signal: {alert.signal})")