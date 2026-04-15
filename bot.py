import os
import socket
import hashlib
import base64
import dns.resolver
import whois
import requests
import ipaddress
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN print("TOKEN =", TOKEN)

# ── /start ──────────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡️ *CyberTools Bot* by @Mr_0x0bot\n\n"
        "Available commands:\n"
        "/ip `<ip>` — IP Lookup\n"
        "/dns `<domain>` — DNS Records\n"
        "/whois `<domain>` — WHOIS Info\n"
        "/port `<host> <port>` — Port Check\n"
        "/hash `<text>` — Hash Generator\n"
        "/b64enc `<text>` — Base64 Encode\n"
        "/b64dec `<text>` — Base64 Decode\n"
        "/ua `<user-agent>` — Parse User-Agent\n"
        "/unshorten `<url>` — Expand Short URL\n"
        "/ping `<host>` — Ping Host\n"
        "/tor `<ip>` — Tor Exit Node Check\n"
        "/myip — Your IP Info",
        parse_mode="Markdown"
    )

# ── /ip ─────────────────────────────────────────────────
async def ip_lookup(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: /ip <ip address>")
        return
    ip = ctx.args[0]
    try:
        r = requests.get(f"https://ipapi.co/{ip}/json/", timeout=10)
        d = r.json()
        if "error" in d:
            await update.message.reply_text(f"❌ {d.get('reason', 'Invalid IP')}")
            return
        text = (
            f"🌐 *IP Lookup: {ip}*\n\n"
            f"🏳️ Country: {d.get('country_name')} {d.get('country_code')}\n"
            f"🏙️ City: {d.get('city')}\n"
            f"📍 Region: {d.get('region')}\n"
            f"🕐 Timezone: {d.get('timezone')}\n"
            f"📡 ISP: {d.get('org')}\n"
            f"🔢 ASN: {d.get('asn')}\n"
            f"📮 Postal: {d.get('postal')}\n"
            f"🗺️ Coords: {d.get('latitude')}, {d.get('longitude')}"
        )
        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ── /myip ────────────────────────────────────────────────
async def my_ip(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        r = requests.get("https://ipapi.co/json/", timeout=10)
        d = r.json()
        text = (
            f"🖥️ *Server IP Info*\n\n"
            f"IP: `{d.get('ip')}`\n"
            f"🏳️ Country: {d.get('country_name')}\n"
            f"📡 ISP: {d.get('org')}"
        )
        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ── /dns ─────────────────────────────────────────────────
async def dns_lookup(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: /dns <domain>")
        return
    domain = ctx.args[0]
    try:
        lines = [f"🔍 *DNS Records for {domain}*\n"]
        for rtype in ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]:
            try:
                answers = dns.resolver.resolve(domain, rtype)
                records = [str(r) for r in answers]
                lines.append(f"*{rtype}:*\n" + "\n".join(f"  `{rec}`" for rec in records))
            except Exception:
                pass
        await update.message.reply_text("\n".join(lines) or "No records found.", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ── /whois ───────────────────────────────────────────────
async def whois_lookup(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: /whois <domain>")
        return
    domain = ctx.args[0]
    try:
        w = whois.whois(domain)
        created = w.creation_date
        expires = w.expiration_date
        if isinstance(created, list): created = created[0]
        if isinstance(expires, list): expires = expires[0]
        text = (
            f"📋 *WHOIS: {domain}*\n\n"
            f"Registrar: {w.registrar}\n"
            f"Created: {created}\n"
            f"Expires: {expires}\n"
            f"Name Servers: {', '.join(w.name_servers) if w.name_servers else 'N/A'}\n"
            f"Status: {w.status if isinstance(w.status, str) else (w.status[0] if w.status else 'N/A')}"
        )
        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ── /port ────────────────────────────────────────────────
async def port_check(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if len(ctx.args) < 2:
        await update.message.reply_text("Usage: /port <host> <port>")
        return
    host, port_str = ctx.args[0], ctx.args[1]
    try:
        port = int(port_str)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        status = "🟢 OPEN" if result == 0 else "🔴 CLOSED"
        await update.message.reply_text(f"🔌 *Port Scan*\n\nHost: `{host}`\nPort: `{port}`\nStatus: {status}", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ── /hash ────────────────────────────────────────────────
async def hash_gen(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: /hash <text>")
        return
    text = " ".join(ctx.args).encode()
    result = (
        f"#️⃣ *Hash Generator*\n\n"
        f"*MD5:*\n`{hashlib.md5(text).hexdigest()}`\n\n"
        f"*SHA1:*\n`{hashlib.sha1(text).hexdigest()}`\n\n"
        f"*SHA256:*\n`{hashlib.sha256(text).hexdigest()}`\n\n"
        f"*SHA512:*\n`{hashlib.sha512(text).hexdigest()}`"
    )
    await update.message.reply_text(result, parse_mode="Markdown")

# ── /b64enc ──────────────────────────────────────────────
async def b64_encode(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: /b64enc <text>")
        return
    text = " ".join(ctx.args)
    encoded = base64.b64encode(text.encode()).decode()
    await update.message.reply_text(f"🔐 *Base64 Encoded:*\n`{encoded}`", parse_mode="Markdown")

# ── /b64dec ──────────────────────────────────────────────
async def b64_decode(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: /b64dec <encoded>")
        return
    try:
        decoded = base64.b64decode(" ".join(ctx.args)).decode()
        await update.message.reply_text(f"🔓 *Base64 Decoded:*\n`{decoded}`", parse_mode="Markdown")
    except Exception:
        await update.message.reply_text("❌ Invalid Base64 string.")

# ── /ua ──────────────────────────────────────────────────
async def user_agent(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: /ua <user-agent string>")
        return
    ua = " ".join(ctx.args)
    try:
        r = requests.get(f"https://api.apicagent.com/?ua={requests.utils.quote(ua)}", timeout=10)
        d = r.json()
        text = (
            f"🕵️ *User-Agent Parser*\n\n"
            f"Browser: {d.get('browser', {}).get('name')} {d.get('browser', {}).get('version')}\n"
            f"OS: {d.get('os', {}).get('name')} {d.get('os', {}).get('version')}\n"
            f"Device: {d.get('device', {}).get('type')}\n"
            f"Bot: {'Yes' if d.get('is_bot') else 'No'}"
        )
        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ── /unshorten ───────────────────────────────────────────
async def unshorten(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: /unshorten <url>")
        return
    url = ctx.args[0]
    try:
        r = requests.head(url, allow_redirects=True, timeout=10)
        await update.message.reply_text(f"🔗 *Expanded URL:*\n`{r.url}`", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ── /ping ────────────────────────────────────────────────
async def ping_host(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: /ping <host>")
        return
    host = ctx.args[0]
    try:
        start = datetime.now()
        socket.setdefaulttimeout(5)
        socket.gethostbyname(host)
        ms = (datetime.now() - start).microseconds // 1000
        await update.message.reply_text(f"📡 *Ping {host}*\n\nDNS resolved in ~{ms}ms ✅", parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(f"📡 *Ping {host}*\n\n❌ Host unreachable", parse_mode="Markdown")

# ── /tor ─────────────────────────────────────────────────
async def tor_check(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: /tor <ip>")
        return
    ip = ctx.args[0]
    try:
        r = requests.get(f"https://check.torproject.org/cgi-bin/TorBulkExitList.py?ip=1.1.1.1", timeout=10)
        exit_nodes = r.text.splitlines()
        is_tor = ip in exit_nodes
        status = "🧅 YES — This is a Tor exit node!" if is_tor else "✅ NO — Not a Tor exit node"
        await update.message.reply_text(f"🧅 *Tor Check: {ip}*\n\n{status}", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ── Main ─────────────────────────────────────────────────
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ip", ip_lookup))
    app.add_handler(CommandHandler("myip", my_ip))
    app.add_handler(CommandHandler("dns", dns_lookup))
    app.add_handler(CommandHandler("whois", whois_lookup))
    app.add_handler(CommandHandler("port", port_check))
    app.add_handler(CommandHandler("hash", hash_gen))
    app.add_handler(CommandHandler("b64enc", b64_encode))
    app.add_handler(CommandHandler("b64dec", b64_decode))
    app.add_handler(CommandHandler("ua", user_agent))
    app.add_handler(CommandHandler("unshorten", unshorten))
    app.add_handler(CommandHandler("ping", ping_host))
    app.add_handler(CommandHandler("tor", tor_check))
    app.run_polling(drop_pending_updates=True)
