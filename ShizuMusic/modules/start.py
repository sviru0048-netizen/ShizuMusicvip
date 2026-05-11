# --------------------------------------------------------------------------------
#  KRISH X STAR CODER © 2026
#  Developed by KRISH X STAR CODER ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

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
            f"<b>│❍ Hey</b> <a href='tg://user?id={uid}'>{name}</a> 🥀\n"
            f"<b>│❍ This is {config.BOT_NAME} !</b>\n"
            "<b>├────────────────────▣</b>\n"
            "<b>│❍ A fast & powerful Telegram</b>\n"
            "<b>│ Music Player Bot with</b>\n"
            "<b>│ awesome features.</b>\n"
            "<b>├────────────────────▣</b>\n"
            "<b>│❍ Click Help for all commands.</b>\n"
            "<b>├────────────────────▣</b>\n"
            f"<b>│❍ Powered by » <a href='https://t.me/KRISH_HACKER_OP'>KRISH X STAR CODER</a></b>\n"
            "<b>╰────────────────────▣</b>"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("⛩️ Add Me Baby ⛩️", url=f"{config.BOT_LINK}?startgroup=true")],
            [
                InlineKeyboardButton("🍬 Support 🍬", url="https://t.me/KRISH_HACKER_OP"),
                InlineKeyboardButton("🍹 Updates 🍹", url=config.UPDATES_CHANNEL),
            ],
            [InlineKeyboardButton("🏩 Help & Commands 🏩", callback_data="show_help")],
            [
                InlineKeyboardButton("🫧 Owner 🫧", url="https://t.me/KRISH_HACKER_OWNER"),
                InlineKeyboardButton("🍡 KRISH X STAR CODER 🍡", url="https://t.me/KRISH_HACKER_OWNER"),
            ],
        ])

        await message.reply_animation(
            config.START_ANIMATION,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
            message_effect_id=random.choice(EFFECT_ID),
        )

    # ── GROUP ─────────────────────────────────────────────────────────────────
    else:
        chat_title = message.chat.title or "This Chat"
        caption = (
            f"❍ Hey <a href='tg://user?id={uid}'>{name}</a>,\n"
            f"This is <b>{config.BOT_NAME}</b>\n\n"
            f"Thanks for adding me in <b>{chat_title}</b>.\n"
            f"{name} can now play songs here."
        )
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⛩️ Add Me Baby ⛩️", url=f"{config.BOT_LINK}?startgroup=true"),
                InlineKeyboardButton("🍬 Support 🍬", url="https://t.me/KRISH_HACKER_OP"),
            ],
            [InlineKeyboardButton("🏩 Help & Commands 🏩", callback_data="show_help")],
            [
                InlineKeyboardButton("🫧 Owner 🫧", url="https://t.me/KRISH_HACKER_OWNER"),
                InlineKeyboardButton("🍡 KRISH X STAR CODER 🍡", url="https://t.me/KRISH_HACKER_OWNER"),
            ],
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
