from .http_client import make_request
import json
import os

OPENAI_BASE_URL = "https://api.openai.com"

async def forward_openai_request(request, env, path, stream=False):
    """
    Forward a request to OpenAI API with server-side API key injection.
    
    Args:
        request: Original client request
        env: Worker environment (contains secrets)
        path: Request path (e.g., "/openai/v1/chat/completions")
        stream: If True, request upstream with streaming body response
    
    Returns:
        Tuple of (response_body, status_code, response_headers)
    """
    target_domain = "api.openai.com"
    prefix = "/openai/"
    target_path = path[len(prefix):] if path.startswith(prefix) else path.lstrip("/")

    # Hardcoded API key
    api_key = env.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": request.headers.get("content-type", "application/json"),
        "User-Agent": "ai-proxy-worker/1.0",
    }

    method = getattr(request, "method", "POST")

    body = None
    if method.upper() != "GET":
        # Try to forward JSON body; fallback to raw text
        try:
            body = await request.json()
        except Exception:
            try:
                body = await request.text()
            except Exception:
                body = None

    response_body, status_code, response_headers = await make_request(
        domain=target_domain,
        path=target_path,
        method=method,
        headers=headers,
        body=body,
        stream=bool(stream),
    )
    return response_body, status_code, response_headers
