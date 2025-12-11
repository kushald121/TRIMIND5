"""Test script to verify OpenRouter API key and model access."""
import asyncio
import httpx
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import OPENROUTER_API_KEY, OPENROUTER_API_URL

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
            print(f"✓ {model}: SUCCESS - {data['choices'][0]['message']['content'][:50]}")
            return True
    except httpx.HTTPStatusError as e:
        try:
            error_json = e.response.json()
            error_msg = error_json.get('error', {}).get('message', str(error_json))
            print(f"✗ {model}: FAILED ({e.response.status_code}) - {error_msg}")
        except:
            print(f"✗ {model}: FAILED ({e.response.status_code}) - {e.response.text[:200]}")
        return False
    except Exception as e:
        print(f"✗ {model}: ERROR - {str(e)}")
        return False

async def main():
    """Test multiple model identifiers."""
    print(f"Testing API key: {OPENROUTER_API_KEY[:20]}...")
    print("\nTesting model identifiers:\n")
    
    # Test various model name formats
    test_models = [
        "mistralai/mistral-large",
        "mistralai/mistral-large-latest",
        "mistralai/devstral",
        "mistralai/devstral-latest",
        "thudm/glm-4-5-air",
        "thudm/glm-4.5-air",
        "meta-llama/llama-3.1-8b-instruct:free",  # Known working free model
    ]
    
    results = []
    for model in test_models:
        result = await test_model(model)
        results.append((model, result))
        await asyncio.sleep(0.5)  # Rate limiting
    
    print("\n=== SUMMARY ===")
    working = [m for m, r in results if r]
    failing = [m for m, r in results if not r]
    
    if working:
        print(f"\n✓ Working models ({len(working)}):")
        for m in working:
            print(f"  - {m}")
    
    if failing:
        print(f"\n✗ Failing models ({len(failing)}):")
        for m in failing:
            print(f"  - {m}")

if __name__ == "__main__":
    asyncio.run(main())

