import os
import socket
import requests
import subprocess
import json
import re
import hashlib
import base64
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
Application, CommandHandler, CallbackQueryHandler,
MessageHandler, filters, ContextTypes
)

# ─── CONFIG ───────────────────────────────────────────────

BOT_TOKEN = os.environ.get(“BOT_TOKEN”)

# ─── /start ───────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
keyboard = [
[InlineKeyboardButton(“🔍 OSINT Tools”, callback_data=“menu_osint”)],
[InlineKeyboardButton(“🌐 Network Tools”, callback_data=“menu_network”)],
[InlineKeyboardButton(“🛡️ Security Info”, callback_data=“menu_security”)],
[InlineKeyboardButton(“📖 Help”, callback_data=“menu_help”)],
]
reply_markup = InlineKeyboardMarkup(keyboard)
await update.message.reply_text(
“🤖 *CyvxBot — Cybersecurity Toolkit*\n\n”
“Your all-in-one security assistant.\n”
“Choose a category or type a command:”,
parse_mode=“Markdown”,
reply_markup=reply_markup
)

# ─── /help ────────────────────────────────────────────────

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
text = (
“📖 *Available Commands*\n\n”
“*OSINT*\n”
“`/username <n>` — Search username across 15+ platforms\n”
“`/email <email>` — Check email breaches (free)\n”
“`/discord <username>` — Discord user lookup\n”
“`/discordid <id>` — Discord ID lookup (shows badges, avatar, created date)\n”
“`/snapchat <username>` — Snapchat profile lookup\n”
“`/whois <domain>` — WHOIS lookup\n”
“`/dns <domain>` — DNS records\n”
“`/ip <ip>` — IP geolocation\n”
“`/subdomains <domain>` — Find subdomains\n”
“`/dork <target>` — Google dorks\n”
“`/phone <number>` — Phone number info\n\n”
“*Network Tools*\n”
“`/portscan <host>` — Port scanner\n”
“`/ping <host>` — Ping host\n”
“`/headers <url>` — HTTP headers\n”
“`/robots <domain>` — robots.txt\n”
“`/sslcheck <domain>` — SSL certificate info\n\n”
“*Security Info*\n”
“`/tips` — Random security tip\n”
“`/tools` — Security tools list\n”
“`/cve <keyword>` — Search CVEs\n”
“`/hash <text>` — Hash a string\n”
“`/encode <text>` — Base64 encode\n”
“`/decode <text>` — Base64 decode\n”
“`/password <length>` — Generate strong password\n”
)
msg = update.message or update.callback_query.message
await msg.reply_text(text, parse_mode=“Markdown”)

# ─── OSINT: USERNAME ──────────────────────────────────────

async def username_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text(“Usage: `/username <n>`”, parse_mode=“Markdown”)
return

```
username = context.args[0]
platforms = {
    "GitHub": f"https://github.com/{username}",
    "Twitter/X": f"https://twitter.com/{username}",
    "Instagram": f"https://instagram.com/{username}",
    "Reddit": f"https://reddit.com/user/{username}",
    "TikTok": f"https://tiktok.com/@{username}",
    "YouTube": f"https://youtube.com/@{username}",
    "Telegram": f"https://t.me/{username}",
    "Pinterest": f"https://pinterest.com/{username}",
    "Twitch": f"https://twitch.tv/{username}",
    "Medium": f"https://medium.com/@{username}",
    "Dev.to": f"https://dev.to/{username}",
    "HackerNews": f"https://news.ycombinator.com/user?id={username}",
    "Steam": f"https://steamcommunity.com/id/{username}",
    "Spotify": f"https://open.spotify.com/user/{username}",
    "Snapchat": f"https://www.snapchat.com/add/{username}",
}

await update.message.reply_text(f"🔍 Searching `{username}` across 15 platforms...", parse_mode="Markdown")

found = []
not_found = []

for platform, url in platforms.items():
    try:
        r = requests.get(url, timeout=5, allow_redirects=True,
                         headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            found.append(f"✅ [{platform}]({url})")
        else:
            not_found.append(f"❌ {platform}")
    except:
        not_found.append(f"⚠️ {platform}")

result = f"👤 *Username: `{username}`*\n\n"
if found:
    result += f"*Found on {len(found)} platforms:*\n" + "\n".join(found) + "\n\n"
if not_found:
    result += "*Not found:*\n" + " | ".join(not_found)

await update.message.reply_text(result, parse_mode="Markdown", disable_web_page_preview=True)
```

