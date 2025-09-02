import os
import json
import traceback

# Try Cloudflare Workers fetch (correct way for Python Workers)
HAS_WORKERS_FETCH = False
try:
    from pyodide.ffi import to_js as _to_js
    from js import Object, fetch
    
    def to_js(obj):
        return _to_js(obj, dict_converter=Object.fromEntries)
    
    HAS_WORKERS_FETCH = True
    print("DEBUG: Using Cloudflare Workers fetch (js)")
except:
    print("DEBUG: Workers fetch not available, will use requests fallback")
    HAS_WORKERS_FETCH = False


async def make_request(domain: str, path: str, method: str = "POST", headers=None, body=None, stream: bool = False) -> tuple:
    try:
        headers = dict(headers or {})
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        url = f"https://{domain}/{path.lstrip('/')}"
        method_upper = (method or "POST").upper()

        print("HTTP Request →", method_upper, url, path, domain, headers, body, stream)

        if HAS_WORKERS_FETCH:
            # Use Cloudflare Workers fetch (correct syntax)
            try:
                # Prepare options object
                fetch_options = {
                    "method": method_upper,
                    "headers": headers,
                }
                
                if method_upper != "GET" and body is not None:
                    if isinstance(body, (dict, list)):
                        fetch_options["body"] = json.dumps(body)
                    else:
                        fetch_options["body"] = str(body)

                print("REQUEST", url, fetch_options)
                print("DEBUG: Calling Cloudflare Workers fetch with to_js")
                
                # Use correct syntax: fetch(url, to_js(options))
                response = await fetch(url, to_js(fetch_options))
                print("DEBUG: fetch returned successfully, status:", response.status)
                
                response_text = await response.text()
                status_code = response.status
                
                # Convert headers to dict
                response_headers = {}
                try:
                    if hasattr(response, 'headers'):
                        # Handle JS headers object
                        for key in response.headers.keys():
                            response_headers[key] = response.headers.get(key)
                except:
                    response_headers = {}

                print("RESPONSE", status_code, response_text)
                print("HTTP", status_code)
                
                if status_code != 200:
                    print("Response body:", response_text)
                    if status_code == 401:
                        print("Got 401 Unauthorized — OpenAI did not receive a valid Authorization header.")

                return response_text, status_code, response_headers
                
            except Exception as e:
                print("ERROR: Exception in workers fetch:", e)
                traceback.print_exc()
                return str(e), 500, {}
        else:
            # Use requests fallback for local testing
            try:
                import requests
                print("DEBUG: Using requests fallback")
                
                payload = body if isinstance(body, dict) else json.loads(body) if isinstance(body, str) else {}
                
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                print("DEBUG: requests returned, status:", response.status_code)
                
                response_text = response.text
                status_code = response.status_code
                response_headers = dict(response.headers)

                print("RESPONSE", status_code, response_text)
                print("HTTP", status_code)
                
                if status_code != 200:
                    print("Response body:", response_text)
                    if status_code == 401:
                        print("Got 401 Unauthorized — OpenAI did not receive a valid Authorization header.")

                return response_text, status_code, response_headers
                
            except Exception as e:
                print("ERROR: Exception in requests fallback:", e)
                traceback.print_exc()
                return str(e), 500, {}

    except Exception as e:
        print("ERROR: Exception in make_request_internal():", e)
        traceback.print_exc()
        return str(e), 500, {}


if __name__ == "__main__":
    try:
        API_KEY = os.getenv("OPENAI_API_KEY")
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        body = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Say hi from moodys"}], "max_tokens": 20}
        import asyncio
        print(asyncio.run(make_request_internal("api.openai.com", "v1/chat/completions", "POST", headers, body)))
    except Exception as e:
        print("ERROR: Exception in __main__:", e)
        traceback.print_exc()



