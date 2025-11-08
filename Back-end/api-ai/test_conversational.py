"""
Test conversational AI with various question types
"""
import requests
import json

API_BASE = "http://localhost:8000/api"

def ask_question(question):
    """Send a question to the AI and print the response"""
    print(f"\n{'='*60}")
    print(f"❓ QUESTION: {question}")
    print(f"{'='*60}")
    
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
            print(f"✅ ANSWER:\n{answer}\n")
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}\n")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}\n")
        return False

print("="*60)
print("🧪 TESTING CONVERSATIONAL AI")
print("="*60)

# Test 1: Greetings
print("\n📋 TEST 1: GREETINGS & BASIC CONVERSATION")
print("-"*60)
ask_question("Xin chào!")
ask_question("Chào bạn, bạn có thể giúp tôi không?")
ask_question("Cảm ơn bạn nhé!")

# Test 2: General suggestions
print("\n📋 TEST 2: SUGGESTIONS & RECOMMENDATIONS")
print("-"*60)
ask_question("Bạn có thể gợi ý cho tôi nên xem gì trong bảo tàng không?")
ask_question("Những hiện vật nào đáng xem nhất?")
ask_question("Tôi nên bắt đầu tham quan từ đâu?")

# Test 3: Directions
print("\n📋 TEST 3: DIRECTIONS & NAVIGATION")
print("-"*60)
ask_question("Khu vực máy bay ở đâu?")
ask_question("Làm sao để tìm đến phòng trưng bày xe tăng?")
ask_question("Nhà vệ sinh ở đâu?")

# Test 4: Specific artifacts
print("\n📋 TEST 4: SPECIFIC ARTIFACTS")
print("-"*60)
ask_question("Hãy cho tôi biết về máy bay F-5A Freedom Fighter")
ask_question("Xe tăng T-54 có gì đặc biệt?")
ask_question("Máy bay này được sử dụng như thế nào trong chiến tranh?")

# Test 5: Historical questions
print("\n📋 TEST 5: HISTORICAL QUESTIONS")
print("-"*60)
ask_question("Chiến tranh Việt Nam diễn ra khi nào?")
ask_question("Ai là những người tham gia chiến tranh?")
ask_question("Tại sao có bảo tàng này?")

# Test 6: Mixed questions
print("\n📋 TEST 6: MIXED CONVERSATIONAL QUESTIONS")
print("-"*60)
ask_question("Này, bạn biết gì về những chiếc máy bay ở đây không?")
ask_question("Tôi thấy có nhiều vũ khí quá, chúng từ đâu vậy?")
ask_question("Bảo tàng này có gì thú vị không?")

print("\n" + "="*60)
print("✅ TEST COMPLETED!")
print("="*60)
print("\n📊 SUMMARY:")
print("- AI should respond naturally to greetings")
print("- AI should provide helpful suggestions")
print("- AI should give directions and navigation help")
print("- AI should explain artifacts in detail")
print("- AI should answer historical questions")
print("- AI should handle mixed conversational questions")
print("\n🎯 The AI should NEVER refuse to answer!")

