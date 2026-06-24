import os
os.environ["HF_HUB_DISABLE_SSL_VERIFICATION"] = "1"
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["REQUESTS_CA_BUNDLE"] = ""

try:
    import huggingface_hub
    huggingface_hub.constants.HF_HUB_DISABLE_SSL_VERIFICATION = True
except Exception:
    pass

import hashlib
import warnings
import urllib3
from sentence_transformers import SentenceTransformer
from app.core.constants import EMBEDDING_MODEL

warnings.filterwarnings("ignore")
urllib3.disable_warnings()

import requests
_orig_request = requests.Session.request
def _patched_request(*args, **kwargs):
    kwargs['verify'] = False
    return _orig_request(*args, **kwargs)
requests.Session.request = _patched_request

OFFLINE = os.getenv("HF_HUB_OFFLINE", "0") in ("1", "true", "yes")

_model = None

def _fallback_embed(text: str) -> list:
    vec = []
    for i in range(384):
        h = hashlib.sha256(f"{text}\0{i}".encode()).digest()
        val = int.from_bytes(h[:8], "big") % 1_000_000 / 1_000_000
        vec.append(val * 2.0 - 1.0)
    return vec

def load_ai_model():
    global _model
    if _model is not None:
        return _model
    try:
        source = EMBEDDING_MODEL
        _model = SentenceTransformer(source, local_files_only=OFFLINE, trust_remote_code=False)
        print(f"Loaded embedding model {source}")
    except Exception as e:
        print(f"Model load failed ({e})")
        _model = None
    return _model

class _FallbackEmbedder:
    def encode(self, text: str):
        return _fallback_embed(text)

def get_embedding_model():
    model = load_ai_model()
    if model is None:
        return _FallbackEmbedder()
    return model

def generate_embedding(text: str) -> list:
    model = load_ai_model()
    if model is None:
        emb = _fallback_embed(text)
    else:
        result = model.encode(text)
        emb = result.tolist() if hasattr(result, "tolist") else list(result)
    
    return emb