# ─── OSINT: EMAIL (FREE) ──────────────────────────────────

async def email_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text(“Usage: `/email <email>`”, parse_mode=“Markdown”)
return

```
email = context.args[0]
await update.message.reply_text(f"🔍 Checking `{email}`...", parse_mode="Markdown")

results = []

# Check 1: Verify domain MX records
try:
    domain = email.split("@")[1]
    r = requests.get(f"https://dns.google/resolve?name={domain}&type=MX", timeout=5)
    data = r.json()
    if data.get("Answer"):
        results.append(f"✅ Email domain `{domain}` is *valid*")
    else:
        results.append(f"❌ Email domain `{domain}` has *no mail servers* — likely fake")
except:
    results.append("⚠️ Could not verify domain")

# Check 2: Gravatar profile
try:
    email_hash = hashlib.md5(email.lower().encode()).hexdigest()
    r = requests.get(f"https://www.gravatar.com/{email_hash}.json", timeout=5)
    if r.status_code == 200:
        data = r.json()
        display_name = data.get("entry", [{}])[0].get("displayName", "Unknown")
        profile_url = data.get("entry", [{}])[0].get("profileUrl", "")
        results.append(f"👤 Gravatar profile found!\n  Name: *{display_name}*\n  URL: {profile_url}")
    else:
        results.append("❌ No Gravatar profile linked to this email")
except:
    results.append("⚠️ Gravatar check failed")

# Check 3: Check if email appears in public paste sites via Google
results.append(f"🔍 [Search on HaveIBeenPwned](https://haveibeenpwned.com/account/{email})")
results.append(f"🔍 [Search on DeHashed](https://dehashed.com/search?query={email})")

result_text = f"📧 *Email Report: `{email}`*\n\n" + "\n\n".join(results)
await update.message.reply_text(result_text, parse_mode="Markdown", disable_web_page_preview=True)
```

# ─── OSINT: DISCORD USERNAME ──────────────────────────────

async def discord_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text(“Usage: `/discord <username>`\nFor ID lookup use: `/discordid <id>`”, parse_mode=“Markdown”)
return

```
username = context.args[0]
await update.message.reply_text(f"💬 Looking up Discord `{username}`...", parse_mode="Markdown")

result = f"💬 *Discord Lookup: `{username}`*\n\n"
result += f"🔗 *Search Links:*\n"
result += f"• [Discord.id](https://discord.id/?prefill={username})\n"
result += f"• [DiscordHub](https://discordhub.com/user/search?q={username})\n"
result += f"• [Discord Lookup](https://discordlookup.mesalytic.moe/)\n\n"
result += f"💡 *To get full info (badges, avatar, account age):*\n"
result += f"Find their User ID → use `/discordid <id>`\n\n"
result += f"*How to get Discord User ID:*\n"
result += f"1. Open Discord settings\n"
result += f"2. Enable Developer Mode\n"
result += f"3. Right-click any user → Copy ID"

await update.message.reply_text(result, parse_mode="Markdown", disable_web_page_preview=True)
```

# ─── OSINT: DISCORD ID ────────────────────────────────────

async def discord_id_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text(“Usage: `/discordid <user_id>`\nExample: `/discordid 123456789012345678`”, parse_mode=“Markdown”)
return

