# py-llm
Python based offline LLM web gui with FastAPI

**Python + FastAPI + Uvicorn + Llama-Cpp-Python**

Using an offline large-language-model (llm) we
can interact via python and a web browser.

The llm models used must have a GGUF format.

For this demo we use Google-Gemma-3-1B found at
this huggingface url : [download-link](https://huggingface.co/bartowski/google_gemma-3-1b-it-GGUF/blob/main/google_gemma-3-1b-it-Q4_K_M.gguf)

Some of the use cases may be:
- text generation [chatbot, content creation] 
- summarization [articles, documents, meetings]
- translation [multilingual]
- q&a [context based answering]
- classification [categorize text, topic, tone]
- creative writing [stories, poems, scripts]
- learning tool [tutoring, simple concepts]
- data extraction [parse structured info]
- automation [generate templates, mails, reports]

Focuses on clarity, modularity, and learnability, it is ideal for 
experimenting with Web Gui programming, streaming responses,
and event‑driven architecture.

## Features
- fast prototype with python
- works offline once venv setup in place
- secure access with login password
- dynamic content loading
- load-unload model in ram memory
- minimal accessible web ui display
- toggle raw/markdown text display
- replay last command when available
- load/append text from file
- support display url images
- display markdown syntax as demo content
- save existing context as markdown text file
- allows logging out
- supports model tweaking, stream mode, instructions
- allows markdown code block evaluation 
only for python with **eval** button

## Usage

Script `.\do-py.sh` must be configured for execution `chmod +x do-py.sh`
then call it and follow the menu instructions from top to bottom:
```bash
    m -- fetch the model (done once)
    b -- setup the venv
    s -- install requirements
    r -- run the program
    
    c -- clean the venv
    x -- exit
```

Configure module `./src/app/init.py` and edit some lines like these:
```python
class Init:
    # network
    HOST                = "0.0.0.0"
    PORT                = 12345

    # llm
    LLM_MODEL_NAME      = "google_gemma-3-1b-it-Q4_K_M.gguf"
    ...
    LLM_VERBOSE         = False
    LLM_STREAM          = True

    ...
    # system
    SYSTEM_INSTRUCTIONS = """always answer in french"""
    ...
    SESSION_PASSWORD    = "pass"
```

Minimal debug is enabled by default in low verbose mode:
```python
[run] http://192.168.1.10:12345
[llm] loading data/google_gemma-3-1b-it-Q4_K_M.gguf
llama_context: n_ctx_seq (8192) < n_ctx_train (32768) -- the full capacity of the model will not be utilized
llama_kv_cache_iswa: using full-size SWA cache (ref: https://github.com/ggml-org/llama.cpp/pull/13194#issuecomment-2868343055)
[llm] model ready
[21:36:47]  [192.168.1.10]  CONNECT  page loaded
[21:36:51]  [192.168.1.10]  LOGIN  OK
[21:36:58]  [192.168.1.10]  QUESTION #1  hello
[21:36:58]  [192.168.1.10]  CTX_TOKENS  21/8192  (0%)
[21:36:58]  [192.168.1.10]  STREAM  start
[21:37:00]  [192.168.1.10]  STREAM  end  ~15 tokens
[21:37:00]  [192.168.1.10]  ANSWER  Bonjour ! 😊   Comment puis-je vous aider aujourd'hui ?
[21:37:00]  [192.168.1.10]  CTX_TOKENS  68/8192  (0%)
[21:38:52]  [192.168.1.10]  QUESTION #2  redige 10 phrases de lorem ipsum traduit en français
[21:38:52]  [192.168.1.10]  CTX_TOKENS  68/8192  (0%)
[21:38:52]  [192.168.1.10]  STREAM  start
[21:39:08]  [192.168.1.10]  STREAM  end  ~161 tokens
[21:39:08]  [192.168.1.10]  ANSWER  Okay, here are 10 phrases in Lorem Ipsum translated into French:  1.  Le soleil …
[21:39:08]  [192.168.1.10]  CTX_TOKENS  247/8192  (3%)
[21:39:26]  [192.168.1.10]  CTX_CLEAR
[21:39:30]  [192.168.1.10]  LOGOUT
```

# License
-------
Copyright (c) 2026 alexander14k28@gmail.com

See [LICENSE](LICENSE) for the license governing this project.
