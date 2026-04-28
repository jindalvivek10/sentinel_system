'''
Python Memory Management Cheat Sheet
Strings (str): Immutable. Shallow copies return the same memory address. 100% safe.

Tuples (tuple): Immutable. Shallow copies return the same memory address. Safe (unless they contain mutable objects).

Lists (list): Mutable. Shallow copies create a new container but use the same item pointers. Unsafe if items are mutable.

Dictionaries (dict): Mutable. Shallow copies create a new container but use the same value pointers. Unsafe if values are mutable.

Sets (set): Mutable. Shallow copies create a new container but use the same item pointers. Unsafe if items are mutable.

Frozensets (frozenset): Immutable. Shallow copies return the same memory address. 100% safe.
'''

import copy  # Provides shallow and deep copy operations for objects
from typing import NamedTuple, Any  # Used for type hinting and defining structured, immutable data types

# Senior Engineer: "I used a deep copy because I wanted to be safe."

# Staff Engineer: "I used an immutable data structure so I could use a shallow copy, making the system 10x
# faster while remaining 100% safe."
class SensorLog(NamedTuple):
    """
    A NamedTuple representing a structured sensor log.
    NamedTuple is used here because it is:
    1. Immutable: Once created, the data cannot be changed, ensuring data integrity.
    2. Memory Efficient: It has a lower memory footprint compared to a standard class or dictionary.
    3. Readable: Allows accessing data using dot notation (e.g., log.id) instead of keys.
    """
    id: str
    active: bool
    low_battery: bool
    signal: int

class SentinelLogProcessor:
    """
    Handles the parsing and internal storage of sensor telemetry logs.
    """
    def __init__(self) -> None:
        # Initialize an empty list to store SensorLog instances.
        # Type hinting list[SensorLog] helps editors provide better autocompletion.
        self.logs: list[SensorLog] = []

    def process_batch(self, raw_logs: list[str]) -> None:
        """
        Parses raw sensor strings into immutable SensorLog objects.
        Expected input format: "SensorName:0xHexCode"
        """
        # Bitmasks for 16-bit status codes:
        # 0x0001 -> 0000 0000 0000 0001 (Targets Bit 0)
        # 0x0002 -> 0000 0000 0000 0010 (Targets Bit 1)
        # 0x001C -> 0000 0000 0001 1100 (Targets Bits 2, 3, and 4)
        MASK_ACTIVE = 0x0001
        MASK_LOW_BATTERY = 0x0002
        MASK_SIGNAL = 0x001C

        for entry in raw_logs:
            try:
                # Basic validation: ensure the delimiter exists
                if ":" not in entry:
                    continue
                
                # String manipulation:
                # .split(":") splits the string into a list [id, hex_val]
                # .strip() removes any accidental whitespace or newline characters
                s_id, hex_val = entry.split(":")
                status_code = int(hex_val.strip(), 16)

                # Data Extraction Logic:
                # 1. bitwise & (AND) filters the specific bits we care about.
                # 2. bool() converts a non-zero result to True and zero to False.
                # 3. >> (Right Shift) moves the bits to the right. 
                #    For signal (bits 2-4), we shift by 2 to get the integer value (0-7).
                log_entry = SensorLog(
                    id=s_id.strip(),
                    active=bool(status_code & MASK_ACTIVE),
                    low_battery=bool(status_code & MASK_LOW_BATTERY),
                    signal=(status_code & MASK_SIGNAL) >> 2
                )
                
                # Add the immutable record to our collection
                self.logs.append(log_entry)

            except (ValueError, TypeError):
                # Exception Handling:
                # ValueError: Raised if int() conversion fails (e.g., "0xZZZZ").
                # TypeError: Raised if data is None or unexpected types are encountered.
                # We 'continue' to skip the malformed log without crashing the whole process.
                continue

    def get_log_snapshot(self) -> list[SensorLog]:
        """
        Returns a snapshot of the current logs.
        
        The notation [:] creates a 'shallow copy' of the list.
        
        Safety Note: While it is a shallow copy, the items inside (SensorLog) 
        are immutable NamedTuples. This means the caller can't modify the 
        original data inside the processor, making this operation O(n) and 
        completely thread-safe and memory-safe for this architecture.

        If you use return self.logs: When you call logs.clear() in your 
        if __name__ == "__main__": block, you are clearing the actual internal list inside 
        the processor instance. Any subsequent calls to get_log_snapshot() would return an 
        empty list because the source of truth was wiped out.
        """
        return self.logs[:]