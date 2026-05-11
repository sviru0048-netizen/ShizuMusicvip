# --------------------------------------------------------------------------------
# KRISH X STAR CODER Branding
# --------------------------------------------------------------------------------

import asyncio
import importlib
import os
import re
import sys
import threading
import time

import requests
from flask import Flask
from pyrogram import idle
from pyrogram.types import BotCommand

import config
from ShizuMusic import LOGGER, assistant, bot, call_py
from ShizuMusic.modules import ALL_MODULES

ASSISTANT_USERNAME: str = ""

_flask = Flask(__name__)

@_flask.route("/")
def _home():
    return "❍ KRISH X STAR CODER Music Bot is running 💕", 200

@_flask.route("/health")
def _health():
    return "OK", 200

def _run_flask() -> None:
    _flask.run(host="0.0.0.0", port=config.PORT, use_reloader=False)

def _keep_alive() -> None:
    url = os.getenv("RENDER_EXTERNAL_URL", f"http://0.0.0.0:{config.PORT}")
    while True:
        try:
            requests.get(url, timeout=10)
            LOGGER.info(f"Keep-alive ping sent → {url}")
        except Exception as e:
            LOGGER.warning(f"Keep-alive ping failed: {e}")
        time.sleep(300)

async def _notify_owner(me, assistant_username: str) -> None:
    if not config.LOGGER_ID:
        return
    try:
        await bot.send_message(
            config.LOGGER_ID,
            f"🎵 KRISH X STAR CODER Bot Started 💕\n\n"
            f"❍ Bot : @{me.username}\n"
            f"❍ Assistant : @{assistant_username}",
        )
    except Exception as e:
        LOGGER.warning(f"Logger Notification Error : {e}")
