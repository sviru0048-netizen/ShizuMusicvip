"""
ShizuMusic/modules/start.py
/start command — welcome message for PM and groups.
"""
from pymongo import MongoClient
from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from ShizuMusic import bot

_mongo        = MongoClient(config.MONGO_DB_URL)
_db           = _mongo["ShizuMusic"]
broadcast_col = _db["broadcast"]


@bot.on_message(filters.command("start"))
async def start_handler(_, message: Message) -> None:
    uid       = message.from_user.id
    name      = message.from_user.first_name or "User"
    chat_id   = message.chat.id
    chat_type = message.chat.type

    if chat_type == ChatType.PRIVATE:
        caption = (
            "<b>╭────────────────────▣</b>\n"
            f"<b>│❍ нєу</b> <a href='tg://user?id={uid}'>{name}</a>, 🥀\n"
            f"<b>│❍ ᴛʜɪs ɪs {config.BOT_NAME} !</b>\n"
            "<b>├────────────────────▣</b>\n"
            "<b>│❍ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ </b>\n"
            "<b>│ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ ᴡɪᴛʜ </b>\n"
            "<b>│sᴏᴍᴇ ᴀᴡᴇsᴏᴍᴇ ғᴇᴀᴛᴜʀᴇs.</b>\n"
            "<b>├────────────────────▣</b>\n"
            "<b>│❍ ᴄʟɪᴄᴋ ʜᴇʟᴩ ғᴏʀ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs.</b>\n"
            "<b>├────────────────────▣</b>\n"
            f"<b>│❍ 𝖯ᴏᴡᴇʀᴇᴅ 𝖡ʏ » <a href='{config.BOT_LINK}'>{config.BOT_NAME}</a></b>\n"
            "<b>╰────────────────────▣</b>"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("⛩️ ᴧᴅᴅ мᴇ ʙᴧʙʏ ⛩️", url=f"{config.BOT_LINK}?startgroup=true")],
            [
                InlineKeyboardButton("🍬 sᴜᴩᴩᴏʀᴛ 🍬", url=config.SUPPORT_GROUP),
                InlineKeyboardButton("🍹 ᴜᴩᴅᴀᴛᴇ 🍹",   url=config.UPDATES_CHANNEL),
            ],
            [InlineKeyboardButton("🏩 ʜᴇʟᴩ ᴧиᴅ ᴄᴏᴍᴍᴧɴᴅs 🏩", callback_data="show_help")],
            [
                InlineKeyboardButton("🫧 ᴏᴡɴᴇʀ 🫧",  url=f"tg://user?id={config.OWNER_ID}"),
                InlineKeyboardButton("🍡 sᴏᴜʀᴄᴇ 🍡", url="https://github.com"),
            ],
        ])
        await message.reply_animation(
            config.START_ANIMATION,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )
        if not broadcast_col.find_one({"chat_id": chat_id}):
            broadcast_col.insert_one({"chat_id": chat_id, "type": "private"})

    else:
        chat_title = message.chat.title or "ᴛʜɪs ᴄʜᴀᴛ"
        caption = (
            f"❍ ʜᴇʏ <a href='tg://user?id={uid}'>{name}</a>,\n"
            f"ᴛʜɪs ɪs <b>{config.BOT_NAME}</b>\n\n"
            f"ᴛʜᴀɴᴋs ғᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ ɪɴ <b>{chat_title}</b>.\n"
            f"{name} ᴄᴀɴ ɴᴏᴡ ᴩʟᴀʏ sᴏɴɢs ʜᴇʀᴇ."
        )
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⛩️ ᴧᴅᴅ мᴇ ʙᴧʙʏ ⛩️", url=f"{config.BOT_LINK}?startgroup=true"),
                InlineKeyboardButton("🍬 sᴜᴩᴩᴏʀᴛ 🍬",       url=config.SUPPORT_GROUP),
            ],
            [InlineKeyboardButton("🏩 ʜᴇʟᴩ ᴧиᴅ ᴄᴏᴍᴍᴧɴᴅs 🏩", callback_data="show_help")],
        ])
        await message.reply_animation(
            config.START_ANIMATION,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )
        if not broadcast_col.find_one({"chat_id": chat_id}):
            broadcast_col.insert_one({"chat_id": chat_id, "type": "group"})
