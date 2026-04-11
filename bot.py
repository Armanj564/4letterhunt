import os
import random
import string
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get(“BOT_TOKEN”)

# WebShare proxies

PROXY_USER = “ainrlxbm”
PROXY_PASS = “xidaz286f66o”
PROXIES = [
f”http://{PROXY_USER}:{PROXY_PASS}@31.59.20.176:6754”,
f”http://{PROXY_USER}:{PROXY_PASS}@198.23.239.134:6540”,
f”http://{PROXY_USER}:{PROXY_PASS}@45.38.107.97:6014”,
f”http://{PROXY_USER}:{PROXY_PASS}@107.172.163.27:6543”,
f”http://{PROXY_USER}:{PROXY_PASS}@198.105.121.200:6462”,
f”http://{PROXY_USER}:{PROXY_PASS}@216.10.27.159:6837”,
f”http://{PROXY_USER}:{PROXY_PASS}@142.111.67.146:5611”,
f”http://{PROXY_USER}:{PROXY_PASS}@191.96.254.138:6185”,
f”http://{PROXY_USER}:{PROXY_PASS}@31.58.9.4:6077”,
f”http://{PROXY_USER}:{PROXY_PASS}@64.137.10.153:5803”,
]

HEADERS = {
“User-Agent”: “Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36”,
“Accept”: “text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8”,
“Accept-Language”: “en-US,en;q=0.9”,
}

scanning = {}

def gen_username():
chars = string.ascii_lowercase + string.digits
return ‘’.join(random.choices(chars, k=4))

def get_proxy():
return random.choice(PROXIES)

async def check_tiktok(username):
proxy = get_proxy()
try:
async with aiohttp.ClientSession() as session:
async with session.get(
f”https://www.tiktok.com/@{username}”,
headers=HEADERS,
proxy=proxy,
timeout=aiohttp.ClientTimeout(total=12),
allow_redirects=True
) as r:
if r.status == 404:
return True
text = await r.text()
if “Couldn't find this account” in text or ‘“statusCode”:10202’ in text or “user-not-found” in text.lower():
return True
if f’“uniqueId”:”{username}”’ in text.lower() or ‘“nickname”’ in text:
return False
return None
except Exception:
return None

def fmt(status):
if status is True:
return “✅”
elif status is False:
return “❌”
return “❓”

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
“👾 *4Char Username Checker*\n\n”
“Checks TikTok 4-letter usernames using proxy rotation.\n\n”
“Commands:\n”
“/check — check 10 usernames\n”
“/check 30 — check up to 50\n”
“/scan — auto scan until stopped\n”
“/stop — stop auto scan\n\n”
“✅ available  ❌ taken  ❓ unknown”,
parse_mode=“Markdown”
)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
count = 10
if context.args:
try:
count = max(1, min(50, int(context.args[0])))
except ValueError:
pass

```
msg = await update.message.reply_text(f"🔍 Checking {count} usernames on TikTok...")

lines = []
available = []

for i in range(count):
    username = gen_username()
    status = await check_tiktok(username)

    if status is True:
        available.append(username)
        lines.append(f"✅ `{username}` — AVAILABLE!")
    elif status is False:
        lines.append(f"❌ `{username}`")
    else:
        lines.append(f"❓ `{username}`")

    await asyncio.sleep(0.5)

text = "\n".join(lines)
text += f"\n\n━━━━━━━━━━\n🟢 *{len(available)} available* out of {count} checked"
if available:
    text += f"\n\n🔥 Found: " + ", ".join(f"`{u}`" for u in available)
await msg.edit_text(text, parse_mode="Markdown")
```

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
user_id = update.effective_user.id
if scanning.get(user_id):
await update.message.reply_text(“Already scanning! Use /stop to stop.”)
return

```
scanning[user_id] = True
found = []
scanned = 0

msg = await update.message.reply_text("🟢 Auto scan started! Use /stop to stop.\n\nScanning...")

while scanning.get(user_id):
    username = gen_username()
    status = await check_tiktok(username)
    scanned += 1

    if status is True:
        found.append(username)
        await update.message.reply_text(f"🔥 AVAILABLE: `@{username}` on TikTok!", parse_mode="Markdown")

    if scanned % 10 == 0:
        try:
            await msg.edit_text(
                f"📊 Scanned: *{scanned}* | 🟢 Found: *{len(found)}*\n/stop to stop scanning",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    await asyncio.sleep(0.8)

await update.message.reply_text(
    f"🔴 *Scan stopped!*\n\n📊 Scanned: {scanned}\n🟢 Found: {len(found)}\n\nFound: " +
    (", ".join(f"`{u}`" for u in found) if found else "none"),
    parse_mode="Markdown"
)
```

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
user_id = update.effective_user.id
scanning[user_id] = False
await update.message.reply_text(“🔴 Stopping scan…”)

if **name** == “**main**”:
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler(“start”, start))
app.add_handler(CommandHandler(“check”, check))
app.add_handler(CommandHandler(“scan”, scan))
app.add_handler(CommandHandler(“stop”, stop))
print(“Bot is running…”)
app.run_polling()
