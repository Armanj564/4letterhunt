import os
import random
import string
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get(“BOT_TOKEN”)

# ── Proxies ───────────────────────────────────────────────────────

PROXY_USER = “ainrlxbm”
PROXY_PASS = “xidaz286f66o”
PROXY_LIST = [
(“31.59.20.176”,    6754),
(“198.23.239.134”,  6540),
(“45.38.107.97”,    6014),
(“107.172.163.27”,  6543),
(“198.105.121.200”, 6462),
(“216.10.27.159”,   6837),
(“142.111.67.146”,  5611),
(“191.96.254.138”,  6185),
(“31.58.9.4”,       6077),
(“64.137.10.153”,   5803),
]

# ── Global state ──────────────────────────────────────────────────

scanning = False
found_list = []
scanned_count = 0
scan_length = 4
scan_delay = 0.5

def random_proxy():
ip, port = random.choice(PROXY_LIST)
return f”http://{PROXY_USER}:{PROXY_PASS}@{ip}:{port}”

def gen_username(length):
chars = string.ascii_lowercase + string.digits
return ‘’.join(random.choices(chars, k=length))

# ── Instagram checker (most reliable) ────────────────────────────

async def check_instagram(session, username, proxy):
try:
url = f”https://www.instagram.com/{username}/”
headers = {
“User-Agent”: “Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36”,
“Accept”: “text/html,application/xhtml+xml”,
“Accept-Language”: “en-US,en;q=0.9”,
}
async with session.get(url, headers=headers, proxy=proxy, timeout=aiohttp.ClientTimeout(total=10), allow_redirects=True) as r:
if r.status == 404:
return True   # available
if r.status == 200:
text = await r.text()
# If page has no user data it’s available
if ‘”@type”:“ProfilePage”’ not in text and ‘og:type” content=“profile”’ not in text:
return True
return False
if r.status in [429, 403]:
return None  # rate limited, skip
return None
except Exception:
return None

# ── TikTok checker ────────────────────────────────────────────────

async def check_tiktok(session, username, proxy):
try:
url = f”https://www.tiktok.com/@{username}”
headers = {
“User-Agent”: “Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36”,
}
async with session.get(url, headers=headers, proxy=proxy, timeout=aiohttp.ClientTimeout(total=10), allow_redirects=True) as r:
text = await r.text()
if “user-not-found” in text or ‘“statusCode”:10202’ in text or “Couldn’t find this account” in text:
return True
if ‘“uniqueId”’ in text or ‘“authorStats”’ in text:
return False
return None
except Exception:
return None

# ── Scan loop ─────────────────────────────────────────────────────

async def scan_loop(context, chat_id):
global scanning, found_list, scanned_count

```
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

        scanned_count += 1

        platforms_available = []
        if ig is True:  platforms_available.append("📸 Instagram")
        if tt is True:  platforms_available.append("🎵 TikTok")

        # report if available on at least 1 platform
        if len(platforms_available) >= 1:
            entry = f"{username} — {', '.join(platforms_available)}"
            found_list.append(entry)
            await context.bot.send_message(
                chat_id,
                f"✅ *Available username found!*\n\n"
                f"👤 `{username}`\n"
                f"🌐 Free on: {', '.join(platforms_available)}\n\n"
                f"🔗 instagram.com/{username}\n"
                f"🔗 tiktok.com/@{username}",
                parse_mode="Markdown"
            )

        if scanned_count % 20 == 0:
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
```

