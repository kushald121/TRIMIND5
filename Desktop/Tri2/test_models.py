"""Test script to verify OpenRouter API key and model access."""
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

async def test_model(model: str):
    """Test a single model."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Say hello world"}
        ],
        "max_tokens": 100,
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            content = data['choices'][0]['message']['content']
            print(f"✅ {model}: {content.strip()}")
            return True
        except Exception as e:
            print(f"❌ {model}: {e}")
            return False

async def main():
    """Test all models."""
    if not OPENROUTER_API_KEY:
        print("❌ OPENROUTER_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        return
    
    print(f"Testing API key: {OPENROUTER_API_KEY[:10]}...\n")
    
    models = [
        "meta-llama/llama-3.1-8b-instruct:free",
        "mistralai/mistral-7b-instruct:free",
        "google/gemma-2-9b-it:free"
    ]
    
    print("Testing models:")
    results = await asyncio.gather(*[test_model(model) for model in models])
    
    success_count = sum(results)
    print(f"\nResults: {success_count}/{len(models)} models working")

if __name__ == "__main__":
    asyncio.run(main())