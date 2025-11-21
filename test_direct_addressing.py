#!/usr/bin/env python3
"""Test direct addressing functionality"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from routing.topic_analyzer import TopicAnalyzer

def test_direct_addressing():
    """Test direct addressing patterns"""
    analyzer = TopicAnalyzer()

    test_cases = [
        # Direct addressing (should always switch)
        ("Botan, what do you think about Kin-Koi live stream by Miko Sakura", "yuri", "botan"),
        ("Kasho, can you give me music advice?", "botan", "kasho"),
        ("Yuri, tell me about books", "botan", "yuri"),
        ("Hey Botan, what's up?", "kasho", "botan"),
        ("Hi Yuri, how are you?", "botan", "yuri"),
        ("botan what do you think", "yuri", "botan"),  # No comma

        # Non-direct addressing (should use topic analysis)
        ("What do you think about Botan?", "kasho", "kasho"),  # Talking ABOUT Botan, not TO Botan
        ("I like streaming", "kasho", "kasho"),  # No direct address
    ]

    print("🧪 Testing Direct Addressing\n")
    print("=" * 60)

    passed = 0
    failed = 0

    for message, current, expected in test_cases:
        selected, scores = analyzer.select_character(message, current)

        if selected == expected:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1

        print(f"\n{status}")
        print(f"Message: '{message}'")
        print(f"Current: {current} → Selected: {selected} (Expected: {expected})")

    print("\n" + "=" * 60)
    print(f"\nResults: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️ Some tests failed")
        return False


if __name__ == "__main__":
    success = test_direct_addressing()
    sys.exit(0 if success else 1)