# ── Commands ──────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
name = update.effective_user.first_name or “hunter”
await update.message.reply_text(
f”👾 *Hey {name}, welcome to 4Char Hunter!*\n\n”
“━━━━━━━━━━━━━━━━━━\n”
“🎯 I hunt rare short usernames across *Instagram* and *TikTok* using proxies!\n\n”
“━━━━━━━━━━━━━━━━━━\n”
“📡 *Scanning:*\n”
“▸ /scan — Start hunting\n”
“▸ /stop — Stop scanning\n\n”
“📋 *Results:*\n”
“▸ /list — Show found usernames\n”
“▸ /export — Download as .txt file\n”
“▸ /clear — Clear the list\n”
“▸ /stats — View statistics\n\n”
“⚙️ *Settings:*\n”
“▸ /setspeed fast|slow\n”
“▸ /setlength 3|4|5\n”
“▸ /platforms\n\n”
“━━━━━━━━━━━━━━━━━━\n”
“🚀 Send /scan to start!”,
parse_mode=“Markdown”
)

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
global scanning, scanned_count, found_list
if scanning:
await update.message.reply_text(“⚠️ Already scanning! Send /stop first.”)
return
scanning = True
scanned_count = 0
found_list = []
asyncio.create_task(scan_loop(context, update.effective_chat.id))
await update.message.reply_text(
f”🚀 *Scan started!*\n\n”
f”📏 Length: `{scan_length}`\n”
f”⚡ Speed: `{'fast' if scan_delay == 0.3 else 'slow'}`\n”
f”🌐 Platforms: Instagram, TikTok\n\n”
f”I’ll notify you every time I find one ✅”,
parse_mode=“Markdown”
)

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
global scanning
if not scanning:
await update.message.reply_text(“⚠️ Not scanning right now.”)
return
scanning = False
await update.message.reply_text(“🛑 Stopping scan…”)

async def list_found(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not found_list:
await update.message.reply_text(“📭 Nothing found yet. Send /scan to start!”)
return
text = f”✅ *Found {len(found_list)} username(s):*\n\n”
text += “\n”.join(f”▸ `{u}`” for u in found_list)
await update.message.reply_text(text, parse_mode=“Markdown”)

async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not found_list:
await update.message.reply_text(“📭 Nothing to export yet!”)
return
content = “\n”.join(found_list)
with open(“found.txt”, “w”) as f:
f.write(content)
await update.message.reply_document(
document=open(“found.txt”, “rb”),
filename=“found_usernames.txt”,
caption=f”📄 {len(found_list)} username(s) exported!”
)

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
global found_list
found_list = []
await update.message.reply_text(“🗑️ List cleared!”)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
f”📊 *Statistics:*\n\n”
f”🔍 Scanned: `{scanned_count}`\n”
f”✅ Found: `{len(found_list)}`\n”
f”📏 Length: `{scan_length}`\n”
f”⚡ Speed: `{'fast' if scan_delay == 0.3 else 'slow'}`\n”
f”🔄 Status: `{'scanning ✅' if scanning else 'idle 🔴'}`”,
parse_mode=“Markdown”
)

async def setspeed(update: Update, context: ContextTypes.DEFAULT_TYPE):
global scan_delay
if not context.args:
await update.message.reply_text(“⚙️ Usage: /setspeed fast|slow”)
return
speed = context.args[0].lower()
if speed == “fast”:
scan_delay = 0.3
await update.message.reply_text(“⚡ Speed set to *fast*!”, parse_mode=“Markdown”)
elif speed == “slow”:
scan_delay = 2.0
await update.message.reply_text(“🐢 Speed set to *slow*!”, parse_mode=“Markdown”)
else:
await update.message.reply_text(“⚠️ Use: /setspeed fast|slow”)

async def setlength(update: Update, context: ContextTypes.DEFAULT_TYPE):
global scan_length
if not context.args:
await update.message.reply_text(“⚙️ Usage: /setlength 3|4|5”)
return
try:
length = int(context.args[0])
if length not in [3, 4, 5]:
raise ValueError
scan_length = length
await update.message.reply_text(f”📏 Length set to *{length}*!”, parse_mode=“Markdown”)
except:
await update.message.reply_text(“⚠️ Use: /setlength 3|4|5”)

async def platforms(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
“🌐 *Active Platforms:*\n\n”
“▸ 📸 Instagram\n”
“▸ 🎵 TikTok\n\n”
“✅ Reports username if free on any platform.”,
parse_mode=“Markdown”
)

# ── Main ──────────────────────────────────────────────────────────

if **name** == “**main**”:
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler(“start”,     start))
app.add_handler(CommandHandler(“scan”,      scan))
app.add_handler(CommandHandler(“stop”,      stop))
app.add_handler(CommandHandler(“list”,      list_found))
app.add_handler(CommandHandler(“export”,    export))
app.add_handler(CommandHandler(“clear”,     clear))
app.add_handler(CommandHandler(“stats”,     stats))
app.add_handler(CommandHandler(“setspeed”,  setspeed))
app.add_handler(CommandHandler(“setlength”, setlength))
app.add_handler(CommandHandler(“platforms”, platforms))
print(“✅ Bot running…”)
app.run_polling()
