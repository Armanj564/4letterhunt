import os
import random
import string
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def gen_username():
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=4))

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
    await update.message.reply_text(
        "👾 *4Char Username Checker*\n\n"
        "Generates random 4-letter usernames and checks them across platforms.\n\n"
        "Commands:\n"
        "/check — check 10 usernames\n"
        "/check 30 — check up to 50\n\n"
        "✅ available  ❌ taken  ❓ unknown\n"
        "Platforms: Discord • Instagram • TikTok",
        parse_mode="Markdown"
    )

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = 10
    if context.args:
        try:
            count = max(1, min(50, int(context.args[0])))
        except ValueError:
            pass

    msg = await update.message.reply_text(f"🔍 Scanning {count} usernames...")

    lines = []
    available_count = 0

    async with aiohttp.ClientSession() as session:
        for i in range(count):
            username = gen_username()
            ig, tt, dc = await asyncio.gather(
                check_instagram(session, username),
                check_tiktok(session, username),
                check_discord(session, username),
            )

            all_free = ig is True and tt is True and dc is True

            if all_free:
                available_count += 1
                line = f"🔥 `{username}` ALL FREE\nIG:{fmt(ig)} TT:{fmt(tt)} DC:{fmt(dc)}"
            else:
                line = f"`{username}` IG:{fmt(ig)} TT:{fmt(tt)} DC:{fmt(dc)}"

            lines.append(line)
            await asyncio.sleep(1.5)

    text = "\n\n".join(lines)
    text += f"\n\n━━━━━━━━━━\n🟢 *{available_count} fully available* out of {count} checked"
    await msg.edit_text(text, parse_mode="Markdown")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    print("Bot is running...")
    app.run_polling()
