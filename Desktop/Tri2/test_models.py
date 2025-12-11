"""Test script to verify OpenRouter API key and model access."""
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

async def test_model(model: str):
    """Test a single model."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Say 'test successful'"}],
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            content = data['choices'][0]['message']['content']
            print(f"✓ {model}: SUCCESS")
            print(f"  Response: {content[:100]}")
            return True
    except httpx.HTTPStatusError as e:
        try:
            error_json = e.response.json()
            error_msg = error_json.get('error', {}).get('message', str(error_json))
            print(f"X {model}: FAILED ({e.response.status_code})")
            print(f"  Error: {error_msg}")
        except:
            print(f"X {model}: FAILED ({e.response.status_code})")
            print(f"  Response: {e.response.text[:200]}")
        return False
    except Exception as e:
        print(f"X {model}: ERROR - {str(e)}")
        return False

async def main():
    """Test multiple model identifiers."""
    print(f"Testing API key: {OPENROUTER_API_KEY[:30]}...\n")
    
    # Test various model name formats - start with free models
    test_models = [
        "meta-llama/llama-3.1-8b-instruct:free",  # Known working free model
        "mistralai/mistral-7b-instruct:free",
        "mistralai/mistral-large",
        "mistralai/mistral-large-latest",
        "mistralai/devstral",
        "mistralai/devstral-latest",
        "thudm/glm-4-5-air",
        "thudm/glm-4.5-air",
    ]
    
    print("Testing models:\n")
    results = []
    for model in test_models:
        result = await test_model(model)
        results.append((model, result))
        print()
        await asyncio.sleep(0.5)  # Rate limiting
    
    print("=== SUMMARY ===")
    working = [m for m, r in results if r]
    failing = [m for m, r in results if not r]
    
    if working:
        print(f"\n✓ Working models ({len(working)}):")
        for m in working:
            print(f"  - {m}")
    
    if failing:
        print(f"\nX Failing models ({len(failing)}):")
        for m in failing:
            print(f"  - {m}")

if __name__ == "__main__":
    asyncio.run(main())

