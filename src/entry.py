from workers import WorkerEntrypoint, Response
import re
from urllib.parse import urlparse
from openai_proxy import handle_openai
from bedrock_proxy import handle_bedrock
from gemini_proxy import handle_gemini

# Match /openai, /bedrock, /gemini with optional extra segments (e.g., /openai/chat)
_PROVIDER_ROUTE = re.compile(r"^/(openai|bedrock|gemini)(?:/.*)?$")

_PROVIDER_HANDLERS = {
    "openai": handle_openai,
    "bedrock": handle_bedrock,
    "gemini": handle_gemini,
}

class Default(WorkerEntrypoint):
    async def on_fetch(self, request, env, ctx):
        return await self.fetch(request)

    async def fetch(self, request):
        path = urlparse(request.url).path
        match = _PROVIDER_ROUTE.match(path)
        if match:
            provider = match.group(1)
            handler = _PROVIDER_HANDLERS.get(provider)
            if handler is not None:
                return await handler(request, self.env, path)

        return Response.json({
            "ok": True,
            "service": "ai-proxy-worker",
            "message": "Hello from Python Workers"
        })
