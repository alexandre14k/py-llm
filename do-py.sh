#!/bin/bash

SCR=$0
APP="$(basename $(pwd))"
SRC="src"
RUN="run.py"
ENV="env"
DATA="data"
REQ="spec.md"

do_model() {
    set -e

    url1="https://huggingface.co/bartowski/"
    url2="google_gemma-3-1b-it-GGUF/resolve/main"
    model="google_gemma-3-1b-it-Q4_K_M.gguf"
    
    URL="$url1$url2"
    DST="src/data"

    wget -c "$URL/$model" -O "$DST/$model"

    echo "done -> $DST"
}

do_run() {
    echo "${FUNCNAME[0]}"
    if do_env; then
        if [[ -f "$SRC/$RUN" ]]; then
            cd "$SRC"
            python3 -B "$RUN"
            cd ..
        else
            echo "no $SRC/$RUN"
        fi
    fi
}

do_env() {
    if [[ -f "$ENV/bin/activate" ]]; then
        echo "${FUNCNAME[0]}"
        source $ENV/bin/activate
        return 0
    else
        no_env
        return 1
    fi
}

do_build() {
    echo "${FUNCNAME[0]}"
    python3 -B -m venv $ENV
}

do_setup() {
    echo "${FUNCNAME[0]}"
    if do_env; then
        if curl -s --head https://pypi.org > /dev/null 2>&1; then
            # pip install -qqq --upgrade pip setuptools wheel
            pip install -r $REQ -q
        fi
    fi
}

do_clean() {
    echo "${FUNCNAME[0]}"
    if [[ -d "$ENV" ]]; then
        rm -rf $ENV
    fi
}

no_env() {
    echo "${FUNCNAME[0]}"
}

do_default() {
    do_clear_screen
    do_menu
}

do_clear_screen() {
    clear
}

do_menu() {
    cat <<EOF
    # app <$APP>

    m -- fetch the model (done once)
    b -- setup the venv
    s -- install requirements
    r -- run the program
    
    c -- clean the venv
    x -- exit
EOF
}

do_input() {
    read -p '>>> ' value
    echo "$value"
}

do_main() {
    do_default
    while true; do
        value=$(do_input)

        case "$value" in
            r) do_run;;
            s) do_setup;;
            b) do_build;;
            c) do_clean;;
            m) do_model;;
            x) break;;
            *) do_default;;
        esac
    done
}

do_start() {
    if [ -t 0 ]; then
        do_main
    else
        title="$APP"
        xfce4-terminal\
            --title="$title"\
            -e "bash -c '$SCR $@; exec bash'"
    fi
}

do_start
