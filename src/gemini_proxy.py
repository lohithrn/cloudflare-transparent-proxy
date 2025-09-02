from workers import Response

async def handle_gemini(request, env, path):
    # TODO: Add API key handling and upstream call to Google Gemini
    return Response.json({
        "ok": True,
        "provider": "gemini",
        "path": path,
        "message": "Gemini proxy stub"
    }) 