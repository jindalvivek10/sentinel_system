from processor import SentinelLogProcessor, SensorLog

def run_tests():
    processor = SentinelLogProcessor()
    
    # 1. Define Test Data
    raw_input = [
        "Traf_01:0x0005",  # Active=True,  LowBat=False, Signal=1
        "Gate_99:0x001E",  # Active=False, LowBat=True,  Signal=7
        "Bridge_X:0x0000", # Active=False, LowBat=False, Signal=0
    ]

    expected_results = {
        "Traf_01": {"active": True, "low_battery": False, "signal": 1},
        "Gate_99": {"active": False, "low_battery": True, "signal": 7},
        "Bridge_X": {"active": False, "low_battery": False, "signal": 0}
    }
    
    print("--- [1] Processing Batch ---")
    processor.process_batch(raw_input)
    logs = processor.get_log_snapshot()

    # 2. Automated Validation Loop
    print(f"--- [2] Running {len(expected_results)} Validations ---")
    passed_count = 0
    
    for log in logs:
        # Access data using dot notation (log.id) instead of brackets (log['id'])
        s_id = log.id
        if s_id in expected_results:
            exp = expected_results[s_id]
            
            # Check all values
            if log.active == exp['active'] and \
               log.low_battery == exp['low_battery'] and \
               log.signal == exp['signal']:
                print(f"✅ PASS: {s_id}")
                passed_count += 1
            else:
                print(f"❌ FAIL: {s_id} | Got: {log}")

    # 3. Memory Integrity Test (The Immutability Proof)
    print("\n--- [3] Memory Integrity Test ---")
    try:
        # Attempting to change an immutable NamedTuple will raise an AttributeError
        logs[0].id = "TAMPERED"
        print("❌ FAIL: Data was mutable! This is not Staff-level.")
    except AttributeError:
        print("✅ PASS: Immutability confirmed. Attributes cannot be modified.")

    if passed_count == len(expected_results):
        print("\n✨ ALL TESTS PASSED SUCCESSFULLY ✨")

if __name__ == "__main__":
    run_tests()