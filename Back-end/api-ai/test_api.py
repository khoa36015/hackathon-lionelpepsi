#!/usr/bin/env python3
"""
Simple test script to verify the AI API is working correctly
"""
import requests
import json

API_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    print("🔍 Testing /api/health endpoint...")
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_ask_with_message():
    """Test the /api/ask endpoint with 'message' field"""
    print("\n🔍 Testing /api/ask with 'message' field...")
    try:
        payload = {"message": "Trực thăng UH-1 Huey là gì?"}
        response = requests.post(
            f"{API_URL}/api/ask",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response keys: {list(data.keys())}")
        if "response" in data:
            print(f"   ✅ Has 'response' field: {data['response'][:100]}...")
        if "message" in data:
            print(f"   ✅ Has 'message' field: {data['message'][:100]}...")
        if "answer" in data:
            print(f"   ✅ Has 'answer' field: {data['answer'][:100]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_ask_with_question():
    """Test the /api/ask endpoint with 'question' field"""
    print("\n🔍 Testing /api/ask with 'question' field...")
    try:
        payload = {"question": "Máy bay F-5A là gì?"}
        response = requests.post(
            f"{API_URL}/api/ask",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response keys: {list(data.keys())}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_cors():
    """Test CORS headers"""
    print("\n🔍 Testing CORS headers...")
    try:
        response = requests.options(
            f"{API_URL}/api/ask",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        print(f"   CORS Headers:")
        for header, value in response.headers.items():
            if "access-control" in header.lower():
                print(f"      {header}: {value}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 AI API Test Suite")
    print("=" * 60)
    
    results = []
    results.append(("Health Check", test_health()))
    results.append(("CORS Headers", test_cors()))
    results.append(("Ask with 'message'", test_ask_with_message()))
    results.append(("Ask with 'question'", test_ask_with_question()))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n🎉 All tests passed! API is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\n💡 Make sure:")
        print("   1. The AI API server is running: python app.py")
        print("   2. The server is listening on port 8000")
        print("   3. You have restarted the server after making changes")

