import asyncio
import importlib
import os
import re
import sys
import threading
import time
from collections import deque

import requests
from flask import Flask
from pyrogram import idle
from pyrogram.types import BotCommand

import config
from ShizuMusic import LOGGER, assistant, bot, call_py
from ShizuMusic.modules import ALL_MODULES

# Shared assistant username
ASSISTANT_USERNAME = ""

# ── Flask health check ────────────────────────────────────────────────────────

_flask = Flask(__name__)


@_flask.route("/")
def _home():
    return "❍ ꜱʜɪᴢᴜᴍᴜꜱɪᴄ ɪꜱ ʀᴜɴɴɪɴɢ ᴍᴀᴅᴇ ʙʏ ʙᴀᴅᴍᴜɴᴅᴀ 💕", 200


@_flask.route("/health")
def _health():
    return "OK", 200


def _run_flask() -> None:
    _flask.run(host="0.0.0.0", port=config.PORT, use_reloader=False)


# ── Keep-Alive Ping ───────────────────────────────────────────────────────────

def _keep_alive() -> None:
    """Ping own Render URL every 5 minutes so the service never sleeps."""
    url = "https://shizumusicbot-w7jq.onrender.com"
    while True:
        try:
            requests.get(url, timeout=10)
            LOGGER.info(f"Keep-alive ping sent → {url}")
        except Exception as e:
            LOGGER.warning(f"Keep-alive ping failed: {e}")
        time.sleep(300)  # 5 minutes


# ── Watchdog ──────────────────────────────────────────────────────────────────

async def _watchdog() -> None:
    """Restart process if no Telegram activity for 4 hours."""

    from pyrogram.handlers import CallbackQueryHandler, MessageHandler

    dq: deque = deque(maxlen=500)
    start = time.time()

    async def _tick(_, __):
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
                    await bot.send_message(
                        config.LOGGER_ID,
                        "⚠️ ꜱʜɪᴢᴜᴍᴜꜱɪᴄ ʀᴇꜱᴛᴀʀᴛɪɴɢ\n\n❍ ɴᴏ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴄᴛɪᴠɪᴛʏ ᴅᴇᴛᴇᴄᴛᴇᴅ."
                    )
                except Exception:
                    pass

            os._exit(0)


# ── Startup notification ──────────────────────────────────────────────────────

async def _notify_owner(me, assistant_username: str) -> None:
    """Send startup notification to the logger chat."""
    try:
        await bot.send_message(
            config.LOGGER_ID,
            f"✅ ShizuMusic Started\n\n❍ Bot : @{me.username}\n❍ Assistant : @{assistant_username}",
        )
    except Exception as e:
        LOGGER.warning(f"Logger Notification Error : {e}")
        LOGGER.info("Could not DM owner — start bot once in PM.")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    # 1. Flask
    threading.Thread(target=_run_flask, daemon=True).start()
    LOGGER.info(f"Flask health server on port {config.PORT}")

    # 2. Keep-alive ping
    threading.Thread(target=_keep_alive, daemon=True).start()
    LOGGER.info("Keep-alive thread started")

    # 3. PyTgCalls
    call_py.start()
    LOGGER.info("PyTgCalls started")

    # 4. Bot start (with FLOOD_WAIT retry)
    for attempt in range(10):
        try:
            bot.start()
            LOGGER.info("Bot client started")
            break

        except Exception as e:

            if "FLOOD_WAIT" in str(e):
                m = re.search(r"(\d+)", str(e))

                wait = min(
                    int(m.group(1)) + 5 if m else 300,
                    1800
                )

                LOGGER.warning(
                    f"FLOOD_WAIT — sleeping {wait}s "
                    f"(attempt {attempt + 1}/10)"
                )

                time.sleep(wait)

            else:
                LOGGER.error(f"Bot start failed: {e}")
                sys.exit(1)

    else:
        LOGGER.error("Bot failed to start after 10 attempts")
        sys.exit(1)

    me = bot.get_me()
    LOGGER.info(f"Bot: @{me.username}")

    # 5. Set bot commands
    try:
        bot.set_bot_commands(
            [
                BotCommand("start", "✧ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ✧"),
                BotCommand("help", "✧ ɢᴇᴛ ʜᴇʟᴘ ᴍᴇɴᴜ ✧"),
                BotCommand("play", "✧ ᴘʟᴀʏ ᴀ sᴏɴɢ ✧"),
                BotCommand("pause", "✧ ᴘᴀᴜsᴇ ᴘʟᴀʏʙᴀᴄᴋ ✧"),
                BotCommand("resume", "✧ ʀᴇsᴜᴍᴇ ᴘʟᴀʏʙᴀᴄᴋ ✧"),
                BotCommand("skip", "✧ sᴋɪᴘ sᴏɴɢ ✧"),
                BotCommand("stop", "✧ sᴛᴏᴘ & ᴄʟᴇᴀʀ ✧"),
                BotCommand("ping", "✧ ʙᴏᴛ sᴛᴀᴛs ✧"),
            ]
        )

        LOGGER.info("Bot commands set")

    except Exception as e:
        LOGGER.warning(f"Could not set bot commands: {e}")

    # 6. Assistant
    try:
        if not assistant.is_connected:
            assistant.start()

        am = assistant.get_me()

        ASSISTANT_USERNAME = am.username

        LOGGER.info(f"Assistant: @{ASSISTANT_USERNAME}")

    except Exception as e:
        LOGGER.error(f"Assistant start failed: {e}")
        sys.exit(1)

    # 7. Load modules
    for mod in ALL_MODULES:
        try:
            importlib.import_module(f"ShizuMusic.modules.{mod}")
            LOGGER.info(f"Loaded module: {mod}")

        except Exception as e:
            LOGGER.error(f"Failed to load module {mod}: {e}")

    # Stream-end handler
    try:
        import ShizuMusic.core.call  # noqa: F401
    except Exception as e:
        LOGGER.error(f"Failed to load call handler: {e}")

    # 8. Notify owner
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_notify_owner(me, ASSISTANT_USERNAME))

    # 9. Watchdog
    loop.create_task(_watchdog())

    LOGGER.info("✅ ShizuMusic is running")

    idle()

    # ── Graceful shutdown ─────────────────────────────────────────────────────

    try:
        bot.stop()
    except Exception:
        pass

    try:
        assistant.stop()
    except Exception:
        pass

    LOGGER.info("ShizuMusic stopped.")
