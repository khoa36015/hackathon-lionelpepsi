\
import os, json, numpy as np, re
from typing import List, Dict, Any
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

VECTOR_DIR = os.environ.get("VECTOR_DIR", "./vectorstore")
DATASET_PATH = os.environ.get("DATASET_PATH", "./data/war_remnants_ai_training_v3.json")
EMB_MODEL = os.environ.get("EMB_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

@dataclass
class Chunk:
    text: str
    meta: Dict[str, Any]

def _normalize_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def load_dataset(path=DATASET_PATH) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def make_chunks(data: Dict[str, Any], max_chars: int = 800) -> List[Chunk]:
    chunks: List[Chunk] = []

    # historical_timeline
    for tl in data.get("historical_timeline", []):
        for key in ("narrative_vi","narrative_en"):
            if tl.get(key):
                txt = _normalize_ws(tl[key])
                for i in range(0, len(txt), max_chars):
                    piece = txt[i:i+max_chars]
                    chunks.append(Chunk(piece, {"section": "timeline", "title_vi": tl.get("title_vi"), "title_en": tl.get("title_en")}))

    # extended_artifacts
    for art in data.get("extended_artifacts", []):
        for field in ("paragraphs_vi","paragraphs_en"):
            for p in art.get(field, []):
                txt = _normalize_ws(p)
                for i in range(0, len(txt), max_chars):
                    piece = txt[i:i+max_chars]
                    chunks.append(Chunk(piece, {"section": "artifact", "name_vi": art.get("name_vi"), "name_en": art.get("name_en")}))

    # witness_accounts
    for wit in data.get("witness_accounts", []):
        for key in ("account_vi","account_en"):
            if wit.get(key):
                txt = _normalize_ws(wit[key])
                for i in range(0, len(txt), max_chars):
                    piece = txt[i:i+max_chars]
                    chunks.append(Chunk(piece, {"section": "witness", "role_vi": wit.get("role_vi"), "role_en": wit.get("role_en")}))

    # peace_reflection
    pr = data.get("peace_reflection", {})
    for key in ("vi","en"):
        if pr.get(key):
            txt = _normalize_ws(pr[key])
            for i in range(0, len(txt), max_chars):
                piece = txt[i:i+max_chars]
                chunks.append(Chunk(piece, {"section": "reflection"}))

    return chunks

def build_index(chunks: List[Chunk]):
    os.makedirs(VECTOR_DIR, exist_ok=True)
    model = SentenceTransformer(EMB_MODEL)
    texts = [c.text for c in chunks]
    embs = model.encode(texts, convert_to_numpy=True, show_progress_bar=False, normalize_embeddings=True)
    np.save(os.path.join(VECTOR_DIR, "embeddings.npy"), embs)
    with open(os.path.join(VECTOR_DIR, "texts.jsonl"), "w", encoding="utf-8") as fw:
        for c in chunks:
            fw.write(json.dumps({"text": c.text, "meta": c.meta}, ensure_ascii=False) + "\n")

def load_index():
    emb_path = os.path.join(VECTOR_DIR, "embeddings.npy")
    txt_path = os.path.join(VECTOR_DIR, "texts.jsonl")
    if not (os.path.exists(emb_path) and os.path.exists(txt_path)):
        return None, None
    embs = np.load(emb_path)
    rows = []
    with open(txt_path, "r", encoding="utf-8") as fr:
        for line in fr:
            rows.append(json.loads(line))
    return embs, rows

def ensure_index():
    embs, rows = load_index()
    if embs is not None:
        return embs, rows
    data = load_dataset()
    chunks = make_chunks(data)
    build_index(chunks)
    return load_index()

def retrieve(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    embs, rows = ensure_index()
    model = SentenceTransformer(EMB_MODEL)
    q_emb = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    sims = cosine_similarity(q_emb, embs)[0]
    idxs = np.argsort(-sims)[:top_k]
    results = []
    for rank, i in enumerate(idxs, start=1):
        item = rows[int(i)]
        item["score"] = float(sims[int(i)])
        item["rank"] = rank
        results.append(item)
    return results
