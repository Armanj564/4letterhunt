import os
import random
import string
import asyncio
import aiohttp
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# ── State ──────────────────────────────────────────────────────────────────────
scanning = {}
found_list = {}
stats_db = {}
banned_users = set()
whitelisted = set()
private_mode = False
scan_settings = {}

def default_settings():
    return {
        "length": 4,
        "mode": "mixed",
        "prefix": "",
        "suffix": "",
        "no_repeat": False,
        "must_start_letter": False,
        "must_start_number": False,
        "blacklist": [],
        "platforms": ["tiktok", "instagram", "discord"],
        "require_all": False,
        "require_count": 1,
        "speed": "normal",
        "max_scan": 0,
        "score_filter": 0,
    }

def get_settings(chat_id):
    if chat_id not in scan_settings:
        scan_settings[chat_id] = default_settings()
    return scan_settings[chat_id]

def init_stats(chat_id):
    if chat_id not in stats_db:
        stats_db[chat_id] = {"scanned": 0, "found": 0, "start_time": time.time(), "all_time_scanned": 0, "all_time_found": 0, "best_finds": []}

def init_found(chat_id):
    if chat_id not in found_list:
        found_list[chat_id] = []

# ── Generator ──────────────────────────────────────────────────────────────────
def gen_username(s):
    length = s["length"]
    mode = s["mode"]
    prefix = s["prefix"]
    suffix = s["suffix"]
    blacklist = s["blacklist"]
    if mode == "letters":
        pool = string.ascii_lowercase
    elif mode == "numbers":
        pool = string.digits
    else:
        pool = string.ascii_lowercase + string.digits
    pool = [c for c in pool if c not in blacklist]
    if not pool:
        pool = list(string.ascii_lowercase)
    remaining = length - len(prefix) - len(suffix)
    if remaining <= 0:
        return (prefix + suffix)[:length]
    for _ in range(100):
        mid = ''.join(random.choices(pool, k=remaining))
        username = prefix + mid + suffix
        if s["no_repeat"] and len(set(username)) != len(username):
            continue
        if s["must_start_letter"] and not username[0].isalpha():
            continue
        if s["must_start_number"] and not username[0].isdigit():
            continue
        return username
    return prefix + ''.join(random.choices(pool, k=remaining)) + suffix

# ── Score ──────────────────────────────────────────────────────────────────────
def score_username(u):
    score = 50
    if u.isalpha(): score += 20
    if len(set(u)) == len(u): score += 10
    if u[0].isalpha(): score += 5
    vowels = set("aeiou")
    if any(c in vowels for c in u) and any(c not in vowels for c in u): score += 15
    return min(score, 100)

def score_emoji(score):
    if score >= 90: return "💎"
    if score >= 75: return "🔥"
    if score >= 60: return "✨"
    return "👍"

# ── Platform Checkers ──────────────────────────────────────────────────────────
async def check_tiktok(session, username):
    try:
        async with session.get(f"https://www.tiktok.com/@{username}", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as r:
            if r.status == 404: return True
            text = await r.text()
            if "Couldn&#x27;t find this account" in text or "user-not-found" in text.lower(): return True
            if '"uniqueId"' in text: return False
            return None
    except: return None

async def check_instagram(session, username):
    try:
        async with session.get(f"https://www.instagram.com/{username}/", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as r:
            if r.status == 404: return True
            text = await r.text()
            if "Sorry, this page" in text or "userNotFound" in text: return True
            if '"edge_followed_by"' in text: return False
            return None
    except: return None

async def check_discord(session, username):
    try:
        async with session.get(f"https://discord.id/?prefill={username}", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=8)) as r:
            text = await r.text()
            if "Unknown User" in text: return True
            if "discriminator" in text: return False
            return None
    except: return None

async def check_roblox(session, username):
    try:
        async with session.get(f"https://api.roblox.com/users/get-by-username?username={username}", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=8)) as r:
            data = await r.json()
            return not bool(data.get("Id"))
    except: return None

async def check_twitch(session, username):
    try:
        async with session.get(f"https://www.twitch.tv/{username}", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=8)) as r:
            if r.status == 404: return True
            text = await r.text()
            if '"login"' in text: return False
            return None
    except: return None

