import aiohttp
import time
import os
import socket
import requests
import subprocess
import hashlib
import base64
import random
import string
import ssl as ssl_lib
from datetime import datetime, timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
# 🔥 cooldown system
user_cooldowns = {}

def is_spamming(user_id):
    now = time.time()

    if user_id in user_cooldowns:
        if now - user_cooldowns[user_id] < 3:
            return True

    user_cooldowns[user_id] = now
    return False

BOT_TOKEN = os.environ.get("BOT_TOKEN")

SEPARATOR = "━━━━━━━━━━━━━━━━━━━━━━"
WARNING = "⚠️ *WARNING:* Use only on systems you own or have permission to test. Unauthorized use is illegal."

# ================================================================
# START
# ================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 OSINT", callback_data="menu_osint"),
         InlineKeyboardButton("🌐 Network", callback_data="menu_network")],
        [InlineKeyboardButton("🔐 Security", callback_data="menu_security"),
         InlineKeyboardButton("📖 Help", callback_data="menu_help")],
    ]
    text = (
        f"{SEPARATOR}\n"
        "🕵️ *CyvxBot — OSINT & Security Toolkit*\n"
        f"{SEPARATOR}\n\n"
        "Professional cybersecurity intelligence tool.\n\n"
        "All data is pulled from *real public sources*.\n"
        "Every command returns real information.\n\n"
        f"⚠️ *For educational and authorized use only.*\n"
        f"{SEPARATOR}"
    )
    await update.message.reply_text(text, parse_mode="Markdown",
                                     reply_markup=InlineKeyboardMarkup(keyboard))

# ================================================================
# HELP
# ================================================================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"{SEPARATOR}\n"
        "📖 *ALL COMMANDS*\n"
        f"{SEPARATOR}\n\n"
        "*🔍 OSINT*\n"
        "`/ip <address>` — IP location & threat info\n"
        "`/whois <domain>` — Domain ownership info\n"
        "`/dns <domain>` — DNS records\n"
        "`/subdomains <domain>` — Find subdomains\n"
        "`/github <username>` — GitHub profile intel\n"
        "`/reddit <username>` — Reddit profile intel\n"
        "`/snowflake <discord_id>` — Discord ID decoder\n"
        "`/phone <+number>` — Phone number info\n"
        "`/email <email>` — Email intelligence\n"
        "`/username <name>` — Username search\n"
        "`/dork <target>` — Google dork generator\n\n"
        "*🌐 Network*\n"
        "`/portscan <host>` — Scan open ports\n"
        "`/ping <host>` — Ping a host\n"
        "`/headers <url>` — HTTP security headers\n"
        "`/sslcheck <domain>` — SSL certificate info\n"
        "`/robots <domain>` — robots.txt viewer\n"
        "`/techstack <url>` — Detect tech stack\n"
        "`/urlscan <url>` — Scan URL for threats\n"
        "`/wayback <url>` — Archive history\n\n"
        "*🔐 Security*\n"
        "`/hash <text>` — Generate hashes\n"
        "`/crack <hash>` — Crack MD5 hash\n"
        "`/encode <text>` — Base64 encode\n"
        "`/decode <text>` — Base64 decode\n"
        "`/password <length>` — Generate password\n"
        "`/cve <keyword>` — Search CVEs\n"
        "`/tips` — Security tips\n"
        "`/tools` — Security tools list\n\n"
        f"{WARNING}"
    )
    msg = update.message or update.callback_query.message
    await msg.reply_text(text, parse_mode="Markdown")

# ================================================================
# IP LOOKUP
# ================================================================

async def ip_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/ip <address>`\nExample: `/ip 8.8.8.8`", parse_mode="Markdown")
        return

    ip = context.args[0]
    await update.message.reply_text(f"🔍 Investigating `{ip}`...", parse_mode="Markdown")

    try:
        async with session.get(f"https://ipapi.co/{ip}/json/") as r:
    data = await r.json()
    print(data)

        if d.get("error"):
            await update.message.reply_text(f"❌ Invalid IP address: `{ip}`", parse_mode="Markdown")
            return

        # Threat check
        try:
            threat = requests.get(f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip}",
                                  headers={"Key": "free", "Accept": "application/json"}, timeout=5)
            abuse_score = "N/A"
        except:
            abuse_score = "N/A"

        country_flag = d.get("country", "")
        text = (
            f"{SEPARATOR}\n"
            f"🌍 *IP INTELLIGENCE REPORT*\n"
            f"{SEPARATOR}\n\n"
            f"🎯 IP: `{ip}`\n"
            f"🌍 Country: `{d.get('country_name', 'N/A')}` {country_flag}\n"
            f"🏙️ City: `{d.get('city', 'N/A')}`\n"
            f"📍 Region: `{d.get('region', 'N/A')}`\n"
            f"🏢 ISP: `{d.get('org', 'N/A')}`\n"
            f"🌐 ASN: `{d.get('asn', 'N/A')}`\n"
            f"🕐 Timezone: `{d.get('timezone', 'N/A')}`\n"
            f"📮 Postal: `{d.get('postal', 'N/A')}`\n"
            f"🗺️ Coordinates: `{d.get('latitude', 'N/A')}, {d.get('longitude', 'N/A')}`\n\n"
            f"🔗 *Investigate further:*\n"
            f"• [Shodan](https://www.shodan.io/host/{ip})\n"
            f"• [VirusTotal](https://www.virustotal.com/gui/ip-address/{ip})\n"
            f"• [AbuseIPDB](https://www.abuseipdb.com/check/{ip})\n"
            f"{SEPARATOR}\n"
            f"{WARNING}"
        )
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"

    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================================================================
# WHOIS
# ================================================================

async def whois_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/whois <domain>`\nExample: `/whois google.com`", parse_mode="Markdown")
        return

    domain = context.args[0].lower().replace("https://", "").replace("http://", "").split("/")[0]
    await update.message.reply_text(f"🔍 Running WHOIS on `{domain}`...", parse_mode="Markdown")

    try:
        r = requests.get(f"https://rdap.org/domain/{domain}", timeout=10)
        d = r.json()

        events = d.get("events", [])
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

        status = d.get("status", [])
        nameservers = [ns.get("ldhName", "") for ns in d.get("nameservers", [])]

        text = (
            f"{SEPARATOR}\n"
            f"🌐 *WHOIS REPORT: {domain}*\n"
            f"{SEPARATOR}\n\n"
            f"📅 Registered: `{registered}`\n"
            f"🔄 Last Updated: `{updated}`\n"
            f"⏰ Expires: `{expires}`\n"
            f"📊 Status: `{', '.join(status[:2]) if status else 'N/A'}`\n"
            f"🖥️ Nameservers:\n"
        )
        for ns in nameservers[:4]:
            text += f"  • `{ns}`\n"

        text += (
            f"\n🔗 *Investigate further:*\n"
            f"• [ViewDNS](https://viewdns.info/whois/?domain={domain})\n"
            f"• [DomainTools](https://whois.domaintools.com/{domain})\n"
            f"{SEPARATOR}\n"
            f"{WARNING}"
        )
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"

    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================================================================
