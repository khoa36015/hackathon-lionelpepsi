
# RAG Museum AI (War Remnants Museum) — Complete Project

A ready-to-run **Retrieval-Augmented Generation (RAG)** API that reads the bilingual training dataset
and answers questions grounded in the JSON content.

## Features
- 🔎 Local embeddings with `sentence-transformers`
- 📚 Retrieval over timeline, artifacts, witnesses, reflections
- 🤖 Generation via **OpenRouter** (set your API key)
- 🌐 Flask API + CORS + simple Web demo (`index.html`)
- 🐳 Docker & docker-compose included

## Project Structure
```
rag_museum_ai/
├── app.py                  # Flask API
├── rag_core.py             # RAG logic: chunk → embed → retrieve
├── data/
│   └── war_remnants_ai_training_v3.json
├── vectorstore/            # auto-generated embeddings
├── index.html              # simple web tester
├── requirements.txt
├── .env.example
├── README.md
├── Dockerfile
└── docker-compose.yml
```

## 1) Local Run
```bash
cd rag_museum_ai
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env → add your OPENROUTER_API_KEY and model if needed
python app.py
```

### Test
```bash
curl -X POST http://localhost:8000/api/ask   -H "Content-Type: application/json"   -d '{"question":"Kể câu chuyện về bức ảnh Em bé Napalm"}'
```

## 2) Docker
```bash
cd rag_museum_ai
docker build -t rag-museum-ai:latest .
docker run -p 8000:8000 --env-file .env rag-museum-ai:latest
```
Or with compose:
```bash
docker-compose up --build
```

## 3) API Endpoints
- `GET /api/health` → model status
- `POST /api/ask` → `{ "question": "...", "top_k": 6, "max_tokens": 500 }`
- `POST /api/reindex` → rebuild embeddings after you edit the dataset

## 4) Environment (.env)
```
OPENROUTER_API_KEY=sk-or-your-key
RAG_LLM_MODEL=openai/gpt-4o-mini
DATASET_PATH=./data/war_remnants_ai_training_v3.json
HOST=0.0.0.0
PORT=8000
```

## 5) Troubleshooting
- If you see: `OPENROUTER_API_KEY is missing` → check `.env`
- Slow first response? It may be building the embedding index (`vectorstore/`).
- Change embedding model: set `EMB_MODEL` env: `sentence-transformers/all-MiniLM-L6-v2` (default).

## 6) Security Notes
- This project avoids political advocacy; answers are grounded in dataset content.
- Consider rate limiting and input size checks for production.

Enjoy!