async def check_github(session, username):
    try:
        async with session.get(f"https://github.com/{username}", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=8)) as r:
            if r.status == 404: return True
            if r.status == 200: return False
            return None
    except: return None

async def check_snapchat(session, username):
    try:
        async with session.get(f"https://www.snapchat.com/add/{username}", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=8)) as r:
            if r.status == 404: return True
            text = await r.text()
            if "pageNotFound" in text: return True
            if '"username"' in text: return False
            return None
    except: return None

async def check_twitter(session, username):
    try:
        async with session.get(f"https://twitter.com/{username}", headers=HEADERS, timeout=aiohttp.ClientTimeout(total=8)) as r:
            if r.status == 404: return True
            if r.status == 200: return False
            return None
    except: return None

PLATFORM_CHECKERS = {
    "tiktok": check_tiktok,
    "instagram": check_instagram,
    "discord": check_discord,
    "roblox": check_roblox,
    "twitch": check_twitch,
    "github": check_github,
    "snapchat": check_snapchat,
    "twitter": check_twitter,
}

PLATFORM_EMOJI = {
    "tiktok": "🎵", "instagram": "📸", "discord": "💬",
    "roblox": "🎮", "twitch": "🟣", "github": "🐙",
    "snapchat": "👻", "twitter": "🐦",
}

def fmt(status):
    if status is True: return "✅"
    if status is False: return "❌"
    return "❓"

async def check_platforms(session, username, platforms, require_all=False, require_count=1):
    results = {}
    for p in platforms:
        if p in PLATFORM_CHECKERS:
            results[p] = await PLATFORM_CHECKERS[p](session, username)
    available = [p for p, r in results.items() if r is True]
    is_hit = len(available) == len(platforms) if require_all else len(available) >= require_count
    return results, is_hit, available

def is_allowed(user_id):
    if user_id in banned_users: return False
    if private_mode and user_id != OWNER_ID and user_id not in whitelisted: return False
    return True

# ── Commands ───────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        await update.message.reply_text("❌ No access."); return
    await update.message.reply_text(
        "👾 *4-LetterHunt Bot*\n\n"
        "/check — check 10 usernames\n"
        "/check 30 — check up to 50\n"
        "/check abcd — check specific username\n"
        "/scan — auto scan until /stop\n"
        "/stop — stop scanning\n\n"
        "*Settings:*\n"
        "/settings — view settings\n"
        "/setlength 4\n/setmode letters|numbers|mixed\n"
        "/setprefix x\n/setsuffix 0\n"
        "/setplatforms tiktok instagram discord roblox twitch github snapchat twitter\n"
        "/setspeed fast|normal|slow\n"
        "/setmaxscan 100\n/setscorefilter 70\n"
        "/togglerepeat\n/togglestartletter\n/togglestartnumber\n"
        "/blacklist abc\n/requireall\n/requirecount 2\n\n"
        "*Results:*\n"
        "/list — found usernames\n/export — download as file\n/clear — clear list\n/stats\n\n"
        "*Admin:*\n"
        "/ban /unban /whitelist /private /reset\n\n"
        "✅ available  ❌ taken  ❓ unknown",
        parse_mode="Markdown"
    )