# DNS
# ================================================================

async def dns_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/dns <domain>`\nExample: `/dns google.com`", parse_mode="Markdown")
        return

    domain = context.args[0]
    await update.message.reply_text(f"🔍 Fetching DNS records for `{domain}`...", parse_mode="Markdown")

    try:
        type_map = {1: "A", 2: "NS", 5: "CNAME", 15: "MX", 16: "TXT", 28: "AAAA"}
        records = {}

        for rtype in [1, 28, 15, 2, 16, 5]:
            r = requests.get(f"https://dns.google/resolve?name={domain}&type={rtype}", timeout=10)
            d = r.json()
            answers = d.get("Answer", [])
            for ans in answers:
                t = type_map.get(ans.get("type", 0), "OTHER")
                if t not in records:
                    records[t] = []
                records[t].append(ans.get("data", ""))

        if not records:
            await update.message.reply_text(f"❌ No DNS records found for `{domain}`", parse_mode="Markdown")
            return

        text = (
            f"{SEPARATOR}\n"
            f"🌐 *DNS RECORDS: {domain}*\n"
            f"{SEPARATOR}\n\n"
        )
        for rtype, values in records.items():
            text += f"*{rtype} Records:*\n"
            for v in values[:5]:
                text += f"  • `{v}`\n"
            text += "\n"

        text += f"{SEPARATOR}\n{WARNING}"
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"

    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# SUBDOMAINS
# ================================================================

async def subdomains(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/subdomains <domain>`\nExample: `/subdomains google.com`", parse_mode="Markdown")
        return

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
                if sub.endswith(domain) and sub != domain:
                    subs.add(sub)

        if not subs:
            await update.message.reply_text(f"❌ No subdomains found for `{domain}`", parse_mode="Markdown")
            return

        subs = sorted(list(subs))
        text = (
            f"{SEPARATOR}\n"
            f"🔎 *SUBDOMAINS: {domain}*\n"
            f"{SEPARATOR}\n\n"
            f"Found *{len(subs)}* subdomains:\n\n"
        )
        for s in subs[:30]:
            text += f"• `{s}`\n"

        if len(subs) > 30:
            text += f"\n_...and {len(subs) - 30} more_\n"

        text += f"\n{SEPARATOR}\n{WARNING}"
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"

    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# GITHUB
# ================================================================

async def github_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/github <username>`\nExample: `/github torvalds`", parse_mode="Markdown")
        return

    username = context.args[0]
    await update.message.reply_text(f"🔍 Investigating GitHub user `{username}`...", parse_mode="Markdown")

    try:
        r = requests.get(f"https://api.github.com/users/{username}",
                         headers={"User-Agent": "CyvxBot"}, timeout=10)

        if r.status_code == 404:
            await update.message.reply_text(f"❌ GitHub user `{username}` not found.", parse_mode="Markdown")
            return

        d = r.json()

        # Get repos
        repos_r = requests.get(f"https://api.github.com/users/{username}/repos?per_page=5&sort=updated",
                                headers={"User-Agent": "CyvxBot"}, timeout=10)
        repos = repos_r.json() if repos_r.status_code == 200 else []

        created = d.get("created_at", "N/A")[:10]
        updated = d.get("updated_at", "N/A")[:10]

        text = (
            f"{SEPARATOR}\n"
            f"💻 *GITHUB INTELLIGENCE: {username}*\n"
            f"{SEPARATOR}\n\n"
            f"👤 Name: `{d.get('name', 'N/A')}`\n"
            f"📧 Email: `{d.get('email', 'Hidden/None')}`\n"
            f"🌍 Location: `{d.get('location', 'N/A')}`\n"
            f"🏢 Company: `{d.get('company', 'N/A')}`\n"
            f"🔗 Blog: `{d.get('blog', 'N/A')}`\n"
            f"📝 Bio: `{d.get('bio', 'N/A')}`\n\n"
            f"📊 *Stats:*\n"
            f"• Repos: `{d.get('public_repos', 0)}`\n"
            f"• Followers: `{d.get('followers', 0)}`\n"
            f"• Following: `{d.get('following', 0)}`\n"
            f"• Gists: `{d.get('public_gists', 0)}`\n\n"
            f"📅 Created: `{created}`\n"
            f"🔄 Last Active: `{updated}`\n\n"
        )

        if repos:
            text += f"📁 *Recent Repos:*\n"
            for repo in repos[:5]:
                lang = repo.get("language", "N/A")
                stars = repo.get("stargazers_count", 0)
                text += f"• [{repo['name']}](https://github.com/{username}/{repo['name']}) — ⭐{stars} — `{lang}`\n"

        text += (
            f"\n🔗 Profile: [github.com/{username}](https://github.com/{username})\n"
            f"{SEPARATOR}\n{WARNING}"
        )
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"

    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================================================================
# REDDIT
# ================================================================

async def reddit_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/reddit <username>`\nExample: `/reddit spez`", parse_mode="Markdown")
        return

    username = context.args[0]
    await update.message.reply_text(f"🔍 Investigating Reddit user `{username}`...", parse_mode="Markdown")

    try:
        r = requests.get(f"https://www.reddit.com/user/{username}/about.json",
                         headers={"User-Agent": "CyvxBot/1.0"}, timeout=10)

        if r.status_code == 404:
            await update.message.reply_text(f"❌ Reddit user `{username}` not found.", parse_mode="Markdown")
            return

        d = r.json().get("data", {})
        created = datetime.fromtimestamp(d.get("created_utc", 0), tz=timezone.utc).strftime("%Y-%m-%d")
        cake_day = datetime.fromtimestamp(d.get("created_utc", 0), tz=timezone.utc).strftime("%B %d")

        text = (
            f"{SEPARATOR}\n"
            f"🤖 *REDDIT INTELLIGENCE: u/{username}*\n"
            f"{SEPARATOR}\n\n"
            f"👤 Username: `u/{username}`\n"
            f"📅 Account Created: `{created}`\n"
            f"🎂 Cake Day: `{cake_day}`\n\n"
            f"📊 *Stats:*\n"
            f"• Post Karma: `{d.get('link_karma', 0):,}`\n"
            f"• Comment Karma: `{d.get('comment_karma', 0):,}`\n"
            f"• Total Karma: `{d.get('total_karma', 0):,}`\n\n"
            f"✅ Verified Email: `{'Yes' if d.get('has_verified_email') else 'No'}`\n"
            f"🥇 Reddit Premium: `{'Yes' if d.get('is_gold') else 'No'}`\n"
            f"🛡️ Moderator: `{'Yes' if d.get('is_mod') else 'No'}`\n"
            f"🤖 Bot: `{'Yes' if d.get('is_employee') else 'No'}`\n\n"
            f"🔗 Profile: [reddit.com/u/{username}](https://reddit.com/u/{username})\n"
            f"{SEPARATOR}\n{WARNING}"
        )
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"

    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================================================================
