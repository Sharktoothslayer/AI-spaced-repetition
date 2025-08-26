#!/usr/bin/env python3
"""
Test script to debug vocabulary loading issues
"""

import requests
import json

# Configuration
API_BASE_URL = "http://100.107.135.85:5000"  # Change this to your server URL

def test_vocabulary_endpoints():
    """Test vocabulary-related endpoints to debug the issue"""
    print("🔍 Testing vocabulary endpoints...")
    print(f"📡 API Base URL: {API_BASE_URL}")
    print("-" * 50)
    
    # Test 1: Debug vocabulary endpoint
    print("\n1️⃣ Testing debug vocabulary endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/debug/vocabulary", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Debug endpoint working:")
            print(f"   - File exists: {data.get('file_exists')}")
            print(f"   - File size: {data.get('file_size')} bytes")
            print(f"   - Word count: {data.get('word_count')}")
            print(f"   - Data file path: {data.get('data_file_path')}")
            print(f"   - Sample words: {data.get('sample_words')}")
        else:
            print(f"❌ Debug endpoint failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error testing debug endpoint: {e}")
    
    # Test 2: Get all words endpoint
    print("\n2️⃣ Testing get all words endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/sr/words", timeout=10)
        if response.status_code == 200:
            data = response.json()
            words = data.get('words', [])
            print(f"✅ Get words endpoint working:")
            print(f"   - Total words: {len(words)}")
            print(f"   - First 5 words: {[w['word'] for w in words[:5]] if words else 'None'}")
            print(f"   - Last 5 words: {[w['word'] for w in words[-5:]] if words else 'None'}")
        else:
            print(f"❌ Get words endpoint failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error testing get words endpoint: {e}")
    
    # Test 3: Check if vocabulary.json exists locally
    print("\n3️⃣ Checking local vocabulary.json...")
    try:
        with open("vocabulary.json", "r", encoding="utf-8") as f:
            local_data = json.load(f)
            print(f"✅ Local vocabulary.json found:")
            print(f"   - File size: {len(json.dumps(local_data))} bytes")
            print(f"   - Word count: {len(local_data)}")
            print(f"   - Sample words: {list(local_data.keys())[:5] if local_data else 'None'}")
    except FileNotFoundError:
        print("❌ Local vocabulary.json not found")
    except Exception as e:
        print(f"❌ Error reading local vocabulary.json: {e}")

if __name__ == "__main__":
    test_vocabulary_endpoints()
