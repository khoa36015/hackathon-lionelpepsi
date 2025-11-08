"""
Test natural AI responses - no more robotic answers!
"""
import requests
import json

API_BASE = "http://localhost:8000/api"

def ask_question(question):
    """Send a question to the AI and print the response"""
    print(f"\n{'='*70}")
    print(f"❓ {question}")
    print(f"{'='*70}")
    
    try:
        response = requests.post(
            f"{API_BASE}/ask",
            headers={'Content-Type': 'application/json'},
            json={"message": question},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('answer') or data.get('response') or data.get('message')
            print(f"\n🤖 AI: {answer}\n")
            
            # Check for robotic phrases
            bad_phrases = [
                "không có thông tin",
                "hiện tại, mình không có",
                "xin lỗi, nhưng mình không có",
                "trong bối cảnh này",
                "trong bối cảnh đã cung cấp"
            ]
            
            is_robotic = any(phrase in answer.lower() for phrase in bad_phrases)
            
            if is_robotic:
                print("❌ ROBOTIC RESPONSE DETECTED!")
                print("   AI should use general knowledge instead of refusing!")
            else:
                print("✅ NATURAL RESPONSE!")
            
            return not is_robotic
        else:
            print(f"❌ Error {response.status_code}: {response.text}\n")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}\n")
        return False

print("="*70)
print("🧪 TESTING NATURAL AI RESPONSES")
print("="*70)
print("\nGoal: AI should NEVER say 'I don't have information'")
print("      AI should use general knowledge about Vietnam War")
print("="*70)

results = []

# Test 1: Greetings
print("\n\n📋 TEST 1: GREETINGS")
print("-"*70)
results.append(ask_question("Xin chào!"))
results.append(ask_question("Chào bạn, bạn khỏe không?"))

# Test 2: Aircraft questions (not in database)
print("\n\n📋 TEST 2: AIRCRAFT QUESTIONS (Testing General Knowledge)")
print("-"*70)
results.append(ask_question("Hãy cho tôi biết về máy bay A-37 Dragonfly"))
results.append(ask_question("Máy bay F-5A Freedom Fighter là gì?"))
results.append(ask_question("F-4 Phantom được sử dụng như thế nào trong chiến tranh?"))
results.append(ask_question("Cho tôi biết về máy bay B-52"))

# Test 3: Tank questions
print("\n\n📋 TEST 3: TANK QUESTIONS")
print("-"*70)
results.append(ask_question("Xe tăng T-54 có gì đặc biệt?"))
results.append(ask_question("M48 Patton là loại xe tăng gì?"))
results.append(ask_question("Xe tăng nào được sử dụng nhiều nhất trong chiến tranh Việt Nam?"))

# Test 4: Weapons
print("\n\n📋 TEST 4: WEAPONS")
print("-"*70)
results.append(ask_question("AK-47 là súng gì?"))
results.append(ask_question("M16 khác gì với AK-47?"))
results.append(ask_question("Súng trường nào được quân đội Mỹ sử dụng?"))

# Test 5: Historical events
print("\n\n📋 TEST 5: HISTORICAL EVENTS")
print("-"*70)
results.append(ask_question("Chiến dịch Tết Mậu Thân là gì?"))
results.append(ask_question("Trận Điện Biên Phủ diễn ra như thế nào?"))
results.append(ask_question("Hiệp định Paris 1973 nói về điều gì?"))

# Test 6: General museum questions
print("\n\n📋 TEST 6: GENERAL MUSEUM QUESTIONS")
print("-"*70)
results.append(ask_question("Bảo tàng có những gì?"))
results.append(ask_question("Tôi nên xem gì trước?"))
results.append(ask_question("Có hiện vật nào về máy bay không?"))

# Summary
print("\n\n" + "="*70)
print("📊 TEST SUMMARY")
print("="*70)

natural_count = sum(results)
total_count = len(results)
success_rate = (natural_count / total_count * 100) if total_count > 0 else 0

print(f"\n✅ Natural responses: {natural_count}/{total_count}")
print(f"❌ Robotic responses: {total_count - natural_count}/{total_count}")
print(f"📈 Success rate: {success_rate:.1f}%")

if success_rate >= 90:
    print("\n🎉 EXCELLENT! AI is responding naturally!")
elif success_rate >= 70:
    print("\n👍 GOOD! But still some robotic responses")
else:
    print("\n⚠️ NEEDS IMPROVEMENT! Too many robotic responses")

print("\n" + "="*70)

