from processor_old import SentinelLogProcessor

def run_tests():
    processor = SentinelLogProcessor()
    
    # 1. Define the actual raw strings we are sending to the city system
    raw_input = [
        "Traf_01:0x0005",  # Active=True,  LowBat=False, Signal=1
        "Gate_99:0x001E",  # Active=False, LowBat=True,  Signal=7
        "Bridge_X:0x0000", # Active=False, LowBat=False, Signal=0
        "Malformed_Data",  # Should be ignored
        "Broken:0xZZZZ"    # Should be ignored
    ]

    # 2. Define what the dictionary SHOULD look like after processing
    expected_results = {
        "Traf_01": {"active": True, "low_battery": False, "signal": 1},
        "Gate_99": {"active": False, "low_battery": True, "signal": 7},
        "Bridge_X": {"active": False, "low_battery": False, "signal": 0}
    }
    
    print("--- [1] Processing Batch ---")
    processor.process_batch(raw_input)
    logs = processor.get_log_snapshot()

    # 3. Automated Validation Loop
    print(f"--- [2] Running {len(expected_results)} Validations ---")
    passed_count = 0
    
    for log in logs:
        s_id = log['id']
        if s_id in expected_results:
            expected = expected_results[s_id]
            # Check all values match
            if all(log[k] == expected[k] for k in expected):
                print(f"✅ PASS: {s_id}")
                passed_count += 1
            else:
                print(f"❌ FAIL: {s_id} | Expected {expected} | Got {log}")

    # 4. Final Verification
    if passed_count == len(expected_results):
        print("\n✨ ALL TESTS PASSED SUCCESSFULLY ✨")
    else:
        print(f"\n⚠️ WARNING: Only {passed_count}/{len(expected_results)} passed.")

    # 5. Memory Integrity Check
    print("\n--- [3] Memory Integrity Test ---")
    if logs:
        logs[0]['id'] = "TAMPERED"
        if processor.get_log_snapshot()[0]['id'] != "TAMPERED":
            print("✅ PASS: Deep copy protected the original data.")
        else:
            print("❌ FAIL: Original data was corrupted!")

if __name__ == "__main__":
    run_tests()

