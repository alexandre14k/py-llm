# src/app/web/html.py
# ---- code below ----

from app.mod import *
from app.init import Init
from app.web.css import Css
from app.web.js import Js


class Html:

    @staticmethod
    def page() -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{Init.APP_TITLE}</title>
    <style>{Css.get()}</style>
</head>
<body>
<div id="app">
    <h1>{Init.APP_TITLE}</h1>

    <div id="login-box">
        <input
            id="password-input"
            type="password"
            placeholder="session password"
            autocomplete="current-password"
            onkeydown="if(event.key==='Enter') Login.submit()"
        />
        <button class="btn btn-login" onclick="Login.submit()">login</button>
        <span id="login-error"></span>
    </div>

    <div id="chat-box">
        <div id="output" class="markdown-view"></div>

        <div id="ctx-meter-row">
            <span id="ctx-label">ctx</span>
            <div id="ctx-meter">
                <div id="ctx-meter-fill" style="width:0%"></div>
            </div>
            <span id="ctx-pct">0 %</span>
            <span id="ctx-q">q 0/{Init.LLM_MAX_QUESTIONS}</span>
        </div>

        <div id="status-bar"></div>

        <div id="input-row">
            <textarea
                id="user-input"
                placeholder="message… (Enter send · Shift+Enter newline)"
                rows="2"
            ></textarea>
            <button class="btn btn-retry" id="retry-btn"
                    onclick="Chat.retry()">retry</button>
            <button class="btn btn-send"  id="send-btn"
                    onclick="Chat.send()">send</button>
        </div>

        <div id="output-controls">
            <div class="toggle-row">
                <input type="checkbox" id="raw-toggle" />
                <label for="raw-toggle">raw</label>
            </div>
            <button class="btn btn-demo"   id="demo-btn"
                    onclick="Demo.run()">demo</button>
            <button class="btn btn-load"   id="load-btn"
                    onclick="Ctx.openFile()">load file</button>
            <button class="btn btn-save"   id="save-btn"
                    onclick="Ctx.save()">save chat</button>
            <button class="btn btn-clear"  id="clear-btn"
                    onclick="Ctx.clear()">clear ctx</button>
            <button class="btn btn-llm"    id="llm-btn"
                    data-state="unloaded"
                    onclick="Llm.toggle()">llm ?</button>
            <button class="btn btn-logout" id="logout-btn"
                    onclick="Chat.logout()">logout</button>
        </div>

        <input type="file" id="file-input" accept=".txt,.md,.csv"
               style="display:none" onchange="Ctx.onFile(event)" />
    </div>
</div>
<script>{Js.get()}</script>
</body>
</html>"""
