# src/app/web/js.py
# ---- code below ----

from app.mod import *


class Js:

    @staticmethod
    def get() -> str:
        return r"""

const Labels = {
    loginBtn:        "login",
    logoutBtn:       "logout",
    sendBtn:         "send",
    retryBtn:        "retry",
    demoBtn:         "demo",
    loadFileBtn:     "load file",
    saveChatBtn:     "save chat",
    clearCtxBtn:     "clear ctx",
    llmLoaded:       "unload llm",
    llmUnloaded:     "load llm",
    llmUnknown:      "llm ?",
    rawLabel:        "raw",
    placeholderPwd:  "session password",
    placeholderMsg:  "message… (Enter send · Shift+Enter newline)",
    statusThinking:  "thinking…",
    statusStreaming: "streaming…",
    statusAuth:      "authenticating…",
    statusLogout:    "logging out…",
    statusLoading:   "loading…",
    statusUnloading: "unloading…",
    statusEvalRun:   "running python…",
    statusEvalDone:  "eval done",
    statusSaved:     "saved ",
    statusFileLoad:  "loaded ",
    statusFileChars: " chars into context",
    statusSelectFile:"select a file…",
    statusCtxClear:  "context cleared",
    statusNoSave:    "nothing to save",
    statusNoRetry:   "no previous prompt",
    statusNetErr:    "network error",
    statusDemoLoad:  "demo loaded",
    statusRawMode:   "raw mode",
    statusMdMode:    "markdown mode",
    degradedMsg:     "degraded mode context — clear chat advised",
    ctxLabel:        "ctx",
    ctxQLabel:       "q ",
    loginRequired:   "password required",
    loginFailed:     "login failed",
    sessionExpired:  "session expired",
};

const State = {
    rawMode:    false,
    history:    [],
    busy:       false,
    streaming:  false,
    qCount:     0,
    ctxUsed:    0,
    ctxTotal:   8192,
    maxQ:       10,
    degraded:   false,
};

const Dom = {
    loginBox:    () => document.getElementById('login-box'),
    chatBox:     () => document.getElementById('chat-box'),
    loginError:  () => document.getElementById('login-error'),
    output:      () => document.getElementById('output'),
    userInput:   () => document.getElementById('user-input'),
    sendBtn:     () => document.getElementById('send-btn'),
    retryBtn:    () => document.getElementById('retry-btn'),
    statusBar:   () => document.getElementById('status-bar'),
    rawToggle:   () => document.getElementById('raw-toggle'),
    passwordIn:  () => document.getElementById('password-input'),
    llmBtn:      () => document.getElementById('llm-btn'),
    ctxFill:     () => document.getElementById('ctx-meter-fill'),
    ctxPct:      () => document.getElementById('ctx-pct'),
    ctxQ:        () => document.getElementById('ctx-q'),
    ctxLabel:    () => document.getElementById('ctx-label'),
};

const IMG_EXTS = ['jpg', 'jpeg', 'png', 'webp', 'svg'];

function _isImgUrl(url) {
    const clean = url.split('?')[0].split('#')[0];
    const ext   = clean.split('.').pop().toLowerCase();
    return IMG_EXTS.includes(ext);
}

function _imgTag(src, alt) {
    return `<a href="${src}" target="_blank" rel="noopener">`
         + `<img src="${src}" alt="${Md.esc(alt)}" `
         + `style="max-width:200px;max-height:200px;`
         + `object-fit:contain;border-radius:4px;`
         + `display:block;margin:0.3rem 0;`
         + `border:1px solid #ccc;background:#fafafa">`
         + `</a>`;
}

const Md = {
    render(raw) {
        const lines = raw.split('\n');
        let html = '';
        let i = 0;

        while (i < lines.length) {
            const line = lines[i];

            // fenced code block
            if (line.trimStart().startsWith('```')) {
                const lang = line.trim().slice(3).trim();
                let code   = '';
                i++;
                while (i < lines.length && !lines[i].trimStart().startsWith('```')) {
                    code += Md.esc(lines[i]) + '\n';
                    i++;
                }
                i++; // closing ```
                const codeEl = '<pre><code'
                    + (lang ? ' class="lang-' + Md.esc(lang) + '"' : '')
                    + '>' + code + '</code></pre>';
                if (lang === 'python') {
                    html += '<div class="code-block">' + codeEl
                          + '<button class="btn-eval"'
                          + ' onclick="Eval.run(this)">&#9654; eval</button>'
                          + '</div>';
                } else {
                    html += codeEl;
                }
                continue;
            }

            // markdown table
            if (line.includes('|') && i + 1 < lines.length
                    && /^[|\s\-:]+$/.test(lines[i + 1])) {
                html += '<table>';
                const headers = Md.tableRow(line);
                html += '<thead><tr>'
                      + headers.map(h => '<th>' + Md.inline(h) + '</th>').join('')
                      + '</tr></thead>';
                i += 2;
                html += '<tbody>';
                while (i < lines.length && lines[i].includes('|')) {
                    const cells = Md.tableRow(lines[i]);
                    html += '<tr>'
                          + cells.map(c => '<td>' + Md.inline(c) + '</td>').join('')
                          + '</tr>';
                    i++;
                }
                html += '</tbody></table>';
                continue;
            }

            const h3 = line.match(/^### (.+)/);
            const h2 = line.match(/^## (.+)/);
            const h1 = line.match(/^# (.+)/);
            if (h3) { html += '<h3>' + Md.inline(h3[1]) + '</h3>'; i++; continue; }
            if (h2) { html += '<h2>' + Md.inline(h2[1]) + '</h2>'; i++; continue; }
            if (h1) { html += '<h1>' + Md.inline(h1[1]) + '</h1>'; i++; continue; }

            if (line.startsWith('> ')) {
                html += '<blockquote>' + Md.inline(line.slice(2)) + '</blockquote>';
                i++; continue;
            }
            if (/^[*-] /.test(line)) {
                html += '<ul>';
                while (i < lines.length && /^[*-] /.test(lines[i])) {
                    html += '<li>' + Md.inline(lines[i].replace(/^[*-] /, '')) + '</li>';
                    i++;
                }
                html += '</ul>';
                continue;
            }
            if (/^\d+\. /.test(line)) {
                html += '<ol>';
                while (i < lines.length && /^\d+\. /.test(lines[i])) {
                    html += '<li>' + Md.inline(lines[i].replace(/^\d+\. /, '')) + '</li>';
                    i++;
                }
                html += '</ol>';
                continue;
            }
            if (/^---+$/.test(line.trim())) { html += '<hr>'; i++; continue; }
            if (line.trim() === '')         { html += '<br>'; i++; continue; }
            html += '<p>' + Md.inline(line) + '</p>';
            i++;
        }
        return html;
    },

    tableRow(line) {
        return line.split('|').map(s => s.trim()).filter(
            (s, idx, arr) =>
                !(idx === 0 && s === '') && !(idx === arr.length - 1 && s === '')
        );
    },

    inline(text) {
        return text
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            .replace(/\*([^*]+)\*/g, '<em>$1</em>')
            .replace(/~~([^~]+)~~/g, '<del>$1</del>')
            // image: ![alt](url) — preview if image ext
            .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (_, alt, src) => {
                if (_isImgUrl(src)) return _imgTag(src, alt);
                return `<img src="${src}" alt="${Md.esc(alt)}" `
                     + `style="max-width:100%">`;
            })
            // link: [label](url) — preview below label if image ext
            .replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, href) => {
                if (_isImgUrl(href)) {
                    return `<a href="${href}" target="_blank" rel="noopener">`
                         + `${Md.esc(label)}`
                         + `<br>${_imgTag(href, label)}</a>`;
                }
                return `<a href="${href}" target="_blank">${Md.esc(label)}</a>`;
            });
    },

    esc(text) {
        return text
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }
};

const Output = {
    append(role, content) {
        State.history.push({ role, content });
        Output.redraw();
    },

    redraw() {
        const el = Dom.output();
        el.innerHTML = '';
        el.classList.toggle('markdown-view', !State.rawMode);

        for (const { role, content } of State.history) {
            const div = document.createElement('div');
            div.className = role === 'user' ? 'msg-user' : 'msg-assistant';
            if (State.rawMode) {
                div.textContent = (role === 'user' ? '> ' : '') + content;
            } else {
                if (role === 'user') {
                    const b = document.createElement('strong');
                    b.textContent = '> ';
                    div.appendChild(b);
                    const span = document.createElement('span');
                    span.innerHTML = Md.inline(content);
                    div.appendChild(span);
                } else {
                    div.innerHTML = Md.render(content);
                }
            }
            el.appendChild(div);
        }
        el.scrollTop = el.scrollHeight;
    },

    startStream() {
        const el  = Dom.output();
        const div = document.createElement('div');
        div.className = 'msg-assistant stream-cursor';
        el.appendChild(div);
        let accumulated = '';

        return {
            push(token) {
                accumulated += token;
                if (State.rawMode) {
                    div.textContent = accumulated;
                } else {
                    div.innerHTML = Md.render(accumulated);
                }
                el.scrollTop = el.scrollHeight;
            },
            finish() {
                div.classList.remove('stream-cursor');
                State.history.push({ role: 'assistant', content: accumulated });
                return accumulated;
            }
        };
    },

    clear() {
        State.history = [];
        Dom.output().innerHTML = '';
    }
};

const Status = {
    set(msg, degraded = false) {
        const bar = Dom.statusBar();
        bar.textContent = msg;
        bar.classList.toggle('degraded', degraded);
    },
    clear() {
        const bar = Dom.statusBar();
        bar.textContent = '';
        bar.classList.remove('degraded');
    }
};

const CtxMeter = {
    update(used, total, qCount, maxQ) {
        State.ctxUsed  = used;
        State.ctxTotal = total;
        State.qCount   = qCount;

        const pct  = total > 0 ? Math.min(100, Math.round(used / total * 100)) : 0;
        const fill = Dom.ctxFill();
        fill.style.width = pct + '%';
        fill.classList.remove('warn', 'crit');
        if (pct >= 95)      fill.classList.add('crit');
        else if (pct >= 80) fill.classList.add('warn');

        Dom.ctxPct().textContent = pct + ' %';
        Dom.ctxQ().textContent   = Labels.ctxQLabel + qCount + '/' + maxQ;
        Dom.ctxLabel().textContent = Labels.ctxLabel;
    },

    async refresh() {
        try {
            const r = await Api.ctxInfo();
            if (!r.ok) return;
            const d = await r.json();
            CtxMeter.update(
                d.tokens_used  || 0,
                d.context_size || 8192,
                d.q_count      || 0,
                d.max_q        || 10,
            );
        } catch (_) {}
    }
};

const Api = {
    async login(password) {
        return fetch('/login', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ password }),
        });
    },
    async chat(message) {
        return fetch('/chat', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ message, history: State.history }),
        });
    },
    async chatStream(message) {
        return fetch('/chat/stream', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ message, history: State.history }),
        });
    },
    async logout()    { return fetch('/logout',     { method: 'POST' }); },
    async history()   { return fetch('/history'); },
    async ctxInfo()   { return fetch('/ctx/info'); },
    async llmLoad()   { return fetch('/llm/load',   { method: 'POST' }); },
    async llmUnload() { return fetch('/llm/unload', { method: 'POST' }); },
    async llmStatus() { return fetch('/llm/status'); },
    async ctxAppend(role, content) {
        return fetch('/context/append', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ role, content }),
        });
    },
    async ctxClear() {
        return fetch('/context/clear', { method: 'POST' });
    },
    async fileSaveNotify(filename, chars) {
        return fetch('/log/file_save', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ filename, chars }),
        }).catch(() => {});
    },
    async retryNotify() {
        return fetch('/log/retry', { method: 'POST' }).catch(() => {});
    },
};

const Llm = {
    async refresh() {
        const btn = Dom.llmBtn();
        try {
            const r = await Api.llmStatus();
            const d = await r.json();
            if (d.ready) {
                btn.textContent   = Labels.llmLoaded;
                btn.dataset.state = 'loaded';
            } else {
                btn.textContent   = Labels.llmUnloaded;
                btn.dataset.state = 'unloaded';
            }
        } catch (_) {
            btn.textContent = Labels.llmUnknown;
        }
    },

    async toggle() {
        const btn = Dom.llmBtn();
        btn.disabled = true;
        const isLoaded = btn.dataset.state === 'loaded';
        Status.set(isLoaded ? Labels.statusUnloading : Labels.statusLoading);
        try {
            const r = isLoaded ? await Api.llmUnload() : await Api.llmLoad();
            const d = await r.json().catch(() => ({}));
            if (!r.ok) Status.set(d.detail || 'error');
            else        Status.clear();
        } catch (_) {
            Status.set(Labels.statusNetErr);
        } finally {
            btn.disabled = false;
            await Llm.refresh();
            await CtxMeter.refresh();
        }
    }
};

const Ctx = {
    openFile() {
        document.getElementById('file-input').value = '';
        document.getElementById('file-input').click();
        Status.set(Labels.statusSelectFile);
    },

    onFile(evt) {
        const file = evt.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = async e => {
            const text   = e.target.result;
            const notice = `[file: ${file.name}]\n${text}`;
            State.history.push({ role: 'user', content: notice });
            await Api.ctxAppend('user', notice);
            Output.redraw();
            Status.set(Labels.statusFileLoad + file.name
                       + ' (' + text.length + ' chars)'
                       + Labels.statusFileChars);
            setTimeout(() => Status.clear(), 3000);
            await CtxMeter.refresh();
        };
        reader.readAsText(file);
    },

    save() {
        if (!State.history.length) {
            Status.set(Labels.statusNoSave);
            setTimeout(() => Status.clear(), 2000);
            return;
        }
        let md = '';
        for (const { role, content } of State.history) {
            if (role === 'user')           md += `**>** ${content}\n\n`;
            else if (role === 'assistant') md += `${content}\n\n---\n\n`;
        }
        const blob  = new Blob([md.trim()], { type: 'text/markdown' });
        const url   = URL.createObjectURL(blob);
        const a     = document.createElement('a');
        const fname = `chat-${new Date().toISOString()
                        .slice(0, 19).replace(/:/g, '-')}.md`;
        a.href     = url;
        a.download = fname;
        a.click();
        URL.revokeObjectURL(url);
        Api.fileSaveNotify(fname, md.length);
        Status.set(Labels.statusSaved + fname);
        setTimeout(() => Status.clear(), 3000);
    },

    async clear() {
        if (!State.history.length) return;
        State.history    = [];
        State.degraded   = false;
        Dom.output().innerHTML = '';
        await Api.ctxClear();
        Status.clear();
        Status.set(Labels.statusCtxClear);
        setTimeout(() => Status.clear(), 2000);
        await CtxMeter.refresh();
    }
};

const Eval = {
    async run(btn) {
        const pre  = btn.previousElementSibling;
        const code = pre ? (pre.querySelector('code') || pre).innerText : '';
        if (!code.trim()) return;
        btn.disabled    = true;
        btn.textContent = '⏳ running…';
        Status.set(Labels.statusEvalRun);
        try {
            const r = await fetch('/eval', {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify({ code }),
            });
            const d = await r.json();
            if (r.ok) {
                const out = d.output ?? '(no output)';
                for (let i = State.history.length - 1; i >= 0; i--) {
                    if (State.history[i].role === 'assistant') {
                        State.history[i].content +=
                            '\n\n**Output:**\n```\n' + out + '\n```';
                        break;
                    }
                }
                Output.redraw();
                Status.set(Labels.statusEvalDone);
                setTimeout(() => Status.clear(), 2000);
            } else {
                Status.set('eval error: ' + (d.detail || r.status));
                btn.disabled    = false;
                btn.textContent = '&#9654; eval';
            }
        } catch (_) {
            Status.set(Labels.statusNetErr);
            btn.disabled    = false;
            btn.textContent = '&#9654; eval';
        }
    }
};

const Demo = {
    PROMPT: "display markdown syntax cheatsheet",

    RESPONSE: [
        "# Markdown Cheatsheet",
        "",
        "## Headings",
        "# H1  ## H2  ### H3",
        "",
        "## Emphasis",
        "**bold**  *italic*  ~~strikethrough~~",
        "",
        "## Lists",
        "Unordered:",
        "* Item A",
        "* Item B",
        "",
        "Ordered:",
        "1. First",
        "2. Second",
        "",
        "## Code",
        "Inline: `const x = 42;`",
        "",
        "Block:",
        "```python",
        "def greet(name):",
        "    return f\"Hello, {name}!\"",
        "",
        "print(greet(\"world\"))",
        "```",
        "",
        "## Links & Images",
        "[OpenAI](https://openai.com)",
        "![Sample](https://via.placeholder.com/200x80?text=Image)",
        "",
        "## Blockquote",
        "> This is a blockquote.",
        "",
        "## Table",
        "| Syntax      | Description |",
        "|-------------|-------------|",
        "| `**text**`  | Bold        |",
        "| `*text*`    | Italic      |",
        "",
        "## Horizontal Rule",
        "---",
        "End of cheatsheet.",
    ].join("\n"),

    run() {
        Output.append("user",      Demo.PROMPT);
        Output.append("assistant", Demo.RESPONSE);
        Status.set(Labels.statusDemoLoad);
        setTimeout(() => Status.clear(), 2000);
    }
};

function checkDegraded(d) {
    if (d && d.degraded) {
        State.degraded = true;
        Status.set(Labels.degradedMsg, true);
        return true;
    }
    return false;
}

const Login = {
    async submit() {
        const pw  = Dom.passwordIn().value.trim();
        const err = Dom.loginError();
        err.textContent = '';
        if (!pw) { err.textContent = Labels.loginRequired; return; }
        Status.set(Labels.statusAuth);
        try {
            const r = await Api.login(pw);
            if (r.ok) {
                Dom.loginBox().style.display = 'none';
                Dom.chatBox().style.display  = 'flex';
                Status.clear();
                await Llm.refresh();
                await Chat.loadHistory();
                await CtxMeter.refresh();
            } else {
                const d = await r.json().catch(() => ({}));
                err.textContent = d.detail || Labels.loginFailed;
                Status.clear();
            }
        } catch (_) {
            err.textContent = Labels.statusNetErr;
            Status.clear();
        }
    }
};

const Chat = {

    _lockUI(locked) {
        State.busy              = locked;
        Dom.sendBtn().disabled  = locked;
        Dom.retryBtn().disabled = locked;
    },

    async send() {
        if (State.busy) return;
        const input = Dom.userInput();
        const msg   = input.value.trim();
        if (!msg) return;

        input.value = '';
        Chat._lockUI(true);

        if (State.degraded) {
            Status.set(Labels.degradedMsg, true);
            Chat._lockUI(false);
            return;
        }

        State.history.push({ role: 'user', content: msg });
        Output.redraw();

        await Chat._sendStream(msg);
    },

    async _sendStream(msg) {
        Status.set(Labels.statusStreaming);
        try {
            const r = await Api.chatStream(msg);
            if (r.status === 401) { Chat.handleUnauth(); return; }
            if (!r.ok) {
                const d = await r.json().catch(() => ({}));
                if (d.degraded) {
                    Status.set(Labels.degradedMsg, true);
                    State.degraded = true;
                } else {
                    Status.set('error: ' + (d.detail || r.status));
                }
                State.history.pop();
                Output.redraw();
                return;
            }

            const streamer = Output.startStream();
            const reader   = r.body.getReader();
            const decoder  = new TextDecoder();
            let done    = false;
            let pending = '';

            while (!done) {
                const { value, done: doneFlag } = await reader.read();
                done = doneFlag;
                if (value) {
                    pending += decoder.decode(value, { stream: true });
                    const events = pending.split('\n\n');
                    pending = events.pop() ?? '';
                    for (const evt of events) {
                        const lines = evt.split('\n');
                        const parts = lines
                            .filter(l => l.startsWith('data: '))
                            .map(l => l.slice(6));
                        const token = parts.join('\n');
                        if (token === '[DONE]') { done = true; break; }
                        if (token.startsWith('[ERROR]')) {
                            Status.set('llm error: ' + token.slice(8));
                            done = true; break;
                        }
                        streamer.push(token);
                    }
                }
            }

            streamer.finish();
        } catch (_) {
            Status.set(Labels.statusNetErr);
            State.history.pop();
            Output.redraw();
        } finally {
            Chat._lockUI(false);
            await CtxMeter.refresh();
            if (!State.degraded) Status.clear();
        }
    },

    async _sendPlain(msg) {
        Status.set(Labels.statusThinking);
        try {
            const r = await Api.chat(msg);
            if (r.status === 401) { Chat.handleUnauth(); return; }
            const d = await r.json();
            if (r.ok) {
                Output.append('assistant', d.response);
                if (!checkDegraded(d)) Status.clear();
            } else {
                if (d.degraded) {
                    Status.set(Labels.degradedMsg, true);
                    State.degraded = true;
                } else {
                    Status.set('error: ' + (d.detail || r.status));
                }
                State.history.pop();
                Output.redraw();
            }
        } catch (_) {
            Status.set(Labels.statusNetErr);
            State.history.pop();
            Output.redraw();
        } finally {
            Chat._lockUI(false);
            await CtxMeter.refresh();
        }
    },

    async loadHistory() {
        try {
            const r = await Api.history();
            if (!r.ok) return;
            const d = await r.json();
            if (Array.isArray(d.history)) {
                State.history = d.history;
                Output.redraw();
            }
        } catch (_) {}
    },

    retry() {
        const last = [...State.history].reverse()
                         .find(h => h.role === 'user');
        if (!last) {
            Status.set(Labels.statusNoRetry);
            setTimeout(() => Status.clear(), 2000);
            return;
        }
        Api.retryNotify();
        if (State.history.length
                && State.history[State.history.length - 1].role === 'assistant') {
            State.history.pop();
        }
        if (State.history.length
                && State.history[State.history.length - 1].role === 'user') {
            State.history.pop();
        }
        Output.redraw();
        Dom.userInput().value = last.content;
        Chat.send();
    },

    handleUnauth() {
        Chat._lockUI(false);
        Dom.chatBox().style.display  = 'none';
        Dom.loginBox().style.display = 'flex';
        Dom.loginError().textContent = Labels.sessionExpired;
        Status.clear();
    },

    async logout() {
        Status.set(Labels.statusLogout);
        await Api.logout();
        Output.clear();
        State.degraded = false;
        State.qCount   = 0;
        State.ctxUsed  = 0;
        Dom.chatBox().style.display  = 'none';
        Dom.loginBox().style.display = 'flex';
        Dom.passwordIn().value = '';
        CtxMeter.update(0, State.ctxTotal, 0, State.maxQ);
        Status.clear();
    }
};

document.addEventListener('DOMContentLoaded', async () => {
    Dom.llmBtn().textContent    = Labels.llmUnknown;
    document.querySelector('label[for="raw-toggle"]').textContent = Labels.rawLabel;
    document.getElementById('logout-btn').textContent  = Labels.logoutBtn;
    document.getElementById('send-btn').textContent    = Labels.sendBtn;
    document.getElementById('retry-btn').textContent   = Labels.retryBtn;
    document.getElementById('demo-btn').textContent    = Labels.demoBtn;
    document.getElementById('load-btn').textContent    = Labels.loadFileBtn;
    document.getElementById('save-btn').textContent    = Labels.saveChatBtn;
    document.getElementById('clear-btn').textContent   = Labels.clearCtxBtn;
    Dom.passwordIn().placeholder = Labels.placeholderPwd;
    Dom.userInput().placeholder  = Labels.placeholderMsg;
    document.querySelector('#login-box .btn-login').textContent = Labels.loginBtn;

    try {
        const r = await Api.history();
        if (r.ok) {
            const d = await r.json();
            Dom.loginBox().style.display = 'none';
            Dom.chatBox().style.display  = 'flex';
            await Llm.refresh();
            await CtxMeter.refresh();
            if (Array.isArray(d.history)) {
                State.history = d.history;
                Output.redraw();
            }
        }
    } catch (_) {}

    Dom.rawToggle().addEventListener('change', () => {
        State.rawMode = Dom.rawToggle().checked;
        Output.redraw();
        Status.set(State.rawMode ? Labels.statusRawMode : Labels.statusMdMode);
        setTimeout(() => Status.clear(), 1500);
    });

    Dom.userInput().addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            Chat.send();
        }
    });
});
"""
