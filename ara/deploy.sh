#!/bin/bash
set -e

host="notedwin@192.168.0.75"

# ssh "${host}" "sudo apt update && sudo apt install tmux neovim libpq5 -y"

scp .env "${host}":~/.env
scp main.py "${host}":~/main.py
scp pyproject.toml "${host}":~/pyproject.toml

ssh "${host}" "echo '@reboot /usr/bin/tmux new-session -d -s notedwin \"cd /home/notedwin/ && uv run /home/notedwin/main.py\"' | crontab -"
# uv pip install aranet4 psycopg python-dotenv
# beszel command from webui

# connect to aranet4
# sudo bluetoothctl
# > scan on
# > pair $MAC
# > scan off

