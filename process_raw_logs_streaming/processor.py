from typing import NamedTuple, Iterable, Iterator

class SensorLog(NamedTuple):
    id: str
    active: bool
    low_battery: bool
    signal: int

class SentinelProcessor:
    """
    MIDDLEWARE: Business logic and data cleaning.
    """
    MASK_ACTIVE = 0x0001
    MASK_LOW_BATTERY = 0x0002
    MASK_SIGNAL = 0x001C

    def filter_critical_alerts(self, stream: Iterable[str]) -> Iterator[SensorLog]:
        """
        Pure transformation logic. Takes a stream, yields critical logs.
        """
        for entry in stream:
            print(f"====processing stream entry = {entry}====")
            try:
                if ":" not in entry: continue
                
                s_id, hex_val = entry.split(":", 1)
                status_code = int(hex_val.strip(), 16)

                is_active = bool(status_code & self.MASK_ACTIVE)
                is_low_battery = bool(status_code & self.MASK_LOW_BATTERY)

                # Filter only for 'Critical' status
                if is_active and is_low_battery:
                    yield SensorLog(
                        id=s_id.strip(),
                        active=is_active,
                        low_battery=is_low_battery,
                        signal=(status_code & self.MASK_SIGNAL) >> 2
                    )
            except (ValueError, TypeError):
                continue