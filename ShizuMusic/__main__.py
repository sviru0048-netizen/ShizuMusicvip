"""
ShizuMusic/__main__.py

Main startup file for ShizuMusic.
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
from pyrogram.handlers import (
    CallbackQueryHandler,
    MessageHandler,
)
from pyrogram.types import BotCommand

import config
from ShizuMusic import (
    LOGGER,
    assistant,
    bot,
    call_py,
)
from ShizuMusic.modules import ALL_MODULES


# ─────────────────────────────────────────────
# ASSISTANT USERNAME
# ─────────────────────────────────────────────
ASSISTANT_USERNAME = ""


# ─────────────────────────────────────────────
# FLASK HEALTH SERVER
# ─────────────────────────────────────────────
app = Flask(__name__)


@app.route("/")
def home():
    return (
        "✅ ShizuMusic is running!",
        200,
    )


@app.route("/health")
def health():
    return ("OK", 200)


def run_flask() -> None:
    app.run(
        host="0.0.0.0",
        port=config.PORT,
        use_reloader=False,
    )


# ─────────────────────────────────────────────
# WATCHDOG
# ─────────────────────────────────────────────
async def watchdog() -> None:
    """
    Restart process if no activity
    for 4 hours.
    """

    dq: deque = deque(maxlen=500)
    start_time = time.time()

    async def tick(_, __):
        dq.append(time.time())

    try:
        bot.add_handler(
            MessageHandler(tick),
            group=-99,
        )
        bot.add_handler(
            CallbackQueryHandler(tick),
            group=-99,
        )
    except Exception:
        pass

    while True:

        await asyncio.sleep(60)

        now = time.time()

        # Ignore first 5 mins
        if now - start_time < 300:
            continue

        last = dq[-1] if dq else None

        # Restart if inactive for 4 hours
        if (
            not last
            or (now - last) > 14400
        ):

            LOGGER.error("Watchdog Restart Triggered")

            if config.LOGGER_ID:
                try:
                    await bot.send_message(
                        config.LOGGER_ID,
                        "⚠️ ShizuMusic Restarting\n\n❍ No Telegram activity detected.",
                    )
                except Exception:
                    pass

            os._exit(0)


# ─────────────────────────────────────────────
# ASYNC MAIN
# ─────────────────────────────────────────────
async def main() -> None:

    global ASSISTANT_USERNAME

    # ─────────────────────────────────────────
    # FLASK SERVER
    # ─────────────────────────────────────────
    threading.Thread(
        target=run_flask,
        daemon=True,
    ).start()

    LOGGER.info(f"Flask Server Started : {config.PORT}")

    # ─────────────────────────────────────────
    # PYTGCALLS
    # ─────────────────────────────────────────
    try:
        call_py.start()
        LOGGER.info("PyTgCalls Started")
    except Exception as e:
        LOGGER.error(f"PyTgCalls Error : {e}")
        sys.exit(1)

    # ─────────────────────────────────────────
    # BOT START
    # ─────────────────────────────────────────
    for attempt in range(10):
        try:
            await bot.start()
            LOGGER.info("Bot Client Started")
            break
        except Exception as e:

            # FLOOD WAIT
            if "FLOOD_WAIT" in str(e):
                match = re.search(r"(\d+)", str(e))
                wait = min(
                    (int(match.group(1)) + 5 if match else 300),
                    1800,
                )
                LOGGER.warning(
                    f"FloodWait : Sleeping {wait}s "
                    f"(Attempt {attempt + 1}/10)"
                )
                await asyncio.sleep(wait)
            else:
                LOGGER.error(f"Bot Start Failed : {e}")
                sys.exit(1)
    else:
        LOGGER.error("Bot Failed To Start After 10 Attempts")
        sys.exit(1)

    # ─────────────────────────────────────────
    # BOT INFO
    # ─────────────────────────────────────────
    me = await bot.get_me()
    LOGGER.info(f"Bot Username : @{me.username}")

    # ─────────────────────────────────────────
    # BOT COMMANDS
    # ─────────────────────────────────────────
    try:
        await bot.set_bot_commands(
            [
                BotCommand("start",  "Start The Bot"),
                BotCommand("help",   "Help Menu"),
                BotCommand("play",   "Play Music"),
                BotCommand("pause",  "Pause Music"),
                BotCommand("resume", "Resume Music"),
                BotCommand("skip",   "Skip Track"),
                BotCommand("stop",   "Stop Playback"),
                BotCommand("ping",   "Bot Stats"),
            ]
        )
        LOGGER.info("Bot Commands Set")
    except Exception as e:
        LOGGER.warning(f"Commands Error : {e}")

    # ─────────────────────────────────────────
    # ASSISTANT START
    # ─────────────────────────────────────────
    try:
        if not assistant.is_connected:
            await assistant.start()

        assistant_me = await assistant.get_me()
        ASSISTANT_USERNAME = assistant_me.username
        LOGGER.info(f"Assistant : @{ASSISTANT_USERNAME}")
    except Exception as e:
        LOGGER.error(f"Assistant Error : {e}")
        sys.exit(1)

    # ─────────────────────────────────────────
    # LOAD MODULES
    # ─────────────────────────────────────────
    for module in ALL_MODULES:
        try:
            importlib.import_module(f"ShizuMusic.modules.{module}")
            LOGGER.info(f"Loaded Module : {module}")
        except Exception as e:
            LOGGER.error(f"Module Load Failed {module} : {e}")

    # ─────────────────────────────────────────
    # LOAD STREAM END HANDLER
    # ─────────────────────────────────────────
    try:
        import ShizuMusic.core.call  # noqa: F401
        LOGGER.info("Call Handler Loaded")
    except Exception as e:
        LOGGER.error(f"Call Handler Error : {e}")

    # ─────────────────────────────────────────
    # OWNER NOTIFICATION
    # ─────────────────────────────────────────
    try:
        await bot.send_message(
            config.LOGGER_ID,
            f"✅ ShizuMusic Started\n\n❍ Bot : @{me.username}\n❍ Assistant : @{ASSISTANT_USERNAME}",
        )
    except Exception as e:
        LOGGER.warning(f"Logger Notification Error : {e}")

    # ─────────────────────────────────────────
    # WATCHDOG
    # ─────────────────────────────────────────
    asyncio.get_event_loop().create_task(watchdog())

    LOGGER.info("✅ ShizuMusic Running")

    # ─────────────────────────────────────────
    # IDLE
    # ─────────────────────────────────────────
    await idle()

    # ─────────────────────────────────────────
    # SHUTDOWN
    # ─────────────────────────────────────────
    try:
        await bot.stop()
    except Exception:
        pass

    try:
        await assistant.stop()
    except Exception:
        pass

    LOGGER.info("ShizuMusic Stopped")


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(main())
