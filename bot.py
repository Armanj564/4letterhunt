import os
import random
import string
import asyncio
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

user_state = {}
user_found = {}
scanning_tasks = {}

def gen_username(length=4, mode="mixed"):
    if mode == "letters":
        chars = string.ascii_lowercase
    elif mode == "numbers":
        chars = string.digits
    else:
        chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))

async def check_instagram(session, username):
    try:
        async with session.get(
            f"https://www.instagram.com/{username}/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=10),
            allow_redirects=True
        ) as r:
            if r.status == 404:
                return True
            text = await r.text()
            if "Sorry, this page" in text or "userNotFound" in text:
                return True
            if '"edge_followed_by"' in text or '"username"' in text:
                return False
            return None
    except Exception:
        return None

async def check_tiktok(session, username):
    try:
        async with session.get(
            f"https://www.tiktok.com/@{username}",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=10),
            allow_redirects=True
        ) as r:
            if r.status == 404:
                return True
            text = await r.text()
            if "Couldn&#x27;t find this account" in text or "user-not-found" in text.lower() or 'statusCode\":404' in text:
                return True
            if '"uniqueId"' in text or '"nickname"' in text:
                return False
            return None
    except Exception:
        return None

async def check_discord(session, username):
    try:
        async with session.get(
            f"https://discord.id/?prefill={username}",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=8)
        ) as r:
            text = await r.text()
            if "Unknown User" in text or "not found" in text.lower():
                return True
            if "discriminator" in text or "avatar" in text:
                return False
            return None
    except Exception:
        return None

