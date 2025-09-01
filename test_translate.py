import requests
import json

def test_google_translate(word):
    """Test Google Translate API with a single word"""
    print(f"\n🔍 Testing word: '{word}'")
    print("=" * 50)
    
    # Google Translate URL (same as your app)
    google_url = "https://translate.googleapis.com/translate_a/single"
    params = {
        'client': 'gtx',
        'sl': 'it',  # Italian
        'tl': 'en',  # English
        'dt': 't',
        'q': word
    }
    
    print(f"🌐 URL: {google_url}")
    print(f"📤 Parameters: {params}")
    
    try:
        # Make request
        response = requests.get(google_url, params=params, timeout=15)
        print(f"�� Response Status: {response.status_code}")
        
        if response.status_code == 200:
            # Parse response
            data = response.json()
            print(f"📥 Raw Response: {json.dumps(data, indent=2)}")
            
            # Extract translations (same logic as your app)
            if data and len(data) > 0 and len(data[0]) > 0:
                print(f"\n�� Response Structure:")
                print(f"  - data length: {len(data)}")
                print(f"  - data[0] length: {len(data[0])}")
                
                all_translations = []
                for i, translation_block in enumerate(data[0]):
                    print(f"  - data[0][{i}]: {translation_block}")
                    if translation_block and len(translation_block) > 0:
                        english_word = translation_block[0]
                        if english_word and english_word != word:
                            all_translations.append(english_word)
                
                print(f"\n✅ Extracted Translations: {all_translations}")
                
                if all_translations:
                    combined = ", ".join(all_translations[:3])
                    print(f"🎯 Combined Result: '{combined}'")
                else:
                    print("❌ No valid translations extracted")
            else:
                print("❌ Unexpected response format")
        else:
            print(f"❌ Request failed: {response.text}")
            
    except Exception as e:
        print(f"💥 Error: {str(e)}")

def main():
    print("🚀 Google Translate Test Script")
    print("Test individual Italian words and see the raw API response")
    print("=" * 60)
    
    while True:
        word = input("\n�� Enter Italian word to test (or 'quit' to exit): ").strip()
        
        if word.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
            
        if word:
            test_google_translate(word)
        else:
            print("⚠️ Please enter a word")

if __name__ == "__main__":
    main()