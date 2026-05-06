"""
ShizuMusic/modules/broadcast.py
/broadcast command — owner only, forward a replied message to all chats.
"""
import asyncio

from pymongo import MongoClient
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

import config
from ShizuMusic import bot

_mongo        = MongoClient(config.MONGO_DB_URL)
broadcast_col = _mongo["ShizuMusic"]["broadcast"]


@bot.on_message(filters.command("broadcast") & filters.user(config.OWNER_ID))
async def broadcast_cmd(_, message: Message) -> None:
    if not message.reply_to_message:
        await message.reply(
            "<b>❌ ʀᴇᴩʟʏ ᴛᴏ ᴛʜᴇ ᴍᴇssᴀɢᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ.</b>",
            parse_mode=ParseMode.HTML,
        )
        return

    bm   = message.reply_to_message
    ok   = 0
    fail = 0

    for doc in broadcast_col.find({}):
        try:
            await bot.forward_messages(int(doc["chat_id"]), bm.chat.id, bm.id)
            ok += 1
        except Exception:
            fail += 1
        await asyncio.sleep(0.4)

    await message.reply(
        f"<b>✅ ʙʀᴏᴀᴅᴄᴀsᴛ ᴅᴏɴᴇ.</b>\n<b>✓</b> {ok}  <b>✗</b> {fail}",
        parse_mode=ParseMode.HTML,
    )
