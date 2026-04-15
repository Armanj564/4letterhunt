import requests
import dns.resolver
import whois
import base64
import hashlib
import socket
from datetime import datetime

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "YOUR_BOT_TOKEN_HERE"

# ── START ─────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡️ CyberTools Bot\n\n"
        "/ip <ip>\n/dns <domain>\n/whois <domain>\n/myip",
        parse_mode="Markdown"
    )

# ── IP LOOKUP ─────────────────────────
async def ip_lookup(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: /ip <ip>")
        return

    ip = ctx.args[0]
    try:
        r = requests.get(f"https://ipapi.co/{ip}/json/", timeout=10)
        d = r.json()

        text = (
            f"🌐 IP: {ip}\n\n"
            f"Country: {d.get('country_name')}\n"
            f"City: {d.get('city')}\n"
            f"ISP: {d.get('org')}\n"
            f"Coords: {d.get('latitude')}, {d.get('longitude')}"
        )

        await update.message.reply_text(text)

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# ── MY IP ─────────────────────────────
async def my_ip(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    r = requests.get("https://ipapi.co/json/")
    d = r.json()

    await update.message.reply_text(
        f"Your IP: {d.get('ip')}\nCountry: {d.get('country_name')}"
    )

# ── DNS ───────────────────────────────
async def dns_lookup(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: /dns <domain>")
        return

    domain = ctx.args[0]
    try:
        answers = dns.resolver.resolve(domain, "A")
        ips = "\n".join(str(r) for r in answers)
        await update.message.reply_text(f"DNS A records:\n{ips}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# ── MAIN ──────────────────────────────
if __name__ == "__main__":
    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
        raise ValueError("BOT TOKEN is missing!")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ip", ip_lookup))
    app.add_handler(CommandHandler("myip", my_ip))
    app.add_handler(CommandHandler("dns", dns_lookup))

    app.run_polling()