```
user_id = context.args[0]

if not user_id.isdigit():
    await update.message.reply_text("❌ Discord User ID must be numbers only!", parse_mode="Markdown")
    return

await update.message.reply_text(f"🔍 Looking up Discord ID `{user_id}`...", parse_mode="Markdown")

try:
    r = requests.get(
        f"https://discordlookup.mesalytic.moe/v1/user/{user_id}",
        timeout=10
    )

    if r.status_code == 200:
        data = r.json()
        username = data.get("username", "N/A")
        global_name = data.get("global_name", "N/A")
        avatar = data.get("avatar", {})
        avatar_url = avatar.get("link", "No avatar") if isinstance(avatar, dict) else "No avatar"
        created = data.get("created_at", "N/A")
        badges = data.get("badges", [])
        badge_names = ", ".join(badges) if badges else "None"
        bot = data.get("is_bot", False)

        result = (
            f"💬 *Discord User: `{user_id}`*\n\n"
            f"👤 Username: `{username}`\n"
            f"🏷️ Display Name: `{global_name}`\n"
            f"📅 Account Created: `{created}`\n"
            f"🏅 Badges: `{badge_names}`\n"
            f"🤖 Bot: `{'Yes' if bot else 'No'}`\n"
            f"🖼️ Avatar: [Click here]({avatar_url})\n"
        )
    elif r.status_code == 404:
        result = f"❌ Discord user ID `{user_id}` not found."
    else:
        result = f"⚠️ Could not fetch. Status: {r.status_code}"

except Exception as e:
    result = f"❌ Error: {str(e)}"

await update.message.reply_text(result, parse_mode="Markdown", disable_web_page_preview=True)
```

# ─── OSINT: SNAPCHAT ──────────────────────────────────────

async def snapchat_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text(“Usage: `/snapchat <username>`”, parse_mode=“Markdown”)
return

```
username = context.args[0]
await update.message.reply_text(f"👻 Looking up Snapchat `{username}`...", parse_mode="Markdown")

try:
    url = f"https://www.snapchat.com/add/{username}"
    r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})

    result = f"👻 *Snapchat Lookup: `{username}`*\n\n"

    if r.status_code == 200:
        if username.lower() in r.text.lower():
            result += f"✅ *Profile EXISTS!*\n\n"
            result += f"🔗 Add URL: [snapchat.com/add/{username}]({url})\n"
            result += f"👤 Username: `{username}`\n"
            result += f"📸 Snapcode: [View](https://app.snapchat.com/web/deeplink/snapcode?username={username}&type=SVG)\n"
        else:
            result += f"❌ User `{username}` not found on Snapchat."
    else:
        result += f"❌ User `{username}` not found on Snapchat."

except Exception as e:
    result = f"❌ Error: {str(e)}"

await update.message.reply_text(result, parse_mode="Markdown", disable_web_page_preview=True)
```

# ─── OSINT: PHONE ─────────────────────────────────────────

async def phone_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text(“Usage: `/phone <number>`\nExample: `/phone +9647501234567`”, parse_mode=“Markdown”)
return

```
phone = context.args[0]
await update.message.reply_text(f"📱 Looking up `{phone}`...", parse_mode="Markdown")

result = f"📱 *Phone Lookup: `{phone}`*\n\n"

if phone.startswith("+"):
    country_codes = {
        "1": "🇺🇸 USA/Canada", "44": "🇬🇧 UK", "49": "🇩🇪 Germany",
        "33": "🇫🇷 France", "7": "🇷🇺 Russia", "86": "🇨🇳 China",
        "91": "🇮🇳 India", "55": "🇧🇷 Brazil", "81": "🇯🇵 Japan",
        "964": "🇮🇶 Iraq", "966": "🇸🇦 Saudi Arabia", "971": "🇦🇪 UAE",
        "90": "🇹🇷 Turkey", "98": "🇮🇷 Iran", "92": "🇵🇰 Pakistan",
        "962": "🇯🇴 Jordan", "963": "🇸🇾 Syria", "961": "🇱🇧 Lebanon",
    }
    num = phone[1:]
    country = (country_codes.get(num[:3]) or
               country_codes.get(num[:2]) or
               country_codes.get(num[:1]) or "Unknown")

    result += f"🌍 Country: `{country}`\n"
    result += f"📞 Number: `{phone}`\n"
    result += f"🔢 Digits: `{len(num)}`\n\n"
    result += f"🔍 *Search this number:*\n"
    result += f"• [Truecaller](https://www.truecaller.com/search/us/{num})\n"
    result += f"• [WhoCalledMe](https://www.whocalledme.com/PhoneNumber/{num})\n"
    result += f"• [NumLookup](https://www.numlookup.com/)\n"
else:
    result += "⚠️ Please include country code\nExample: `/phone +9647501234567`"

await update.message.reply_text(result, parse_mode="Markdown", disable_web_page_preview=True)
```

