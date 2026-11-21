"""Unified test runner for all AI module volumes."""

import os
import sys
import unittest

# Ensure both the repository root and ai/ directory are on sys.path.
AI_ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(AI_ROOT)
for path in (REPO_ROOT, AI_ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)


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

    # Load and run all tests; import failures must fail CI instead of being
    # silently omitted from an otherwise successful empty test suite.
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    load_errors = []

    for test_file in test_files:
        module_name = os.path.splitext(os.path.basename(test_file))[0]
        try:
            module = __import__(module_name)
            suite.addTests(loader.loadTestsFromModule(module))
        except Exception as e:
            load_errors.append((module_name, e))
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
    load_error_count = len(load_errors)
    if failures == 0 and errors == 0 and load_error_count == 0 and total > 0:
        print("ALL TESTS PASSED!")
    else:
        print(f"IMPORT ERRORS: {load_error_count}")
    print(f"{'=' * 60}")

    sys.exit(0 if failures == 0 and errors == 0 and load_error_count == 0 and total > 0 else 1)