# DISCORD SNOWFLAKE
# ================================================================

async def snowflake(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/snowflake <discord_id>`\nExample: `/snowflake 123456789012345678`", parse_mode="Markdown")
        return

    user_id = context.args[0]
    if not user_id.isdigit():
        await update.message.reply_text("❌ Discord ID must be numbers only!", parse_mode="Markdown")
        return

    await update.message.reply_text(f"🔍 Decoding Discord ID `{user_id}`...", parse_mode="Markdown")

    try:
        # Decode snowflake timestamp
        discord_epoch = 1420070400000
        timestamp_ms = (int(user_id) >> 22) + discord_epoch
        created_at = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)

        # Calculate account age
        age = datetime.now(tz=timezone.utc) - created_at
        years = age.days // 365
        months = (age.days % 365) // 30
        days = age.days % 30

        # Try API lookup
        try:
            r = requests.get(f"https://discordlookup.mesalytic.moe/v1/user/{user_id}", timeout=10)
            if r.status_code == 200:
                d = r.json()
                username = d.get("username", "N/A")
                global_name = d.get("global_name", "N/A")
                avatar = d.get("avatar", {})
                avatar_url = avatar.get("link", "N/A") if isinstance(avatar, dict) else "N/A"
                badges = d.get("badges", [])
                is_bot = d.get("is_bot", False)
                badge_text = ", ".join(badges) if badges else "None"
            else:
                username = "N/A"
                global_name = "N/A"
                avatar_url = "N/A"
                badge_text = "N/A"
                is_bot = False
        except:
            username = "N/A"
            global_name = "N/A"
            avatar_url = "N/A"
            badge_text = "N/A"
            is_bot = False

        text = (
            f"{SEPARATOR}\n"
            f"💬 *DISCORD ID INTELLIGENCE*\n"
            f"{SEPARATOR}\n\n"
            f"🆔 ID: `{user_id}`\n"
            f"👤 Username: `{username}`\n"
            f"🏷️ Display Name: `{global_name}`\n"
            f"🤖 Bot Account: `{'Yes' if is_bot else 'No'}`\n\n"
            f"📅 *Account Created:*\n"
            f"• Date: `{created_at.strftime('%B %d, %Y')}`\n"
            f"• Time: `{created_at.strftime('%H:%M:%S UTC')}`\n"
            f"• Age: `{years}y {months}m {days}d`\n\n"
            f"🏅 Badges: `{badge_text}`\n"
            f"🖼️ Avatar: {'[Click here](' + avatar_url + ')' if avatar_url != 'N/A' else '`None`'}\n\n"
            f"💡 *What badges mean:*\n"
            f"• Early Supporter = joined before 2018\n"
            f"• Bug Hunter = found Discord bugs\n"
            f"• Staff = Discord employee\n"
            f"• Nitro = pays for Discord premium\n"
            f"{SEPARATOR}\n{WARNING}"
        )
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"

    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================================================================
# PHONE
# ================================================================

async def phone_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/phone <+number>`\nExample: `/phone +9647501234567`", parse_mode="Markdown")
        return

    phone = context.args[0]
    await update.message.reply_text(f"🔍 Investigating `{phone}`...", parse_mode="Markdown")

    country_codes = {
        "1": "🇺🇸 USA/Canada", "44": "🇬🇧 United Kingdom",
        "49": "🇩🇪 Germany", "33": "🇫🇷 France",
        "7": "🇷🇺 Russia", "86": "🇨🇳 China",
        "91": "🇮🇳 India", "55": "🇧🇷 Brazil",
        "81": "🇯🇵 Japan", "964": "🇮🇶 Iraq",
        "966": "🇸🇦 Saudi Arabia", "971": "🇦🇪 UAE",
        "90": "🇹🇷 Turkey", "98": "🇮🇷 Iran",
        "92": "🇵🇰 Pakistan", "962": "🇯🇴 Jordan",
        "963": "🇸🇾 Syria", "961": "🇱🇧 Lebanon",
        "20": "🇪🇬 Egypt", "212": "🇲🇦 Morocco",
        "216": "🇹🇳 Tunisia", "213": "🇩🇿 Algeria",
    }

    if not phone.startswith("+"):
        await update.message.reply_text("❌ Please include country code\nExample: `/phone +9647501234567`", parse_mode="Markdown")
        return

    num = phone[1:]
    country = (country_codes.get(num[:3]) or
               country_codes.get(num[:2]) or
               country_codes.get(num[:1]) or "🌍 Unknown")

    text = (
        f"{SEPARATOR}\n"
        f"📱 *PHONE INTELLIGENCE*\n"
        f"{SEPARATOR}\n\n"
        f"📞 Number: `{phone}`\n"
        f"🌍 Country: `{country}`\n"
        f"🔢 Digits: `{len(num)}`\n\n"
        f"🔍 *Search this number:*\n"
        f"• [Truecaller](https://www.truecaller.com/search/us/{num})\n"
        f"• [WhoCalledMe](https://www.whocalledme.com/PhoneNumber/{num})\n"
        f"• [NumLookup](https://www.numlookup.com/)\n"
        f"• [SpyDialer](https://www.spydialer.com/)\n\n"
        f"💡 Click the links above to find owner name and carrier\n"
        f"{SEPARATOR}\n{WARNING}"
    )

    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================================================================
# EMAIL
# ================================================================

async def email_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/email <email>`\nExample: `/email test@gmail.com`", parse_mode="Markdown")
        return

    email = context.args[0]
    await update.message.reply_text(f"🔍 Investigating `{email}`...", parse_mode="Markdown")

    results = []

    # Check 1: Domain MX records
    try:
        domain = email.split("@")[1]
        r = requests.get(f"https://dns.google/resolve?name={domain}&type=MX", timeout=5)
        d = r.json()
        if d.get("Answer"):
            results.append(f"✅ Domain `{domain}` is *valid* — has mail servers")
        else:
            results.append(f"❌ Domain `{domain}` has *no mail servers* — likely fake email")
    except:
        results.append("⚠️ Could not verify domain")

    # Check 2: Disposable email check
    try:
        disposable_domains = ["guerrillamail.com", "tempmail.com", "10minutemail.com",
                              "throwaway.email", "mailinator.com", "yopmail.com",
                              "trashmail.com", "sharklasers.com", "temp-mail.org"]
        domain = email.split("@")[1]
        if domain in disposable_domains:
            results.append(f"🚨 `{domain}` is a *disposable/temporary* email service!")
        else:
            results.append(f"✅ `{domain}` is *not* a known disposable email service")
    except:
        pass

    # Check 3: Gravatar
    try:
        email_hash = hashlib.md5(email.lower().encode()).hexdigest()
        r = requests.get(f"https://www.gravatar.com/{email_hash}.json", timeout=5)
        if r.status_code == 200:
            d = r.json()
            name = d.get("entry", [{}])[0].get("displayName", "Unknown")
            results.append(f"👤 Gravatar profile found!\n  • Display Name: *{name}*\n  • This email has an online presence")
        else:
            results.append("❌ No Gravatar profile linked to this email")
    except:
        results.append("⚠️ Gravatar check unavailable")

    text = (
        f"{SEPARATOR}\n"
        f"📧 *EMAIL INTELLIGENCE*\n"
        f"{SEPARATOR}\n\n"
        f"📧 Email: `{email}`\n\n"
        f"*Checks:*\n"
        + "\n".join(results) +
        f"\n\n🔍 *Check for breaches:*\n"
        f"• [HaveIBeenPwned](https://haveibeenpwned.com/account/{email})\n"
        f"• [DeHashed](https://dehashed.com/search?query={email})\n"
        f"• [LeakCheck](https://leakcheck.io/)\n"
        f"{SEPARATOR}\n{WARNING}"
    )

    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================================================================
# USERNAME
# ================================================================

async def username_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/username <name>`\nExample: `/username johndoe`", parse_mode="Markdown")
        return

    username = context.args[0]
    platforms = {
        "GitHub": f"https://github.com/{username}",
        "Reddit": f"https://reddit.com/user/{username}",
        "TikTok": f"https://tiktok.com/@{username}",
        "Telegram": f"https://t.me/{username}",
        "Pinterest": f"https://pinterest.com/{username}",
        "Twitch": f"https://twitch.tv/{username}",
        "Medium": f"https://medium.com/@{username}",
        "Steam": f"https://steamcommunity.com/id/{username}",
        "Snapchat": f"https://www.snapchat.com/add/{username}",
        "HackerNews": f"https://news.ycombinator.com/user?id={username}",
        "Dev.to": f"https://dev.to/{username}",
        "Spotify": f"https://open.spotify.com/user/{username}",
    }

    await update.message.reply_text(f"🔍 Searching `{username}` across {len(platforms)} platforms...", parse_mode="Markdown")

    found = []
    not_found = []

    for platform, url in platforms.items():
        try:
            r = requests.get(url, timeout=5, allow_redirects=True,
                             headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                found.append(f"✅ [{platform}]({url})")
            else:
                not_found.append(platform)
        except:
            not_found.append(platform)

    text = (
        f"{SEPARATOR}\n"
        f"👤 *USERNAME SEARCH: {username}*\n"
        f"{SEPARATOR}\n\n"
    )

    if found:
        text += f"*Found on {len(found)} platforms:*\n"
        text += "\n".join(found) + "\n\n"

    if not_found:
        text += f"*Not found on:* {', '.join(not_found)}\n"

    text += f"\n{SEPARATOR}\n{WARNING}"

    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================================================================
# DORK
# ================================================================

async def dork(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/dork <target>`\nExample: `/dork example.com`", parse_mode="Markdown")
        return

    target = " ".join(context.args)
    dorks = [
        f"site:{target} filetype:pdf",
        f"site:{target} filetype:xls OR filetype:xlsx",
        f"site:{target} inurl:admin",
        f"site:{target} inurl:login",
        f"site:{target} inurl:config",
        f"site:{target} \"index of\"",
        f"site:{target} inurl:backup",
        f"site:{target} ext:sql",
        f"site:{target} inurl:phpinfo",
        f"site:{target} intext:password",
        f"\"@{target}\" filetype:xls",
        f"site:pastebin.com \"{target}\"",
        f"site:github.com \"{target}\"",
        f"site:trello.com \"{target}\"",
    ]

    text = (
        f"{SEPARATOR}\n"
        f"🎯 *GOOGLE DORKS: {target}*\n"
        f"{SEPARATOR}\n\n"
        f"Copy these into Google:\n\n"
    )
    for d in dorks:
        text += f"`{d}`\n\n"

    text += f"{SEPARATOR}\n{WARNING}"
    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# PORT SCAN
# ================================================================

async def port_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/portscan <host>`\nExample: `/portscan google.com`", parse_mode="Markdown")
        return

    host = context.args[0]
    ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 6379, 8080, 8443]

    if len(context.args) > 1:
        try:
            ports = [int(p.strip()) for p in context.args[1].split(",")]
        except:
            pass

    await update.message.reply_text(f"🔍 Scanning ports on `{host}`...", parse_mode="Markdown")

    try:
        ip = socket.gethostbyname(host)
    except socket.gaierror:
        await update.message.reply_text(f"❌ Could not resolve `{host}`", parse_mode="Markdown")
        return

    open_ports = []
    closed_count = 0
    service_map = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
        53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP",
        443: "HTTPS", 445: "SMB", 3306: "MySQL", 3389: "RDP",
        5432: "PostgreSQL", 6379: "Redis", 8080: "HTTP-Alt", 8443: "HTTPS-Alt"
    }

    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            sock.close()
            if result == 0:
                open_ports.append(port)
            else:
                closed_count += 1
        except:
            closed_count += 1

    text = (
        f"{SEPARATOR}\n"
        f"🖥️ *PORT SCAN: {host}*\n"
        f"{SEPARATOR}\n\n"
        f"🎯 Target: `{host}` (`{ip}`)\n"
        f"🔍 Ports Scanned: `{len(ports)}`\n\n"
    )

    if open_ports:
        text += f"✅ *Open Ports ({len(open_ports)}):*\n"
        for p in open_ports:
            svc = service_map.get(p, "Unknown")
            risk = "🔴" if p in [23, 445, 3389] else "🟡" if p in [21, 25, 3306] else "🟢"
            text += f"  {risk} Port `{p}` — *{svc}*\n"
    else:
        text += "✅ No open ports found — host is well secured\n"

    text += (
        f"\n🔒 Closed/Filtered: `{closed_count}` ports\n"
        f"\n🔴 High Risk  🟡 Medium Risk  🟢 Low Risk\n"
        f"{SEPARATOR}\n{WARNING}"
    )

    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# PING
# ================================================================

async def ping_host(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/ping <host>`\nExample: `/ping google.com`", parse_mode="Markdown")
        return

    host = context.args[0]
    await update.message.reply_text(f"📡 Pinging `{host}`...", parse_mode="Markdown")

    try:
        output = subprocess.check_output(["ping", "-c", "4", host],
                                          stderr=subprocess.STDOUT, timeout=15, text=True)
        lines = output.strip().split("\n")
        summary = "\n".join(lines[-3:])
        text = (
            f"{SEPARATOR}\n"
            f"📡 *PING: {host}*\n"
            f"{SEPARATOR}\n\n"
            f"```\n{summary}\n```\n"
            f"{SEPARATOR}\n{WARNING}"
        )
    except subprocess.CalledProcessError:
        text = f"❌ Host `{host}` is *unreachable* or blocking ping."
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"

    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# HTTP HEADERS
# ================================================================

async def http_headers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/headers <url>`\nExample: `/headers google.com`", parse_mode="Markdown")
        return

    url = context.args[0]
    if not url.startswith("http"):
        url = "https://" + url

    await update.message.reply_text(f"🔍 Analyzing headers for `{url}`...", parse_mode="Markdown")

    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "Mozilla/5.0"})
        headers = dict(r.headers)

        security_headers = {
            "Strict-Transport-Security": "Prevents downgrade attacks",
            "Content-Security-Policy": "Prevents XSS attacks",
            "X-Frame-Options": "Prevents clickjacking",
            "X-Content-Type-Options": "Prevents MIME sniffing",
            "Referrer-Policy": "Controls referrer info",
            "Permissions-Policy": "Controls browser features",
        }

        server = headers.get("Server", "Hidden")
        powered = headers.get("X-Powered-By", "Hidden")

        text = (
            f"{SEPARATOR}\n"
            f"📋 *HTTP SECURITY ANALYSIS*\n"
            f"{SEPARATOR}\n\n"
            f"🎯 URL: `{url}`\n"
            f"📊 Status: `{r.status_code}`\n"
            f"🖥️ Server: `{server}`\n"
            f"⚙️ Powered By: `{powered}`\n\n"
            f"*Security Headers:*\n"
        )

        score = 0
        for h, desc in security_headers.items():
            if h in headers:
                text += f"✅ `{h}`\n   _{desc}_\n\n"
                score += 1
            else:
                text += f"❌ `{h}` *MISSING*\n   _{desc}_\n\n"

        grade = "A" if score >= 5 else "B" if score >= 4 else "C" if score >= 3 else "D" if score >= 2 else "F"
        text += (
            f"🏆 Security Grade: *{grade}* ({score}/6 headers present)\n"
            f"{SEPARATOR}\n{WARNING}"
        )
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"

    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# SSL CHECK