# ─── OSINT: WHOIS ─────────────────────────────────────────

async def whois_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text(“Usage: `/whois <domain>`”, parse_mode=“Markdown”)
return

```
domain = context.args[0]
await update.message.reply_text(f"🔍 WHOIS lookup for `{domain}`...", parse_mode="Markdown")

try:
    r = requests.get(f"https://rdap.org/domain/{domain}", timeout=10)
    data = r.json()

    status = data.get("status", [])
    events = data.get("events", [])

    registered = updated = expires = "N/A"
    for e in events:
        action = e.get("eventAction", "")
        date = e.get("eventDate", "N/A")[:10]
        if action == "registration":
            registered = date
        elif action == "last changed":
            updated = date
        elif action == "expiration":
            expires = date

    nameservers = [ns.get("ldhName", "") for ns in data.get("nameservers", [])]

    result = (
        f"🌐 *WHOIS: {domain}*\n\n"
        f"📅 Registered: `{registered}`\n"
        f"🔄 Updated: `{updated}`\n"
        f"⏰ Expires: `{expires}`\n"
        f"📊 Status: `{', '.join(status[:2]) if status else 'N/A'}`\n"
        f"🖥️ Nameservers: `{', '.join(nameservers[:2]) if nameservers else 'N/A'}`\n"
    )
except Exception as e:
    result = f"❌ Error: {str(e)}"

await update.message.reply_text(result, parse_mode="Markdown")
```

# ─── OSINT: DNS ───────────────────────────────────────────

async def dns_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text(“Usage: `/dns <domain>`”, parse_mode=“Markdown”)
return

```
domain = context.args[0]
await update.message.reply_text(f"🔍 DNS records for `{domain}`...", parse_mode="Markdown")

try:
    r = requests.get(f"https://dns.google/resolve?name={domain}&type=ANY", timeout=10)
    data = r.json()
    answers = data.get("Answer", [])

    if not answers:
        await update.message.reply_text(f"No DNS records found for `{domain}`", parse_mode="Markdown")
        return

    type_map = {1: "A", 2: "NS", 5: "CNAME", 15: "MX", 16: "TXT", 28: "AAAA"}
    result = f"🌐 *DNS Records: {domain}*\n\n"
    for ans in answers[:15]:
        rtype = type_map.get(ans.get("type", 0), str(ans.get("type", "?")))
        data_val = ans.get("data", "")
        result += f"`{rtype}` → `{data_val}`\n"

except Exception as e:
    result = f"❌ Error: {str(e)}"

await update.message.reply_text(result, parse_mode="Markdown")
```

# ─── OSINT: IP INFO ───────────────────────────────────────

async def ip_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text(“Usage: `/ip <ip_address>`”, parse_mode=“Markdown”)
return

```
ip = context.args[0]
await update.message.reply_text(f"🔍 Looking up `{ip}`...", parse_mode="Markdown")

try:
    r = requests.get(f"https://ipapi.co/{ip}/json/", timeout=10)
    data = r.json()
    result = (
        f"🌍 *IP Info: `{ip}`*\n\n"
        f"📍 Location: `{data.get('city', 'N/A')}, {data.get('region', 'N/A')}, {data.get('country_name', 'N/A')}`\n"
        f"🏢 ISP/Org: `{data.get('org', 'N/A')}`\n"
        f"🌐 ASN: `{data.get('asn', 'N/A')}`\n"
        f"🕐 Timezone: `{data.get('timezone', 'N/A')}`\n"
        f"📮 Postal: `{data.get('postal', 'N/A')}`\n"
        f"🗺️ Lat/Lon: `{data.get('latitude', 'N/A')}, {data.get('longitude', 'N/A')}`\n"
    )
except Exception as e:
    result = f"❌ Error: {str(e)}"

await update.message.reply_text(result, parse_mode="Markdown")
```

