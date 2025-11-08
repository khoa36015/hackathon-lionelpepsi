"""
Test FPT.AI TTS integration
"""
import requests
import json

# Test 1: Direct FPT.AI API call
print("=" * 50)
print("Test 1: Direct FPT.AI API Call")
print("=" * 50)

response = requests.post(
    'https://api.fpt.ai/hmi/tts/v5',
    headers={
        'api_key': '8OuJvLUvBBfqok7MkamxBelt4yb3JHWF',
        'voice': 'banmai'
    },
    data='Xin chào, đây là giọng đọc tiếng Việt'.encode('utf-8')
)

print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 2: Our wrapper function
print("\n" + "=" * 50)
print("Test 2: Our Wrapper Function")
print("=" * 50)

from fpt_tts import synthesize_speech

result = synthesize_speech("Xin chào, đây là giọng đọc tiếng Việt", voice="banmai")
print(f"Result: {json.dumps(result, indent=2, ensure_ascii=False)}")

# Test 3: Flask API endpoint (if server is running)
print("\n" + "=" * 50)
print("Test 3: Flask API Endpoint")
print("=" * 50)

try:
    response = requests.post(
        'http://localhost:8000/api/tts',
        headers={'Content-Type': 'application/json'},
        json={
            'text': 'Xin chào, đây là giọng đọc tiếng Việt',
            'voice': 'banmai',
            'speed': 0
        },
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
except requests.exceptions.ConnectionError:
    print("❌ Server is not running. Start it with: python app.py")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 50)
print("✅ Tests Complete!")
print("=" * 50)

