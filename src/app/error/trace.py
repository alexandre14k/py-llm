# src/app/error/trace.py
# ---- code below ----

from app.mod import *


class Trace:

    _root: str = str(Path(Sys.argv[0]).resolve().parent)

    @classmethod
    def _relative(cls, path: str) -> str:
        try:
            return str(Path(path).resolve().relative_to(cls._root))
        except ValueError:
            return path

    @classmethod
    def _format_tb(cls, tb) -> List[str]:
        lines = []
        for frame in Traceback.extract_tb(tb):
            rel = cls._relative(frame.filename)
            col = getattr(frame, "colno", 0) or 0
            lines.append(
                f"  {rel}  line:{frame.lineno}:col:{col}"
                f"  in {frame.name}"
            )
        return lines

    @classmethod
    def capture(cls, exc: Exception) -> str:
        tb     = exc.__traceback__
        frames = cls._format_tb(tb)
        header = f"[{type(exc).__name__}] {exc}"
        body   = "\n".join(frames) if frames else "  (no traceback)"
        return f"{header}\n{body}"

    @classmethod
    def print(cls, exc: Exception) -> None:
        print(cls.capture(exc), file=Sys.stderr)