# ================================================================

async def ssl_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/sslcheck <domain>`\nExample: `/sslcheck google.com`", parse_mode="Markdown")
        return

    domain = context.args[0].replace("https://", "").replace("http://", "").split("/")[0]
    await update.message.reply_text(f"🔐 Checking SSL for `{domain}`...", parse_mode="Markdown")

    try:
        ctx = ssl_lib.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(5)
            s.connect((domain, 443))
            cert = s.getpeercert()

        expires_str = cert.get("notAfter", "N/A")
        issued_str = cert.get("notBefore", "N/A")
        issuer = dict(x[0] for x in cert.get("issuer", []))
        subject = dict(x[0] for x in cert.get("subject", []))
        san = cert.get("subjectAltName", [])
        domains = [d[1] for d in san if d[0] == "DNS"]

        # Check expiry
        try:
            expires = datetime.strptime(expires_str, "%b %d %H:%M:%S %Y %Z")
            days_left = (expires - datetime.utcnow()).days
            expiry_status = f"🟢 {days_left} days left" if days_left > 30 else f"🔴 EXPIRES SOON: {days_left} days!"
        except:
            expiry_status = expires_str

        text = (
            f"{SEPARATOR}\n"
            f"🔐 *SSL CERTIFICATE REPORT*\n"
            f"{SEPARATOR}\n\n"
            f"🎯 Domain: `{domain}`\n"
            f"✅ SSL Status: *VALID*\n\n"
            f"📅 Issued: `{issued_str}`\n"
            f"⏰ Expires: `{expires_str}`\n"
            f"📊 Status: {expiry_status}\n\n"
            f"🏢 Issuer: `{issuer.get('organizationName', 'N/A')}`\n"
            f"🌐 Common Name: `{subject.get('commonName', 'N/A')}`\n\n"
            f"🔗 *Covered Domains:*\n"
        )
        for d in domains[:5]:
            text += f"  • `{d}`\n"

        text += f"\n{SEPARATOR}\n{WARNING}"

    except ssl_lib.SSLError:
        text = f"❌ `{domain}` has an *INVALID* SSL certificate!\n\n⚠️ This site may be dangerous."
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"

    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# ROBOTS
# ================================================================

async def robots_txt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/robots <domain>`\nExample: `/robots google.com`", parse_mode="Markdown")
        return

    domain = context.args[0]
    if not domain.startswith("http"):
        domain = "https://" + domain

    try:
        r = requests.get(f"{domain}/robots.txt", timeout=10)
        content = r.text[:2000]
        text = (
            f"{SEPARATOR}\n"
            f"🤖 *ROBOTS.TXT: {domain}*\n"
            f"{SEPARATOR}\n\n"
            f"💡 Pages the site tries to hide from search engines:\n\n"
            f"```\n{content}\n```\n"
            f"{SEPARATOR}\n{WARNING}"
        )
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"

    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# TECH STACK
