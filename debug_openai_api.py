#!/usr/bin/env python3
"""
Debug OpenAI API Connection
"""

import requests
import json
import os

def test_openai_api():
    api_key = "YOUR_OPENAI_API_KEY_HERE"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test with different models
    models_to_test = [
        "gpt-5",
        "gpt-5-mini", 
        "gpt-5-nano",
        "gpt-4",
        "gpt-4-turbo"
    ]
    
    for model in models_to_test:
        print(f"\n🧪 Testing model: {model}")
        print("-" * 40)
        
        test_data = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Hello! Just testing API connection."}
            ],
            "max_completion_tokens": 50
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=test_data,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print(f"✅ SUCCESS! Response: {content[:100]}...")
                print(f"Model used: {result.get('model', 'Unknown')}")
                break
            else:
                print(f"❌ Error Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    # Also test listing available models
    print(f"\n📋 Testing model list endpoint...")
    try:
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            models = response.json()
            available_models = [model['id'] for model in models['data']]
            gpt5_models = [m for m in available_models if 'gpt-5' in m]
            
            print(f"✅ Available GPT-5 models: {gpt5_models}")
            print(f"📊 Total models available: {len(available_models)}")
        else:
            print(f"❌ Model list error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Model list exception: {e}")

if __name__ == "__main__":
    test_openai_api()