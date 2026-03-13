"""
Automated test script — sends 15+ test messages through the API
and prints the classified intent + confidence for each.

Usage:
    python tests/test_router.py
    (server must be running at http://localhost:8000)
"""

import json
import sys
import urllib.request
import urllib.error

API_URL = "http://localhost:8000/api/chat"

TEST_MESSAGES = [
    ("how do i sort a list of objects in python?", "code"),
    ("explain this sql query for me", "code"),
    ("This paragraph sounds awkward, can you help me fix it?", "writing"),
    ("I'm preparing for a job interview, any tips?", "career"),
    ("what's the average of these numbers: 12, 45, 23, 67, 34", "data"),
    ("Help me make this better.", "unclear"),
    (
        "I need to write a function that takes a user id and returns their profile, "
        "but also i need help with my resume.",
        "unclear",
    ),
    ("hey", "unclear"),
    ("Can you write me a poem about clouds?", "unclear"),
    ("Rewrite this sentence to be more professional.", "writing"),
    ("I'm not sure what to do with my career.", "career"),
    ("what is a pivot table", "data"),
    ("fxi thsi bug pls: for i in range(10) print(i)", "code"),
    ("How do I structure a cover letter?", "career"),
    ("My boss says my writing is too verbose.", "writing"),
    # Manual override test
    ("@code Fix this: for i in range(10) print(i)", "code"),
]


def send(message: str) -> dict:
    body = json.dumps({"message": message}).encode()
    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def main():
    passed = 0
    total = len(TEST_MESSAGES)

    print(f"\n{'#':<3} {'Expected':<10} {'Got':<10} {'Conf':>6}  Message")
    print("-" * 80)

    for i, (msg, expected) in enumerate(TEST_MESSAGES, 1):
        try:
            data = send(msg)
            intent = data.get("intent", "???")
            conf = data.get("confidence", 0)
            match = "✓" if intent == expected else "✗"
            if intent == expected:
                passed += 1
            short_msg = msg[:50] + ("…" if len(msg) > 50 else "")
            print(f"{i:<3} {expected:<10} {intent:<10} {conf:>5.0%}  {match} {short_msg}")
        except urllib.error.URLError as e:
            print(f"{i:<3} {'ERROR':<10} Could not reach server: {e}")
        except Exception as e:
            print(f"{i:<3} {'ERROR':<10} {e}")

    print("-" * 80)
    pct = (passed / total * 100) if total else 0
    print(f"Result: {passed}/{total} matched expected intent ({pct:.0f}%)\n")
    sys.exit(0 if passed >= total * 0.7 else 1)


if __name__ == "__main__":
    main()
