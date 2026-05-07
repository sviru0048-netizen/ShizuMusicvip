"""
ShizuMusic/modules/broadcast.py

/broadcast command — owner only.
Forward a replied message to all saved chats.
"""

import asyncio

from pymongo import MongoClient
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

import config
from ShizuMusic import bot


# ─────────────────────────────────────────────
# MONGODB
# ─────────────────────────────────────────────
_mongo = MongoClient(config.MONGO_DB_URL)

broadcast_col = _mongo["ShizuMusic"]["broadcast"]


# ─────────────────────────────────────────────
# BROADCAST COMMAND
# ─────────────────────────────────────────────
@bot.on_message(
    filters.command("broadcast")
    & filters.user(config.OWNER_ID)
)
async def broadcast_cmd(_, message: Message) -> None:

    # Reply Check
    if not message.reply_to_message:

        await message.reply(
            """
<b>❍ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ</b>

<b>❍ ᴛʜᴇɴ ᴜsᴇ /broadcast.</b>
""",
            parse_mode=ParseMode.HTML,
        )
        return

    bm = message.reply_to_message

    success = 0
    failed = 0

    # Processing Message
    processing = await message.reply(
        """
<b>❍ ʙʀᴏᴀᴅᴄᴀsᴛ sᴛᴀʀᴛᴇᴅ</b>

<b>❍ sᴇɴᴅɪɴɢ ᴍᴇssᴀɢᴇs...</b>
""",
        parse_mode=ParseMode.HTML,
    )

    # Send Broadcast
    for doc in broadcast_col.find({}):

        try:

            await bot.forward_messages(
                int(doc["chat_id"]),
                bm.chat.id,
                bm.id,
            )

            success += 1

        except Exception:

            failed += 1

        await asyncio.sleep(0.4)

    # Final Result
    await processing.edit_text(
        f"""
<b>❍ ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</b>

<b>❍ sᴜᴄᴄᴇss :</b> <code>{success}</code>
<b>❍ ғᴀɪʟᴇᴅ :</b> <code>{failed}</code>
""",
        parse_mode=ParseMode.HTML,
    )