# ─── OSINT: SUBDOMAINS ────────────────────────────────────

async def subdomains(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text(“Usage: `/subdomains <domain>`”, parse_mode=“Markdown”)
return

```
domain = context.args[0]
await update.message.reply_text(f"🔍 Finding subdomains for `{domain}`...", parse_mode="Markdown")

try:
    r = requests.get(f"https://crt.sh/?q=%.{domain}&output=json", timeout=15)
    data = r.json()
    subs = set()
    for entry in data:
        name = entry.get("name_value", "")
        for sub in name.split("\n"):
            sub = sub.strip().lstrip("*.")
            if sub.endswith(domain):
                subs.add(sub)

    if not subs:
        result = f"No subdomains found for `{domain}`"
    else:
        subs = sorted(list(subs))[:30]
        result = f"🔎 *Subdomains for {domain}* ({len(subs)} found):\n\n"
        result += "\n".join([f"`{s}`" for s in subs])

except Exception as e:
    result = f"❌ Error: {str(e)}"

await update.message.reply_text(result, parse_mode="Markdown")
```

# ─── OSINT: GOOGLE DORKS ─────────────────────────────────

async def dork(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text(“Usage: `/dork <domain or keyword>`”, parse_mode=“Markdown”)
return

```
target = " ".join(context.args)
dorks = [
    f"`site:{target} filetype:pdf`",
    f"`site:{target} filetype:xls OR filetype:xlsx`",
    f"`site:{target} inurl:admin`",
    f"`site:{target} inurl:login`",
    f"`site:{target} intext:password`",
    f"`site:{target} inurl:config`",
    f"`site:{target} \"index of\"`",
    f"`site:{target} inurl:backup`",
    f"`site:{target} ext:sql`",
    f"`site:{target} inurl:phpinfo`",
    f"`\"@{target}\" filetype:xls`",
    f"`site:pastebin.com \"{target}\"`",
]
result = f"🎯 *Google Dorks for: {target}*\n\n" + "\n".join(dorks)
result += "\n\n⚠️ _Use only on targets you have permission to test._"
await update.message.reply_text(result, parse_mode="Markdown")
```

# ─── NETWORK: PORT SCANNER ────────────────────────────────

async def port_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text(“Usage: `/portscan <host>`”, parse_mode=“Markdown”)
return

```
host = context.args[0]
common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 6379, 8080, 8443]
ports = common_ports

if len(context.args) > 1:
    try:
        ports = [int(p.strip()) for p in context.args[1].split(",")]
    except:
        pass

await update.message.reply_text(f"🔍 Scanning `{host}`...", parse_mode="Markdown")

open_ports = []
closed_ports = []

try:
    ip = socket.gethostbyname(host)
except socket.gaierror:
    await update.message.reply_text(f"❌ Could not resolve `{host}`", parse_mode="Markdown")
    return

for port in ports:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        r = sock.connect_ex((ip, port))
        sock.close()
        if r == 0:
            open_ports.append(port)
        else:
            closed_ports.append(port)
    except:
        closed_ports.append(port)

service_map = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 6379: "Redis",
    8080: "HTTP-Alt", 8443: "HTTPS-Alt"
}

result_text = f"🖥️ *Port Scan: {host}* (`{ip}`)\n\n"
if open_ports:
    result_text += "✅ *Open Ports:*\n"
    for p in open_ports:
        result_text += f"  `{p}` — {service_map.get(p, 'Unknown')}\n"
else:
    result_text += "❌ No open ports found\n"
result_text += f"\n🔒 Closed: {len(closed_ports)} ports"

await update.message.reply_text(result_text, parse_mode="Markdown")
```

# ─── NETWORK: PING ────────────────────────────────────────

async def ping_host(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text(“Usage: `/ping <host>`”, parse_mode=“Markdown”)
return

```
host = context.args[0]
await update.message.reply_text(f"📡 Pinging `{host}`...", parse_mode="Markdown")

