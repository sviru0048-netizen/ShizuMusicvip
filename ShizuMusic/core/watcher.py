"""
ShizuMusic/core/watcher.py
Watchdog — restarts the process if no Telegram activity for 4 hours.
"""

import asyncio
import os
import time
from collections import deque

import config
from ShizuMusic import LOGGER, bot


async def watchdog() -> None:
    """
    Monitors Telegram activity.
    If no message or callback is received for 4 hours (14 400 s),
    the process is killed so the host platform (Render, Railway, …)
    can restart it automatically.

    A 5-minute warm-up grace period is applied after startup so a
    freshly-deployed instance is never killed before it can receive
    its first update.
    """

    from pyrogram.handlers import CallbackQueryHandler, MessageHandler

    dq: deque = deque(maxlen=500)
    start = time.time()

    async def _tick(_, __) -> None:
        dq.append(time.time())

    # Register silent activity trackers at the lowest priority group
    try:
        bot.add_handler(MessageHandler(_tick), group=-99)
        bot.add_handler(CallbackQueryHandler(_tick), group=-99)
    except Exception as e:
        LOGGER.warning(f"Watchdog: could not register handlers — {e}")

    while True:
        await asyncio.sleep(60)

        now = time.time()

        # Grace period — don't trigger in first 5 minutes
        if now - start < 300:
            continue

        last = dq[-1] if dq else None

        if not last or (now - last) > 14_400:
            LOGGER.error("Watchdog: no Telegram activity for 4 h — restarting")

            if config.LOGGER_ID:
                try:
                    await bot.send_message(
                        config.LOGGER_ID,
                        "⚠️ ꜱʜɪᴢᴜᴍᴜꜱɪᴄ ʀᴇꜱᴛᴀʀᴛɪɴɢ\n\n"
                        "❍ ɴᴏ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴄᴛɪᴠɪᴛʏ ᴅᴇᴛᴇᴄᴛᴇᴅ.",
                    )
                except Exception:
                    pass

            os._exit(0)
          
