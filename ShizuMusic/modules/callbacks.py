"""
ShizuMusic/modules/callbacks.py
Inline button callbacks — pause, resume, skip, stop, clear, help, noop.
"""
import asyncio

from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

import config
from ShizuMusic import bot, call_py
from ShizuMusic.core.call import leave_vc
from ShizuMusic.core.player import play_song
from ShizuMusic.core.queue import clear_queue, peek_current, pop_current, queue_size
from ShizuMusic.utils.formatters import short
from ShizuMusic.utils.helpers import delete_file
from ShizuMusic.utils.permissions import is_user_authorized


@bot.on_callback_query()
async def on_callback(client, cbq: CallbackQuery) -> None:
    chat_id = cbq.message.chat.id
    user    = cbq.from_user
    data    = cbq.data

    # Auth-gated actions
    if data in ("pause", "resume", "skip", "stop", "clear"):
        if not await is_user_authorized(cbq):
            await cbq.answer("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ.", show_alert=True)
            return

    # ── Pause ─────────────────────────────────────────────────────────────────
    if data == "pause":
        try:
            await call_py.pause(chat_id)
            await cbq.answer("⏸ ᴘᴀᴜsᴇᴅ")
            await client.send_message(
                chat_id,
                f"<b>⏸ ᴘᴀᴜsᴇᴅ ʙʏ</b> {user.first_name}",
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            await cbq.answer("❌ ᴄᴏᴜʟᴅ ɴᴏᴛ ᴘᴀᴜsᴇ", show_alert=True)

    # ── Resume ────────────────────────────────────────────────────────────────
    elif data == "resume":
        try:
            await call_py.resume(chat_id)
            await cbq.answer("▶️ ʀᴇsᴜᴍᴇᴅ")
            await client.send_message(
                chat_id,
                f"<b>▶️ ʀᴇsᴜᴍᴇᴅ ʙʏ</b> {user.first_name}",
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            await cbq.answer("❌ ᴄᴏᴜʟᴅ ɴᴏᴛ ʀᴇsᴜᴍᴇ", show_alert=True)

    # ── Skip ──────────────────────────────────────────────────────────────────
    elif data == "skip":
        if not queue_size(chat_id):
            await cbq.answer("❌ ǫᴜᴇᴜᴇ ɪs ᴇᴍᴘᴛʏ", show_alert=True)
            return
        skipped = pop_current(chat_id)
        try:
            await call_py.leave_call(chat_id)
        except Exception:
            pass
        await asyncio.sleep(2)
        delete_file(skipped.get("file_path", ""))
        await client.send_message(
            chat_id,
            f"<b>⏭ sᴋɪᴩᴩᴇᴅ ʙʏ</b> {user.first_name}\n"
            f"<b>❍ sᴏɴɢ :</b> {short(skipped['title'])}",
            parse_mode=ParseMode.HTML,
        )
        nxt = peek_current(chat_id)
        if nxt:
            await cbq.answer("⏭ ᴘʟᴀʏɪɴɢ ɴᴇxᴛ…")
            dm = await bot.send_message(
                chat_id,
                f"<b>🎧 ɴᴇxᴛ :</b> {nxt['title']}",
                parse_mode=ParseMode.HTML,
            )
            await play_song(chat_id, dm, nxt)
        else:
            await cbq.answer("⏭ ǫᴜᴇᴜᴇ ᴇᴍᴘᴛʏ")

    # ── Stop ──────────────────────────────────────────────────────────────────
    elif data == "stop":
        await leave_vc(chat_id)
        await cbq.answer("⏹ sᴛᴏᴩᴩᴇᴅ")
        await client.send_message(
            chat_id,
            f"<b>⏹ sᴛᴏᴩᴩᴇᴅ ʙʏ</b> {user.first_name}",
            parse_mode=ParseMode.HTML,
        )

    # ── Clear ─────────────────────────────────────────────────────────────────
    elif data == "clear":
        clear_queue(chat_id)
        await cbq.answer("🗑️ ᴄʟᴇᴀʀᴇᴅ")
        await cbq.message.edit(
            "<b>🗑️ ǫᴜᴇᴜᴇ ᴄʟᴇᴀʀᴇᴅ ʙʏ</b> " + user.first_name,
            parse_mode=ParseMode.HTML,
        )

    # ── Noop (progress bar button) ────────────────────────────────────────────
    elif data == "noop":
        await cbq.answer()

    # ── Help menu ─────────────────────────────────────────────────────────────
    elif data == "show_help":
        await _show_help(cbq)

    elif data == "go_back":
        await _go_back(cbq)

    elif data.startswith("help_"):
        await _help_section(cbq, data)


# ── Help pages ────────────────────────────────────────────────────────────────

async def _go_back(cbq: CallbackQuery) -> None:
    uid  = cbq.from_user.id
    name = cbq.from_user.first_name or "User"
    caption = (
        "<b>╭────────────────────▣</b>\n"
        f"<b>│❍ нєу</b> <a href='tg://user?id={uid}'>{name}</a>, 🥀\n"
        f"<b>│❍ ᴛʜɪs ɪs {config.BOT_NAME} !</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴜsɪᴄ ʙᴏᴛ.</b>\n"
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
    await cbq.message.edit_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=kb)


async def _show_help(cbq: CallbackQuery) -> None:
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("❍ ᴘʟᴀʏ ❍",   callback_data="help_music"),
            InlineKeyboardButton("❍ ᴀᴅᴍɪɴ ❍",  callback_data="help_admin"),
        ],
        [InlineKeyboardButton("❍ ᴜᴛɪʟɪᴛʏ ❍", callback_data="help_util")],
        [InlineKeyboardButton("⌯ ʜᴏᴍᴇ ⌯",    callback_data="go_back")],
    ])
    await cbq.message.edit_text(
        "<b>📜 ᴄʜᴏᴏsᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ :</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=kb,
    )