try:
    output = subprocess.check_output(["ping", "-c", "4", host], stderr=subprocess.STDOUT, timeout=15, text=True)
    lines = output.strip().split("\n")
    summary = "\n".join(lines[-3:])
    result = f"📡 *Ping: {host}*\n\n```\n{summary}\n```"
except subprocess.CalledProcessError:
    result = f"❌ Host `{host}` is unreachable."
except Exception as e:
    result = f"❌ Error: {str(e)}"

await update.message.reply_text(result, parse_mode="Markdown")
```

# ─── NETWORK: HTTP HEADERS ────────────────────────────────

async def http_headers(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text(“Usage: `/headers <url>`”, parse_mode=“Markdown”)
return

```
url = context.args[0]
if not url.startswith("http"):
    url = "https://" + url

try:
    r = requests.head(url, timeout=10, allow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
    headers = dict(r.headers)
    security_headers = ["Strict-Transport-Security", "Content-Security-Policy", "X-Frame-Options", "X-Content-Type-Options", "Server"]
    result = f"📋 *HTTP Headers: {url}*\n\nStatus: `{r.status_code}`\n\n"
    for h in security_headers:
        val = headers.get(h, "Missing")
        icon = "✅" if h in headers else "⚠️"
        result += f"{icon} `{h}`: `{val[:50]}`\n"
except Exception as e:
    result = f"❌ Error: {str(e)}"

await update.message.reply_text(result, parse_mode="Markdown")
```

# ─── NETWORK: ROBOTS.TXT ─────────────────────────────────

async def robots_txt(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text(“Usage: `/robots <domain>`”, parse_mode=“Markdown”)
return

```
domain = context.args[0]
if not domain.startswith("http"):
    domain = "https://" + domain

try:
    r = requests.get(f"{domain}/robots.txt", timeout=10)
    content = r.text[:2000]
    result = f"🤖 *robots.txt for {domain}*\n\n```\n{content}\n```"
except Exception as e:
    result = f"❌ Error: {str(e)}"

await update.message.reply_text(result, parse_mode="Markdown")
```

# ─── NETWORK: SSL CHECK ───────────────────────────────────

async def ssl_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text(“Usage: `/sslcheck <domain>`”, parse_mode=“Markdown”)
return

```
domain = context.args[0]
await update.message.reply_text(f"🔐 Checking SSL for `{domain}`...", parse_mode="Markdown")

try:
    import ssl
    import socket as sock
    ctx = ssl.create_default_context()
    with ctx.wrap_socket(sock.socket(), server_hostname=domain) as s:
        s.settimeout(5)
        s.connect((domain, 443))
        cert = s.getpeercert()
        expires = cert.get("notAfter", "N/A")
        issuer = dict(x[0] for x in cert.get("issuer", []))
        subject = dict(x[0] for x in cert.get("subject", []))
        result = (
            f"🔐 *SSL Certificate: {domain}*\n\n"
            f"✅ SSL is *valid*\n"
            f"📅 Expires: `{expires}`\n"
            f"🏢 Issuer: `{issuer.get('organizationName', 'N/A')}`\n"
            f"🌐 Domain: `{subject.get('commonName', 'N/A')}`\n"
        )
except ssl.SSLError:
    result = f"❌ `{domain}` has an *invalid* SSL certificate!"
except Exception as e:
    result = f"❌ Error: {str(e)}"

await update.message.reply_text(result, parse_mode="Markdown")
```

# ─── SECURITY: TIPS ───────────────────────────────────────

async def security_tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
tips = [
“🔐 Use a password manager. Never reuse passwords.”,
“🛡️ Enable 2FA on every account.”,
“📡 Avoid public WiFi for sensitive tasks. Use a VPN.”,
“🔄 Keep your OS and apps updated.”,
“🎣 Phishing is the #1 attack vector. Verify sender emails.”,
“🔑 Use hardware security keys (YubiKey) for critical accounts.”,
“💾 Backup your data: 3-2-1 rule.”,
“🧅 Tor Browser hides your identity online.”,
“🔍 Google yourself to see what info is publicly available.”,
“📱 Check app permissions — does a flashlight need your contacts?”,
“🛜 Change your router’s default credentials.”,
“🔒 Full disk encryption protects lost devices.”,
“⚠️ Social engineering bypasses all technical defenses.”,
“🕵️ Use crt.sh and Shodan to audit your own domain.”,
“💡 Bug bounty programs pay you to find vulnerabilities legally.”,
“🔓 Never store passwords in plain text.”,
“📵 Cover your webcam when not in use.”,
]
tip = random.choice(tips)
await update.message.reply_text(f”💡 *Security Tip*\n\n{tip}”, parse_mode=“Markdown”)

# ─── SECURITY: TOOLS LIST ─────────────────────────────────

async def tools_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
result = (
“🧰 *Essential Cybersecurity Tools*\n\n”
“*Recon/OSINT*\n• `theHarvester` • `Amass` • `Shodan` • `Maltego` • `Sherlock`\n\n”
“*Scanning*\n• `Nmap` • `Nikto` • `Masscan`\n\n”
“*Exploitation*\n• `Metasploit` • `SQLmap` • `Burp Suite`\n\n”
“*Password*\n• `Hashcat` • `John the Ripper` • `Hydra`\n\n”
“*Wireless*\n• `Aircrack-ng` • `Wireshark`\n\n”
“*OS*\n• `Kali Linux` • `Parrot OS`\n”
)
await update.message.reply_text(result, parse_mode=“Markdown”)

# ─── SECURITY: CVE SEARCH ─────────────────────────────────

async def cve_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text(“Usage: `/cve <keyword>`”, parse_mode=“Markdown”)
return

```
keyword = " ".join(context.args)
await update.message.reply_text(f"🔍 Searching CVEs for `{keyword}`...", parse_mode="Markdown")

try:
    r = requests.get(f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={keyword}&resultsPerPage=5", timeout=15)
    data = r.json()
    vulns = data.get("vulnerabilities", [])

    if not vulns:
        await update.message.reply_text(f"No CVEs found for `{keyword}`", parse_mode="Markdown")
        return

    result = f"🚨 *CVEs for: {keyword}*\n\n"
    for v in vulns:
        cve = v.get("cve", {})
        cve_id = cve.get("id", "N/A")
        desc = cve.get("descriptions", [{}])[0].get("value", "N/A")[:150]
        metrics = cve.get("metrics", {})
        score = "N/A"
        if "cvssMetricV31" in metrics:
            score = metrics["cvssMetricV31"][0]["cvssData"]["baseScore"]
        result += f"*{cve_id}* (Score: `{score}`)\n{desc}...\n\n"

except Exception as e:
    result = f"❌ Error: {str(e)}"

await update.message.reply_text(result, parse_mode="Markdown")
```

# ─── SECURITY: HASH ───────────────────────────────────────

async def hash_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text(“Usage: `/hash <text>`”, parse_mode=“Markdown”)
return

```
text = " ".join(context.args).encode()
result = (
    f"#️⃣ *Hash Results*\n\n"
    f"`MD5`:    `{hashlib.md5(text).hexdigest()}`\n"
    f"`SHA1`:   `{hashlib.sha1(text).hexdigest()}`\n"
    f"`SHA256`: `{hashlib.sha256(text).hexdigest()}`\n"
    f"`SHA512`: `{hashlib.sha512(text).hexdigest()}`\n"
)
await update.message.reply_text(result, parse_mode="Markdown")
```

# ─── SECURITY: BASE64 ─────────────────────────────────────

async def encode_b64(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text(“Usage: `/encode <text>`”, parse_mode=“Markdown”)
return
text = “ “.join(context.args)
encoded = base64.b64encode(text.encode()).decode()
await update.message.reply_text(f”🔒 *Base64 Encoded:*\n`{encoded}`”, parse_mode=“Markdown”)

async def decode_b64(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text(“Usage: `/decode <text>`”, parse_mode=“Markdown”)
return
try:
text = “ “.join(context.args)
decoded = base64.b64decode(text.encode()).decode()
await update.message.reply_text(f”🔓 *Base64 Decoded:*\n`{decoded}`”, parse_mode=“Markdown”)
except:
await update.message.reply_text(“❌ Invalid Base64 string.”)

# ─── SECURITY: PASSWORD GENERATOR ────────────────────────

async def generate_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
import string
length = 16
if context.args:
try:
length = min(int(context.args[0]), 64)
except:
pass

```
chars = string.ascii_letters + string.digits + "!@#$%^&*"
password = ''.join(random.choice(chars) for _ in range(length))
result = (
    f"🔑 *Generated Password ({length} chars):*\n\n"
    f"`{password}`\n\n"
    f"💡 _Save this in a password manager!_"
)
await update.message.reply_text(result, parse_mode="Markdown")
```

# ─── MENU CALLBACKS ───────────────────────────────────────

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()
data = query.data

```
if data == "menu_osint":
    text = (
        "🔍 *OSINT Commands*\n\n"
        "`/username <n>` — 15 platforms\n"
        "`/email <email>` — Breach check\n"
        "`/discord <username>` — Discord lookup\n"
        "`/discordid <id>` — Discord ID info\n"
        "`/snapchat <username>` — Snapchat lookup\n"
        "`/whois <domain>` — WHOIS info\n"
        "`/dns <domain>` — DNS records\n"
        "`/ip <ip>` — IP geolocation\n"
        "`/subdomains <domain>` — Subdomains\n"
        "`/dork <target>` — Google dorks\n"
        "`/phone <number>` — Phone info\n"
    )
elif data == "menu_network":
    text = (
        "🌐 *Network Commands*\n\n"
        "`/portscan <host>` — Port scanner\n"
        "`/ping <host>` — Ping host\n"
        "`/headers <url>` — HTTP headers\n"
        "`/robots <domain>` — robots.txt\n"
        "`/sslcheck <domain>` — SSL certificate\n"
    )
elif data == "menu_security":
    text = (
        "🛡️ *Security Commands*\n\n"
        "`/tips` — Security tip\n"
        "`/tools` — Tools list\n"
        "`/cve <keyword>` — CVE search\n"
        "`/hash <text>` — Hash string\n"
        "`/encode <text>` — Base64 encode\n"
        "`/decode <text>` — Base64 decode\n"
        "`/password <length>` — Generate password\n"
    )
elif data == "menu_help":
    await help_command(update, context)
    return
else:
    return

await query.edit_message_text(text, parse_mode="Markdown")
```

# ─── MAIN ─────────────────────────────────────────────────

def main():
app = Application.builder().token(BOT_TOKEN).build()

```
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("username", username_lookup))
app.add_handler(CommandHandler("email", email_check))
app.add_handler(CommandHandler("discord", discord_lookup))
app.add_handler(CommandHandler("discordid", discord_id_lookup))
app.add_handler(CommandHandler("snapchat", snapchat_lookup))
app.add_handler(CommandHandler("phone", phone_lookup))
app.add_handler(CommandHandler("whois", whois_lookup))
app.add_handler(CommandHandler("dns", dns_lookup))
app.add_handler(CommandHandler("ip", ip_info))
app.add_handler(CommandHandler("subdomains", subdomains))
app.add_handler(CommandHandler("dork", dork))
app.add_handler(CommandHandler("portscan", port_scan))
app.add_handler(CommandHandler("ping", ping_host))
app.add_handler(CommandHandler("headers", http_headers))
app.add_handler(CommandHandler("robots", robots_txt))
app.add_handler(CommandHandler("sslcheck", ssl_check))
app.add_handler(CommandHandler("tips", security_tips))
app.add_handler(CommandHandler("tools", tools_list))
app.add_handler(CommandHandler("cve", cve_search))
app.add_handler(CommandHandler("hash", hash_text))
app.add_handler(CommandHandler("encode", encode_b64))
app.add_handler(CommandHandler("decode", decode_b64))
app.add_handler(CommandHandler("password", generate_password))
app.add_handler(CallbackQueryHandler(menu_callback))

print("🤖 CyvxBot is running...")
app.run_polling()
```

if **name** == “**main**”:
main()
