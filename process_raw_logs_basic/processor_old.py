import copy
from typing import Any  # We still need 'Any' for mixed-type dictionaries

class SentinelLogProcessor:
    """
    Handles the processing and storage of sensor logs from the sentinel system.
    Logs are received as hex-encoded strings and converted into structured dictionaries.
    """
    def __init__(self) -> None:
        # This stores the processed logs internally. 
        # Using a list of dictionaries for flexibility in older versions.
        self.logs: list[dict[str, Any]] = []

    def process_batch(self, raw_logs: list[str]) -> None:
        """
        Parses a list of raw log strings into a structured format.
        Expected format for each string: "SensorID:0xHEXVAL"
        """
        # Bitmasks for extracting specific flags from the 16-bit status code
        MASK_ACTIVE = 0x0001       # 0000 0001 (Bit 0)
        MASK_LOW_BATTERY = 0x0002  # 0000 0010 (Bit 1)
        MASK_SIGNAL = 0x001C       # 0001 1100 (Bits 2, 3, and 4)

        for entry in raw_logs:
            try:
                # Skip entries that do not follow the expected "ID:Value" format
                if ":" not in entry:
                    continue
                
                # Split the raw string into a list [ID, HexValue]. 
                # We unpack these directly into two variables for cleaner access.
                sensor_id, hex_val = entry.split(":")
                
                # Convert the hex string (e.g., "0x001E") to an integer.
                # The base 16 parameter tells Python how to interpret the string.
                status_code = int(hex_val, 16)

                # Create a structured dictionary from the parsed bits
                log_entry = {
                    # Clean up the ID by removing leading/trailing whitespace 
                    # that might have been in the raw log string.
                    "id": sensor_id.strip(),
                    # Check if the 'active' bit is set (Bit 0)
                    "active": bool(status_code & MASK_ACTIVE),
                    # Check if the 'low battery' bit is set (Bit 1)
                    "low_battery": bool(status_code & MASK_LOW_BATTERY),
                    # Extract the 3-bit signal value (Bits 2-4).
                    # We mask the bits then shift right by 2 to get the actual value (0-7).
                    "signal": (status_code & MASK_SIGNAL) >> 2
                }
                
                # Add the successfuly parsed log to our internal record list.
                self.logs.append(log_entry)

            except (ValueError, TypeError):
                # If int conversion fails (ValueError) or data is None (TypeError),
                # we skip this specific log and continue with the rest of the batch.
                continue

    def get_log_snapshot(self) -> list[dict[str, Any]]:
        """
        Returns a deep copy of the current logs. 
        Because dictionaries are mutable, returning a deep copy prevents external
        code from accidentally modifying the processor's internal state.
        """
        return copy.deepcopy(self.logs)
