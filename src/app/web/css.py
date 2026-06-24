# src/app/web/css.py
# ---- code below ----

from app.mod import *


class Css:

    @staticmethod
    def get() -> str:
        return """
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    background-color: #808080;
    font-family: system-ui, -apple-system, sans-serif;
    font-size: 1rem;
    color: #111;
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: 100vh;
    padding: 1rem;
}

#app {
    background-color: #f5f5f5;
    width: 100%;
    max-width: 1200px;
    border-radius: 6px;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

h1 {
    font-size: 1.2rem;
    font-weight: 600;
    color: #222;
    text-align: center;
}

/* login */
#login-box {
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
    max-width: 320px;
    margin: 0 auto;
}

#login-box input {
    padding: 0.4rem 0.6rem;
    border: 1px solid #aaa;
    border-radius: 4px;
    font: inherit;
    background: #fff;
}

#login-error {
    color: #b00;
    font-size: 0.85rem;
}

/* chat */
#chat-box {
    display: none;
    flex-direction: column;
    gap: 0.8rem;
}

/* toolbar — row on wide, wrapping column on mobile */
#output-controls {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
}

#output-controls .toggle-row {
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

/* on narrow screens stack buttons vertically */
@media (max-width: 768px) {
    #app {
        max-width: 100%;
        border-radius: 0;
        padding: 0.8rem;
    }

    #output-controls {
        flex-direction: column;
        align-items: stretch;
    }

    #output-controls .toggle-row {
        justify-content: center;
    }

    .btn {
        width: 100%;
        text-align: center;
        padding: 0.55rem 0.8rem;
    }

    #input-row {
        flex-direction: column;
    }

    #input-row .btn {
        width: 100%;
    }
}

#output-controls label {
    cursor: pointer;
    user-select: none;
}

#output {
    background: #fff;
    border: 1px solid #bbb;
    border-radius: 4px;
    padding: 0.8rem;
    min-height: 320px;
    max-height: 560px;
    overflow-y: auto;
    font-size: 0.92rem;
    line-height: 1.6;
    white-space: pre-wrap;
    word-break: break-word;
}

#output.markdown-view { white-space: normal; }

#output .msg-user {
    margin-bottom: 0.6rem;
    padding: 0.4rem 0.6rem;
    background: #e8e8e8;
    border-radius: 4px;
    font-weight: 500;
}

#output .msg-assistant {
    margin-bottom: 0.8rem;
    padding: 0.4rem 0.6rem;
}

/* streaming cursor */
#output .stream-cursor::after {
    content: "▋";
    animation: blink 0.7s step-end infinite;
}
@keyframes blink { 50% { opacity: 0; } }

/* markdown rendered */
#output h1,#output h2,#output h3 {
    margin: 0.4rem 0 0.2rem;
    font-weight: 600;
}
#output code {
    background: #e2e2e2;
    padding: 0.1rem 0.3rem;
    border-radius: 3px;
    font-size: 0.88em;
}
#output pre {
    background: #e2e2e2;
    padding: 0.6rem;
    border-radius: 4px;
    overflow-x: auto;
    margin: 0.4rem 0;
}
#output pre code { background: none; padding: 0; }
#output ul,#output ol { padding-left: 1.4rem; }
#output blockquote {
    border-left: 3px solid #aaa;
    padding-left: 0.6rem;
    color: #555;
}

.code-block { margin: 0.4rem 0; }
.code-block pre { margin: 0; }
.btn-eval {
    margin-top: 0.2rem;
    font-size: 0.75rem;
    padding: 0.15rem 0.5rem;
    background: #3a6a8a;
    color: #fff;
    border: none;
    border-radius: 3px;
    cursor: pointer;
    font-family: inherit;
}
.btn-eval:hover    { background: #2a5a7a; }
.btn-eval:disabled { background: #999; cursor: not-allowed; }

#input-row {
    display: flex;
    gap: 0.5rem;
}

#user-input {
    flex: 1;
    padding: 0.4rem 0.6rem;
    border: 1px solid #aaa;
    border-radius: 4px;
    font: inherit;
    resize: vertical;
    min-height: 2.4rem;
    background: #fff;
}

.btn {
    padding: 0.35rem 0.9rem;
    border: none;
    border-radius: 4px;
    font: inherit;
    font-size: 0.82rem;
    cursor: pointer;
    transition: background 0.15s;
    white-space: nowrap;
}
.btn:disabled { background: #999 !important; cursor: not-allowed; }

.btn-login   { background: #444; color: #fff; font-size: 1rem;
               padding: 0.4rem 1rem; }
.btn-login:hover { background: #222; }

.btn-send    { background: #444; color: #fff; font-size: 1rem;
               padding: 0.4rem 1rem; }
.btn-send:hover  { background: #222; }

.btn-logout  { background: #777; color: #fff; }
.btn-logout:hover { background: #555; }

.btn-demo    { background: #4a6a8a; color: #fff; }
.btn-demo:hover { background: #2a4a6a; }

.btn-load    { background: #6a5a8a; color: #fff; }
.btn-load:hover { background: #4a3a6a; }

.btn-save    { background: #4a7a6a; color: #fff; }
.btn-save:hover { background: #2a5a4a; }

.btn-clear   { background: #8a6a3a; color: #fff; }
.btn-clear:hover { background: #6a4a2a; }

.btn-retry   { background: #6a6a4a; color: #fff; }
.btn-retry:hover { background: #4a4a2a; }

.btn-llm     { background: #5a7a5a; color: #fff; }
.btn-llm:hover { background: #3a5a3a; }
.btn-llm[data-state="unloaded"] { background: #7a5a5a; }
.btn-llm[data-state="unloaded"]:hover { background: #5a3a3a; }

/* table */
#output table {
    border-collapse: collapse;
    width: 100%;
    margin: 0.5rem 0;
    font-size: 0.9rem;
}
#output th, #output td {
    border: 1px solid #bbb;
    padding: 0.3rem 0.6rem;
    text-align: left;
}
#output th { background: #e0e0e0; font-weight: 600; }
#output hr { border: none; border-top: 1px solid #bbb; margin: 0.6rem 0; }
#output img { max-width: 100%; border-radius: 4px; margin: 0.4rem 0; }
#output a { color: #2255aa; }

/* status bar */
#status-bar {
    font-size: 0.78rem;
    color: #555;
    min-height: 1rem;
}
#status-bar.degraded {
    color: #b05000;
    font-weight: 600;
}

/* token meter */
#ctx-meter-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.75rem;
    color: #555;
}
#ctx-meter {
    flex: 1;
    height: 6px;
    background: #ddd;
    border-radius: 3px;
    overflow: hidden;
}
#ctx-meter-fill {
    height: 100%;
    background: #5a7a5a;
    transition: width 0.4s, background 0.4s;
    border-radius: 3px;
}
#ctx-meter-fill.warn  { background: #c08020; }
#ctx-meter-fill.crit  { background: #b03020; }
"""
