from __future__ import annotations
import asyncio
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from app.core.config import settings


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(settings.MODEL_NAME, cache_folder=settings.MODEL_CACHE_DIR)


async def embed_text(text: str) -> list[float]:
    loop = asyncio.get_event_loop()
    model = _get_model()
    embedding = await loop.run_in_executor(None, lambda: model.encode(text, normalize_embeddings=True))
    return embedding.tolist()


async def embed_batch(texts: list[str]) -> list[list[float]]:
    loop = asyncio.get_event_loop()
    model = _get_model()
    embeddings = await loop.run_in_executor(
        None,
        lambda: model.encode(texts, normalize_embeddings=True, batch_size=32)
    )
    return [e.tolist() for e in embeddings]
