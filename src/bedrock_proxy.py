from workers import Response

async def handle_bedrock(request, env, path):
    # TODO: Add API key handling and upstream call to AWS Bedrock
    return Response.json({
        "ok": True,
        "provider": "bedrock",
        "path": path,
        "message": "Bedrock proxy stub"
    }) 