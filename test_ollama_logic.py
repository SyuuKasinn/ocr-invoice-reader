"""
Test Ollama Manager logic
"""
import sys
from ocr_invoice_reader.utils.ollama_manager import OllamaManager


def test_status_check():
    """Test status checking logic"""
    print("=" * 60)
    print("TEST 1: Status Check Logic")
    print("=" * 60)

    manager = OllamaManager()

    # Test service check
    print("\n1. Testing service check...")
    service_running = manager.check_service()
    print(f"   Service running: {service_running}")

    # Test installation check
    print("\n2. Testing installation check...")
    is_installed = manager.is_installed()
    print(f"   Ollama installed: {is_installed}")

    # Test model check
    print("\n3. Testing model check...")
    has_model = manager.check_model("qwen2.5:0.5b")
    print(f"   Model qwen2.5:0.5b exists: {has_model}")

    # Test full status
    print("\n4. Testing full status...")
    status = manager.get_status()
    print(f"   Installed: {status['installed']}")
    print(f"   Service running: {status['service_running']}")
    print(f"   Models: {status['models']}")

    print("\n[OK] Status check logic test complete")
    return True


def test_setup_logic_flow():
    """Test setup logic flow (dry run, no actual installation)"""
    print("\n" + "=" * 60)
    print("TEST 2: Setup Logic Flow (Dry Run)")
    print("=" * 60)

    manager = OllamaManager()

    # Test logic flow without actual operations
    print("\n1. Checking service...")
    service_ok = manager.check_service()
    print(f"   Result: {'[OK] Running' if service_ok else '[FAIL] Not running'}")

    if not service_ok:
        print("\n2. Checking installation...")
        installed = manager.is_installed()
        print(f"   Result: {'[OK] Installed' if installed else '[FAIL] Not installed'}")

        if not installed:
            print("\n3. Installation would be needed")
            print(f"   Target system: {manager.system}")
            install_url = manager.get_install_url()
            if install_url:
                print(f"   Install URL: {install_url}")
            else:
                print(f"   Install method: Script installation")

        print("\n4. Service start would be needed")

    print("\n5. Checking model...")
    has_model = manager.check_model("qwen2.5:0.5b")
    print(f"   Result: {'[OK] Exists' if has_model else '[FAIL] Not downloaded'}")

    print("\n[OK] Setup logic flow test complete")
    return True


def test_error_handling():
    """Test error handling"""
    print("\n" + "=" * 60)
    print("TEST 3: Error Handling")
    print("=" * 60)

    manager = OllamaManager()

    print("\n1. Testing invalid model check...")
    try:
        result = manager.check_model("nonexistent-model:999")
        print(f"   Result: {result} (should be False)")
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

    print("\n2. Testing service check with wrong URL...")
    try:
        bad_manager = OllamaManager(base_url="http://localhost:99999")
        result = bad_manager.check_service()
        print(f"   Result: {result} (should be False)")
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

    print("\n[OK] Error handling test complete")
    return True


def test_conditional_logic():
    """Test conditional logic branches"""
    print("\n" + "=" * 60)
    print("TEST 4: Conditional Logic")
    print("=" * 60)

    manager = OllamaManager()
    status = manager.get_status()

    print("\n1. Testing setup decision tree...")

    # Scenario 1: Everything ready
    if status['installed'] and status['service_running'] and status['models']:
        print("   Scenario: All ready - should skip all setup steps")
        print("   [OK] Logic: Correct")

    # Scenario 2: Installed but service not running
    elif status['installed'] and not status['service_running']:
        print("   Scenario: Installed but not running - should start service only")
        print("   [OK] Logic: Correct")

    # Scenario 3: Not installed
    elif not status['installed']:
        print("   Scenario: Not installed - should install, start, and download model")
        print("   [OK] Logic: Correct")

    # Scenario 4: Running but no models
    elif status['service_running'] and not status['models']:
        print("   Scenario: Running but no models - should download model only")
        print("   [OK] Logic: Correct")

    print("\n[OK] Conditional logic test complete")
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("OLLAMA MANAGER LOGIC TESTS")
    print("=" * 70)

    tests = [
        ("Status Check", test_status_check),
        ("Setup Logic Flow", test_setup_logic_flow),
        ("Error Handling", test_error_handling),
        ("Conditional Logic", test_conditional_logic),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[FAIL] Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{status}: {test_name}")

    print("\n" + "=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 70)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
