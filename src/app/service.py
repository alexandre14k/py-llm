# src/app/service.py
# ---- code below ----

from contextlib       import asynccontextmanager
from app.mod          import *
from app.security     import Security
from app.llm          import LlmService
from app.web.html     import Html
from app.error.status import Status
from app.error.trace  import Trace
from app.log          import Log

import asyncio


@asynccontextmanager
async def _lifespan(app):
    if Init.LLM_AUTOLOAD:
        llm = LlmService.get()
        if not llm.ready:
            llm.load(Init.LLM_MODEL_PATH)
    yield


class PythonEval:
    TIMEOUT = 10

    @staticmethod
    def run(code: str) -> str:
        try:
            r = Subprocess.run(
                [Sys.executable, "-c", code],
                capture_output = True,
                text           = True,
                timeout        = PythonEval.TIMEOUT,
            )
            out = r.stdout.strip()
            err = r.stderr.strip()
            if out and err:
                return out + "\n[stderr]\n" + err
            return out or err or "(no output)"
        except Subprocess.TimeoutExpired:
            return f"[timeout after {PythonEval.TIMEOUT}s]"
        except Exception as exc:
            return f"[error: {exc}]"


def _degraded_check(request: Request) -> Optional[Dict[str, Any]]:
    """Return degraded info dict or None."""
    llm     = LlmService.get()
    q_count = Security.get_q_count(request)
    ctx_sz  = llm.context_size

    if q_count >= Init.LLM_MAX_QUESTIONS:
        ip = Security.get_ip(request)
        Log.degraded(ip, f"max questions reached: {q_count}")
        return {"degraded": True, "reason": "max_questions"}

    if ctx_sz > 0:
        hist       = Security.get_history(request)
        sys_chars  = len(Init.SYSTEM_INSTRUCTIONS)
        hist_chars = sum(len(e.get("content", "")) for e in hist)
        estimated  = (sys_chars + hist_chars) // 4 + (len(hist) + 1) * 16
        if estimated / ctx_sz >= Init.LLM_CTX_WARN_PCT:
            ip = Security.get_ip(request)
            Log.degraded(ip, f"token estimate: {estimated}/{ctx_sz}")
            return {"degraded": True, "reason": "token_limit"}

    return None


def _estimate_tokens(request: Request) -> int:
    """Char-based token estimate for the current session."""
    hist       = Security.get_history(request)
    sys_chars  = len(Init.SYSTEM_INSTRUCTIONS)
    hist_chars = sum(len(e.get("content", "")) for e in hist)
    return (sys_chars + hist_chars) // 4 + (len(hist) + 1) * 16


