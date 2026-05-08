import os
from typing import Optional
try:
    import redis
except Exception:
    redis = None

from app.schemas import ChatSession


class SessionStore:
    """Simple pluggable session store.

    - If `REDIS_URL` is set and `redis` is installed, uses Redis.
    - Otherwise falls back to an in-memory dict (suitable for single-instance demos).
    """

    def __init__(self):
        self._redis_url = os.getenv("REDIS_URL")
        if self._redis_url and redis is not None:
            self._client = redis.from_url(self._redis_url)
            self._use_redis = True
        else:
            self._client = {}
            self._use_redis = False

    def get(self, session_id: str) -> Optional[ChatSession]:
        if not session_id:
            return None
        if self._use_redis:
            data = self._client.get(session_id)
            if not data:
                return None
            # Redis stores bytes; app expects object - leave JSON serialization to future work
            import pickle

            return pickle.loads(data)
        return self._client.get(session_id)

    def save(self, session: ChatSession):
        if self._use_redis:
            import pickle

            self._client.set(session.session_id, pickle.dumps(session))
        else:
            self._client[session.session_id] = session

    def create(self, session: ChatSession):
        self.save(session)
