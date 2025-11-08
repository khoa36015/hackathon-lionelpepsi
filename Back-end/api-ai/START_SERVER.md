# 🚀 How to Start the AI API Server

## Prerequisites

1. Make sure you have Python installed
2. Make sure you have installed dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Make sure you have a `.env` file with your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_key_here
   RAG_LLM_MODEL=openai/gpt-4o-mini
   HOST=0.0.0.0
   PORT=8000
   ```

## Starting the Server

### Option 1: Direct Python
```bash
cd Back-end/api-ai
python app.py
```

You should see:
```
🚀 Running on http://0.0.0.0:8000
```

### Option 2: With Auto-reload (Development)
```bash
cd Back-end/api-ai
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows CMD
$env:FLASK_ENV="development"  # Windows PowerShell

python app.py
```

## Testing the Server

### Test 1: Health Check
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{"status":"ok","model":"openai/gpt-4o-mini"}
```

### Test 2: Ask Endpoint (with message)
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"message": "Trực thăng UH-1 Huey là gì?"}'
```

### Test 3: Run Test Suite
```bash
cd Back-end/api-ai
python test_api.py
```

## Troubleshooting

### Issue: "Failed to fetch" from frontend

**Solution 1: Restart the server**
1. Stop the server (Ctrl+C)
2. Start it again: `python app.py`
3. Wait for "🚀 Running on http://0.0.0.0:8000"

**Solution 2: Check if port 8000 is already in use**
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

If something else is using port 8000, either:
- Kill that process
- Change the PORT in `.env` file

**Solution 3: Check firewall**
- Make sure Windows Firewall allows connections on port 8000
- Try accessing http://localhost:8000/api/health in your browser

**Solution 4: Check CORS**
- The server should show CORS headers in the response
- Run the test suite: `python test_api.py`

### Issue: "OPENROUTER_API_KEY not set"

Create a `.env` file in `Back-end/api-ai/` with:
```
OPENROUTER_API_KEY=your_actual_key_here
```

### Issue: Server starts but requests fail

1. Check the server logs for errors
2. Run the test suite: `python test_api.py`
3. Check if the vectorstore is initialized:
   ```bash
   ls -la vectorstore/
   ```
   If empty, run:
   ```bash
   curl -X POST http://localhost:8000/api/reindex
   ```

## Server Logs

When the server is running correctly, you should see:
```
🚀 Running on http://0.0.0.0:8000
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8000
```

When a request comes in, you should see:
```
127.0.0.1 - - [DATE] "POST /api/ask HTTP/1.1" 200 -
```

## Quick Checklist

Before testing the frontend:
- [ ] AI API server is running on port 8000
- [ ] Health check returns 200 OK
- [ ] Test suite passes all tests
- [ ] Frontend is running on port 5173
- [ ] Backend API is running on port 3000

## Need Help?

Run the test suite to diagnose issues:
```bash
python test_api.py
```

This will test:
- ✅ Health endpoint
- ✅ CORS headers
- ✅ Ask endpoint with 'message' field
- ✅ Ask endpoint with 'question' field

