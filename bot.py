import os
import socket
import requests
import hashlib
import base64
import random
import string
import ssl as ssl_lib
import time
from datetime import datetime, timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")

SEP = "━━━━━━━━━━━━━━━━━━━━━━"
WARN = "⚠️ *WARNING:* Use only on systems you own or have permission to test. Unauthorized use is illegal."

# ================================================================
# START & HELP
# ================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 OSINT", callback_data="menu_osint"),
         InlineKeyboardButton("🌐 Network", callback_data="menu_network")],
        [InlineKeyboardButton("🔐 Security", callback_data="menu_security"),
         InlineKeyboardButton("📖 Help", callback_data="menu_help")],
    ]
    text = (
        f"{SEP}\n"
        "🕵️ *CyvxBot — OSINT & Security Toolkit*\n"
        f"{SEP}\n\n"
        "Professional cybersecurity intelligence tool.\n"
        "All data pulled from *real public sources*.\n\n"
        f"⚠️ *For educational and authorized use only.*\n"
        f"{SEP}"
    )
    await update.message.reply_text(text, parse_mode="Markdown",
                                     reply_markup=InlineKeyboardMarkup(keyboard))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"{SEP}\n📖 *ALL COMMANDS*\n{SEP}\n\n"
        "*🔍 OSINT*\n"
        "`/ip` — IP location & intel\n"
        "`/whois` — Domain ownership\n"
        "`/dns` — DNS records\n"
        "`/subdomains` — Find subdomains\n"
        "`/github` — GitHub profile\n"
        "`/reddit` — Reddit profile\n"
        "`/steam` — Steam profile\n"
        "`/twitch` — Twitch channel info\n"
        "`/snowflake` — Discord ID decoder\n"
        "`/phone` — Phone number info\n"
        "`/email` — Email intelligence\n"
        "`/username` — Username search\n"
        "`/dork` — Google dorks\n\n"
        "*🌐 Network*\n"
        "`/portscan` — Port scanner\n"
        "`/ping` — Ping host\n"
        "`/headers` — HTTP headers\n"
        "`/sslcheck` — SSL certificate\n"
        "`/robots` — robots.txt\n"
        "`/techstack` — Tech detection\n"
        "`/urlscan` — URL threat scan\n"
        "`/wayback` — Archive history\n\n"
        "*🔐 Security*\n"
        "`/hash` — Generate hashes\n"
        "`/crack` — Crack MD5 hash\n"
        "`/encode` — Base64 encode\n"
        "`/decode` — Base64 decode\n"
        "`/password` — Generate password\n"
        "`/cve` — CVE search\n"
        "`/tips` — Security tips\n"
        "`/tools` — Tools list\n\n"
        f"{WARN}"
    )
    msg = update.message or update.callback_query.message
    await msg.reply_text(text, parse_mode="Markdown")

# ================================================================
# IP
# ================================================================

async def ip_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/ip <address>`\nExample: `/ip 8.8.8.8`", parse_mode="Markdown")
        return
    ip = context.args[0]
    await update.message.reply_text(f"🔍 Investigating `{ip}`...", parse_mode="Markdown")
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
        d = r.json()
        if d.get("status") == "fail":
            await update.message.reply_text(f"❌ Invalid IP: `{ip}`", parse_mode="Markdown")
            return
        text = (
            f"{SEP}\n🌍 *IP INTELLIGENCE REPORT*\n{SEP}\n\n"
            f"🎯 IP: `{ip}`\n"
            f"🌍 Country: `{d.get('country', 'N/A')}`\n"
            f"🏙️ City: `{d.get('city', 'N/A')}`\n"
            f"📍 Region: `{d.get('regionName', 'N/A')}`\n"
            f"🏢 ISP: `{d.get('isp', 'N/A')}`\n"
            f"🌐 ASN: `{d.get('as', 'N/A')}`\n"
            f"🕐 Timezone: `{d.get('timezone', 'N/A')}`\n"
            f"🗺️ Coordinates: `{d.get('lat', 'N/A')}, {d.get('lon', 'N/A')}`\n\n"
            f"🔗 *Investigate further:*\n"
            f"• [Shodan](https://www.shodan.io/host/{ip})\n"
            f"• [VirusTotal](https://www.virustotal.com/gui/ip-address/{ip})\n"
            f"• [AbuseIPDB](https://www.abuseipdb.com/check/{ip})\n"
            f"{SEP}\n{WARN}"
        )
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"
    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================================================================
# WHOIS
# ================================================================

async def whois_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/whois <domain>`", parse_mode="Markdown")
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
            if action == "registration": registered = date
            elif action == "last changed": updated = date
            elif action == "expiration": expires = date
        status = d.get("status", [])
        nameservers = [ns.get("ldhName", "") for ns in d.get("nameservers", [])]
        text = (
            f"{SEP}\n🌐 *WHOIS REPORT: {domain}*\n{SEP}\n\n"
            f"📅 Registered: `{registered}`\n"
            f"🔄 Last Updated: `{updated}`\n"
            f"⏰ Expires: `{expires}`\n"
            f"📊 Status: `{', '.join(status[:2]) if status else 'N/A'}`\n"
            f"🖥️ Nameservers:\n"
        )
        for ns in nameservers[:4]:
            text += f"  • `{ns}`\n"
        text += f"\n🔗 [ViewDNS](https://viewdns.info/whois/?domain={domain}) | [DomainTools](https://whois.domaintools.com/{domain})\n{SEP}\n{WARN}"
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"
    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================================================================
