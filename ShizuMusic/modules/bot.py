# --------------------------------------------------------------------------------
#  KRISH X STAR CODER © 2026
#  Developed by KRISH X STAR CODER ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

import random
from pyrogram import filters
from pyrogram.errors import ChatAdminRequired
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from ShizuMusic import bot
from ShizuMusic.database import (
    add_broadcast_chat,
    add_served_chat,
    remove_broadcast_chat,
    remove_served_chat,
)

# ── Custom Left notification photos ───────────────────────────────────────────
LEFT_PHOTOS = [
    "https://telegra.ph/file/your_custom_photo1.jpg",
    "https://telegra.ph/file/your_custom_photo2.jpg",
    "https://telegra.ph/file/your_custom_photo3.jpg",
]

# ══════════════════════════════════════════════════════════════════════════════
# BOT ADDED TO GROUP
# ══════════════════════════════════════════════════════════════════════════════

@bot.on_message(filters.new_chat_members, group=-10)
async def bot_added_watcher(_, message: Message) -> None:
    try:
        chat    = message.chat
        chat_id = chat.id
        me      = await bot.get_me()

        for member in message.new_chat_members:
            if member.id != me.id:
                continue

            add_served_chat(chat_id)
            add_broadcast_chat(chat_id, "group")

            added_by = message.from_user
            added_by_mention = added_by.mention if added_by else "Unknown"

            admin_request_text = (
                "<b>╭──────────────────────▣</b>\n"
                "<b>│❍ Thanks for adding me! 🥀</b>\n"
                "<b>├──────────────────────▣</b>\n"
                "<b>│❍ Please make me an Admin</b>\n"
                "<b>│  with these permissions:</b>\n"
                "<b>├──────────────────────▣</b>\n"
                "<b>│ ❍ Delete Messages</b>\n"
                "<b>│ ❍ Manage Video Chats</b>\n"
                "<b>│ ❍ Invite Users</b>\n"
                "<b>├──────────────────────▣</b>\n"
                "<b>│❍ Without admin perms</b>\n"
                "<b>│  some features won’t work 🚫</b>\n"
                "<b>╰──────────────────────▣</b>\n"
                "<b>Powered by KRISH X STAR CODER</b>\n"
                "<b>Owner: https://t.me/KRISH_HACKER_OWNER</b>\n"
                "<b>Support: https://t.me/KRISH_HACKER_OP</b>"
            )
            admin_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("⚡ Make Me Admin ⚡", url=f"tg://user?id={me.id}")]
            ])
            try:
                await message.reply_text(
                    admin_request_text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=admin_kb,
                )
            except Exception:
                pass

    except Exception as e:
        print(f"[watcher] bot_added_watcher error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# BOT LEFT / REMOVED FROM GROUP
# ══════════════════════════════════════════════════════════════════════════════

@bot.on_message(filters.left_chat_member, group=-12)
async def bot_left_watcher(_, message: Message) -> None:
    try:
        left_member = message.left_chat_member
        if not left_member:
            return

        me = await bot.get_me()
        if left_member.id != me.id:
            return

        chat    = message.chat
        chat_id = chat.id

        remove_served_chat(chat_id)
        remove_broadcast_chat(chat_id)

        removed_by = message.from_user
        removed_by_mention = removed_by.mention if removed_by else "Unknown User"

        left_text = (
            "<b>✫ Bot Removed ✫</b>\n\n"
            f"<b>📌 Chat Title :</b> {chat.title}\n"
            f"<b>🍂 Chat ID    :</b> <code>{chat_id}</code>\n"
            f"<b>👢 Removed By :</b> {removed_by_mention}\n"
            f"<b>🤖 Bot        :</b> @{me.username}\n\n"
            "<b>Powered by KRISH X STAR CODER</b>\n"
            "<b>Owner: https://t.me/KRISH_HACKER_OWNER</b>\n"
            "<b>Support: https://t.me/KRISH_HACKER_OP</b>"
        )

        try:
            await bot.send_photo(
                config.LOGGER_ID,
                photo=random.choice(LEFT_PHOTOS),
                caption=left_text,
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            await bot.send_message(
                config.LOGGER_ID,
                left_text,
                parse_mode=ParseMode.HTML,
            )

    except Exception as e:
        print(f"[watcher] bot_left_watcher error: {e}")
