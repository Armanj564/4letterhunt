import os
import random
import string
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# ── Proxies ───────────────────────────────────────────────────────
PROXY_USER = "ainrlxbm"
PROXY_PASS = "xidaz286f66o"
PROXY_LIST = [
    ("31.59.20.176",    6754),
    ("198.23.239.134",  6540),
    ("45.38.107.97",    6014),
    ("107.172.163.27",  6543),
    ("198.105.121.200", 6462),
    ("216.10.27.159",   6837),
    ("142.111.67.146",  5611),
    ("191.96.254.138",  6185),
    ("31.58.9.4",       6077),
    ("64.137.10.153",   5803),
]

# ── Global state ──────────────────────────────────────────────────
scanning = False
found_list = []
scanned_count = 0
scan_length = 4
scan_delay = 1.0

def random_proxy():
    ip, port = random.choice(PROXY_LIST)
    return f"http://{PROXY_USER}:{PROXY_PASS}@{ip}:{port}"

def gen_username(length):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
}

# ── Checkers ──────────────────────────────────────────────────────
async def check_instagram(session, username, proxy):
    try:
        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
        headers = {**HEADERS, "X-IG-App-ID": "936619743392459"}
        async with session.get(url, headers=headers, proxy=proxy, timeout=aiohttp.ClientTimeout(total=8)) as r:
            if r.status == 404:
                return True
            if r.status == 200:
                return False
            return None
    except:
        return None

async def check_tiktok(session, username, proxy):
    try:
        url = f"https://www.tiktok.com/@{username}"
        async with session.get(url, headers=HEADERS, proxy=proxy, timeout=aiohttp.ClientTimeout(total=8)) as r:
            text = await r.text()
            if '"statusCode":10202' in text or "Couldn't find this account" in text:
                return True
            if '"uniqueId"' in text:
                return False
            return None
    except:
        return None

async def check_discord(session, username, proxy):
    try:
        url = "https://discord.com/api/v9/unique-username/username-attempt-unauthed-desktop"
        payload = {"username": username}
        async with session.post(url, json=payload, headers=HEADERS, proxy=proxy, timeout=aiohttp.ClientTimeout(total=8)) as r:
            data = await r.json()
            if data.get("taken") is False:
                return True
            if data.get("taken") is True:
                return False
            return None
    except:
        return None

# ── Scan loop ─────────────────────────────────────────────────────
async def scan_loop(context, chat_id):
    global scanning, found_list, scanned_count

    status_msg = await context.bot.send_message(
        chat_id,
        "🔍 *Scanning...*\n\n📊 Scanned: `0` | ✅ Found: `0`\n\nSend /stop to stop.",
        parse_mode="Markdown"
    )

    async with aiohttp.ClientSession() as session:
        while scanning:
            username = gen_username(scan_length)
            proxy = random_proxy()

            ig = await check_instagram(session, username, proxy)
            tt = await check_tiktok(session, username, proxy)
            dc = await check_discord(session, username, proxy)

            scanned_count += 1

            platforms_available = []
            if ig is True: platforms_available.append("📸 Instagram")
            if tt is True: platforms_available.append("🎵 TikTok")
            if dc is True: platforms_available.append("💬 Discord")

            if len(platforms_available) >= 2:
                entry = f"{username} — {', '.join(platforms_available)}"
                found_list.append(entry)
                await context.bot.send_message(
                    chat_id,
                    f"✅ *Available!*\n\n"
                    f"👤 Username: `{username}`\n"
                    f"🌐 Free on: {', '.join(platforms_available)}",
                    parse_mode="Markdown"
                )

            if scanned_count % 10 == 0:
                try:
                    await status_msg.edit_text(
                        f"🔍 *Scanning...*\n\n📊 Scanned: `{scanned_count}` | ✅ Found: `{len(found_list)}`\n\nSend /stop to stop.",
                        parse_mode="Markdown"
                    )
                except:
                    pass

            await asyncio.sleep(scan_delay)

    await context.bot.send_message(
        chat_id,
        f"🛑 *Scan stopped!*\n\n"
        f"📊 Scanned: `{scanned_count}`\n"
        f"✅ Found: `{len(found_list)}`",
        parse_mode="Markdown"
    )