# DNS
# ================================================================

async def dns_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/dns <domain>`", parse_mode="Markdown")
        return
    domain = context.args[0]
    await update.message.reply_text(f"🔍 Fetching DNS records for `{domain}`...", parse_mode="Markdown")
    try:
        type_map = {1: "A", 2: "NS", 5: "CNAME", 15: "MX", 16: "TXT", 28: "AAAA"}
        records = {}
        for rtype in [1, 28, 15, 2, 16, 5]:
            r = requests.get(f"https://dns.google/resolve?name={domain}&type={rtype}", timeout=10)
            d = r.json()
            for ans in d.get("Answer", []):
                t = type_map.get(ans.get("type", 0), "OTHER")
                if t not in records: records[t] = []
                records[t].append(ans.get("data", ""))
        if not records:
            await update.message.reply_text(f"❌ No DNS records found for `{domain}`", parse_mode="Markdown")
            return
        text = f"{SEP}\n🌐 *DNS RECORDS: {domain}*\n{SEP}\n\n"
        for rtype, values in records.items():
            text += f"*{rtype} Records:*\n"
            for v in values[:5]:
                text += f"  • `{v}`\n"
            text += "\n"
        text += f"{SEP}\n{WARN}"
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"
    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# SUBDOMAINS — FIXED
# ================================================================

async def subdomains(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/subdomains <domain>`", parse_mode="Markdown")
        return
    domain = context.args[0]
    await update.message.reply_text(f"🔍 Finding subdomains for `{domain}`...", parse_mode="Markdown")
    try:
        subs = set()

        # Try crt.sh first
        try:
            r = requests.get(
                f"https://crt.sh/?q=%.{domain}&output=json",
                timeout=20,
                headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
            )
            if r.status_code == 200:
                data = r.json()
                for entry in data:
                    name = entry.get("name_value", "")
                    for sub in name.split("\n"):
                        sub = sub.strip().lstrip("*.")
                        if sub.endswith(domain) and sub != domain:
                            subs.add(sub)
        except:
            pass

        # Backup: HackerTarget
        if not subs:
            try:
                r2 = requests.get(
                    f"https://api.hackertarget.com/hostsearch/?q={domain}",
                    timeout=15
                )
                if r2.status_code == 200 and "error" not in r2.text.lower():
                    for line in r2.text.strip().split("\n"):
                        if "," in line:
                            sub = line.split(",")[0].strip()
                            if sub.endswith(domain):
                                subs.add(sub)
            except:
                pass

        if not subs:
            text = f"❌ No subdomains found for `{domain}`\n\nTry: [crt.sh](https://crt.sh/?q=%.{domain})"
        else:
            subs = sorted(list(subs))
            text = f"{SEP}\n🔎 *SUBDOMAINS: {domain}*\n{SEP}\n\nFound *{len(subs)}* subdomains:\n\n"
            for s in subs[:30]:
                text += f"• `{s}`\n"
            if len(subs) > 30:
                text += f"\n_...and {len(subs) - 30} more_\n"
            text += f"\n{SEP}\n{WARN}"
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"
    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================================================================
# GITHUB
# ================================================================

