import asyncio
from backend.config import COUNCIL_MODELS, CHAIRMAN_MODEL
from backend.openrouter import query_model

async def test_council_models():
    """Test the specific models used in the LLM Council."""
    messages = [
        {"role": "user", "content": "Say hello world"}
    ]
    
    print("Testing Council Models...")
    print(f"Council Models: {COUNCIL_MODELS}")
    print(f"Chairman Model: {CHAIRMAN_MODEL}")
    print()
    
    # Test council models
    for model in COUNCIL_MODELS:
        print(f"Testing council model: {model}")
        response = await query_model(model, messages, timeout=30.0)
        if response is None:
            print(f"❌ {model}: Failed")
        else:
            content = response.get('content', '')[:50]
            print(f"✅ {model}: {content}...")
    
    print()
    print(f"Testing chairman model: {CHAIRMAN_MODEL}")
    response = await query_model(CHAIRMAN_MODEL, messages, timeout=30.0)
    if response is None:
        print(f"❌ {CHAIRMAN_MODEL}: Failed")
    else:
        content = response.get('content', '')[:50]
        print(f"✅ {CHAIRMAN_MODEL}: {content}...")

if __name__ == "__main__":
    asyncio.run(test_council_models())