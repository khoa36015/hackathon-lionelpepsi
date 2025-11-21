"""
Smoke tests for Google Cloud Text-to-Speech integration.
"""

import json

import requests

from google_tts import get_available_voices, synthesize_speech

VOICE = "vi-VN-Neural2-A"
TEXT_SAMPLE = "Xin chào, đây là giọng đọc tiếng Việt từ Google Cloud."


def print_section(title: str):
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)


print_section("Test 1: Voice catalog")
voices = get_available_voices()
print(json.dumps(voices, indent=2, ensure_ascii=False))

print_section("Test 2: Direct synthesize_speech() call")
result = synthesize_speech(TEXT_SAMPLE, voice=VOICE)
print(json.dumps(result, indent=2, ensure_ascii=False))

print_section("Test 3: Flask API endpoint")

try:
    response = requests.post(
        "http://localhost:8000/api/tts",
        headers={"Content-Type": "application/json"},
        json={
            "text": TEXT_SAMPLE,
            "voice": VOICE,
            "speaking_rate": 1.0,
            "pitch": 0.0,
        },
        timeout=15,
    )
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except requests.exceptions.ConnectionError:
    print("❌ Server is not running. Start it with: python app.py")
except Exception as exc:
    print(f"❌ Error: {exc}")

print_section("✅ Tests Complete!")