# ================================================================

async def techstack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/techstack <url>`\nExample: `/techstack google.com`", parse_mode="Markdown")
        return

    url = context.args[0]
    if not url.startswith("http"):
        url = "https://" + url

    await update.message.reply_text(f"🔍 Detecting tech stack for `{url}`...", parse_mode="Markdown")

    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        headers = dict(r.headers)
        body = r.text[:5000]

        detected = []

        # Server
        server = headers.get("Server", "")
        if server:
            detected.append(f"🖥️ Server: `{server}`")

        powered = headers.get("X-Powered-By", "")
        if powered:
            detected.append(f"⚙️ Powered By: `{powered}`")

        # CMS detection
        if "wp-content" in body or "wp-includes" in body:
            detected.append("📝 CMS: `WordPress`")
        elif "Drupal" in body:
            detected.append("📝 CMS: `Drupal`")
        elif "Joomla" in body:
            detected.append("📝 CMS: `Joomla`")
        elif "shopify" in body.lower():
            detected.append("🛒 Platform: `Shopify`")
        elif "squarespace" in body.lower():
            detected.append("🌐 Platform: `Squarespace`")
        elif "wix.com" in body.lower():
            detected.append("🌐 Platform: `Wix`")

        # JS Frameworks
        if "react" in body.lower() or "reactdom" in body.lower():
            detected.append("⚛️ Framework: `React`")
        if "vue.js" in body.lower() or "vuejs" in body.lower():
            detected.append("💚 Framework: `Vue.js`")
        if "angular" in body.lower():
            detected.append("🔴 Framework: `Angular`")
        if "jquery" in body.lower():
            detected.append("📦 Library: `jQuery`")
        if "next.js" in body.lower() or "__next" in body:
            detected.append("▲ Framework: `Next.js`")

        # CDN
        if "cloudflare" in str(headers).lower():
            detected.append("☁️ CDN: `Cloudflare`")
        elif "akamai" in str(headers).lower():
            detected.append("☁️ CDN: `Akamai`")
        elif "fastly" in str(headers).lower():
            detected.append("☁️ CDN: `Fastly`")

        # Analytics
        if "google-analytics" in body or "gtag" in body:
            detected.append("📊 Analytics: `Google Analytics`")
        if "hotjar" in body.lower():
            detected.append("📊 Analytics: `Hotjar`")

        text = (
            f"{SEPARATOR}\n"
            f"🔬 *TECH STACK: {url}*\n"
            f"{SEPARATOR}\n\n"
        )

        if detected:
            text += "*Detected Technologies:*\n\n"
            for tech in detected:
                text += f"• {tech}\n"
        else:
            text += "❌ Could not detect specific technologies\n"

        text += f"\n{SEPARATOR}\n{WARNING}"

    except Exception as e:
        text = f"❌ Error: `{str(e)}`"

    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# URL SCAN
# ================================================================

async def urlscan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/urlscan <url>`\nExample: `/urlscan google.com`", parse_mode="Markdown")
        return

    url = context.args[0]
    if not url.startswith("http"):
        url = "https://" + url

    await update.message.reply_text(f"🔍 Scanning `{url}` for threats...", parse_mode="Markdown")

    try:
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]

        text = (
            f"{SEPARATOR}\n"
            f"🛡️ *URL THREAT SCAN: {url}*\n"
            f"{SEPARATOR}\n\n"
            f"🔍 *Scan with these free tools:*\n\n"
            f"• [VirusTotal](https://www.virustotal.com/gui/url/{url}) — 70+ antivirus engines\n"
            f"• [URLScan.io](https://urlscan.io/search/#{domain}) — Full page analysis\n"
            f"• [Google Safe Browsing](https://transparencyreport.google.com/safe-browsing/search?url={url}) — Google blacklist\n"
            f"• [PhishTank](https://www.phishtank.com/index.php) — Phishing database\n"
            f"• [URLVoid](https://www.urlvoid.com/scan/{domain}/) — Multiple blacklists\n\n"
            f"💡 Click the links above for real-time threat analysis\n"
            f"{SEPARATOR}\n{WARNING}"
        )
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"

    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================================================================