async def _help_section(cbq: CallbackQuery, data: str) -> None:
    back = InlineKeyboardMarkup([[InlineKeyboardButton("⌯ ʙᴀᴄᴋ ⌯", callback_data="show_help")]])
    texts = {
        "help_music": (
            "<b>╭────────────────────▣</b>\n"
            "<b>│🎵 ᴍᴜsɪᴄ ᴄᴏᴍᴍᴀɴᴅs</b>\n"
            "<b>├────────────────────▣</b>\n"
            "<b>│❍ /play</b> &lt;song or URL&gt;\n"
            "<b>│❍ /pause</b>  — ᴘᴀᴜsᴇ  <i>(ᴀᴅᴍɪɴ)</i>\n"
            "<b>│❍ /resume</b> — ʀᴇsᴜᴍᴇ <i>(ᴀᴅᴍɪɴ)</i>\n"
            "<b>│❍ /skip</b>   — sᴋɪᴩ   <i>(ᴀᴅᴍɪɴ)</i>\n"
            "<b>│❍ /stop</b>   — sᴛᴏᴩ   <i>(ᴀᴅᴍɪɴ)</i>\n"
            "<b>│❍ /clear</b>  — ᴄʟᴇᴀʀ ǫᴜᴇᴜᴇ <i>(ᴀᴅᴍɪɴ)</i>\n"
            "<b>╰────────────────────▣</b>"
        ),
        "help_admin": (
            "<b>╭────────────────────▣</b>\n"
            "<b>│🛡️ ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs</b>\n"
            "<b>├────────────────────▣</b>\n"
            "<b>│❍ /mute</b>   @user\n"
            "<b>│❍ /unmute</b> @user\n"
            "<b>│❍ /kick</b>   @user\n"
            "<b>│❍ /ban</b>    @user\n"
            "<b>│❍ /unban</b>  @user\n"
            "<b>╰────────────────────▣</b>"
        ),
        "help_util": (
            "<b>╭────────────────────▣</b>\n"
            "<b>│🔍 ᴜᴛɪʟɪᴛʏ</b>\n"
            "<b>├────────────────────▣</b>\n"
            "<b>│❍ /ping</b>   — sᴛᴀᴛs & ʟᴀᴛᴇɴᴄʏ\n"
            "<b>│❍ /reboot</b> — ʀᴇsᴇᴛ ᴄʜᴀᴛ sᴛᴀᴛᴇ\n"
            f"<b>│❍ ᴍᴀx sᴏɴɢ: {config.MAX_DURATION_SECONDS // 60} ᴍɪɴᴜᴛᴇs</b>\n"
            "<b>╰────────────────────▣</b>"
        ),
    }
    await cbq.message.edit_text(
        texts.get(data, "?"),
        parse_mode=ParseMode.HTML,
        reply_markup=back,
    )
