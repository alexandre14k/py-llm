# src/app/llm.py
# ---- code below ----

from app.mod import *
from app.error.status import Status
from app.error.trace  import Trace


class LlmService:

    _instance: Optional["LlmService"] = None
    _lock = Threading.Lock()

    def __init__(self) -> None:
        self._model:        Optional[Llama] = None
        self._ready:        bool            = False
        self._tokens_used:  int             = 0

    @classmethod
    def get(cls) -> "LlmService":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def load(self, model_path: str) -> None:
        if self._ready:
            return
        print(f"[llm] loading {model_path}")
        try:
            self._model = Llama(
                model_path   = model_path,
                n_ctx        = Init.LLM_CONTEXT_SIZE,
                n_threads    = Init.LLM_THREADS,
                n_gpu_layers = Init.LLM_GPU_LAYERS,
                n_batch      = Init.LLM_BATCH_SIZE,
                use_mmap     = True,
                flash_attn   = True,
                verbose      = Init.LLM_VERBOSE,
            )
            self._ready      = True
            self._tokens_used = 0
            print("[llm] model ready")
        except Exception as exc:
            Trace.print(exc)
            raise RuntimeError(Status.internal(str(exc)))

    @property
    def ready(self) -> bool:
        return self._ready

    @property
    def tokens_used(self) -> int:
        return self._tokens_used

    @property
    def context_size(self) -> int:
        return Init.LLM_CONTEXT_SIZE

    def _build_messages(
        self,
        history: List[Dict[str, Any]],
        message: str,
    ) -> List[Dict[str, str]]:
        raw: List[Dict[str, str]] = []
        for entry in history:
            role    = entry.get("role", "")
            content = entry.get("content", "").strip()
            if role in ("user", "assistant") and content:
                raw.append({"role": role, "content": content})

        merged: List[Dict[str, str]] = []
        for turn in raw:
            if merged and merged[-1]["role"] == turn["role"]:
                # collapse into previous turn with a separator
                merged[-1]["content"] += "\n" + turn["content"]
            else:
                merged.append(dict(turn))

        if merged and merged[-1]["role"] == "user":
            if merged[-1]["content"].strip() == message.strip():
                merged.pop()
            elif merged[-1]["role"] == "user":
                merged[-1]["content"] += "\n" + message
                message = ""   # sentinel: already included

        messages: List[Dict[str, str]] = []
        if Init.SYSTEM_INSTRUCTIONS:
            messages.append({
                "role":    "system",
                "content": Init.SYSTEM_INSTRUCTIONS,
            })
        messages.extend(merged)
        if message:
            messages.append({"role": "user", "content": message})
        return messages

    def _extract_text(self, output: Dict[str, Any]) -> str:
        try:
            return output["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError):
            return ""

    def _update_token_count(self, output: Dict[str, Any]) -> None:
        try:
            usage = output.get("usage", {})
            self._tokens_used = usage.get("total_tokens", self._tokens_used)
        except Exception:
            pass

    def chat(
        self,
        message: str,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        if not self._ready or self._model is None:
            raise RuntimeError(Status.llm_not_ready())

        messages = self._build_messages(history or [], message)
        try:
            output = self._model.create_chat_completion(
                messages    = messages,
                max_tokens  = Init.LLM_MAX_TOKENS,
                temperature = Init.LLM_TEMPERATURE,
                top_p       = Init.LLM_TOP_P,
                stream      = False,
            )
            self._update_token_count(output)
            return self._extract_text(output)
        except Exception as exc:
            Trace.print(exc)
            raise RuntimeError(Status.llm_inference_failed(str(exc)))

    async def chat_stream(
        self,
        message: str,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> AsyncGenerator[str, None]:
        if not self._ready or self._model is None:
            raise RuntimeError(Status.llm_not_ready())

        messages = self._build_messages(history or [], message)
        try:
            stream = self._model.create_chat_completion(
                messages    = messages,
                max_tokens  = Init.LLM_MAX_TOKENS,
                temperature = Init.LLM_TEMPERATURE,
                top_p       = Init.LLM_TOP_P,
                stream      = True,
            )
            token_count = 0
            for chunk in stream:
                delta = (
                    chunk.get("choices", [{}])[0]
                        .get("delta", {})
                        .get("content", "")
                )
                if delta:
                    token_count += 1
                    yield delta
            # approximate token tracking for stream
            self._tokens_used += token_count
        except Exception as exc:
            Trace.print(exc)
            raise RuntimeError(Status.llm_inference_failed(str(exc)))

    def unload(self) -> None:
        with self._lock:
            if self._model is not None:
                try:
                    self._model.close()
                except Exception:
                    pass
                del self._model
                self._model = None
            self._ready      = False
            self._tokens_used = 0
        import gc
        gc.collect()
        try:
            import ctypes
            ctypes.CDLL("libc.so.6").malloc_trim(0)
        except Exception:
            pass
        print("[llm] model unloaded")