def fmt(status):
    if status is True:
        return "✅"
    elif status is False:
        return "❌"
    return "❓"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    keyboard = [
        [InlineKeyboardButton("🚀 Start Scanning", callback_data="goto_check")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="goto_settings"),
         InlineKeyboardButton("📋 My List", callback_data="goto_list")],
        [InlineKeyboardButton("❓ Help", callback_data="goto_help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"👋 *Welcome, {name}!*\n\n"
        "🔍 *4LetterHunt* — the ultimate username sniper bot\n\n"
        "━━━━━━━━━━━━━━━\n"
        "💎 Find rare 4-letter usernames\n"
        "⚡️ Auto scan non-stop\n"
        "🎯 Check Discord, Instagram & TikTok\n"
        "💾 Save found usernames\n"
        "⚙️ Custom length & filters\n"
        "━━━━━━━━━━━━━━━\n\n"
        "👇 *Choose an option below:*",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🎮 Discord", callback_data="scan_discord"),
            InlineKeyboardButton("📸 Instagram", callback_data="scan_instagram"),
            InlineKeyboardButton("🎵 TikTok", callback_data="scan_tiktok"),
        ],
        [InlineKeyboardButton("💥 All 3 Platforms", callback_data="scan_all")],
        [InlineKeyboardButton("🤖 AUTO SCAN (non-stop)", callback_data="scan_auto")],
        [InlineKeyboardButton("🔙 Back", callback_data="goto_start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎯 *Select Platform*\n\n"
        "Pick where to scan usernames 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def settings_menu(update, context, edit=False):
    uid = update.effective_user.id
    if uid not in user_state:
        user_state[uid] = {"length": 4, "mode": "mixed"}
    s = user_state[uid]
    keyboard = [
        [
            InlineKeyboardButton("3️⃣ 3 chars", callback_data="len_3"),
            InlineKeyboardButton("4️⃣ 4 chars", callback_data="len_4"),
            InlineKeyboardButton("5️⃣ 5 chars", callback_data="len_5"),
        ],
        [
            InlineKeyboardButton("🔤 Letters only", callback_data="mode_letters"),
            InlineKeyboardButton("🔢 Numbers only", callback_data="mode_numbers"),
            InlineKeyboardButton("🔀 Mixed", callback_data="mode_mixed"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="goto_start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        f"⚙️ *Settings*\n\n"
        f"📏 Length: *{s.get('length', 4)} chars*\n"
        f"🔤 Mode: *{s.get('mode', 'mixed')}*\n\n"
        "Change your preferences below 👇"
    )
    if edit:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await settings_menu(update, context)

async def show_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    found = user_found.get(uid, [])
    if not found:
        await update.message.reply_text(
            "📭 *No usernames found yet!*\n\nUse /check to start scanning 🔍",
            parse_mode="Markdown"
        )
        return
    text = f"📋 *Your Found Usernames*\n\n"
    text += "\n".join(f"✅ `{u}`" for u in found[-50:])
    text += f"\n\n🏆 *Total found: {len(found)}*"
    await update.message.reply_text(text, parse_mode="Markdown")

async def clear_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_found[uid] = []
    await update.message.reply_text("🗑️ *List cleared!*", parse_mode="Markdown")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in scanning_tasks and not scanning_tasks[uid].done():
        scanning_tasks[uid].cancel()
        found = len(user_found.get(uid, []))
        await update.message.reply_text(
            f"🛑 *Auto scan stopped!*\n\n"
            f"💾 Use /list to see all {found} found usernames",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("⚠️ No active scan running.")

async def do_scan(context, chat_id, uid, platform, auto=False, length=4, mode="mixed"):
    count = 0
    available_count = 0
    batch = []

    async with aiohttp.ClientSession() as session:
        while True:
            username = gen_username(length, mode)
            count += 1

            if platform == "discord":
                status = await check_discord(session, username)
                if status is True:
                    available_count += 1
                    user_found.setdefault(uid, []).append(username)
                    line = f"🔥 *FOUND* `{username}` — 🎮 Discord"
                elif status is False:
                    line = f"❌ `{username}`"
                else:
                    line = f"❓ `{username}`"

            elif platform == "instagram":
                status = await check_instagram(session, username)
                if status is True:
                    available_count += 1
                    user_found.setdefault(uid, []).append(username)
                    line = f"🔥 *FOUND* `{username}` — 📸 Instagram"
                elif status is False:
                    line = f"❌ `{username}`"
                else:
                    line = f"❓ `{username}`"

            elif platform == "tiktok":
                status = await check_tiktok(session, username)
                if status is True:
                    available_count += 1
                    user_found.setdefault(uid, []).append(username)
                    line = f"🔥 *FOUND* `{username}` — 🎵 TikTok"
                elif status is False:
                    line = f"❌ `{username}`"
                else:
                    line = f"❓ `{username}`"

            else:
                ig, tt, dc = await asyncio.gather(
                    check_instagram(session, username),
                    check_tiktok(session, username),
                    check_discord(session, username),
                )
                all_free = ig is True and tt is True and dc is True
                any_free = ig is True or tt is True or dc is True
                if all_free:
                    available_count += 1
                    user_found.setdefault(uid, []).append(username)
                    line = f"💎 *ALL FREE* `{username}` IG:{fmt(ig)} TT:{fmt(tt)} DC:{fmt(dc)}"
                elif any_free:
                    line = f"⚡️ `{username}` IG:{fmt(ig)} TT:{fmt(tt)} DC:{fmt(dc)}"
                else:
                    line = f"❌ `{username}` IG:{fmt(ig)} TT:{fmt(tt)} DC:{fmt(dc)}"

            batch.append(line)

            if len(batch) >= 10:
                text = "\n".join(batch)
                text += f"\n\n📊 Scanned: *{count}* | 🟢 Found: *{available_count}*"
                if auto:
                    text += "\n_/stop to stop scanning_"
                try:
                    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
                except Exception:
                    pass
                batch = []

            if not auto and count >= 100:
                if batch:
                    text = "\n".join(batch)
                    text += f"\n\n━━━━━━━━━━\n🟢 *{available_count} available* out of {count}\n💾 Use /list to see saved usernames"
                    try:
                        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
                    except Exception:
                        pass
                break

            await asyncio.sleep(0.8)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = update.effective_user.id
    chat_id = update.effective_chat.id
    data = query.data

    if data == "goto_start":
        name = update.effective_user.first_name
        keyboard = [
            [InlineKeyboardButton("🚀 Start Scanning", callback_data="goto_check")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="goto_settings"),
             InlineKeyboardButton("📋 My List", callback_data="goto_list")],
            [InlineKeyboardButton("❓ Help", callback_data="goto_help")]
        ]
        await query.edit_message_text(
            f"👋 *Welcome, {name}!*\n\n"
            "🔍 *4LetterHunt* — the ultimate username sniper bot\n\n"
            "━━━━━━━━━━━━━━━\n"
            "💎 Find rare 4-letter usernames\n"
            "⚡️ Auto scan non-stop\n"
            "🎯 Check Discord, Instagram & TikTok\n"
            "💾 Save found usernames\n"
            "⚙️ Custom length & filters\n"
            "━━━━━━━━━━━━━━━\n\n"
            "👇 *Choose an option below:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    if data == "goto_check":
        keyboard = [
            [
                InlineKeyboardButton("🎮 Discord", callback_data="scan_discord"),
                InlineKeyboardButton("📸 Instagram", callback_data="scan_instagram"),
                InlineKeyboardButton("🎵 TikTok", callback_data="scan_tiktok"),
            ],
            [InlineKeyboardButton("💥 All 3 Platforms", callback_data="scan_all")],
            [InlineKeyboardButton("🤖 AUTO SCAN (non-stop)", callback_data="scan_auto")],
            [InlineKeyboardButton("🔙 Back", callback_data="goto_start")]
        ]
        await query.edit_message_text(
            "🎯 *Select Platform*\n\nPick where to scan 👇",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    if data == "goto_settings":
        await settings_menu(update, context, edit=True)
        return

    if data == "goto_list":
        found = user_found.get(uid, [])
        if not found:
            await query.edit_message_text("📭 *No usernames found yet!*\n\nUse /check to start scanning 🔍", parse_mode="Markdown")
        else:
            text = f"📋 *Your Found Usernames*\n\n"
            text += "\n".join(f"✅ `{u}`" for u in found[-50:])
            text += f"\n\n🏆 *Total: {len(found)}*"
            await query.edit_message_text(text, parse_mode="Markdown")
        return

    if data == "goto_help":
        await query.edit_message_text(
            "❓ *Help*\n\n"
            "/check — pick platform & scan\n"
            "/stop — stop auto scan\n"
            "/list — view found usernames\n"
            "/clear — clear your list\n"
            "/settings — change length & mode\n\n"
            "🔥 = available on that platform\n"
            "💎 = available on ALL platforms\n"
            "❌ = taken\n"
            "❓ = unknown/error\n\n"
            "Auto scan runs forever until /stop",
            parse_mode="Markdown"
        )
        return

    if data.startswith("len_"):
        length = int(data.split("_")[1])
        user_state.setdefault(uid, {})["length"] = length
        await query.edit_message_text(f"✅ Length set to *{length}* characters!\n\nUse /check to scan", parse_mode="Markdown")
        return

    if data.startswith("mode_"):
        mode = data.split("_")[1]
        user_state.setdefault(uid, {})["mode"] = mode
        await query.edit_message_text(f"✅ Mode set to *{mode}*!\n\nUse /check to scan", parse_mode="Markdown")
        return

    platform = data.replace("scan_", "")
    auto = platform == "auto"
    if uid not in user_state:
        user_state[uid] = {"length": 4, "mode": "mixed"}
    length = user_state[uid].get("length", 4)
    mode = user_state[uid].get("mode", "mixed")

    if auto:
        platform = "all"
        await query.edit_message_text(
            "🤖 *Auto scan started!*\n\n"
            "⚡️ Scanning non-stop across all platforms\n"
            "📩 Results sent every 10 usernames\n\n"
            "Send /stop to stop ✋",
            parse_mode="Markdown"
        )
    else:
        await query.edit_message_text(
            f"🔍 *Scanning 100 usernames...*\n"
            f"Platform: *{platform.upper()}*\n"
            f"Length: *{length}* | Mode: *{mode}*\n\n"
            "Results coming soon ⚡️",
            parse_mode="Markdown"
        )

    task = asyncio.create_task(do_scan(context, chat_id, uid, platform, auto=auto, length=length, mode=mode))
    scanning_tasks[uid] = task

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("list", show_list))
    app.add_handler(CommandHandler("clear", clear_list))
    app.add_handler(CommandHandler("settings", settings))
    app.add_handler(CallbackQueryHandler(button))
    print("Bot is running...")
    app.run_polling()
