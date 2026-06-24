# src/run.py
# ---- code below ----

import sys as Sys
import os  as Os

Os.chdir(Os.path.dirname(Os.path.abspath(__file__)))
Sys.path.insert(0, Os.path.dirname(Os.path.abspath(__file__)))

from app.mod         import *
from app.init        import Init
from app.service     import Service
from app.error.trace import Trace

app = Service().app


def _lan_ip() -> str:
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main() -> None:
    Init.display()
    ip = _lan_ip()
    print(f"[run] http://{ip}:{Init.PORT}")
    try:
        Uvicorn.run(
            "run:app",
            host        = Init.HOST,
            port        = Init.PORT,
            log_level   = "warning",
            reload      = True,
            reload_dirs = [Os.path.dirname(Os.path.abspath(__file__))],
        )
    except KeyboardInterrupt:
        print("\n[run] exit")
        Sys.exit(0)
    except Exception as exc:
        Trace.print(exc)
        Sys.exit(1)


if __name__ == "__main__":
    main()
