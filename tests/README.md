# AI Proxy Worker Tests

This directory contains test scripts for the AI proxy worker, organized by language.

## Prerequisites

1. Set your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY='your-actual-openai-api-key-here'
   ```

2. Start the local proxy server:
   ```bash
   ./run_local.sh
   ```
   This will start the proxy at `http://127.0.0.1:8787` and automatically use your API key

## Python Tests

Located in `tests/python/`

### Running Python Tests

```bash
cd tests/python
pip install -U openai
python open_ai_python_test.py
```

## JavaScript Tests

Located in `tests/javascript/` with isolated Node.js dependencies.

### Running JavaScript Tests

```bash
cd tests/javascript
npm install
npm run test:openai
```

Or run directly:
```bash
cd tests/javascript
npm install
node open_ai_test.js "Your custom prompt here"
```

## How It Works

Both test scripts are configured to:
- Connect to the localhost proxy at `http://127.0.0.1:8787/openai/v1`
- Use a dummy API key (the proxy injects the real one)
- Use the standard OpenAI chat completions API format
- Handle errors gracefully with helpful messages 