async def github_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/github <username>`", parse_mode="Markdown")
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
        repos_r = requests.get(f"https://api.github.com/users/{username}/repos?per_page=5&sort=updated",
                                headers={"User-Agent": "CyvxBot"}, timeout=10)
        repos = repos_r.json() if repos_r.status_code == 200 else []
        text = (
            f"{SEP}\n💻 *GITHUB INTELLIGENCE: {username}*\n{SEP}\n\n"
            f"👤 Name: `{d.get('name', 'N/A')}`\n"
            f"📧 Email: `{d.get('email', 'Hidden')}`\n"
            f"🌍 Location: `{d.get('location', 'N/A')}`\n"
            f"🏢 Company: `{d.get('company', 'N/A')}`\n"
            f"📝 Bio: `{d.get('bio', 'N/A')}`\n\n"
            f"📊 *Stats:*\n"
            f"• Repos: `{d.get('public_repos', 0)}`\n"
            f"• Followers: `{d.get('followers', 0)}`\n"
            f"• Following: `{d.get('following', 0)}`\n\n"
            f"📅 Created: `{d.get('created_at', 'N/A')[:10]}`\n\n"
        )
        if repos:
            text += "*Recent Repos:*\n"
            for repo in repos[:5]:
                stars = repo.get("stargazers_count", 0)
                lang = repo.get("language", "N/A")
                text += f"• [{repo['name']}](https://github.com/{username}/{repo['name']}) ⭐{stars} `{lang}`\n"
        text += f"\n🔗 [github.com/{username}](https://github.com/{username})\n{SEP}\n{WARN}"
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"
    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================================================================
# REDDIT — FIXED
# ================================================================

async def reddit_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/reddit <username>`", parse_mode="Markdown")
        return
    username = context.args[0]
    await update.message.reply_text(f"🔍 Investigating Reddit user `{username}`...", parse_mode="Markdown")
    try:
        r = requests.get(
            f"https://www.reddit.com/user/{username}/about.json",
            headers={"User-Agent": "CyvxBot/1.0 (by /u/osintbot)"},
            timeout=10
        )
        if r.status_code == 404:
            await update.message.reply_text(f"❌ Reddit user `{username}` not found.", parse_mode="Markdown")
            return
        d = r.json().get("data", {})
        created = datetime.fromtimestamp(d.get("created_utc", 0), tz=timezone.utc).strftime("%Y-%m-%d")
        cake_day = datetime.fromtimestamp(d.get("created_utc", 0), tz=timezone.utc).strftime("%B %d")
        text = (
            f"{SEP}\n🤖 *REDDIT INTELLIGENCE: u/{username}*\n{SEP}\n\n"
            f"👤 Username: `u/{username}`\n"
            f"📅 Created: `{created}`\n"
            f"🎂 Cake Day: `{cake_day}`\n\n"
            f"📊 *Stats:*\n"
            f"• Post Karma: `{d.get('link_karma', 0):,}`\n"
            f"• Comment Karma: `{d.get('comment_karma', 0):,}`\n"
            f"• Total Karma: `{d.get('total_karma', 0):,}`\n\n"
            f"✅ Verified Email: `{'Yes' if d.get('has_verified_email') else 'No'}`\n"
            f"🥇 Reddit Premium: `{'Yes' if d.get('is_gold') else 'No'}`\n"
            f"🛡️ Moderator: `{'Yes' if d.get('is_mod') else 'No'}`\n\n"
            f"🔗 [reddit.com/u/{username}](https://reddit.com/u/{username})\n"
            f"{SEP}\n{WARN}"
        )
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"
    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================================================================
# STEAM — NEW
# ================================================================