async def check_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    chat_id = update.effective_chat.id
    if not is_allowed(uid): return
    s = get_settings(chat_id)
    init_stats(chat_id); init_found(chat_id)

    if context.args and len(context.args) == 1 and not context.args[0].isdigit():
        username = context.args[0].lower()
        msg = await update.message.reply_text(f"🔍 Checking `{username}`...", parse_mode="Markdown")
        async with aiohttp.ClientSession() as session:
            results, is_hit, available = await check_platforms(session, username, s["platforms"], s["require_all"], s["require_count"])
        score = score_username(username)
        lines = [f"{PLATFORM_EMOJI.get(p,'•')} {p.capitalize()}: {fmt(r)}" for p, r in results.items()]
        text = f"`{username}` {score_emoji(score)} Score: {score}/100\n\n" + "\n".join(lines)
        if is_hit: text += f"\n\n🔥 Free on: {', '.join(available)}"
        await msg.edit_text(text, parse_mode="Markdown"); return

    count = 10
    if context.args:
        try: count = max(1, min(50, int(context.args[0])))
        except: pass

    msg = await update.message.reply_text(f"🔍 Checking {count} usernames...")
    lines = []; found = 0
    speed_delay = {"fast": 0.5, "normal": 1.2, "slow": 2.5}.get(s["speed"], 1.2)

    async with aiohttp.ClientSession() as session:
        for _ in range(count):
            username = gen_username(s)
            score = score_username(username)
            if score < s["score_filter"]: continue
            results, is_hit, available = await check_platforms(session, username, s["platforms"], s["require_all"], s["require_count"])
            stats_db[chat_id]["scanned"] += 1
            stats_db[chat_id]["all_time_scanned"] += 1
            plat_str = " ".join(f"{PLATFORM_EMOJI.get(p,'')}{fmt(r)}" for p, r in results.items())
            if is_hit:
                found += 1
                stats_db[chat_id]["found"] += 1
                stats_db[chat_id]["all_time_found"] += 1
                found_list[chat_id].append(username)
                stats_db[chat_id].setdefault("best_finds", []).append(username)
                lines.append(f"🔥 `{username}` {score_emoji(score)}{score} {plat_str}")
            else:
                lines.append(f"❌ `{username}` {plat_str}")
            await asyncio.sleep(speed_delay)

    text = "\n".join(lines) if lines else "No results."
    text += f"\n\n━━━━━━━━━━\n🟢 *{found} available* out of {count}"
    await msg.edit_text(text, parse_mode="Markdown")

async def scan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    chat_id = update.effective_chat.id
    if not is_allowed(uid): return
    if scanning.get(chat_id):
        await update.message.reply_text("⚠️ Already scanning! Use /stop first."); return

    scanning[chat_id] = True
    init_stats(chat_id); init_found(chat_id)
    stats_db[chat_id].update({"scanned": 0, "found": 0, "start_time": time.time()})
    s = get_settings(chat_id)
    speed_delay = {"fast": 0.5, "normal": 1.2, "slow": 2.5}.get(s["speed"], 1.2)

    await update.message.reply_text(
        f"🔎 *Scanning started!*\nPlatforms: {', '.join(s['platforms'])}\nSpeed: {s['speed']} | Length: {s['length']}\n/stop to stop",
        parse_mode="Markdown"
    )
    status_msg = await update.message.reply_text("📊 Scanned: 0 | 🟢 Found: 0")
    last_update = time.time()

    async with aiohttp.ClientSession() as session:
        while scanning.get(chat_id):
            username = gen_username(s)
            score = score_username(username)
            if score < s["score_filter"]:
                continue
            results, is_hit, available = await check_platforms(session, username, s["platforms"], s["require_all"], s["require_count"])
            stats_db[chat_id]["scanned"] += 1
            stats_db[chat_id]["all_time_scanned"] += 1

            if is_hit:
                stats_db[chat_id]["found"] += 1
                stats_db[chat_id]["all_time_found"] += 1
                found_list[chat_id].append(username)
                stats_db[chat_id].setdefault("best_finds", []).append(username)
                sc = stats_db[chat_id]["scanned"]
                fn = stats_db[chat_id]["found"]
                await update.message.reply_text(
                    f"🔥 *AVAILABLE:* `{username}` {score_emoji(score)}\n"
                    f"Score: {score}/100 | Free on: {', '.join(available)}\n"
                    f"#{fn} found | {sc} scanned",
                    parse_mode="Markdown"
                )

            if time.time() - last_update > 10:
                sc = stats_db[chat_id]["scanned"]
                fn = stats_db[chat_id]["found"]
                try: await status_msg.edit_text(f"📊 Scanned: {sc} | 🟢 Found: {fn}\n/stop to stop")
                except: pass
                last_update = time.time()

            if s["max_scan"] > 0 and stats_db[chat_id]["scanned"] >= s["max_scan"]:
                scanning[chat_id] = False
                await update.message.reply_text(f"✅ Reached max scan of {s['max_scan']}. Stopped.")
                break

            await asyncio.sleep(speed_delay)

    sc = stats_db[chat_id].get("scanned", 0)
    fn = stats_db[chat_id].get("found", 0)
    try: await status_msg.edit_text(f"🛑 Stopped.\n📊 Scanned: {sc} | 🟢 Found: {fn}")
    except: pass

async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if scanning.get(chat_id):
        scanning[chat_id] = False
        await update.message.reply_text("🛑 Stopping...")
    else:
        await update.message.reply_text("No active scan.")