# WAYBACK
# ================================================================

async def wayback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/wayback <url>`\nExample: `/wayback google.com`", parse_mode="Markdown")
        return

    url = context.args[0]
    await update.message.reply_text(f"🔍 Checking archive history for `{url}`...", parse_mode="Markdown")

    try:
        r = requests.get(f"https://archive.org/wayback/available?url={url}", timeout=10)
        d = r.json()

        snapshot = d.get("archived_snapshots", {}).get("closest", {})

        if snapshot:
            snap_url = snapshot.get("url", "N/A")
            snap_time = snapshot.get("timestamp", "N/A")
            available = snapshot.get("available", False)

            formatted_time = f"{snap_time[:4]}-{snap_time[4:6]}-{snap_time[6:8]} {snap_time[8:10]}:{snap_time[10:12]}" if len(snap_time) >= 12 else snap_time

            text = (
                f"{SEPARATOR}\n"
                f"📚 *WAYBACK MACHINE: {url}*\n"
                f"{SEPARATOR}\n\n"
                f"✅ Archive found!\n\n"
                f"📅 Latest Snapshot: `{formatted_time}`\n"
                f"🔗 [View Archived Page]({snap_url})\n\n"
                f"📖 [Full History](https://web.archive.org/web/*/{url})\n"
                f"{SEPARATOR}\n{WARNING}"
            )
        else:
            text = (
                f"{SEPARATOR}\n"
                f"📚 *WAYBACK MACHINE: {url}*\n"
                f"{SEPARATOR}\n\n"
                f"❌ No archive snapshots found\n\n"
                f"🔗 [Search manually](https://web.archive.org/web/*/{url})\n"
                f"{SEPARATOR}\n{WARNING}"
            )
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"

    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================================================================
# HASH
# ================================================================

async def hash_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/hash <text>`\nExample: `/hash hello world`", parse_mode="Markdown")
        return

    text_input = " ".join(context.args).encode()
    text = (
        f"{SEPARATOR}\n"
        f"#️⃣ *HASH GENERATOR*\n"
        f"{SEPARATOR}\n\n"
        f"📝 Input: `{' '.join(context.args)}`\n\n"
        f"*Results:*\n"
        f"`MD5`:    `{hashlib.md5(text_input).hexdigest()}`\n"
        f"`SHA1`:   `{hashlib.sha1(text_input).hexdigest()}`\n"
        f"`SHA256`: `{hashlib.sha256(text_input).hexdigest()}`\n"
        f"`SHA512`: `{hashlib.sha512(text_input).hexdigest()}`\n\n"
        f"💡 Hashes are one-way — they cannot be reversed\n"
        f"{SEPARATOR}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# CRACK HASH
# ================================================================

async def crack_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/crack <hash>`\nExample: `/crack 5d41402abc4b2a76b9719d911017c592`", parse_mode="Markdown")
        return

    hash_val = context.args[0]
    await update.message.reply_text(f"🔓 Attempting to crack `{hash_val}`...", parse_mode="Markdown")

    try:
        # Try MD5 crack via free API
        r = requests.get(f"https://md5decrypt.net/Api/api.php?hash={hash_val}&hash_type=md5&email=free&code=free", timeout=10)
        result = r.text.strip()

        if result and result != "Not found":
            text = (
                f"{SEPARATOR}\n"
                f"🔓 *HASH CRACKED!*\n"
                f"{SEPARATOR}\n\n"
                f"🔐 Hash: `{hash_val}`\n"
                f"✅ Result: `{result}`\n\n"
                f"💡 This was found in a rainbow table database\n"
                f"{SEPARATOR}\n{WARNING}"
            )
        else:
            # Try backup
            r2 = requests.get(f"https://hashtoolkit.com/reverse-hash/?hash={hash_val}", timeout=10)
            text = (
                f"{SEPARATOR}\n"
                f"🔓 *HASH CRACK ATTEMPT*\n"
                f"{SEPARATOR}\n\n"
                f"🔐 Hash: `{hash_val}`\n"
                f"❌ Not found in free rainbow tables\n\n"
                f"🔍 *Try these manually:*\n"
                f"• [CrackStation](https://crackstation.net/)\n"
                f"• [HashKiller](https://hashkiller.io/listmanager)\n"
                f"• [MD5Decrypt](https://md5decrypt.net/)\n"
                f"{SEPARATOR}\n{WARNING}"
            )
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"

    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================================================================
# ENCODE / DECODE
# ================================================================

async def encode_b64(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/encode <text>`", parse_mode="Markdown")
        return
    text_input = " ".join(context.args)
    encoded = base64.b64encode(text_input.encode()).decode()
    await update.message.reply_text(
        f"{SEPARATOR}\n🔒 *BASE64 ENCODED*\n{SEPARATOR}\n\n"
        f"Input: `{text_input}`\n\nResult: `{encoded}`\n{SEPARATOR}",
        parse_mode="Markdown"
    )

async def decode_b64(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/decode <text>`", parse_mode="Markdown")
        return
    try:
        text_input = " ".join(context.args)
        decoded = base64.b64decode(text_input.encode()).decode()
        await update.message.reply_text(
            f"{SEPARATOR}\n🔓 *BASE64 DECODED*\n{SEPARATOR}\n\n"
            f"Input: `{text_input}`\n\nResult: `{decoded}`\n{SEPARATOR}",
            parse_mode="Markdown"
        )
    except:
        await update.message.reply_text("❌ Invalid Base64 string.")

# ================================================================
# PASSWORD GENERATOR
# ================================================================

async def generate_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    length = 16
    if context.args:
        try:
            length = min(max(int(context.args[0]), 8), 64)
        except:
            pass

    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    password = "".join(random.choice(chars) for _ in range(length))

    # Strength check
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()-_=+" for c in password)
    strength = sum([has_upper, has_lower, has_digit, has_special])
    grade = "🔴 Weak" if strength < 2 else "🟡 Medium" if strength < 3 else "🟢 Strong" if strength < 4 else "💀 Unbreakable"

    text = (
        f"{SEPARATOR}\n"
        f"🔑 *PASSWORD GENERATOR*\n"
        f"{SEPARATOR}\n\n"
        f"Length: `{length}` characters\n\n"
        f"Password:\n`{password}`\n\n"
        f"Strength: {grade}\n"
        f"{SEPARATOR}\n"
        f"💡 Save this in a password manager!"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# CVE SEARCH
# ================================================================

async def cve_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/cve <keyword>`\nExample: `/cve apache`", parse_mode="Markdown")
        return

    keyword = " ".join(context.args)
    await update.message.reply_text(f"🔍 Searching CVEs for `{keyword}`...", parse_mode="Markdown")

    try:
        r = requests.get(
            f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={keyword}&resultsPerPage=5",
            timeout=15
        )
        data = r.json()
        vulns = data.get("vulnerabilities", [])

        if not vulns:
            await update.message.reply_text(f"❌ No CVEs found for `{keyword}`", parse_mode="Markdown")
            return

        text = (
            f"{SEPARATOR}\n"
            f"🚨 *CVE INTELLIGENCE: {keyword}*\n"
            f"{SEPARATOR}\n\n"
        )

        for v in vulns:
            cve = v.get("cve", {})
            cve_id = cve.get("id", "N/A")
            desc = cve.get("descriptions", [{}])[0].get("value", "N/A")[:200]
            metrics = cve.get("metrics", {})
            score = "N/A"
            severity = ""
            if "cvssMetricV31" in metrics:
                score = metrics["cvssMetricV31"][0]["cvssData"]["baseScore"]
                severity = metrics["cvssMetricV31"][0]["cvssData"]["baseSeverity"]
            elif "cvssMetricV2" in metrics:
                score = metrics["cvssMetricV2"][0]["cvssData"]["baseScore"]

            risk = "🔴" if str(score) >= "7" else "🟡" if str(score) >= "4" else "🟢"
            text += f"{risk} *{cve_id}*\n"
            text += f"Score: `{score}` {severity}\n"
            text += f"{desc[:150]}...\n\n"

        text += f"{SEPARATOR}\n{WARNING}"
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"

    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# TIPS
# ================================================================

async def security_tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tips = [
        "Use a password manager — never reuse passwords across sites.",
        "Enable 2FA on every account, especially email and banking.",
        "Avoid public WiFi for sensitive tasks. Use a VPN.",
        "Keep your OS and apps updated — patches fix known vulnerabilities.",
        "Phishing is the #1 attack vector. Always verify sender emails.",
        "Use hardware security keys (YubiKey) for critical accounts.",
        "Backup your data: 3-2-1 rule (3 copies, 2 media types, 1 offsite).",
        "Google yourself to see what info is publicly available about you.",
        "App permissions matter — does a flashlight app need your contacts?",
        "Change your router's default credentials and disable WPS.",
        "Full disk encryption (BitLocker/FileVault) protects lost devices.",
        "Social engineering bypasses all technical defenses — stay skeptical.",
        "Bug bounty programs pay you to find vulnerabilities legally.",
        "Never store passwords in plain text — always use hashing.",
        "Cover your webcam when not in use.",
        "Use end-to-end encrypted messaging (Signal) for sensitive comms.",
        "Check crt.sh and Shodan to see what's exposed about your domain.",
        "Regularly audit which apps have access to your accounts.",
    ]
    tip = random.choice(tips)
    text = (
        f"{SEPARATOR}\n"
        f"💡 *SECURITY TIP*\n"
        f"{SEPARATOR}\n\n"
        f"🛡️ {tip}\n"
        f"{SEPARATOR}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# TOOLS
# ================================================================

async def tools_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"{SEPARATOR}\n"
        f"🧰 *CYBERSECURITY TOOLS DATABASE*\n"
        f"{SEPARATOR}\n\n"
        f"*Recon/OSINT*\n"
        f"• `theHarvester` — email/domain recon\n"
        f"• `Amass` — subdomain enumeration\n"
        f"• `Shodan` — exposed devices search\n"
        f"• `Maltego` — visual link analysis\n"
        f"• `Sherlock` — username lookup\n"
        f"• `SpiderFoot` — automated OSINT\n\n"
        f"*Scanning*\n"
        f"• `Nmap` — port/service scanner\n"
        f"• `Nikto` — web vulnerability scanner\n"
        f"• `Masscan` — fast port scanner\n"
        f"• `Burp Suite` — web app proxy\n\n"
        f"*Exploitation*\n"
        f"• `Metasploit` — exploitation framework\n"
        f"• `SQLmap` — SQL injection\n"
        f"• `BeEF` — browser exploitation\n\n"
        f"*Password*\n"
        f"• `Hashcat` — GPU password cracking\n"
        f"• `John the Ripper` — password cracking\n"
        f"• `Hydra` — brute force\n\n"
        f"*Wireless*\n"
        f"• `Aircrack-ng` — WiFi auditing\n"
        f"• `Wireshark` — packet analyzer\n\n"
        f"*OS*\n"
        f"• `Kali Linux` — pentesting distro\n"
        f"• `Parrot OS` — security OS\n"
        f"• `Tails OS` — anonymous OS\n"
        f"{SEPARATOR}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# MENU CALLBACKS
# ================================================================

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_osint":
        text = (
            f"{SEPARATOR}\n🔍 *OSINT COMMANDS*\n{SEPARATOR}\n\n"
            "`/ip` — IP location & intel\n"
            "`/whois` — Domain ownership\n"
            "`/dns` — DNS records\n"
            "`/subdomains` — Find subdomains\n"
            "`/github` — GitHub profile\n"
            "`/reddit` — Reddit profile\n"
            "`/snowflake` — Discord ID decode\n"
            "`/phone` — Phone info\n"
            "`/email` — Email intelligence\n"
            "`/username` — Username search\n"
            f"`/dork` — Google dorks\n{SEPARATOR}"
        )
    elif data == "menu_network":
        text = (
            f"{SEPARATOR}\n🌐 *NETWORK COMMANDS*\n{SEPARATOR}\n\n"
            "`/portscan` — Port scanner\n"
            "`/ping` — Ping host\n"
            "`/headers` — HTTP headers\n"
            "`/sslcheck` — SSL certificate\n"
            "`/robots` — robots.txt\n"
            "`/techstack` — Tech detection\n"
            "`/urlscan` — URL threat scan\n"
            f"`/wayback` — Archive history\n{SEPARATOR}"
        )
    elif data == "menu_security":
        text = (
            f"{SEPARATOR}\n🔐 *SECURITY COMMANDS*\n{SEPARATOR}\n\n"
            "`/hash` — Generate hashes\n"
            "`/crack` — Crack MD5 hash\n"
            "`/encode` — Base64 encode\n"
            "`/decode` — Base64 decode\n"
            "`/password` — Generate password\n"
            "`/cve` — CVE search\n"
            "`/tips` — Security tips\n"
            f"`/tools` — Tools list\n{SEPARATOR}"
        )
    elif data == "menu_help":
        await help_command(update, context)
        return
    else:
        return

    await query.edit_message_text(text, parse_mode="Markdown")

# ================================================================
# MAIN
# ================================================================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ip", ip_lookup))
    app.add_handler(CommandHandler("whois", whois_lookup))
    app.add_handler(CommandHandler("dns", dns_lookup))
    app.add_handler(CommandHandler("subdomains", subdomains))
    app.add_handler(CommandHandler("github", github_lookup))
    app.add_handler(CommandHandler("reddit", reddit_lookup))
    app.add_handler(CommandHandler("snowflake", snowflake))
    app.add_handler(CommandHandler("phone", phone_lookup))
    app.add_handler(CommandHandler("email", email_check))
    app.add_handler(CommandHandler("username", username_lookup))
    app.add_handler(CommandHandler("dork", dork))
    app.add_handler(CommandHandler("portscan", port_scan))
    app.add_handler(CommandHandler("ping", ping_host))
    app.add_handler(CommandHandler("headers", http_headers))
    app.add_handler(CommandHandler("sslcheck", ssl_check))
    app.add_handler(CommandHandler("robots", robots_txt))
    app.add_handler(CommandHandler("techstack", techstack))
    app.add_handler(CommandHandler("urlscan", urlscan))
    app.add_handler(CommandHandler("wayback", wayback))
    app.add_handler(CommandHandler("hash", hash_text))
    app.add_handler(CommandHandler("crack", crack_hash))
    app.add_handler(CommandHandler("encode", encode_b64))
    app.add_handler(CommandHandler("decode", decode_b64))
    app.add_handler(CommandHandler("password", generate_password))
    app.add_handler(CommandHandler("cve", cve_search))
    app.add_handler(CommandHandler("tips", security_tips))
    app.add_handler(CommandHandler("tools", tools_list))
    app.add_handler(CallbackQueryHandler(menu_callback))

    print("CyvxBot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
