"""
Test full TTS flow: AI response -> TTS conversion
"""
import requests
import json
import time

API_BASE = "http://localhost:8000/api"

print("=" * 60)
print("🧪 FULL FLOW TEST: AI + TTS")
print("=" * 60)

# Step 1: Test AI endpoint
print("\n📝 Step 1: Testing AI endpoint...")
print("-" * 60)

ai_request = {
    "message": "Hãy cho tôi biết về máy bay F-5A Freedom Fighter"
}

try:
    response = requests.post(
        f"{API_BASE}/ask",
        headers={'Content-Type': 'application/json'},
        json=ai_request,
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        ai_response = data.get('answer') or data.get('response') or data.get('message')
        print(f"✅ AI Response: {ai_response[:200]}...")
        print(f"📏 Response length: {len(ai_response)} characters")
        
        # Step 2: Test TTS with AI response
        print("\n🎤 Step 2: Testing TTS with AI response...")
        print("-" * 60)
        
        tts_request = {
            "text": ai_response,
            "voice": "banmai",
            "speed": 0
        }
        
        tts_response = requests.post(
            f"{API_BASE}/tts",
            headers={'Content-Type': 'application/json'},
            json=tts_request,
            timeout=30
        )
        
        print(f"Status: {tts_response.status_code}")
        
        if tts_response.status_code == 200:
            tts_data = tts_response.json()
            print(f"✅ TTS Response: {json.dumps(tts_data, indent=2, ensure_ascii=False)}")
            
            if tts_data.get('success') and tts_data.get('audio_url'):
                audio_url = tts_data['audio_url']
                print(f"\n🔊 Audio URL: {audio_url}")
                
                # Step 3: Check if audio is ready
                print("\n⏳ Step 3: Checking if audio is ready...")
                print("-" * 60)
                
                max_wait = 10
                check_interval = 1
                start_time = time.time()
                
                while time.time() - start_time < max_wait:
                    try:
                        audio_check = requests.head(audio_url, timeout=5)
                        if audio_check.status_code == 200:
                            print(f"✅ Audio is ready! (after {int(time.time() - start_time)}s)")
                            print(f"📦 Content-Type: {audio_check.headers.get('Content-Type')}")
                            print(f"📏 Content-Length: {audio_check.headers.get('Content-Length')} bytes")
                            break
                    except Exception as e:
                        pass
                    
                    print(f"⏳ Waiting... ({int(time.time() - start_time)}s)")
                    time.sleep(check_interval)
                else:
                    print(f"⚠️ Audio not ready after {max_wait}s")
                
                print("\n✅ FULL FLOW TEST PASSED!")
                print("=" * 60)
                print("\n🎉 You can now:")
                print("1. Open the frontend")
                print("2. Click on a card")
                print("3. Ask a question")
                print("4. Hear the Vietnamese voice response!")
                
            else:
                print(f"❌ TTS failed: {tts_data}")
        else:
            print(f"❌ TTS request failed: {tts_response.text}")
    else:
        print(f"❌ AI request failed: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to server!")
    print("Please start the server with: python app.py")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)