async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    init_found(chat_id)
    fl = found_list[chat_id]
    if not fl:
        await update.message.reply_text("📋 Nothing found yet."); return
    text = "📋 *Found Usernames:*\n\n"
    for i, u in enumerate(fl[-50:], 1):
        score = score_username(u)
        text += f"{i}. `{u}` {score_emoji(score)} {score}/100\n"
    if len(fl) > 50: text += f"\n...+{len(fl)-50} more. Use /export"
    await update.message.reply_text(text, parse_mode="Markdown")

async def export_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    init_found(chat_id)
    fl = found_list[chat_id]
    if not fl:
        await update.message.reply_text("Nothing to export."); return
    path = f"/tmp/found_{chat_id}.txt"
    with open(path, "w") as f:
        f.write("\n".join(fl))
    await update.message.reply_document(document=open(path, "rb"), filename="found_usernames.txt", caption=f"📁 {len(fl)} usernames")

async def clear_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    found_list[chat_id] = []
    await update.message.reply_text("🗑 Cleared.")

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    init_stats(chat_id)
    st = stats_db[chat_id]
    elapsed = int(time.time() - st.get("start_time", time.time()))
    best = st.get("best_finds", [])[-5:]
    best_str = " ".join(f"`{u}`" for u in best) if best else "none"
    await update.message.reply_text(
        f"📊 *Stats*\n\nSession: {st.get('scanned',0)} scanned, {st.get('found',0)} found\n"
        f"All time: {st.get('all_time_scanned',0)} scanned, {st.get('all_time_found',0)} found\n"
        f"Uptime: {elapsed//60}m {elapsed%60}s\n\n🏆 Recent: {best_str}",
        parse_mode="Markdown"
    )

async def settings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    s = get_settings(chat_id)
    await update.message.reply_text(
        f"⚙️ *Settings*\n\n"
        f"Length: `{s['length']}` | Mode: `{s['mode']}`\n"
        f"Prefix: `{s['prefix'] or 'none'}` | Suffix: `{s['suffix'] or 'none'}`\n"
        f"No repeat: `{s['no_repeat']}` | Start letter: `{s['must_start_letter']}` | Start number: `{s['must_start_number']}`\n"
        f"Blacklist: `{', '.join(s['blacklist']) or 'none'}`\n"
        f"Platforms: `{', '.join(s['platforms'])}`\n"
        f"Require all: `{s['require_all']}` | Require count: `{s['require_count']}`\n"
        f"Speed: `{s['speed']}` | Max scan: `{s['max_scan'] or 'unlimited'}` | Score filter: `{s['score_filter']}`",
        parse_mode="Markdown"
    )

