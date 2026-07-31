"""Unified test runner for all AI module volumes."""

import os
import sys
import unittest

# Ensure the ai/ directory is on sys.path
AI_ROOT = os.path.dirname(os.path.abspath(__file__))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)


def discover_ai_tests():
    """Discover all AI volume test files."""
    test_files = []
    for f in os.listdir(AI_ROOT):
        if f.startswith("test_") and f.endswith(".py"):
            test_files.append(os.path.join(AI_ROOT, f))
    return sorted(test_files)


if __name__ == "__main__":
    test_files = discover_ai_tests()
    print(f"Found {len(test_files)} test files:")
    for f in test_files:
        print(f"  - {os.path.basename(f)}")

    # Load and run all tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for test_file in test_files:
        module_name = os.path.splitext(os.path.basename(test_file))[0]
        try:
            module = __import__(module_name)
            suite.addTests(loader.loadTestsFromModule(module))
        except Exception as e:
            print(f"  ERROR loading {module_name}: {e}")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total - failures - errors
    print(f"\n{'=' * 60}")
    print(f"RESULTS: {passed}/{total} passed, {failures} failed, {errors} errors")
    if failures == 0 and errors == 0:
        print("ALL TESTS PASSED!")
    print(f"{'=' * 60}")

    sys.exit(0 if failures == 0 and errors == 0 else 1)
