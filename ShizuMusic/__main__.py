"""
ShizuMusic/__main__.py
Entry point — starts Flask health server, assistant, bot, and PyTgCalls.
"""
import asyncio
import importlib
import os
import re
import sys
import threading
import time
from collections import deque

from flask import Flask
from pyrogram import idle
from pyrogram.types import BotCommand

import config
from ShizuMusic import LOGGER, assistant, bot, call_py
from ShizuMusic.modules import ALL_MODULES

# Shared assistant username (set at startup, read by modules)
ASSISTANT_USERNAME: str = ""

# ── Flask health check ────────────────────────────────────────────────────────

_flask = Flask(__name__)


@_flask.route("/")
def _home():
    return "✅ ShizuMusic is running!", 200


@_flask.route("/health")
def _health():
    return "OK", 200


def _run_flask() -> None:
    _flask.run(host="0.0.0.0", port=config.PORT, use_reloader=False)


# ── Watchdog ──────────────────────────────────────────────────────────────────

async def _watchdog() -> None:
    """Restart process if no Telegram activity for 4 hours."""
    from pyrogram.handlers import CallbackQueryHandler, MessageHandler

    dq: deque = deque(maxlen=500)
    start = time.time()

    async def _tick(c, m):
        dq.append(time.time())

    try:
        bot.add_handler(MessageHandler(_tick), group=-99)
        bot.add_handler(CallbackQueryHandler(_tick), group=-99)
    except Exception:
        pass

    while True:
        await asyncio.sleep(60)
        now = time.time()
        if now - start < 300:
            continue
        last = dq[-1] if dq else None
        if not last or (now - last) > 14400:
            LOGGER.error("Watchdog: no activity — restarting")
            if config.LOGGER_ID:
                try:
                    await bot.send_message(config.LOGGER_ID, "⚡ ɴᴏ ᴀᴄᴛɪᴠɪᴛʏ — ʀᴇsᴛᴀʀᴛɪɴɢ…")
                except Exception:
                    pass
            os._exit(0)


# ── Startup ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    global ASSISTANT_USERNAME

    # 1. Flask
    threading.Thread(target=_run_flask, daemon=True).start()
    LOGGER.info(f"Flask health server on port {config.PORT}")

    # 2. PyTgCalls
    call_py.start()
    LOGGER.info("PyTgCalls started")

    # 3. Bot (with FLOOD_WAIT retry)
    for attempt in range(10):
        try:
            bot.start()
            LOGGER.info("Bot client started")
            break
        except Exception as e:
            if "FLOOD_WAIT" in str(e):
                m    = re.search(r"(\d+)", str(e))
                wait = min(int(m.group(1)) + 5 if m else 300, 1800)
                LOGGER.warning(f"FLOOD_WAIT — sleeping {wait}s (attempt {attempt + 1}/10)")
                time.sleep(wait)
            else:
                LOGGER.error(f"Bot start failed: {e}")
                sys.exit(1)
    else:
        LOGGER.error("Bot failed to start after 10 attempts")
        sys.exit(1)

    me = bot.get_me()
    LOGGER.info(f"Bot: @{me.username}")

    # 4. Set bot commands
    try:
        bot.set_bot_commands([
            BotCommand("start",  "✧ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ✧"),
            BotCommand("help",   "✧ ɢᴇᴛ ʜᴇʟᴩ ᴍᴇɴᴜ ✧"),
            BotCommand("play",   "✧ ᴩʟᴀʏ ᴀ sᴏɴɢ ✧"),
            BotCommand("pause",  "✧ ᴩᴀᴜsᴇ ᴘʟᴀʏʙᴀᴄᴋ ✧"),
            BotCommand("resume", "✧ ʀᴇsᴜᴍᴇ ᴘʟᴀʏʙᴀᴄᴋ ✧"),
            BotCommand("skip",   "✧ sᴋɪᴩ sᴏɴɢ ✧"),
            BotCommand("stop",   "✧ sᴛᴏᴩ & ᴄʟᴇᴀʀ ✧"),
            BotCommand("ping",   "✧ ʙᴏᴛ sᴛᴀᴛs ✧"),
        ])
        LOGGER.info("Bot commands set")
    except Exception as e:
        LOGGER.warning(f"Could not set bot commands: {e}")

    # 5. Assistant
    if not assistant.is_connected:
        assistant.start()
    am = assistant.get_me()
    ASSISTANT_USERNAME = am.username
    LOGGER.info(f"Assistant: @{ASSISTANT_USERNAME}")

    # 6. Load all modules
    for mod in ALL_MODULES:
        importlib.import_module(f"ShizuMusic.modules.{mod}")
        LOGGER.info(f"Loaded module: {mod}")

    # Also register the stream-end handler from core.call
    import ShizuMusic.core.call  # noqa: F401

    # 7. Notify owner
    try:
        bot.send_message(config.OWNER_ID, f"✅ ShizuMusic @{me.username} started!")
    except Exception:
        LOGGER.info("Could not DM owner — make sure you've started the bot in PM.")

    # 8. Watchdog
    loop = asyncio.get_event_loop()
    loop.create_task(_watchdog())

    LOGGER.info("✅ ShizuMusic is running")
    idle()

    # Graceful shutdown
    try:
        bot.stop()
    except Exception:
        pass
    LOGGER.info("ShizuMusic stopped.")