async def setlength(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_settings(update.effective_chat.id)
    try: s["length"] = max(1, min(16, int(context.args[0]))); await update.message.reply_text(f"✅ Length: {s['length']}")
    except: await update.message.reply_text("Usage: /setlength 4")

async def setmode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_settings(update.effective_chat.id)
    try:
        m = context.args[0].lower()
        assert m in ["letters","numbers","mixed"]
        s["mode"] = m; await update.message.reply_text(f"✅ Mode: {m}")
    except: await update.message.reply_text("Usage: /setmode letters|numbers|mixed")

async def setprefix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_settings(update.effective_chat.id)
    s["prefix"] = context.args[0].lower() if context.args else ""
    await update.message.reply_text(f"✅ Prefix: `{s['prefix'] or 'none'}`", parse_mode="Markdown")

async def setsuffix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_settings(update.effective_chat.id)
    s["suffix"] = context.args[0].lower() if context.args else ""
    await update.message.reply_text(f"✅ Suffix: `{s['suffix'] or 'none'}`", parse_mode="Markdown")

async def setplatforms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_settings(update.effective_chat.id)
    valid = list(PLATFORM_CHECKERS.keys())
    chosen = [a.lower() for a in context.args if a.lower() in valid]
    if not chosen:
        await update.message.reply_text(f"Available: {', '.join(valid)}"); return
    s["platforms"] = chosen
    await update.message.reply_text(f"✅ Platforms: {', '.join(chosen)}")

async def setspeed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_settings(update.effective_chat.id)
    try:
        sp = context.args[0].lower()
        assert sp in ["fast","normal","slow"]
        s["speed"] = sp; await update.message.reply_text(f"✅ Speed: {sp}")
    except: await update.message.reply_text("Usage: /setspeed fast|normal|slow")

async def setmaxscan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_settings(update.effective_chat.id)
    try: s["max_scan"] = max(0, int(context.args[0])); await update.message.reply_text(f"✅ Max scan: {s['max_scan'] or 'unlimited'}")
    except: await update.message.reply_text("Usage: /setmaxscan 100")

async def setscorefilter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_settings(update.effective_chat.id)
    try: s["score_filter"] = max(0, min(100, int(context.args[0]))); await update.message.reply_text(f"✅ Score filter: {s['score_filter']}")
    except: await update.message.reply_text("Usage: /setscorefilter 70")

async def togglerepeat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_settings(update.effective_chat.id)
    s["no_repeat"] = not s["no_repeat"]
    await update.message.reply_text(f"✅ No-repeat: {s['no_repeat']}")

async def togglestartletter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_settings(update.effective_chat.id)
    s["must_start_letter"] = not s["must_start_letter"]
    if s["must_start_letter"]: s["must_start_number"] = False
    await update.message.reply_text(f"✅ Must start letter: {s['must_start_letter']}")

async def togglestartnumber(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_settings(update.effective_chat.id)
    s["must_start_number"] = not s["must_start_number"]
    if s["must_start_number"]: s["must_start_letter"] = False
    await update.message.reply_text(f"✅ Must start number: {s['must_start_number']}")

async def blacklist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_settings(update.effective_chat.id)
    if not context.args:
        s["blacklist"] = []; await update.message.reply_text("✅ Blacklist cleared."); return
    s["blacklist"] = list(context.args[0].lower())
    await update.message.reply_text(f"✅ Blacklisted: {', '.join(s['blacklist'])}")

async def requireall_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_settings(update.effective_chat.id)
    s["require_all"] = not s["require_all"]
    await update.message.reply_text(f"✅ Require all: {s['require_all']}")

async def requirecount_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_settings(update.effective_chat.id)
    try: s["require_count"] = max(1, int(context.args[0])); await update.message.reply_text(f"✅ Require count: {s['require_count']}")
    except: await update.message.reply_text("Usage: /requirecount 2")

async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    try: banned_users.add(int(context.args[0])); await update.message.reply_text("✅ Banned")
    except: await update.message.reply_text("Usage: /ban [user_id]")

async def unban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    try: banned_users.discard(int(context.args[0])); await update.message.reply_text("✅ Unbanned")
    except: await update.message.reply_text("Usage: /unban [user_id]")

async def whitelist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    try: whitelisted.add(int(context.args[0])); await update.message.reply_text("✅ Whitelisted")
    except: await update.message.reply_text("Usage: /whitelist [user_id]")

async def private_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global private_mode
    if update.effective_user.id != OWNER_ID: return
    private_mode = not private_mode
    await update.message.reply_text(f"✅ Private mode: {private_mode}")

async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    scan_settings[update.effective_chat.id] = default_settings()
    await update.message.reply_text("✅ Settings reset.")

# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    handlers = [
        ("start", start), ("check", check_cmd), ("scan", scan_cmd), ("stop", stop_cmd),
        ("list", list_cmd), ("export", export_cmd), ("clear", clear_cmd), ("stats", stats_cmd),
        ("settings", settings_cmd), ("setlength", setlength), ("setmode", setmode),
        ("setprefix", setprefix), ("setsuffix", setsuffix), ("setplatforms", setplatforms),
        ("setspeed", setspeed), ("setmaxscan", setmaxscan), ("setscorefilter", setscorefilter),
        ("togglerepeat", togglerepeat), ("togglestartletter", togglestartletter),
        ("togglestartnumber", togglestartnumber), ("blacklist", blacklist_cmd),
        ("requireall", requireall_cmd), ("requirecount", requirecount_cmd),
        ("ban", ban_cmd), ("unban", unban_cmd), ("whitelist", whitelist_cmd),
        ("private", private_cmd), ("reset", reset_cmd),
    ]
    for name, func in handlers:
        app.add_handler(CommandHandler(name, func))
    print("4-LetterHunt Bot running...")
    app.run_polling()
