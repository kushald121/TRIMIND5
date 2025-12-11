"""OpenRouter API client for making LLM requests."""

import httpx
from typing import List, Dict, Any, Optional
from .config import OPENROUTER_API_KEY, OPENROUTER_API_URL


async def query_model(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """
    Query a single model via OpenRouter API.

    Args:
        model: OpenRouter model identifier (e.g., "openai/gpt-4o")
        messages: List of message dicts with 'role' and 'content'
        timeout: Request timeout in seconds

    Returns:
        Response dict with 'content' and optional 'reasoning_details', or None if failed
    """
    print(f"DEBUG: Querying model {model} with {len(messages)} messages")
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 1000,  # Limit tokens to stay within credit limits (6666 available)
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            data = response.json()
            message = data['choices'][0]['message']

            return {
                'content': message.get('content'),
                'reasoning_details': message.get('reasoning_details')
            }

    except httpx.HTTPStatusError as e:
        try:
            error_text = e.response.text
            error_json = e.response.json() if e.response.headers.get('content-type', '').startswith('application/json') else None
            if error_json:
                error_msg = error_json.get('error', {}).get('message', str(error_json))
                print(f"HTTP error querying model {model}: {e.response.status_code} - {error_msg}")
            else:
                print(f"HTTP error querying model {model}: {e.response.status_code} - {error_text[:500]}")
        except:
            print(f"HTTP error querying model {model}: {e.response.status_code} - {str(e)}")
        return None
    except httpx.RequestError as e:
        print(f"Network error querying model {model}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error querying model {model}: {e}")
        return None


async def query_models_parallel(
    models: List[str],
    messages: List[Dict[str, str]]
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Query multiple models in parallel.

    Args:
        models: List of OpenRouter model identifiers
        messages: List of message dicts to send to each model

    Returns:
        Dict mapping model identifier to response dict (or None if failed)
    """
    import asyncio

    # Create tasks for all models
    tasks = [query_model(model, messages) for model in models]

    # Wait for all to complete
    responses = await asyncio.gather(*tasks)

    # Map models to their responses
    return {model: response for model, response in zip(models, responses)}