# ── Commands ──────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "hunter"
    await update.message.reply_text(
        f"👾 *Hey {name}, welcome to 4Char Hunter!*\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🎯 I hunt rare 4-letter usernames across *Instagram*, *TikTok* and *Discord* using proxies — automatically!\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📡 *Scanning:*\n"
        "▸ /scan — Start hunting usernames\n"
        "▸ /stop — Stop the scan\n\n"
        "📋 *Results:*\n"
        "▸ /list — Show all found usernames\n"
        "▸ /export — Download list as .txt file\n"
        "▸ /clear — Clear the found list\n"
        "▸ /stats — View scan statistics\n\n"
        "⚙️ *Settings:*\n"
        "▸ /setspeed fast|slow — Change scan speed\n"
        "▸ /setlength 3|4|5 — Set username length\n"
        "▸ /platforms — Show active platforms\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🚀 Ready? Send /scan to start!",
        parse_mode="Markdown"
    )

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global scanning, scanned_count, found_list
    if scanning:
        await update.message.reply_text("⚠️ Already scanning! Send /stop to stop first.")
        return
    scanning = True
    scanned_count = 0
    found_list = []
    asyncio.create_task(scan_loop(context, update.effective_chat.id))
    await update.message.reply_text(
        f"🚀 *Scan started!*\n\n"
        f"📏 Length: `{scan_length}`\n"
        f"⚡ Speed: `{'fast' if scan_delay == 0.3 else 'slow'}`\n"
        f"🌐 Platforms: Instagram, TikTok, Discord\n\n"
        f"I'll notify you every time I find one ✅",
        parse_mode="Markdown"
    )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global scanning
    if not scanning:
        await update.message.reply_text("⚠️ Not currently scanning.")
        return
    scanning = False
    await update.message.reply_text("🛑 Stopping scan...")

async def list_found(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not found_list:
        await update.message.reply_text("📭 No usernames found yet.\n\nSend /scan to start hunting!")
        return
    text = f"✅ *Found {len(found_list)} username(s):*\n\n"
    text += "\n".join(f"▸ `{u}`" for u in found_list)
    await update.message.reply_text(text, parse_mode="Markdown")

async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not found_list:
        await update.message.reply_text("📭 Nothing to export yet!")
        return
    content = "\n".join(found_list)
    with open("found.txt", "w") as f:
        f.write(content)
    await update.message.reply_document(
        document=open("found.txt", "rb"),
        filename="found_usernames.txt",
        caption=f"📄 {len(found_list)} username(s) exported!"
    )

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global found_list
    found_list = []
    await update.message.reply_text("🗑️ Found list cleared!")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📊 *Scan Statistics:*\n\n"
        f"🔍 Total scanned: `{scanned_count}`\n"
        f"✅ Total found: `{len(found_list)}`\n"
        f"📏 Username length: `{scan_length}`\n"
        f"⚡ Speed: `{'fast' if scan_delay == 0.3 else 'slow'}`\n"
        f"🔄 Status: `{'scanning ✅' if scanning else 'idle 🔴'}`",
        parse_mode="Markdown"
    )

async def setspeed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global scan_delay
    if not context.args:
        await update.message.reply_text("⚙️ Usage: /setspeed fast|slow")
        return
    speed = context.args[0].lower()
    if speed == "fast":
        scan_delay = 0.3
        await update.message.reply_text("⚡ Speed set to *fast*!", parse_mode="Markdown")
    elif speed == "slow":
        scan_delay = 2.0
        await update.message.reply_text("🐢 Speed set to *slow*!", parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠️ Use: /setspeed fast|slow")

async def setlength(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global scan_length
    if not context.args:
        await update.message.reply_text("⚙️ Usage: /setlength 3|4|5")
        return
    try:
        length = int(context.args[0])
        if length not in [3, 4, 5]:
            raise ValueError
        scan_length = length
        await update.message.reply_text(f"📏 Length set to *{length}* characters!", parse_mode="Markdown")
    except:
        await update.message.reply_text("⚠️ Use: /setlength 3|4|5")

async def platforms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌐 *Active Platforms:*\n\n"
        "▸ 📸 Instagram\n"
        "▸ 🎵 TikTok\n"
        "▸ 💬 Discord\n\n"
        "💡 A username is marked ✅ when it's free on *2 or more* platforms at once.",
        parse_mode="Markdown"
    )

# ── Main ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",     start))
    app.add_handler(CommandHandler("scan",      scan))
    app.add_handler(CommandHandler("stop",      stop))
    app.add_handler(CommandHandler("list",      list_found))
    app.add_handler(CommandHandler("export",    export))
    app.add_handler(CommandHandler("clear",     clear))
    app.add_handler(CommandHandler("stats",     stats))
    app.add_handler(CommandHandler("setspeed",  setspeed))
    app.add_handler(CommandHandler("setlength", setlength))
    app.add_handler(CommandHandler("platforms", platforms))
    print("✅ Bot is running...")
    app.run_polling()