async def steam_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/steam <username>`", parse_mode="Markdown")
        return
    username = context.args[0]
    await update.message.reply_text(f"🔍 Looking up Steam user `{username}`...", parse_mode="Markdown")
    try:
        # Resolve vanity URL to Steam ID
        r = requests.get(
            f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?key=&vanityurl={username}",
            timeout=10
        )
        # Use steamid.io as fallback (no API key needed)
        r2 = requests.get(
            f"https://steamcommunity.com/id/{username}/?xml=1",
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        text = (
            f"{SEP}\n🎮 *STEAM INTELLIGENCE: {username}*\n{SEP}\n\n"
        )

        if r2.status_code == 200 and "steamID64" in r2.text:
            import re
            steam_id = re.search(r"<steamID64>(\d+)</steamID64>", r2.text)
            real_name = re.search(r"<realname>(.*?)</realname>", r2.text)
            summary = re.search(r"<summary>(.*?)</summary>", r2.text)
            member_since = re.search(r"<memberSince>(.*?)</memberSince>", r2.text)
            location = re.search(r"<location>(.*?)</location>", r2.text)
            vac_bans = re.search(r"<vacBanned>(\d+)</vacBanned>", r2.text)

            text += f"👤 Username: `{username}`\n"
            if steam_id: text += f"🆔 Steam ID: `{steam_id.group(1)}`\n"
            if real_name: text += f"📛 Real Name: `{real_name.group(1)}`\n"
            if location: text += f"🌍 Location: `{location.group(1)}`\n"
            if member_since: text += f"📅 Member Since: `{member_since.group(1)}`\n"
            if vac_bans: text += f"🔨 VAC Banned: `{'Yes' if vac_bans.group(1) == '1' else 'No'}`\n"
            text += f"\n🔗 [steamcommunity.com/id/{username}](https://steamcommunity.com/id/{username})\n"
        else:
            text += (
                f"⚠️ Profile may be private or not found.\n\n"
                f"🔗 [Search on Steam](https://steamcommunity.com/id/{username})\n"
            )

        text += f"{SEP}\n{WARN}"
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"
    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================================================================
# TWITCH — NEW
# ================================================================

async def twitch_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/twitch <username>`", parse_mode="Markdown")
        return
    username = context.args[0]
    await update.message.reply_text(f"🔍 Looking up Twitch user `{username}`...", parse_mode="Markdown")
    try:
        # Check if channel exists via public page
        r = requests.get(
            f"https://twitch.tv/{username}",
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        text = f"{SEP}\n🎮 *TWITCH INTELLIGENCE: {username}*\n{SEP}\n\n"

        if r.status_code == 200:
            text += f"✅ Channel EXISTS\n\n"
            text += f"👤 Username: `{username}`\n"
            text += f"🔗 Channel: [twitch.tv/{username}](https://twitch.tv/{username})\n\n"
            text += f"🔍 *Check full stats:*\n"
            text += f"• [TwitchTracker](https://twitchtracker.com/{username})\n"
            text += f"• [SullyGnome](https://sullygnome.com/channel/{username})\n"
            text += f"• [StreamsCharts](https://streamscharts.com/channels/{username})\n"
        else:
            text += f"❌ Channel `{username}` not found on Twitch.\n"

        text += f"\n{SEP}\n{WARN}"
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"
    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================================================================
# SNOWFLAKE
# ================================================================

async def snowflake(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/snowflake <discord_id>`", parse_mode="Markdown")
        return
    user_id = context.args[0]
    if not user_id.isdigit():
        await update.message.reply_text("❌ Discord ID must be numbers only!", parse_mode="Markdown")
        return
    await update.message.reply_text(f"🔍 Decoding Discord ID `{user_id}`...", parse_mode="Markdown")
    try:
        discord_epoch = 1420070400000
        timestamp_ms = (int(user_id) >> 22) + discord_epoch
        created_at = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
        age = datetime.now(tz=timezone.utc) - created_at
        years = age.days // 365
        months = (age.days % 365) // 30
        days = age.days % 30

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
                username = global_name = avatar_url = badge_text = "N/A"
                is_bot = False
        except:
            username = global_name = avatar_url = badge_text = "N/A"
            is_bot = False

        text = (
            f"{SEP}\n💬 *DISCORD ID INTELLIGENCE*\n{SEP}\n\n"
            f"🆔 ID: `{user_id}`\n"
            f"👤 Username: `{username}`\n"
            f"🏷️ Display Name: `{global_name}`\n"
            f"🤖 Bot: `{'Yes' if is_bot else 'No'}`\n\n"
            f"📅 *Account Created:*\n"
            f"• Date: `{created_at.strftime('%B %d, %Y')}`\n"
            f"• Time: `{created_at.strftime('%H:%M:%S UTC')}`\n"
            f"• Age: `{years}y {months}m {days}d`\n\n"
            f"🏅 Badges: `{badge_text}`\n"
            f"🖼️ Avatar: {'[Click here](' + avatar_url + ')' if avatar_url != 'N/A' else 'None'}\n"
            f"{SEP}\n{WARN}"
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
    if not phone.startswith("+"):
        await update.message.reply_text("❌ Include country code. Example: `/phone +9647501234567`", parse_mode="Markdown")
        return
    country_codes = {
        "1": "🇺🇸 USA/Canada", "44": "🇬🇧 UK", "49": "🇩🇪 Germany",
        "33": "🇫🇷 France", "7": "🇷🇺 Russia", "86": "🇨🇳 China",
        "91": "🇮🇳 India", "55": "🇧🇷 Brazil", "81": "🇯🇵 Japan",
        "964": "🇮🇶 Iraq", "966": "🇸🇦 Saudi Arabia", "971": "🇦🇪 UAE",
        "90": "🇹🇷 Turkey", "98": "🇮🇷 Iran", "92": "🇵🇰 Pakistan",
        "962": "🇯🇴 Jordan", "963": "🇸🇾 Syria", "961": "🇱🇧 Lebanon",
        "20": "🇪🇬 Egypt", "212": "🇲🇦 Morocco",
    }
    num = phone[1:]
    country = (country_codes.get(num[:3]) or country_codes.get(num[:2]) or
               country_codes.get(num[:1]) or "🌍 Unknown")
    text = (
        f"{SEP}\n📱 *PHONE INTELLIGENCE*\n{SEP}\n\n"
        f"📞 Number: `{phone}`\n"
        f"🌍 Country: `{country}`\n"
        f"🔢 Digits: `{len(num)}`\n\n"
        f"🔍 *Search this number:*\n"
        f"• [Truecaller](https://www.truecaller.com/search/us/{num})\n"
        f"• [WhoCalledMe](https://www.whocalledme.com/PhoneNumber/{num})\n"
        f"• [NumLookup](https://www.numlookup.com/)\n"
        f"• [SpyDialer](https://www.spydialer.com/)\n"
        f"{SEP}\n{WARN}"
    )
    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================================================================
# EMAIL
# ================================================================

async def email_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/email <email>`", parse_mode="Markdown")
        return
    email = context.args[0]
    await update.message.reply_text(f"🔍 Investigating `{email}`...", parse_mode="Markdown")
    results = []
    try:
        domain = email.split("@")[1]
        r = requests.get(f"https://dns.google/resolve?name={domain}&type=MX", timeout=5)
        d = r.json()
        if d.get("Answer"):
            results.append(f"✅ Domain `{domain}` is *valid* — has mail servers")
        else:
            results.append(f"❌ Domain `{domain}` has *no mail servers* — likely fake")
    except:
        results.append("⚠️ Could not verify domain")
    try:
        disposable = ["guerrillamail.com", "tempmail.com", "10minutemail.com",
                      "throwaway.email", "mailinator.com", "yopmail.com"]
        domain = email.split("@")[1]
        if domain in disposable:
            results.append(f"🚨 `{domain}` is a *disposable* email service!")
        else:
            results.append(f"✅ Not a known disposable email service")
    except:
        pass
    try:
        email_hash = hashlib.md5(email.lower().encode()).hexdigest()
        r = requests.get(f"https://www.gravatar.com/{email_hash}.json", timeout=5)
        if r.status_code == 200:
            d = r.json()
            name = d.get("entry", [{}])[0].get("displayName", "Unknown")
            results.append(f"👤 Gravatar profile found! Name: *{name}*")
        else:
            results.append("❌ No Gravatar profile linked")
    except:
        pass
    text = (
        f"{SEP}\n📧 *EMAIL INTELLIGENCE*\n{SEP}\n\n"
        f"📧 Email: `{email}`\n\n"
        "*Checks:*\n" + "\n".join(results) +
        f"\n\n🔍 *Check breaches:*\n"
        f"• [HaveIBeenPwned](https://haveibeenpwned.com/account/{email})\n"
        f"• [DeHashed](https://dehashed.com/search?query={email})\n"
        f"{SEP}\n{WARN}"
    )
    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================================================================
# USERNAME
# ================================================================

async def username_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/username <n>`", parse_mode="Markdown")
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
    text = f"{SEP}\n👤 *USERNAME SEARCH: {username}*\n{SEP}\n\n"
    if found:
        text += f"*Found on {len(found)} platforms:*\n" + "\n".join(found) + "\n\n"
    if not_found:
        text += f"*Not found:* {', '.join(not_found)}\n"
    text += f"\n{SEP}\n{WARN}"
    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================================================================
# DORK
# ================================================================

async def dork(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/dork <target>`", parse_mode="Markdown")
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
        f"site:{target} intext:password",
        f"site:pastebin.com \"{target}\"",
        f"site:github.com \"{target}\"",
        f"site:trello.com \"{target}\"",
    ]
    text = f"{SEP}\n🎯 *GOOGLE DORKS: {target}*\n{SEP}\n\nCopy these into Google:\n\n"
    for d in dorks:
        text += f"`{d}`\n\n"
    text += f"{SEP}\n{WARN}"
    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# PORT SCAN
# ================================================================

async def port_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/portscan <host>`", parse_mode="Markdown")
        return
    host = context.args[0]
    ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 6379, 8080, 8443]
    if len(context.args) > 1:
        try:
            ports = [int(p.strip()) for p in context.args[1].split(",")]
        except:
            pass
    await update.message.reply_text(f"🔍 Scanning `{host}`...", parse_mode="Markdown")
    try:
        ip = socket.gethostbyname(host)
    except socket.gaierror:
        await update.message.reply_text(f"❌ Could not resolve `{host}`", parse_mode="Markdown")
        return
    open_ports = []
    closed = 0
    service_map = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
        80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
        3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 6379: "Redis",
        8080: "HTTP-Alt", 8443: "HTTPS-Alt"
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
                closed += 1
        except:
            closed += 1
    text = f"{SEP}\n🖥️ *PORT SCAN: {host}*\n{SEP}\n\n🎯 IP: `{ip}`\n🔍 Scanned: `{len(ports)}` ports\n\n"
    if open_ports:
        text += f"✅ *Open Ports ({len(open_ports)}):*\n"
        for p in open_ports:
            risk = "🔴" if p in [23, 445, 3389] else "🟡" if p in [21, 25, 3306] else "🟢"
            text += f"  {risk} `{p}` — {service_map.get(p, 'Unknown')}\n"
    else:
        text += "✅ No open ports found\n"
    text += f"\n🔒 Closed: `{closed}` ports\n{SEP}\n{WARN}"
    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# PING — FIXED
# ================================================================

async def ping_host(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/ping <host>`", parse_mode="Markdown")
        return
    host = context.args[0]
    await update.message.reply_text(f"📡 Pinging `{host}`...", parse_mode="Markdown")
    try:
        url = f"https://{host}" if not host.startswith("http") else host
        times = []
        status = None
        for _ in range(3):
            start = time.time()
            r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            ms = round((time.time() - start) * 1000)
            times.append(ms)
            status = r.status_code
        avg = round(sum(times) / len(times))
        text = (
            f"{SEP}\n📡 *PING: {host}*\n{SEP}\n\n"
            f"✅ Host is *ONLINE*\n"
            f"📊 Status Code: `{status}`\n"
            f"⚡ Response Times: `{times[0]}ms, {times[1]}ms, {times[2]}ms`\n"
            f"📈 Average: `{avg}ms`\n"
            f"{SEP}\n{WARN}"
        )
    except:
        text = f"{SEP}\n📡 *PING: {host}*\n{SEP}\n\n❌ Host is *OFFLINE* or unreachable\n{SEP}\n{WARN}"
    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# HTTP HEADERS
# ================================================================

async def http_headers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/headers <url>`", parse_mode="Markdown")
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
        }
        score = 0
        text = (
            f"{SEP}\n📋 *HTTP SECURITY ANALYSIS*\n{SEP}\n\n"
            f"🎯 URL: `{url}`\n"
            f"📊 Status: `{r.status_code}`\n"
            f"🖥️ Server: `{headers.get('Server', 'Hidden')}`\n\n"
            f"*Security Headers:*\n"
        )
        for h, desc in security_headers.items():
            if h in headers:
                text += f"✅ `{h}`\n   _{desc}_\n\n"
                score += 1
            else:
                text += f"❌ `{h}` *MISSING*\n   _{desc}_\n\n"
        grade = "A" if score >= 5 else "B" if score >= 4 else "C" if score >= 3 else "D" if score >= 2 else "F"
        text += f"🏆 Security Grade: *{grade}* ({score}/5)\n{SEP}\n{WARN}"
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"
    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# SSL CHECK
# ================================================================

async def ssl_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/sslcheck <domain>`", parse_mode="Markdown")
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
        try:
            expires = datetime.strptime(expires_str, "%b %d %H:%M:%S %Y %Z")
            days_left = (expires - datetime.utcnow()).days
            expiry_status = f"🟢 {days_left} days left" if days_left > 30 else f"🔴 EXPIRES SOON: {days_left} days!"
        except:
            expiry_status = expires_str
        text = (
            f"{SEP}\n🔐 *SSL CERTIFICATE REPORT*\n{SEP}\n\n"
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
        text += f"\n{SEP}\n{WARN}"
    except ssl_lib.SSLError:
        text = f"❌ `{domain}` has an *INVALID* SSL certificate!"
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"
    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# ROBOTS
# ================================================================

async def robots_txt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/robots <domain>`", parse_mode="Markdown")
        return
    domain = context.args[0]
    if not domain.startswith("http"):
        domain = "https://" + domain
    try:
        r = requests.get(f"{domain}/robots.txt", timeout=10)
        content = r.text[:2000]
        text = f"{SEP}\n🤖 *ROBOTS.TXT: {domain}*\n{SEP}\n\n💡 Pages hidden from search engines:\n\n```\n{content}\n```\n{SEP}\n{WARN}"
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"
    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# TECH STACK
# ================================================================

async def techstack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/techstack <url>`", parse_mode="Markdown")
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
        server = headers.get("Server", "")
        if server: detected.append(f"🖥️ Server: `{server}`")
        powered = headers.get("X-Powered-By", "")
        if powered: detected.append(f"⚙️ Powered By: `{powered}`")
        if "wp-content" in body or "wp-includes" in body: detected.append("📝 CMS: `WordPress`")
        elif "Drupal" in body: detected.append("📝 CMS: `Drupal`")
        elif "Joomla" in body: detected.append("📝 CMS: `Joomla`")
        elif "shopify" in body.lower(): detected.append("🛒 Platform: `Shopify`")
        if "react" in body.lower() or "__react" in body: detected.append("⚛️ Framework: `React`")
        if "vue.js" in body.lower(): detected.append("💚 Framework: `Vue.js`")
        if "angular" in body.lower(): detected.append("🔴 Framework: `Angular`")
        if "next.js" in body.lower() or "__next" in body: detected.append("▲ Framework: `Next.js`")
        if "jquery" in body.lower(): detected.append("📦 Library: `jQuery`")
        if "cloudflare" in str(headers).lower(): detected.append("☁️ CDN: `Cloudflare`")
        elif "akamai" in str(headers).lower(): detected.append("☁️ CDN: `Akamai`")
        if "google-analytics" in body or "gtag" in body: detected.append("📊 Analytics: `Google Analytics`")
        text = f"{SEP}\n🔬 *TECH STACK: {url}*\n{SEP}\n\n"
        if detected:
            text += "*Detected:*\n\n" + "\n".join([f"• {t}" for t in detected])
        else:
            text += "❌ Could not detect specific technologies"
        text += f"\n\n{SEP}\n{WARN}"
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"
    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# URL SCAN
# ================================================================

async def urlscan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/urlscan <url>`", parse_mode="Markdown")
        return
    url = context.args[0]
    if not url.startswith("http"):
        url = "https://" + url
    domain = url.replace("https://", "").replace("http://", "").split("/")[0]
    text = (
        f"{SEP}\n🛡️ *URL THREAT SCAN: {url}*\n{SEP}\n\n"
        f"🔍 *Scan with free tools:*\n\n"
        f"• [VirusTotal](https://www.virustotal.com/gui/url/{url}) — 70+ AV engines\n"
        f"• [URLScan.io](https://urlscan.io/search/#{domain}) — Full analysis\n"
        f"• [Google Safe Browsing](https://transparencyreport.google.com/safe-browsing/search?url={url})\n"
        f"• [PhishTank](https://www.phishtank.com/index.php) — Phishing database\n"
        f"• [URLVoid](https://www.urlvoid.com/scan/{domain}/)\n\n"
        f"💡 Click links above for real-time analysis\n"
        f"{SEP}\n{WARN}"
    )
    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================================================================
# WAYBACK — FIXED
# ================================================================

async def wayback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/wayback <url>`", parse_mode="Markdown")
        return
    url = context.args[0]
    await update.message.reply_text(f"🔍 Checking archive for `{url}`...", parse_mode="Markdown")
    try:
        r = requests.get(
            f"https://archive.org/wayback/available?url={url}",
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        d = r.json()
        snapshot = d.get("archived_snapshots", {}).get("closest", {})
        if snapshot and snapshot.get("available"):
            snap_url = snapshot.get("url", "N/A")
            snap_time = snapshot.get("timestamp", "N/A")
            formatted = f"{snap_time[:4]}-{snap_time[4:6]}-{snap_time[6:8]}" if len(snap_time) >= 8 else snap_time
            text = (
                f"{SEP}\n📚 *WAYBACK MACHINE: {url}*\n{SEP}\n\n"
                f"✅ Archive found!\n\n"
                f"📅 Latest Snapshot: `{formatted}`\n"
                f"🔗 [View Archived Page]({snap_url})\n\n"
                f"📖 [Full History](https://web.archive.org/web/*/{url})\n"
                f"{SEP}\n{WARN}"
            )
        else:
            text = (
                f"{SEP}\n📚 *WAYBACK MACHINE: {url}*\n{SEP}\n\n"
                f"❌ No snapshots available\n\n"
                f"🔗 [Search manually](https://web.archive.org/web/*/{url})\n"
                f"{SEP}\n{WARN}"
            )
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"
    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# ================================================================
# HASH
# ================================================================

async def hash_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/hash <text>`", parse_mode="Markdown")
        return
    text_input = " ".join(context.args).encode()
    text = (
        f"{SEP}\n#️⃣ *HASH GENERATOR*\n{SEP}\n\n"
        f"📝 Input: `{' '.join(context.args)}`\n\n"
        f"*Results:*\n"
        f"`MD5`:    `{hashlib.md5(text_input).hexdigest()}`\n"
        f"`SHA1`:   `{hashlib.sha1(text_input).hexdigest()}`\n"
        f"`SHA256`: `{hashlib.sha256(text_input).hexdigest()}`\n"
        f"`SHA512`: `{hashlib.sha512(text_input).hexdigest()}`\n\n"
        f"💡 Hashes are one-way — cannot be reversed\n{SEP}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# CRACK — FIXED
# ================================================================

async def crack_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/crack <hash>`", parse_mode="Markdown")
        return
    hash_val = context.args[0]
    await update.message.reply_text(f"🔓 Looking up `{hash_val}`...", parse_mode="Markdown")
    try:
        r = requests.get(
            f"https://md5decrypt.net/Api/api.php?hash={hash_val}&hash_type=md5&email=admin&code=code",
            timeout=10
        )
        result = r.text.strip()
        if result and len(result) < 100 and "error" not in result.lower() and "code" not in result.lower():
            text = (
                f"{SEP}\n🔓 *HASH CRACKED!*\n{SEP}\n\n"
                f"🔐 Hash: `{hash_val}`\n"
                f"✅ Result: `{result}`\n\n"
                f"💡 Found in rainbow table database\n{SEP}\n{WARN}"
            )
        else:
            text = (
                f"{SEP}\n🔓 *HASH CRACK*\n{SEP}\n\n"
                f"🔐 Hash: `{hash_val}`\n"
                f"❌ Not found in database\n\n"
                f"🔍 *Try manually:*\n"
                f"• [CrackStation](https://crackstation.net/)\n"
                f"• [HashKiller](https://hashkiller.io/listmanager)\n"
                f"• [MD5Decrypt](https://md5decrypt.net/)\n"
                f"{SEP}\n{WARN}"
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
        f"{SEP}\n🔒 *BASE64 ENCODED*\n{SEP}\n\nInput: `{text_input}`\n\nResult: `{encoded}`\n{SEP}",
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
            f"{SEP}\n🔓 *BASE64 DECODED*\n{SEP}\n\nInput: `{text_input}`\n\nResult: `{decoded}`\n{SEP}",
            parse_mode="Markdown"
        )
    except:
        await update.message.reply_text("❌ Invalid Base64 string.")

# ================================================================
# PASSWORD
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
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()-_=+" for c in password)
    strength = sum([has_upper, has_lower, has_digit, has_special])
    grade = "🔴 Weak" if strength < 2 else "🟡 Medium" if strength < 3 else "🟢 Strong" if strength < 4 else "💀 Unbreakable"
    text = (
        f"{SEP}\n🔑 *PASSWORD GENERATOR*\n{SEP}\n\n"
        f"Length: `{length}` characters\n\n"
        f"Password:\n`{password}`\n\n"
        f"Strength: {grade}\n{SEP}\n"
        f"💡 Save this in a password manager!"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# CVE
# ================================================================

async def cve_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/cve <keyword>`", parse_mode="Markdown")
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
        text = f"{SEP}\n🚨 *CVE INTELLIGENCE: {keyword}*\n{SEP}\n\n"
        for v in vulns:
            cve = v.get("cve", {})
            cve_id = cve.get("id", "N/A")
            desc = cve.get("descriptions", [{}])[0].get("value", "N/A")[:150]
            metrics = cve.get("metrics", {})
            score = "N/A"
            if "cvssMetricV31" in metrics:
                score = metrics["cvssMetricV31"][0]["cvssData"]["baseScore"]
            risk = "🔴" if str(score) >= "7" else "🟡" if str(score) >= "4" else "🟢"
            text += f"{risk} *{cve_id}* (Score: `{score}`)\n{desc}...\n\n"
        text += f"{SEP}\n{WARN}"
    except Exception as e:
        text = f"❌ Error: `{str(e)}`"
    await update.message.reply_text(text, parse_mode="Markdown")

# ================================================================
# TIPS & TOOLS
# ================================================================

async def security_tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tips = [
        "Use a password manager — never reuse passwords.",
        "Enable 2FA on every account.",
        "Avoid public WiFi for sensitive tasks. Use a VPN.",
        "Keep your OS and apps updated.",
        "Phishing is the #1 attack vector — verify sender emails.",
        "Use hardware security keys for critical accounts.",
        "Backup your data: 3-2-1 rule.",
        "Google yourself to see what info is public.",
        "Check app permissions carefully.",
        "Change your router default credentials.",
        "Full disk encryption protects lost devices.",
        "Social engineering bypasses all technical defenses.",
        "Bug bounty programs pay you to find vulnerabilities legally.",
        "Never store passwords in plain text.",
        "Cover your webcam when not in use.",
        "Use Signal for sensitive communications.",
    ]
    tip = random.choice(tips)
    await update.message.reply_text(f"{SEP}\n💡 *SECURITY TIP*\n{SEP}\n\n🛡️ {tip}\n{SEP}", parse_mode="Markdown")

async def tools_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"{SEP}\n🧰 *CYBERSECURITY TOOLS*\n{SEP}\n\n"
        f"*Recon/OSINT*\n• `theHarvester` • `Amass` • `Shodan` • `Maltego` • `Sherlock`\n\n"
        f"*Scanning*\n• `Nmap` • `Nikto` • `Masscan` • `Burp Suite`\n\n"
        f"*Exploitation*\n• `Metasploit` • `SQLmap` • `BeEF`\n\n"
        f"*Password*\n• `Hashcat` • `John the Ripper` • `Hydra`\n\n"
        f"*Wireless*\n• `Aircrack-ng` • `Wireshark`\n\n"
        f"*OS*\n• `Kali Linux` • `Parrot OS` • `Tails OS`\n{SEP}"
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
            f"{SEP}\n🔍 *OSINT COMMANDS*\n{SEP}\n\n"
            "`/ip` — IP intel\n`/whois` — Domain info\n`/dns` — DNS records\n"
            "`/subdomains` — Subdomains\n`/github` — GitHub profile\n"
            "`/reddit` — Reddit profile\n`/steam` — Steam profile\n"
            "`/twitch` — Twitch channel\n`/snowflake` — Discord ID\n"
            "`/phone` — Phone info\n`/email` — Email intel\n"
            f"`/username` — Username search\n`/dork` — Google dorks\n{SEP}"
        )
    elif data == "menu_network":
        text = (
            f"{SEP}\n🌐 *NETWORK COMMANDS*\n{SEP}\n\n"
            "`/portscan` — Port scanner\n`/ping` — Ping host\n"
            "`/headers` — HTTP headers\n`/sslcheck` — SSL cert\n"
            "`/robots` — robots.txt\n`/techstack` — Tech detection\n"
            f"`/urlscan` — URL threat scan\n`/wayback` — Archive history\n{SEP}"
        )
    elif data == "menu_security":
        text = (
            f"{SEP}\n🔐 *SECURITY COMMANDS*\n{SEP}\n\n"
            "`/hash` — Hash generator\n`/crack` — Crack MD5\n"
            "`/encode` — Base64 encode\n`/decode` — Base64 decode\n"
            "`/password` — Generate password\n`/cve` — CVE search\n"
            f"`/tips` — Security tips\n`/tools` — Tools list\n{SEP}"
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
    app.add_handler(CommandHandler("steam", steam_lookup))
    app.add_handler(CommandHandler("twitch", twitch_lookup))
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
