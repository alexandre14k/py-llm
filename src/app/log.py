# src/app/log.py
# ---- code below ----

from app.mod import *


def _ts() -> str:
    import datetime
    return datetime.datetime.now().strftime("%H:%M:%S")


def _fmt(ip: str, event: str, detail: str = "") -> str:
    parts = [f"[{_ts()}]", f"[{ip}]", event]
    if detail:
        parts.append(detail)
    return "  ".join(parts)


class Log:

    @staticmethod
    def connect(ip: str) -> None:
        print(_fmt(ip, "CONNECT", "page loaded"))

    @staticmethod
    def login(ip: str, success: bool) -> None:
        status = "OK" if success else "FAILED"
        print(_fmt(ip, "LOGIN", status))

    @staticmethod
    def logout(ip: str) -> None:
        print(_fmt(ip, "LOGOUT"))

    @staticmethod
    def question(ip: str, q_count: int, message: str) -> None:
        snippet = message[:80].replace("\n", " ")
        if len(message) > 80:
            snippet += "…"
        print(_fmt(ip, f"QUESTION #{q_count}", snippet))

    @staticmethod
    def answer(ip: str, response: str) -> None:
        snippet = response[:80].replace("\n", " ")
        if len(response) > 80:
            snippet += "…"
        print(_fmt(ip, "ANSWER", snippet))

    @staticmethod
    def stream_start(ip: str) -> None:
        print(_fmt(ip, "STREAM", "start"))

    @staticmethod
    def stream_end(ip: str, tokens: int) -> None:
        print(_fmt(ip, "STREAM", f"end  ~{tokens} tokens"))

    @staticmethod
    def llm_load(ip: str) -> None:
        print(_fmt(ip, "LLM", "load requested"))

    @staticmethod
    def llm_unload(ip: str) -> None:
        print(_fmt(ip, "LLM", "unload requested"))

    @staticmethod
    def file_load(ip: str, filename: str, size: int) -> None:
        print(_fmt(ip, "FILE_LOAD", f"{filename}  {size} chars"))

    @staticmethod
    def file_save(ip: str) -> None:
        print(_fmt(ip, "FILE_SAVE"))

    @staticmethod
    def ctx_clear(ip: str) -> None:
        print(_fmt(ip, "CTX_CLEAR"))

    @staticmethod
    def retry(ip: str) -> None:
        print(_fmt(ip, "RETRY"))

    @staticmethod
    def degraded(ip: str, reason: str) -> None:
        print(_fmt(ip, "DEGRADED", reason))

    @staticmethod
    def ctx_tokens(ip: str, used: int, total: int) -> None:
        pct = int(used / total * 100) if total else 0
        print(_fmt(ip, "CTX_TOKENS", f"{used}/{total}  ({pct}%)"))
