from workers import Response
from utils.openai_client import forward_openai_request

async def handle_openai(request, env, path):
    """
    Handle OpenAI proxy requests by forwarding to real OpenAI API with server-side API key.
    
    Client sends request to: /openai/...
    Proxy forwards to: https://api.openai.com/...
    """
    try:
        # Determine if client expects streaming based on Accept header only
        wants_stream = False
        accept_header = request.headers.get("accept", "") or ""
        if "text/event-stream" in accept_header.lower():
            wants_stream = True

        # Forward request to OpenAI with API key injection
        response_body, status_code, response_headers = await forward_openai_request(request, env, path)
        
        # Return the response from OpenAI, preserving headers
        content_type = response_headers.get("content-type", "application/json")
        headers_out = {**response_headers}

        # Streaming passthrough
        if wants_stream and hasattr(response_body, "tee"):
            # response_body is a ReadableStream from fetch; return as-is
            return Response(
                body=response_body,
                status=status_code,
                headers=headers_out
            )

        # Non-streaming: response_body is text
        return Response(
            body=response_body,
            status=status_code,
            headers=headers_out or {"content-type": content_type}
        )
        
    except Exception as e:
        # Return error response
        return Response.json({
            "error": {
                "type": "proxy_error",
                "message": str(e),
                "provider": "openai"
            }
        }, status=500) 