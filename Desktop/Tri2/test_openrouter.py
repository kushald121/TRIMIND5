import asyncio
from backend.openrouter import query_model

async def test_openrouter():
    """Test if OpenRouter API is working with a simple query."""
    messages = [
        {"role": "user", "content": "Say hello world"}
    ]
    
    print("Testing OpenRouter API...")
    response = await query_model("meta-llama/llama-3.1-8b-instruct:free", messages, timeout=30.0)
    
    if response is None:
        print("❌ Failed to get response from OpenRouter API")
        return False
    
    content = response.get('content', '')
    print(f"✅ Success! Response: {content}")
    return True

if __name__ == "__main__":
    asyncio.run(test_openrouter())