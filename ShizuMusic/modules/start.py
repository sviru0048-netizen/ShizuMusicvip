"""
ShizuMusic/modules/start.py
/start command — welcome message for PM and groups.
"""

import random

from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from ShizuMusic import bot

EFFECT_ID = [
    5046509860389126442,
    5107584321108051014,
    5104841245755180586,
    5159385139981059251,
]


@bot.on_message(filters.command("start"))
async def start_handler(_, message: Message) -> None:
    uid       = message.from_user.id
    name      = message.from_user.first_name or "User"
    chat_id   = message.chat.id
    chat_type = message.chat.type

    # ── DB ────────────────────────────────────────────────────────────────────
    try:
        from ShizuMusic.database import (
            add_broadcast_chat,
            add_served_chat,
            add_served_user,
        )
        add_served_user(uid)
        add_served_chat(chat_id)
    except Exception:
        add_broadcast_chat = None

    # ── PRIVATE ───────────────────────────────────────────────────────────────
    if chat_type == ChatType.PRIVATE:

        caption = (
            "<b>╭────────────────────▣</b>\n"
            f"<b>│❍ ʜᴇʏ</b> <a href='tg://user?id={uid}'>{name}</a>, 🥀\n"
            f"<b>│❍ ᴛʜɪs ɪs {config.BOT_NAME} !</b>\n"
            "<b>├────────────────────▣</b>\n"
            "<b>│❍ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ</b>\n"
            "<b>│ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ ᴡɪᴛʜ</b>\n"
            "<b>│ sᴏᴍᴇ ᴀᴡᴇsᴏᴍᴇ ғᴇᴀᴛᴜʀᴇs.</b>\n"
            "<b>├────────────────────▣</b>\n"
            "<b>│❍ ᴄʟɪᴄᴋ ʜᴇʟᴘ ғᴏʀ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs.</b>\n"
            "<b>├────────────────────▣</b>\n"
            f"<b>│❍ ᴘᴏᴡᴇʀᴇᴅ ʙʏ » <a href='t.me/PBXCHATS'>sʜɪᴢᴜ-ᴍᴜsɪᴄ™</a></b>\n"
            "<b>╰────────────────────▣</b>"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("⛩️ ᴧᴅᴅ мᴇ ʙᴧʙʏ ⛩️", url=f"{config.BOT_LINK}?startgroup=true")],
            [
                InlineKeyboardButton("🍬 sᴜᴘᴘᴏʀᴛ 🍬", url=config.SUPPORT_GROUP),
                InlineKeyboardButton("🍹 ᴜᴘᴅᴀᴛᴇs 🍹",  url=config.UPDATES_CHANNEL),
            ],
            [InlineKeyboardButton("🏩 ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅs 🏩", callback_data="show_help")],
            [
                InlineKeyboardButton("🫧 ᴏᴡɴᴇʀ 🫧",  url=f"tg://user?id={config.OWNER_ID}"),
                InlineKeyboardButton("🍡 sᴏᴜʀᴄᴇ 🍡", url="https://github.com/Badmunda05/ShizuMusic/fork"),
            ],
        ])

        await message.reply_animation(
            config.START_ANIMATION,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
            message_effect_id=random.choice(EFFECT_ID),
        )

        # ── Broadcast DB save ─────────────────────────────────────────────────
        try:
            from ShizuMusic.database import add_broadcast_chat
            add_broadcast_chat(chat_id, "private")
        except Exception:
            pass

        # ── LOGGER_ID — PM start notification ────────────────────────────────
        if config.LOGGER_ID:
            try:
                await bot.send_message(
                    config.LOGGER_ID,
                    "<b>#ɴᴇᴡᴜsᴇʀ sᴛᴀʀᴛᴇᴅ</b>\n\n"
                    f"<b>❍ ɴᴀᴍᴇ     :</b> <a href='tg://user?id={uid}'>{name}</a>\n"
                    f"<b>❍ ɪᴅ       :</b> <code>{uid}</code>\n"
                    f"<b>❍ ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username or 'N/A'}",
                    parse_mode=ParseMode.HTML,
                )
            except Exception:
                pass

    # ── GROUP ─────────────────────────────────────────────────────────────────
    else:
        chat_title = message.chat.title or "ᴛʜɪs ᴄʜᴀᴛ"
        caption = (
            f"❍ ʜᴇʏ <a href='tg://user?id={uid}'>{name}</a>,\n"
            f"ᴛʜɪs ɪs <b>{config.BOT_NAME}</b>\n\n"
            f"ᴛʜᴀɴᴋs ғᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ ɪɴ <b>{chat_title}</b>.\n"
            f"{name} ᴄᴀɴ ɴᴏᴡ ᴘʟᴀʏ sᴏɴɢs ʜᴇʀᴇ."
        )
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⛩️ ᴧᴅᴅ мᴇ ʙᴧʙʏ ⛩️", url=f"{config.BOT_LINK}?startgroup=true"),
                InlineKeyboardButton("🍬 sᴜᴘᴘᴏʀᴛ 🍬", url=config.SUPPORT_GROUP),
            ],
            [InlineKeyboardButton("🏩 ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅs 🏩", callback_data="show_help")],
        ])

        await message.reply_animation(
            config.START_ANIMATION,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )

        # ── Admin Request Message ─────────────────────────────────────────────
        admin_msg = (
            "<b>╭──────────────────────▣</b>\n"
            "<b>│❍ ᴛʜᴀɴᴋs ғᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ! 🥀</b>\n"
            "<b>├──────────────────────▣</b>\n"
            "<b>│❍ ᴘʟᴇᴀsᴇ ᴍᴀᴋᴇ ᴍᴇ ᴀɴ ᴀᴅᴍɪɴ</b>\n"
            "<b>│  ᴡɪᴛʜ ᴛʜᴇsᴇ ᴘᴇʀᴍɪssɪᴏɴs:</b>\n"
            "<b>├──────────────────────▣</b>\n"
            "<b>│ ❍ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs</b>\n"
            "<b>│ ❍ ᴍᴀɴᴀɢᴇ ᴠɪᴅᴇᴏ ᴄʜᴀᴛs</b>\n"
            "<b>│ ❍ ɪɴᴠɪᴛᴇ ᴜsᴇʀs</b>\n"
            "<b>├──────────────────────▣</b>\n"
            "<b>│❍ ᴡɪᴛʜᴏᴜᴛ ᴀᴅᴍɪɴ ᴘᴇʀᴍs</b>\n"
            "<b>│  sᴏᴍᴇ ғᴇᴀᴛᴜʀᴇs ᴡᴏɴ'ᴛ ᴡᴏʀᴋ! 🚫</b>\n"
            "<b>╰──────────────────────▣</b>"
        )
        admin_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "⚡ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ ⚡",
                url=f"tg://user?id={(await bot.get_me()).id}"
            )]
        ])
        try:
            await message.reply_text(
                admin_msg,
                parse_mode=ParseMode.HTML,
                reply_markup=admin_kb,
            )
        except Exception:
            pass

        # ── Broadcast DB save ─────────────────────────────────────────────────
        try:
            from ShizuMusic.database import add_broadcast_chat
            add_broadcast_chat(chat_id, "group")
        except Exception:
            pass
