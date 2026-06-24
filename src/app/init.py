# src/app/init.py
# ---- code below ----

class Init:
    # network
    HOST                = "0.0.0.0"
    PORT                = 12345

    # llm
    LLM_MODEL_NAME      = "google_gemma-3-1b-it-Q4_K_M.gguf"
    LLM_MODEL_PATH      = f"data/{LLM_MODEL_NAME}"
    LLM_AUTOLOAD        = True
    LLM_CONTEXT_SIZE    = 8192 # less KV cache pressure
    LLM_MAX_TOKENS      = 512
    LLM_TEMPERATURE     = 0.7
    LLM_TOP_P           = 0.95
    LLM_THREADS         = 2   # physical cores only
    LLM_GPU_LAYERS      = 0   # cpu only no supported gpu
    LLM_BATCH_SIZE      = 256 # smaller fits cache better 
    LLM_VERBOSE         = False
    LLM_STREAM          = True

    # context limits
    LLM_MAX_QUESTIONS   = 10          # max user turns per session
    LLM_CTX_WARN_PCT    = 0.85        # warn at 85 % token usage

    # system
    SYSTEM_INSTRUCTIONS = """always answer in french"""

    # session
    SESSION_COOKIE_NAME = "llm_session"
    SESSION_TTL_SECONDS = 3600
    SESSION_PASSWORD    = "pass"

    # app
    APP_TITLE           = "py-llm"
    APP_VERSION         = "1.0.0"

    @classmethod
    def display(cls) -> None:
        pairs = [
            ("HOST",                cls.HOST),
            ("PORT",                cls.PORT),
            ("LLM_AUTOLOAD",        cls.LLM_AUTOLOAD),
            ("LLM_MODEL_NAME",      cls.LLM_MODEL_NAME),
            ("LLM_MODEL_PATH",      cls.LLM_MODEL_PATH),
            ("LLM_CONTEXT_SIZE",    cls.LLM_CONTEXT_SIZE),
            ("LLM_MAX_TOKENS",      cls.LLM_MAX_TOKENS),
            ("LLM_TEMPERATURE",     cls.LLM_TEMPERATURE),
            ("LLM_TOP_P",           cls.LLM_TOP_P),
            ("LLM_VERBOSE",         cls.LLM_VERBOSE),
            ("LLM_STREAM",          cls.LLM_STREAM),
            ("LLM_MAX_QUESTIONS",   cls.LLM_MAX_QUESTIONS),
            ("LLM_CTX_WARN_PCT",    cls.LLM_CTX_WARN_PCT),
            ("SESSION_COOKIE_NAME", cls.SESSION_COOKIE_NAME),
            ("SESSION_TTL_SECONDS", cls.SESSION_TTL_SECONDS),
            ("SESSION_PASSWORD",    cls.SESSION_PASSWORD),
            ("SYSTEM_INSTRUCTIONS", cls.SYSTEM_INSTRUCTIONS),
            ("APP_TITLE",           cls.APP_TITLE),
            ("APP_VERSION",         cls.APP_VERSION),
        ]
        print("=== Init Config ===")
        for k, v in pairs:
            print(f"  {k:<22} {v}")
        print("===================")
