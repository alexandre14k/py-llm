# src/app/security.py
# ---- code below ----

from app.mod import *
from app.error.status import Status
from app.error.trace  import Trace


class SessionStore:
    """In-memory session store keyed by token."""

    def __init__(self) -> None:
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = Threading.Lock()

    def _now(self) -> float:
        return Time.time()

    def _expired(self, session: Dict[str, Any]) -> bool:
        return self._now() - session["created"] > Init.SESSION_TTL_SECONDS

    def _token(self, ip: str) -> str:
        raw = f"{ip}:{Uuid.uuid4()}:{self._now()}"
        return Hashlib.sha256(raw.encode()).hexdigest()

    def create(self, ip: str) -> str:
        token = self._token(ip)
        with self._lock:
            self._sessions[token] = {
                "ip":         ip,
                "created":    self._now(),
                "history":    [],
                "q_count":    0,
            }
        return token

    def get(self, token: str, ip: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            session = self._sessions.get(token)
            if session is None:
                return None
            if session["ip"] != ip:
                return None
            if self._expired(session):
                del self._sessions[token]
                return None
            return session

    def delete(self, token: str) -> None:
        with self._lock:
            self._sessions.pop(token, None)

    def get_history(self, token: str, ip: str) -> List[Dict[str, Any]]:
        session = self.get(token, ip)
        if session is None:
            return []
        return session["history"]

    def get_q_count(self, token: str, ip: str) -> int:
        session = self.get(token, ip)
        if session is None:
            return 0
        return session.get("q_count", 0)

    def append_history(
        self,
        token:   str,
        ip:      str,
        role:    str,
        content: str,
    ) -> bool:
        with self._lock:
            session = self._sessions.get(token)
            if session is None or session["ip"] != ip:
                return False
            session["history"].append({"role": role, "content": content})
            if role == "user":
                session["q_count"] = session.get("q_count", 0) + 1
            return True

    def clear_history(self, token: str) -> None:
        with self._lock:
            s = self._sessions.get(token)
            if s:
                s["history"]  = []
                s["q_count"]  = 0


class Security:
    """Auth facade used by service layer."""

    _store = SessionStore()

    @staticmethod
    def _hash(password: str) -> str:
        return Hashlib.sha256(password.encode()).hexdigest()

    @classmethod
    def _check_password(cls, password: str) -> bool:
        return cls._hash(password) == cls._hash(Init.SESSION_PASSWORD)

    @staticmethod
    def get_ip(request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    @classmethod
    def login(cls, request: Request, password: str) -> Optional[str]:
        try:
            if not cls._check_password(password):
                return None
            ip    = cls.get_ip(request)
            token = cls._store.create(ip)
            return token
        except Exception as exc:
            Trace.print(exc)
            return None

    @classmethod
    def validate(cls, request: Request) -> Optional[Dict[str, Any]]:
        token = request.cookies.get(Init.SESSION_COOKIE_NAME)
        if not token:
            return None
        ip = cls.get_ip(request)
        return cls._store.get(token, ip)

    @classmethod
    def logout(cls, request: Request) -> None:
        token = request.cookies.get(Init.SESSION_COOKIE_NAME)
        if token:
            cls._store.delete(token)

    @classmethod
    def get_history(cls, request: Request) -> List[Dict[str, Any]]:
        token = request.cookies.get(Init.SESSION_COOKIE_NAME)
        if not token:
            return []
        return cls._store.get_history(token, cls.get_ip(request))

    @classmethod
    def get_q_count(cls, request: Request) -> int:
        token = request.cookies.get(Init.SESSION_COOKIE_NAME)
        if not token:
            return 0
        return cls._store.get_q_count(token, cls.get_ip(request))

    @classmethod
    def append_history(
        cls,
        request: Request,
        role:    str,
        content: str,
    ) -> bool:
        token = request.cookies.get(Init.SESSION_COOKIE_NAME)
        if not token:
            return False
        return cls._store.append_history(
            token, cls.get_ip(request), role, content
        )

    @classmethod
    def clear_history(cls, request: Request) -> None:
        token = request.cookies.get(Init.SESSION_COOKIE_NAME)
        if not token:
            return
        cls._store.clear_history(token)

    @staticmethod
    def set_cookie(response: Response, token: str) -> None:
        response.set_cookie(
            key      = Init.SESSION_COOKIE_NAME,
            value    = token,
            httponly = True,
            samesite = "strict",
            max_age  = Init.SESSION_TTL_SECONDS,
        )

    @staticmethod
    def clear_cookie(response: Response) -> None:
        response.delete_cookie(key=Init.SESSION_COOKIE_NAME)
