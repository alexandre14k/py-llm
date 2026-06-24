# src/app/error/status.py
# ---- code below ----

from app.mod import *


class Status:

    @staticmethod
    def unauthorized() -> str:
        return "401 Unauthorized: invalid credentials"

    @staticmethod
    def forbidden(ip: str) -> str:
        return f"403 Forbidden: access denied for {ip}"

    @staticmethod
    def not_found(path: str) -> str:
        return f"404 Not Found: {path}"

    @staticmethod
    def conflict(detail: str) -> str:
        return f"409 Conflict: {detail}"

    @staticmethod
    def internal(detail: str) -> str:
        return f"500 Internal Server Error: {detail}"

    @staticmethod
    def llm_not_ready() -> str:
        return "503 Service Unavailable: LLM not loaded"

    @staticmethod
    def llm_inference_failed(detail: str) -> str:
        return f"500 LLM Inference Failed: {detail}"

    @staticmethod
    def session_expired() -> str:
        return "440 Session Expired: please log in again"

    @staticmethod
    def bad_request(detail: str) -> str:
        return f"400 Bad Request: {detail}"
