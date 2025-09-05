#!/usr/bin/env python3
"""
Check OpenAI API access and available models
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_openai_models():
    """Check what OpenAI models are available"""
    print("🔍 Checking OpenAI API Access...")
    
    # Check if API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}...")
    
    try:
        import openai
        client = openai.OpenAI()
        
        # Test different models (latest first)
        models_to_test = [
            "gpt-4o",                    # GPT-4 Omni (Latest)
            "gpt-4o-mini",              # GPT-4 Omni Mini (Faster/Cheaper)
            "gpt-4-turbo",              # GPT-4 Turbo
            "gpt-4",                     # GPT-4 (Classic)
            "gpt-3.5-turbo",            # GPT-3.5 Turbo
            "gpt-4o-2024-08-06",        # GPT-4 Omni (Specific version)
            "gpt-4-turbo-2024-04-09"    # GPT-4 Turbo (Specific version)
        ]
        
        available_models = []
        
        for model in models_to_test:
            try:
                print(f"Testing {model}...")
                response = client.chat.completions.create(
                    model=model,
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Test"}]
                )
                available_models.append(model)
                print(f"✅ {model} - Available")
            except Exception as e:
                print(f"❌ {model} - Not available: {e}")
        
        print(f"\n📊 Available Models: {len(available_models)}")
        for model in available_models:
            print(f"  - {model}")
        
        return available_models
        
    except ImportError:
        print("❌ OpenAI package not installed. Run: pip install openai")
        return False
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return False

if __name__ == "__main__":
    available_models = check_openai_models()
    
    if available_models:
        print(f"\n🎉 Found {len(available_models)} available models!")
        
        # Recommend the best model
        if "gpt-4o" in available_models:
            print("🏆 Recommended: gpt-4o (GPT-4 Omni - Latest & Most Capable)")
        elif "gpt-4-turbo" in available_models:
            print("🏆 Recommended: gpt-4-turbo (GPT-4 Turbo - High Performance)")
        elif "gpt-4" in available_models:
            print("🏆 Recommended: gpt-4 (GPT-4 Classic - Reliable)")
        else:
            print("⚠️  No recommended models found")
    else:
        print("❌ No models available")