class Service:

    def __init__(self) -> None:
        self._app = FastAPI.FastAPI(title=Init.APP_TITLE, lifespan=_lifespan)
        self._register_routes()

    @property
    def app(self) -> FastAPI.FastAPI:
        return self._app

    def _guard(self, request: Request) -> Optional[Dict[str, Any]]:
        return Security.validate(request)

    def _register_routes(self) -> None:
        app = self._app

        @app.get("/", response_class=HTMLResponse)
        async def index(request: Request):
            ip = Security.get_ip(request)
            Log.connect(ip)
            return Html.page()

        @app.post("/login")
        async def login(request: Request):
            ip = Security.get_ip(request)
            try:
                body     = await request.json()
                password = body.get("password", "")
                if not password:
                    Log.login(ip, False)
                    return JSONResponse(
                        {"detail": Status.bad_request("password missing")},
                        status_code=400,
                    )
                token = Security.login(request, password)
                if token is None:
                    Log.login(ip, False)
                    return JSONResponse(
                        {"detail": Status.unauthorized()},
                        status_code=401,
                    )
                Log.login(ip, True)
                response = JSONResponse({"ok": True})
                Security.set_cookie(response, token)
                return response
            except Exception as exc:
                Trace.print(exc)
                return JSONResponse(
                    {"detail": Status.internal(str(exc))},
                    status_code=500,
                )

        @app.post("/logout")
        async def logout(request: Request):
            ip = Security.get_ip(request)
            Log.logout(ip)
            Security.logout(request)
            response = JSONResponse({"ok": True})
            Security.clear_cookie(response)
            return response

        @app.get("/history")
        async def history(request: Request):
            if self._guard(request) is None:
                return JSONResponse(
                    {"detail": Status.unauthorized()}, status_code=401)
            hist = Security.get_history(request)
            return JSONResponse({"history": hist})

        @app.get("/ctx/info")
        async def ctx_info(request: Request):
            if self._guard(request) is None:
                return JSONResponse(
                    {"detail": Status.unauthorized()}, status_code=401)
            llm  = LlmService.get()
            hist = Security.get_history(request)
            sys_chars  = len(Init.SYSTEM_INSTRUCTIONS)
            hist_chars = sum(len(e.get("content", "")) for e in hist)
            msg_overhead = (len(hist) + 1) * 16
            estimated    = (sys_chars + hist_chars) // 4 + msg_overhead
            return JSONResponse({
                "tokens_used":  estimated,
                "context_size": llm.context_size,
                "q_count":      Security.get_q_count(request),
                "max_q":        Init.LLM_MAX_QUESTIONS,
            })

        @app.post("/chat")
        async def chat(request: Request):
            if self._guard(request) is None:
                return JSONResponse(
                    {"detail": Status.unauthorized()}, status_code=401)

            llm = LlmService.get()
            if not llm.ready:
                return JSONResponse(
                    {"detail": "model not loaded — click 'load llm' first"},
                    status_code=503,
                )

            deg = _degraded_check(request)
            if deg:
                return JSONResponse(
                    {"detail": Labels.degradedMsg, "degraded": True},
                    status_code=200,
                )

            try:
                body    = await request.json()
                message = body.get("message", "").strip()
                if not message:
                    return JSONResponse(
                        {"detail": Status.bad_request("message empty")},
                        status_code=400,
                    )
                ip      = Security.get_ip(request)
                q_count = Security.get_q_count(request) + 1
                Log.question(ip, q_count, message)
                Log.ctx_tokens(ip, _estimate_tokens(request), llm.context_size)

                history = Security.get_history(request)
                reply   = llm.chat(message, history)

                Security.append_history(request, "user",      message)
                Security.append_history(request, "assistant", reply)

                Log.answer(ip, reply)
                Log.ctx_tokens(ip, _estimate_tokens(request), llm.context_size)

                return JSONResponse({"response": reply})
            except RuntimeError as exc:
                Trace.print(exc)
                return JSONResponse({"detail": str(exc)}, status_code=500)
            except Exception as exc:
                Trace.print(exc)
                return JSONResponse(
                    {"detail": Status.internal(str(exc))}, status_code=500)

        @app.post("/chat/stream")
        async def chat_stream(request: Request):
            if self._guard(request) is None:
                return JSONResponse(
                    {"detail": Status.unauthorized()}, status_code=401)

            llm = LlmService.get()
            if not llm.ready:
                return JSONResponse(
                    {"detail": "model not loaded — click 'load llm' first"},
                    status_code=503,
                )

            deg = _degraded_check(request)
            if deg:
                return JSONResponse(
                    {"detail": Labels.degradedMsg, "degraded": True},
                    status_code=200,
                )

            try:
                body    = await request.json()
                message = body.get("message", "").strip()
                if not message:
                    return JSONResponse(
                        {"detail": Status.bad_request("message empty")},
                        status_code=400,
                    )

                ip      = Security.get_ip(request)
                q_count = Security.get_q_count(request) + 1
                Log.question(ip, q_count, message)
                Log.ctx_tokens(ip, _estimate_tokens(request), llm.context_size)
                history = Security.get_history(request)

                Log.stream_start(ip)

                accumulated: List[str] = []

                async def event_gen() -> AsyncGenerator[bytes, None]:
                    try:
                        async for token in llm.chat_stream(message, history):
                            accumulated.append(token)
                            safe = token.replace("\n", "\ndata: ")
                            yield f"data: {safe}\n\n".encode()
                        yield b"data: [DONE]\n\n"
                    except Exception as exc:
                        Trace.print(exc)
                        err_msg = str(exc).replace("\n", " ")
                        yield f"data: [ERROR] {err_msg}\n\n".encode()
                    finally:
                        full_reply = "".join(accumulated)
                        Security.append_history(request, "user",      message)
                        Security.append_history(request, "assistant", full_reply)
                        Log.stream_end(ip, len(accumulated))
                        Log.answer(ip, full_reply)
                        Log.ctx_tokens(ip, _estimate_tokens(request), llm.context_size)

                return StreamingResponse(
                    event_gen(),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control":  "no-cache",
                        "X-Accel-Buffering": "no",
                    },
                )
            except Exception as exc:
                Trace.print(exc)
                return JSONResponse(
                    {"detail": Status.internal(str(exc))}, status_code=500)

        @app.get("/llm/status")
        async def llm_status(request: Request):
            if self._guard(request) is None:
                return JSONResponse(
                    {"detail": Status.unauthorized()}, status_code=401)
            return JSONResponse({"ready": LlmService.get().ready})

        @app.post("/llm/load")
        async def llm_load(request: Request):
            if self._guard(request) is None:
                return JSONResponse(
                    {"detail": Status.unauthorized()}, status_code=401)
            ip = Security.get_ip(request)
            Log.llm_load(ip)
            try:
                LlmService.get().load(Init.LLM_MODEL_PATH)
                return JSONResponse({"ok": True})
            except Exception as exc:
                Trace.print(exc)
                return JSONResponse(
                    {"detail": Status.internal(str(exc))}, status_code=500)

        @app.post("/llm/unload")
        async def llm_unload(request: Request):
            if self._guard(request) is None:
                return JSONResponse(
                    {"detail": Status.unauthorized()}, status_code=401)
            ip = Security.get_ip(request)
            Log.llm_unload(ip)
            LlmService.get().unload()
            return JSONResponse({"ok": True})

        @app.post("/context/append")
        async def context_append(request: Request):
            if self._guard(request) is None:
                return JSONResponse(
                    {"detail": Status.unauthorized()}, status_code=401)
            try:
                body    = await request.json()
                role    = body.get("role", "user")
                content = body.get("content", "")
                if not content:
                    return JSONResponse(
                        {"detail": Status.bad_request("content empty")},
                        status_code=400)
                ip = Security.get_ip(request)

                if content.startswith("[file:"):
                    line = content.split("\n")[0]
                    fname = line[7:line.index("]")] if "]" in line else "?"
                    Log.file_load(ip, fname, len(content))
                Security.append_history(request, role, content)
                return JSONResponse({"ok": True})
            except Exception as exc:
                Trace.print(exc)
                return JSONResponse(
                    {"detail": Status.internal(str(exc))}, status_code=500)

        @app.post("/context/clear")
        async def context_clear(request: Request):
            if self._guard(request) is None:
                return JSONResponse(
                    {"detail": Status.unauthorized()}, status_code=401)
            ip = Security.get_ip(request)
            Log.ctx_clear(ip)
            Security.clear_history(request)
            return JSONResponse({"ok": True})

        @app.post("/log/file_save")
        async def log_file_save(request: Request):
            if self._guard(request) is None:
                return JSONResponse(
                    {"detail": Status.unauthorized()}, status_code=401)
            ip = Security.get_ip(request)
            Log.file_save(ip)
            return JSONResponse({"ok": True})

        @app.post("/log/retry")
        async def log_retry(request: Request):
            if self._guard(request) is None:
                return JSONResponse(
                    {"detail": Status.unauthorized()}, status_code=401)
            ip = Security.get_ip(request)
            Log.retry(ip)
            return JSONResponse({"ok": True})

        @app.post("/eval")
        async def eval_code(request: Request):
            if self._guard(request) is None:
                return JSONResponse(
                    {"detail": Status.unauthorized()}, status_code=401)
            try:
                body = await request.json()
                code = body.get("code", "").strip()
                if not code:
                    return JSONResponse(
                        {"detail": Status.bad_request("code empty")},
                        status_code=400)
                output = PythonEval.run(code)
                return JSONResponse({"output": output})
            except Exception as exc:
                Trace.print(exc)
                return JSONResponse(
                    {"detail": Status.internal(str(exc))}, status_code=500)


class Labels:
    degradedMsg = "degraded mode context — clear chat advised"
