"""
MX Bikes Hotlap Bot v6
━━━━━━━━━━━━━━━━━━━━━━
Apple-inspired dark mode aesthetic
Clean capitals · Minimal design · Bold readability

Commands:
  /hotlap       - Submit a hotlap
  /leaderboard  - View track leaderboard
  /pb           - View personal bests
  /tracks       - List all tracks
  /delete       - Delete most recent hotlap
"""

import discord
from discord import app_commands, ui
from discord.ext import commands
import json
import os
from datetime import datetime
import io
import base64
from playwright.async_api import async_playwright

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SETUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BOT_TOKEN = "MTQ4OTQ4NTA3Njc4OTE5OTA3OA.GeUsLc.vyssJovsbNBNMymRSZdXdmTkObOn3wt-ObQnhs"
DATA_FILE = "hotlaps.json"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OEM BIKE PACK v0.19.1
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OEM_BIKES = {
    "Beta": [
        ("2024 Beta 450 RX", "Beta 450 RX"),
    ],
    "Fantic": [
        ("2025 Fantic XXF 250", "Fantic XXF 250"),
        ("2025 Fantic XXF 450", "Fantic XXF 450"),
    ],
    "GasGas": [
        ("2024 GasGas MC 125", "GasGas MC 125"),
        ("2024 GasGas MC 250", "GasGas MC 250"),
        ("2024 GasGas MC 250F", "GasGas MC 250F"),
        ("2024 GasGas MC 450F", "GasGas MCF 450"),
    ],
    "Honda": [
        ("2023 Honda CRF250R", "Honda CRF 250"),
        ("2023 Honda CRF450R", "Honda CRF 450"),
    ],
    "Husqvarna": [
        ("2023 Husqvarna TC 85", "Husqvarna TC 85"),
        ("2023 Husqvarna TC 125", "Husqvarna TC 125"),
        ("2023 Husqvarna TC 250", "Husqvarna TC 250"),
        ("2023 Husqvarna FC 250", "Husqvarna FC 250"),
        ("2023 Husqvarna FC 350", "Husqvarna FC 350"),
        ("2023 Husqvarna FC 450", "Husqvarna FC 450"),
    ],
    "Kawasaki": [
        ("2002 Kawasaki KX 500", "Kawasaki KX 500"),
        ("2023 Kawasaki KX 250", "Kawasaki KX 250"),
        ("2023 Kawasaki KX 450", "Kawasaki KX 450"),
    ],
    "KTM": [
        ("2023 KTM 85 SX", "KTM 85 SX"),
        ("2023 KTM 125 SX", "KTM 125 SX"),
        ("2023 KTM 250 SX", "KTM 250 SX"),
        ("2023 KTM 250 SX-F", "KTM 250 SX-F"),
        ("2023 KTM 350 SX-F", "KTM 350 SX-F"),
        ("2023 KTM 450 SX-F", "KTM 450 SX-F"),
    ],
    "Stark": [
        ("2023 Stark Varg", "Stark Varg"),
    ],
    "Suzuki": [
        ("2022 Suzuki RM-Z 250", "Suzuki RM-Z 250"),
        ("2022 Suzuki RM-Z 450", "Suzuki RM-Z 450"),
    ],
    "TM": [
        ("2023 TM MX 125", "TM MX 125"),
        ("2023 TM MX 250", "TM MX 250"),
        ("2023 TM MX 250 FI", "TM MX 250 FI"),
        ("2023 TM MX 450 FI", "TM MX 450 FI"),
    ],
    "Triumph": [
        ("2024 Triumph TF 250-X", "Triumph TF 250-X"),
        ("2024 Triumph TF 450-RC", "Triumph TF 450-RC"),
    ],
    "Yamaha": [
        ("2024 Yamaha YZ 125", "Yamaha YZ 125"),
        ("2024 Yamaha YZ 250", "Yamaha YZ 250"),
        ("2023 Yamaha YZ250F", "Yamaha YZ 250F"),
        ("2024 Yamaha YZ450F", "Yamaha YZ 450F"),
    ],
}

ALL_BIKES = {}
for brand, bikes in OEM_BIKES.items():
    for display, value in bikes:
        ALL_BIKES[value] = {"display": display, "brand": brand}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BRAND SYSTEM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BRAND_COLORS = {
    "Beta":       0xCC0000,
    "Fantic":     0x1A3668,
    "GasGas":     0xD91920,
    "Honda":      0xCC0000,
    "Husqvarna":  0x203B7D,
    "Kawasaki":   0x00A651,
    "KTM":        0xFF6600,
    "Stark":      0x7B2D8E,
    "Suzuki":     0xF5D000,
    "TM":         0x0055A4,
    "Triumph":    0x1E1E1E,
    "Yamaha":     0x0D47A1,
}

# Dark mode neutral for secondary embeds
DARK_EMBED = 0x1C1C1E   # Apple dark mode background
GOLD_ACCENT = 0xFFD60A   # Apple system yellow / gold

BRAND_SELECT_EMOJI = {
    "Beta": "🔴", "Fantic": "🔵", "GasGas": "🔴", "Honda": "❤️",
    "Husqvarna": "💙", "Kawasaki": "💚", "KTM": "🧡", "Stark": "💜",
    "Suzuki": "💛", "TM": "🔷", "Triumph": "🖤", "Yamaha": "💎",
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CARD RENDERER — HTML/CSS → Chromium screenshot
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Embed Inter fonts as base64 so cards render with no external deps
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

def _b64_font(name):
    path = os.path.join(FONT_DIR, name)
    if not os.path.isfile(path):
        print(f"❌ Font file not found: {path}")
        exit(1)
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Load at startup — cached in memory
print("⏳ Loading fonts…")
_FONTS = {
    "bold":  _b64_font("Inter-Bold.ttf"),
    "semi":  _b64_font("Inter-SemiBold.ttf"),
    "med":   _b64_font("Inter-Medium.ttf"),
    "reg":   _b64_font("Inter-Regular.ttf"),
    "light": _b64_font("Inter-Light.ttf"),
}
print("✅ Fonts loaded")

BRAND_COLORS_HEX = {
    "Beta":      "#cc0000", "Fantic":    "#1a3668", "GasGas":    "#d91920",
    "Honda":     "#cc0000", "Husqvarna": "#203b7d", "Kawasaki":  "#00a651",
    "KTM":       "#ff6600", "Stark":     "#7b2d8e", "Suzuki":    "#f5d000",
    "TM":        "#0055a4", "Triumph":   "#505050", "Yamaha":    "#0d47a1",
}

# ── Persistent browser pool ──
_browser = None

async def _get_browser():
    """Reuse a single Chromium instance across all card renders."""
    global _browser
    if _browser is None or not _browser.is_connected():
        pw = await async_playwright().start()
        _browser = await pw.chromium.launch()
    return _browser


def _build_card_html(
    username, badge_type, time_str, track, bike_display,
    class_tag, rank_html, brand, lap_count, date_str,
    improvement=None, avatar_url=None,
):
    bc = BRAND_COLORS_HEX.get(brand, "#888")

    badge_cfg = {
        "track_record":  {"label": "TRACK RECORD",  "bg": "linear-gradient(135deg, #FFD60A, #F0A000)", "fg": "#000", "glow": "#FFD60A"},
        "personal_best": {"label": "PERSONAL BEST", "bg": "linear-gradient(135deg, #0A84FF, #0060DD)", "fg": "#fff", "glow": "#0A84FF"},
        "hotlap":        {"label": "HOTLAP",         "bg": "rgba(255,255,255,0.07)", "fg": "rgba(255,255,255,0.45)", "glow": "transparent"},
    }
    badge = badge_cfg[badge_type]

    is_record = badge_type == "track_record"
    is_pb = badge_type == "personal_best"
    time_color = "#FFD60A" if is_record else "#fff"
    time_glow = f"0 0 30px {bc}55, 0 0 60px {bc}22" if is_record else "0 0 20px rgba(255,255,255,0.04)"
    rank_color = "#FFD60A" if "P1 OF" in rank_html else "rgba(255,255,255,0.7)"

    imp_html = ""
    if improvement:
        imp_html = f'''<div class="imp"><svg width="8" height="7" viewBox="0 0 10 8"><polygon points="5,0 10,8 0,8" fill="#30D158"/></svg><span>{improvement}</span></div>'''

    star_html = ""
    if is_record:
        star_html = '<svg class="star" width="13" height="13" viewBox="0 0 24 24" fill="#FFD60A"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>'

    avatar_html = (
        f'<img src="{avatar_url}" class="av-img"/>'
        if avatar_url
        else f'<div class="av-init">{username[0].upper()}</div>'
    )

    F = _FONTS
    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
@font-face {{ font-family:'I'; font-weight:700; src:url(data:font/ttf;base64,{F["bold"]}) format('truetype'); }}
@font-face {{ font-family:'I'; font-weight:600; src:url(data:font/ttf;base64,{F["semi"]}) format('truetype'); }}
@font-face {{ font-family:'I'; font-weight:500; src:url(data:font/ttf;base64,{F["med"]}) format('truetype'); }}
@font-face {{ font-family:'I'; font-weight:400; src:url(data:font/ttf;base64,{F["reg"]}) format('truetype'); }}
@font-face {{ font-family:'I'; font-weight:300; src:url(data:font/ttf;base64,{F["light"]}) format('truetype'); }}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{background:#000;margin:0;padding:0}}
body{{font-family:'I',system-ui,sans-serif;width:620px;padding:10px}}

/* ── Card shell ── */
.c{{
    position:relative;width:100%;border-radius:16px;
    box-shadow:0 8px 40px rgba(0,0,0,0.8),0 1px 0 rgba(255,255,255,0.06) inset;
}}
.ci{{
    border-radius:14px;overflow:hidden;
    background:linear-gradient(145deg,#19191d 0%,#131316 60%,#101013 100%);
    position:relative;
}}

/* ── Accent stripe — left ── */
.str{{
    position:absolute;left:0;top:0;bottom:0;width:3px;
    background:linear-gradient(180deg,{bc},{bc}66);
    box-shadow:0 0 16px {bc}55,0 0 40px {bc}18;
}}

/* ── Brand ambient light ── */
.gl{{
    position:absolute;top:-50px;right:-40px;width:200px;height:200px;
    border-radius:50%;
    background:radial-gradient(circle,{bc}14 0%,{bc}06 45%,transparent 70%);
    pointer-events:none;
}}

/* ── Noise texture ── */
.nz{{
    position:absolute;inset:0;opacity:0.025;
    background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    pointer-events:none;
}}

.ct{{position:relative;z-index:1;padding:18px 22px 14px 18px;}}

/* ── Top row ── */
.tr{{display:flex;align-items:center;gap:10px;margin-bottom:10px}}
.av{{
    width:34px;height:34px;border-radius:50%;flex-shrink:0;
    border:2px solid {bc};box-shadow:0 0 10px {bc}44;
    overflow:hidden;display:flex;align-items:center;justify-content:center;
    background:rgba(255,255,255,0.05);
}}
.av-img{{width:100%;height:100%;object-fit:cover}}
.av-init{{font-size:13px;font-weight:700;color:rgba(255,255,255,0.55)}}
.un{{
    font-size:14px;font-weight:700;color:#fff;letter-spacing:0.6px;
    flex:1;text-shadow:0 1px 2px rgba(0,0,0,0.4);
}}
.ba{{display:flex;align-items:center;gap:5px}}
.star{{filter:drop-shadow(0 0 3px #FFD60A88)}}
.bd{{
    font-size:9.5px;font-weight:700;letter-spacing:0.7px;
    padding:3.5px 10px;border-radius:100px;
    background:{badge['bg']};color:{badge['fg']};
    box-shadow:0 0 12px {badge['glow']}28;white-space:nowrap;
}}

/* ── Hero row: track left, time right ── */
.hero{{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin-bottom:14px}}
.trk{{
    font-size:38px;font-weight:700;color:#fff;
    letter-spacing:-1px;line-height:1;text-transform:uppercase;
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1;
}}
.tm{{
    font-size:38px;font-weight:700;color:{time_color};
    letter-spacing:-1px;line-height:1;text-shadow:{time_glow};
    white-space:nowrap;flex-shrink:0;
}}
.imp{{
    display:flex;align-items:center;gap:4px;
    font-size:10px;font-weight:700;color:#30D158;
    text-shadow:0 0 8px #30D15833;padding-bottom:4px;
}}
/* ── Divider ── */
.dv{{height:1px;margin-bottom:11px;background:linear-gradient(90deg,rgba(255,255,255,0.07),rgba(255,255,255,0.02))}}
/* ── Info row ── */
.ir{{display:flex;align-items:flex-start;gap:0;margin-bottom:12px;}}
.ic{{display:flex;flex-direction:column;gap:2px}}
.ic.bike{{flex:1;min-width:0;align-items:flex-start}}
.ic.class{{width:75px;flex-shrink:0;text-align:left}}
.ic.rank{{width:130px;flex-shrink:0;text-align:left}}
.il{{font-size:8.5px;font-weight:500;color:rgba(255,255,255,0.28);letter-spacing:1.2px;text-transform:uppercase;}}
.iv{{font-size:12.5px;font-weight:600;color:rgba(255,255,255,0.72);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:1.5;}}
.iv.rk{{color:{rank_color};white-space:nowrap;}}
.iv.gap{{font-size:10.5px;font-weight:500;color:rgba(255,255,255,0.45);white-space:nowrap;}}
/* ── Bike pill ── */
.bp{{
    display:inline-block;width:fit-content;
    font-size:11.5px;font-weight:600;color:rgba(255,255,255,0.88);
    background:{bc}1a;border:1px solid {bc}40;border-radius:5px;
    padding:1px 7px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
    max-width:100%;line-height:1.55;
}}

/* ── Footer ── */
.fd{{height:1px;margin-bottom:9px;background:linear-gradient(90deg,rgba(255,255,255,0.05),rgba(255,255,255,0.015))}}
.ft{{
    display:flex;align-items:center;
    font-size:9.5px;color:rgba(255,255,255,0.22);letter-spacing:0.3px;
}}
.ft .bn{{color:{bc};font-weight:600;text-shadow:0 0 6px {bc}33}}
.ft .sp{{margin:0 7px;opacity:0.35}}
</style></head>
<body>
<div class="c"><div class="ci">
    <div class="str"></div>
    <div class="gl"></div>
    <div class="nz"></div>
    <div class="ct">
        <div class="tr">
            <div class="av">{avatar_html}</div>
            <div class="un">{username.upper()}</div>
            <div style="flex:1"></div>
            <div class="ba">{star_html}<div class="bd">{badge['label']}</div></div>
        </div>
        <div class="hero">
            <div class="trk">{track}</div>
            <div style="display:flex;align-items:baseline;gap:8px;flex-shrink:0">
                <div class="tm">{time_str}</div>
                {imp_html}
            </div>
        </div>
        <div class="dv"></div>
        <div class="ir">
            <div class="ic bike"><div class="il">Bike</div><div class="bp">{bike_display}</div></div>
            <div class="ic class"><div class="il">Class</div><div class="iv">{class_tag}</div></div>
            <div class="ic rank"><div class="il">Rank</div>{rank_html}</div>
        </div>
        <div class="fd"></div>
        <div class="ft">
            <span class="bn">{brand.upper()}</span>
            <span class="sp">&middot;</span><span>{lap_count} LAPS</span>
            <span class="sp">&middot;</span><span>{date_str}</span>
        </div>
    </div>
</div></div>
</body></html>'''


async def render_card_to_buffer(html):
    """Render HTML card to PNG bytes via headless Chromium."""
    browser = await _get_browser()
    page = await browser.new_page(
        viewport={"width": 660, "height": 440},
        device_scale_factor=3,
    )
    try:
        await page.set_content(html, wait_until="networkidle")
        card = page.locator(".c")
        png_bytes = await card.screenshot(type="png", omit_background=True)
    finally:
        await page.close()

    buf = io.BytesIO(png_bytes)
    buf.seek(0)
    return buf

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BOT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except (json.JSONDecodeError, ValueError):
            print(f"⚠️ {DATA_FILE} was corrupted, starting fresh")
    return {"hotlaps": []}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def parse_time(time_str: str) -> float:
    time_str = time_str.strip()
    try:
        if ":" in time_str:
            parts = time_str.split(":")
            return int(parts[0]) * 60 + float(parts[1])
        return float(time_str)
    except ValueError:
        return -1


def format_time(seconds: float) -> str:
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m}:{s:06.3f}" if m > 0 else f"{s:.3f}"


def get_bike_brand(bike: str) -> str:
    if bike in ALL_BIKES:
        return ALL_BIKES[bike]["brand"]
    for b in BRAND_COLORS:
        if b.lower() in bike.lower():
            return b
    return "Unknown"


def get_bike_color(bike: str) -> int:
    return BRAND_COLORS.get(get_bike_brand(bike), DARK_EMBED)


def get_bike_display(bike: str) -> str:
    return ALL_BIKES[bike]["display"] if bike in ALL_BIKES else bike


def get_class_tag(bike: str) -> str:
    if "Varg" in bike: return "ELECTRIC"
    if "500" in bike: return "500CC"
    if "450" in bike: return "450CC"
    if "350" in bike: return "350CC"
    if any(x in bike for x in ["CRF 250", "FC 250", "MC 250F", "MCF", "SX-F", "YZ 250F", "YZ250F", "MX 250 FI", "XXF 250", "TF 250", "RM-Z 250"]):
        return "250F"
    if "250" in bike: return "250CC"
    if "125" in bike: return "125CC"
    if "85" in bike: return "85CC"
    return "OPEN"


def get_rank(data, track, user_id, time_seconds):
    times = [h for h in data["hotlaps"] if h["track"].lower() == track.lower()]
    best = {}
    for h in times:
        uid = h["user_id"]
        if uid not in best or h["time_seconds"] < best[uid]:
            best[uid] = h["time_seconds"]
    if user_id not in best or time_seconds < best[user_id]:
        best[user_id] = time_seconds
    s = sorted(best.values())
    try:
        return s.index(time_seconds) + 1, len(s)
    except ValueError:
        return len(s), len(s)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CARD BUILDER — IMAGE-BASED
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def build_hotlap_card(interaction, track, bike, seconds, data, notes=None, rider=None):
    """Build a hotlap card as a discord.File image attachment."""
    rider = rider or interaction.user
    bike_display = get_bike_display(bike)
    brand = get_bike_brand(bike)
    class_tag = get_class_tag(bike)
    time_str = format_time(seconds)
    date_str = datetime.now().strftime("%b %d, %Y").upper()

    user_times = [
        h for h in data["hotlaps"]
        if h["user_id"] == rider.id
        and h["track"].lower() == track.lower()
    ]
    is_pb = seconds <= min(h["time_seconds"] for h in user_times) if user_times else True

    all_track = [h for h in data["hotlaps"] if h["track"].lower() == track.lower()]
    is_record = seconds <= min(h["time_seconds"] for h in all_track) if all_track else True

    rank, total = get_rank(data, track, rider.id, seconds)

    # Badge type
    if is_record:
        badge_type = "track_record"
    elif is_pb:
        badge_type = "personal_best"
    else:
        badge_type = "hotlap"

    # Rank HTML — position + gap on separate lines
    if rank == 1:
        rank_html = f'<div class="iv rk">P1 OF {total}</div>'
    else:
        best_time = min(h["time_seconds"] for h in all_track)
        gap = seconds - best_time
        rank_html = f'<div class="iv rk">P{rank} OF {total}</div><div class="iv gap">+{gap:.3f}s</div>'

    # Improvement
    improvement = None
    previous = [h for h in user_times if h["time_seconds"] != seconds]
    if previous and is_pb:
        old_pb = min(h["time_seconds"] for h in previous)
        imp = old_pb - seconds
        improvement = f"{imp:.3f}s"

    # Avatar URL (Chromium fetches it directly — no need to download)
    avatar_url = str(rider.display_avatar.url)

    # Build HTML and render to PNG
    html = _build_card_html(
        username=rider.display_name,
        badge_type=badge_type,
        time_str=time_str,
        track=track,
        bike_display=bike_display,
        class_tag=class_tag,
        rank_html=rank_html,
        brand=brand,
        lap_count=len(all_track),
        date_str=date_str,
        improvement=improvement,
        avatar_url=avatar_url,
    )

    img_buf = await render_card_to_buffer(html)
    return discord.File(img_buf, filename="hotlap.png")




# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LEADERBOARD CARD BUILDER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LEADERBOARD_MESSAGES_FILE = "leaderboard_messages.json"

def normalize_track_key(track: str) -> str:
    return " ".join(track.lower().split())


def get_leaderboard_storage_key(channel_id: int, track: str) -> str:
    return f"{channel_id}:{normalize_track_key(track)}"


def get_leaderboard_filename(track: str) -> str:
    return f"leaderboard_{normalize_track_key(track).replace(' ', '_')}.png"


def load_lb_messages():
    if os.path.exists(LEADERBOARD_MESSAGES_FILE):
        try:
            with open(LEADERBOARD_MESSAGES_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except (json.JSONDecodeError, ValueError):
            print(f"⚠️ {LEADERBOARD_MESSAGES_FILE} was corrupted, rebuilding it")
    return {}


def save_lb_messages(data):
    with open(LEADERBOARD_MESSAGES_FILE, "w") as f:
        json.dump(data, f, indent=2)


async def find_existing_leaderboard_messages(channel, track: str, limit: int = 250):
    expected_filename = get_leaderboard_filename(track)
    matches = []

    async for message in channel.history(limit=limit):
        if message.author.id != bot.user.id:
            continue
        if any(att.filename == expected_filename for att in message.attachments):
            matches.append(message)

    return matches


async def remove_leaderboard_message(channel, track: str):
    lb_messages = load_lb_messages()
    storage_key = get_leaderboard_storage_key(channel.id, track)
    legacy_key = normalize_track_key(track)

    message_ids = []
    for key in (storage_key, legacy_key):
        msg_id = lb_messages.get(key)
        if msg_id:
            message_ids.append(msg_id)

    for msg_id in message_ids:
        try:
            msg = await channel.fetch_message(int(msg_id))
            await msg.delete()
        except (discord.NotFound, discord.HTTPException, ValueError):
            pass

    existing_messages = await find_existing_leaderboard_messages(channel, track)
    existing_message_ids = {str(message.id) for message in existing_messages}
    for message in existing_messages:
        try:
            await message.delete()
        except discord.HTTPException:
            pass

    for key in list(lb_messages.keys()):
        if key in {storage_key, legacy_key} or lb_messages.get(key) in existing_message_ids:
            lb_messages.pop(key, None)

    save_lb_messages(lb_messages)


def _build_leaderboard_html(track, ranked, F, BRAND_COLORS_HEX):
    """Build leaderboard card HTML for a track."""
    rows_html = ""
    for i, entry in enumerate(ranked[:10]):
        pos = i + 1
        if pos == 1:
            pos_color = "#FFD60A"
            pos_label = "1"
        elif pos == 2:
            pos_color = "#C0C0C0"
            pos_label = "2"
        elif pos == 3:
            pos_color = "#CD7F32"
            pos_label = "3"
        else:
            pos_color = "rgba(255,255,255,0.3)"
            pos_label = str(pos)

        gap_html = ""
        if i > 0:
            diff = entry["time_seconds"] - ranked[0]["time_seconds"]
            gap_html = f'<span class="lb-gap">+{diff:.3f}s</span>'

        brand = get_bike_brand(entry["bike"])
        bc = BRAND_COLORS_HEX.get(brand, "#888")
        bike_d = get_bike_display(entry["bike"])
        class_tag = get_class_tag(entry["bike"])

        rows_html += f"""
        <div class="lb-row">
            <div class="lb-pos" style="color:{pos_color}">{pos_label}</div>
            <div class="lb-info">
                <div class="lb-name">{entry['username'].upper()}</div>
                <div class="lb-bike"><span class="lb-pill" style="border-color:{bc}55;background:{bc}18">{bike_d}</span><span class="lb-class">{class_tag}</span></div>
            </div>
            <div class="lb-right">
                <div class="lb-time" style="color:{'#FFD60A' if i==0 else '#fff'}">{entry['time_display']}</div>
                {gap_html}
            </div>
        </div>"""

    total_laps = 0  # placeholder, passed in separately
    return rows_html


async def build_leaderboard_card(track, data):
    """Build a leaderboard image card for a track."""
    times = [h for h in data["hotlaps"] if h["track"].lower() == track.lower()]
    if not times:
        return None

    best = {}
    for h in times:
        uid = h["user_id"]
        if uid not in best or h["time_seconds"] < best[uid]["time_seconds"]:
            best[uid] = h
    ranked = sorted(best.values(), key=lambda x: x["time_seconds"])
    total_laps = len(times)

    rows_html = ""
    for i, entry in enumerate(ranked[:10]):
        pos = i + 1
        pos_color = "#FFD60A" if pos == 1 else "#C0C0C0" if pos == 2 else "#CD7F32" if pos == 3 else "rgba(255,255,255,0.3)"
        gap_html = ""
        if i > 0:
            diff = entry["time_seconds"] - ranked[0]["time_seconds"]
            gap_html = f'<div class="lb-gap">+{diff:.3f}s</div>'
        brand = get_bike_brand(entry["bike"])
        bc = BRAND_COLORS_HEX.get(brand, "#888")
        bike_d = get_bike_display(entry["bike"])
        class_tag = get_class_tag(entry["bike"])
        rows_html += f"""
        <div class="lb-row">
            <div class="lb-pos" style="color:{pos_color}">{pos}</div>
            <div class="lb-info">
                <div class="lb-name">{entry["username"].upper()}</div>
                <div class="lb-bike">
                    <span class="lb-pill" style="border-color:{bc}55;background:{bc}18">{bike_d}</span>
                    <span class="lb-class">{class_tag}</span>
                </div>
            </div>
            <div class="lb-right">
                <div class="lb-time" style="color:{'#FFD60A' if i==0 else '#fff'}">{entry["time_display"]}</div>
                {gap_html}
            </div>
        </div>"""

    F = _FONTS
    row_count = min(len(ranked), 10)
    card_height = 90 + 52 + (row_count * 54) + 16 + 36
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
@font-face {{ font-family:'I'; font-weight:700; src:url(data:font/ttf;base64,{F["bold"]}) format('truetype'); }}
@font-face {{ font-family:'I'; font-weight:600; src:url(data:font/ttf;base64,{F["semi"]}) format('truetype'); }}
@font-face {{ font-family:'I'; font-weight:500; src:url(data:font/ttf;base64,{F["med"]}) format('truetype'); }}
@font-face {{ font-family:'I'; font-weight:400; src:url(data:font/ttf;base64,{F["reg"]}) format('truetype'); }}
html,body{{background:#000;margin:0;padding:0}}
body{{font-family:'I',system-ui,sans-serif;width:540px;padding:10px}}
.c{{border-radius:16px;box-shadow:0 8px 40px rgba(0,0,0,0.8);}}
.ci{{border-radius:14px;overflow:hidden;background:linear-gradient(145deg,#19191d,#131316,#101013);position:relative;}}
.str{{position:absolute;left:0;top:0;bottom:0;width:3px;background:linear-gradient(180deg,#FFD60A,#F0A00066);}}
.gl{{position:absolute;top:-40px;right:-30px;width:160px;height:160px;border-radius:50%;background:radial-gradient(circle,#FFD60A10,transparent 70%);pointer-events:none;}}
.ct{{position:relative;z-index:1;padding:16px 20px 12px 18px;}}
.hdr{{margin-bottom:14px;}}
.hdr-label{{font-size:8px;font-weight:500;color:rgba(255,255,255,0.3);letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px;}}
.hdr-track{{font-size:26px;font-weight:700;color:#fff;letter-spacing:-0.5px;line-height:1;text-transform:uppercase;}}
.dv{{height:1px;margin-bottom:10px;background:linear-gradient(90deg,rgba(255,255,255,0.08),transparent);}}
.lb-row{{display:flex;align-items:center;gap:12px;padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.04);}}
.lb-row:last-child{{border-bottom:none;}}
.lb-pos{{font-size:18px;font-weight:700;width:22px;text-align:center;flex-shrink:0;line-height:1;}}
.lb-info{{flex:1;min-width:0;}}
.lb-name{{font-size:11px;font-weight:700;color:#fff;letter-spacing:0.4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.lb-bike{{display:flex;align-items:center;gap:5px;margin-top:2px;}}
.lb-pill{{font-size:9px;font-weight:600;color:rgba(255,255,255,0.7);border:1px solid;border-radius:4px;padding:1px 5px;white-space:nowrap;}}
.lb-class{{font-size:9px;font-weight:500;color:rgba(255,255,255,0.35);}}
.lb-right{{text-align:right;flex-shrink:0;}}
.lb-time{{font-size:13px;font-weight:700;letter-spacing:-0.3px;line-height:1;}}
.lb-gap{{font-size:9.5px;font-weight:500;color:rgba(255,255,255,0.4);margin-top:2px;}}
.footer{{display:flex;align-items:center;justify-content:space-between;margin-top:10px;}}
.footer-l{{font-size:8.5px;color:rgba(255,255,255,0.2);letter-spacing:0.3px;}}
.footer-r{{font-size:8.5px;color:rgba(255,255,255,0.2);}}
</style></head><body>
<div class="c"><div class="ci">
    <div class="str"></div><div class="gl"></div>
    <div class="ct">
        <div class="hdr">
            <div class="hdr-label">🏁 Track Leaderboard</div>
            <div class="hdr-track">{track}</div>
        </div>
        <div class="dv"></div>
        {rows_html}
        <div class="footer">
            <span class="footer-l">👤 {len(ranked)} riders</span>
            <span class="footer-r">🔁 {total_laps} laps</span>
        </div>
    </div>
</div></div>
</body></html>"""

    browser = await _get_browser()
    page = await browser.new_page(
        viewport={"width": 560, "height": card_height},
        device_scale_factor=3,
    )
    try:
        await page.set_content(html, wait_until="networkidle")
        card_el = page.locator(".c")
        png_bytes = await card_el.screenshot(type="png", omit_background=True)
    finally:
        await page.close()

    buf = io.BytesIO(png_bytes)
    buf.seek(0)
    return discord.File(buf, filename=get_leaderboard_filename(track))


async def post_or_update_leaderboard(channel, track, data):
    """Post a new leaderboard card or edit the existing one for this track."""
    card_file = await build_leaderboard_card(track, data)
    lb_messages = load_lb_messages()
    storage_key = get_leaderboard_storage_key(channel.id, track)
    legacy_key = normalize_track_key(track)

    if card_file is None:
        await remove_leaderboard_message(channel, track)
        return

    candidate_ids = []
    for key in (storage_key, legacy_key):
        msg_id = lb_messages.get(key)
        if msg_id:
            candidate_ids.append(msg_id)

    for msg_id in candidate_ids:
        try:
            msg = await channel.fetch_message(int(msg_id))
            await msg.edit(attachments=[card_file])
            lb_messages[storage_key] = str(msg.id)
            if legacy_key != storage_key:
                lb_messages.pop(legacy_key, None)
            save_lb_messages(lb_messages)
            return
        except (discord.NotFound, discord.HTTPException, ValueError):
            pass

    existing_messages = await find_existing_leaderboard_messages(channel, track)
    if existing_messages:
        primary = existing_messages[-1]
        try:
            await primary.edit(attachments=[card_file])
            for duplicate in existing_messages[:-1]:
                try:
                    await duplicate.delete()
                except discord.HTTPException:
                    pass
            lb_messages[storage_key] = str(primary.id)
            if legacy_key != storage_key:
                lb_messages.pop(legacy_key, None)
            save_lb_messages(lb_messages)
            return
        except discord.HTTPException:
            pass

    msg = await channel.send(file=card_file)
    lb_messages[storage_key] = str(msg.id)
    if legacy_key != storage_key:
        lb_messages.pop(legacy_key, None)
    save_lb_messages(lb_messages)


async def refresh_all_leaderboards(channel, data):
    tracks = sorted({h["track"] for h in data["hotlaps"]}, key=str.lower)
    lb_messages = load_lb_messages()

    existing_messages = []
    async for message in channel.history(limit=500):
        if message.author.id != bot.user.id:
            continue
        if any(att.filename.startswith("leaderboard_") for att in message.attachments):
            existing_messages.append(message)

    deleted_count = 0
    seen_ids = set()
    for message in existing_messages:
        if message.id in seen_ids:
            continue
        seen_ids.add(message.id)
        try:
            await message.delete()
            deleted_count += 1
        except discord.HTTPException:
            pass

    prefix = f"{channel.id}:"
    for key in [k for k in list(lb_messages.keys()) if k.startswith(prefix)]:
        lb_messages.pop(key, None)

    for track in tracks:
        lb_messages.pop(normalize_track_key(track), None)

    save_lb_messages(lb_messages)

    posted_count = 0
    for track in tracks:
        card_file = await build_leaderboard_card(track, data)
        if card_file is None:
            continue
        msg = await channel.send(file=card_file)
        lb_messages[get_leaderboard_storage_key(channel.id, track)] = str(msg.id)
        posted_count += 1

    save_lb_messages(lb_messages)
    return deleted_count, posted_count

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BRAND SELECT → BIKE SELECT → MODAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class BrandSelect(ui.Select):
    def __init__(self, target_member: discord.Member | None = None):
        self.target_member = target_member
        options = []
        for brand in OEM_BIKES:
            n = len(OEM_BIKES[brand])
            options.append(discord.SelectOption(
                label=brand.upper(),
                value=brand,
                description=f"{n} model{'s' if n > 1 else ''}",
                emoji=BRAND_SELECT_EMOJI.get(brand, "🏍️"),
            ))
        options.append(discord.SelectOption(
            label="OTHER",
            value="Other / Custom Bike",
            description="Enter bike manually",
            emoji="🏍️",
        ))
        super().__init__(placeholder="SELECT BRAND", options=options)

    async def callback(self, interaction: discord.Interaction):
        brand = self.values[0]
        if brand == "Other / Custom Bike":
            await interaction.response.send_modal(HotlapModal(custom=True, target_member=self.target_member))
        else:
            view = BikeSelectView(brand, target_member=self.target_member)
            emoji = BRAND_SELECT_EMOJI.get(brand, "")
            await interaction.response.edit_message(
                content=f"{emoji}　**{brand.upper()}**　—　Select Model", view=view,
            )


class BrandSelectView(ui.View):
    def __init__(self, target_member: discord.Member | None = None):
        super().__init__(timeout=120)
        self.add_item(BrandSelect(target_member=target_member))


class BikeSelect(ui.Select):
    def __init__(self, brand: str, target_member: discord.Member | None = None):
        self.target_member = target_member
        bikes = OEM_BIKES.get(brand, [])
        options = [
            discord.SelectOption(
                label=display.upper(), value=value,
                description=get_class_tag(value),
            )
            for display, value in bikes
        ]
        super().__init__(placeholder=f"SELECT {brand.upper()} MODEL", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(
            HotlapModal(bike_override=self.values[0], target_member=self.target_member)
        )


class BikeSelectView(ui.View):
    def __init__(self, brand: str, target_member: discord.Member | None = None):
        super().__init__(timeout=120)
        self.add_item(BikeSelect(brand, target_member=target_member))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HOTLAP MODAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class HotlapModal(ui.Modal):
    def __init__(self, bike_override: str = None, custom: bool = False, target_member: discord.Member | None = None):
        super().__init__(title="SUBMIT HOTLAP")
        self.bike_override = bike_override
        self.custom = custom
        self.target_member = target_member

        self.track_input = ui.TextInput(
            label="TRACK",
            placeholder="e.g. Wolf Creek, Temecula Creek, Smeeze",
            required=True, max_length=100,
        )
        self.add_item(self.track_input)

        if custom:
            self.bike_input = ui.TextInput(
                label="BIKE",
                placeholder="e.g. Honda CR500, custom bike name",
                required=True, max_length=100,
            )
            self.add_item(self.bike_input)
        else:
            self.bike_input = None

        self.time_input = ui.TextInput(
            label="LAP TIME",
            placeholder="e.g. 1:56.41 or 56.789",
            required=True, max_length=20,
        )
        self.add_item(self.time_input)

        self.notes_input = ui.TextInput(
            label="NOTES (OPTIONAL)",
            placeholder="e.g. Clean run, new line through S3",
            required=False, max_length=200,
            style=discord.TextStyle.short,
        )
        self.add_item(self.notes_input)

    async def on_submit(self, interaction: discord.Interaction):
        rider = self.target_member or interaction.user
        track = self.track_input.value.strip().title()
        bike = self.bike_input.value.strip() if self.custom else self.bike_override
        time_str = self.time_input.value.strip()
        notes = self.notes_input.value.strip() if self.notes_input.value else None

        seconds = parse_time(time_str)
        if seconds < 0:
            await interaction.response.send_message(
                "Invalid time format — use `1:23.456` or `56.789`", ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        data = load_data()
        data["hotlaps"].append({
            "user_id": rider.id,
            "username": rider.display_name,
            "track": track,
            "bike": bike,
            "time_seconds": seconds,
            "time_display": format_time(seconds),
            "date": datetime.now().strftime("%m/%d/%Y"),
            "notes": notes,
        })
        save_data(data)

        # Send personal card — only visible to submitter
        card_file = await build_hotlap_card(interaction, track, bike, seconds, data, notes, rider=rider)
        await interaction.followup.send(
            content=f"✅ Added hotlap for **{rider.display_name}**",
            file=card_file,
            ephemeral=True,
        )

        # Post/update the public leaderboard card for this track
        await post_or_update_leaderboard(interaction.channel, track, data)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMMANDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@bot.tree.command(name="hotlap", description="Submit a hotlap time")
@app_commands.describe(member="Optional: choose a rider to add the hotlap for")
async def hotlap(interaction: discord.Interaction, member: discord.Member = None):
    target_member = member or interaction.user
    view = BrandSelectView(target_member=target_member)
    await interaction.response.send_message(
        f"🏍️ **Select a brand for {target_member.display_name}**", view=view, ephemeral=True,
    )


@bot.tree.command(name="leaderboard", description="View track leaderboard")
@app_commands.describe(track="Track name", bike_class="Filter by class")
@app_commands.choices(bike_class=[
    app_commands.Choice(name="85cc", value="85"),
    app_commands.Choice(name="125cc", value="125"),
    app_commands.Choice(name="250cc 2T", value="250 2T"),
    app_commands.Choice(name="250F 4T", value="250F"),
    app_commands.Choice(name="350cc", value="350"),
    app_commands.Choice(name="450cc", value="450"),
    app_commands.Choice(name="500cc", value="500"),
    app_commands.Choice(name="Electric", value="Varg"),
    app_commands.Choice(name="All Classes", value="all"),
])
async def leaderboard(
    interaction: discord.Interaction,
    track: str,
    bike_class: app_commands.Choice[str] = None,
):
    data = load_data()
    f = bike_class.value if bike_class else "all"

    times = [h for h in data["hotlaps"] if h["track"].lower() == track.lower()]

    if f != "all":
        if f == "250 2T":
            times = [h for h in times if "250" in h["bike"] and get_class_tag(h["bike"]) == "250CC"]
        elif f == "250F":
            times = [h for h in times if get_class_tag(h["bike"]) == "250F"]
        elif f == "Varg":
            times = [h for h in times if "varg" in h["bike"].lower()]
        else:
            times = [h for h in times if f in h["bike"]]

    if not times:
        await interaction.response.send_message(
            f"No laps recorded on **{track.title()}**", ephemeral=True,
        )
        return

    best = {}
    for h in times:
        uid = h["user_id"]
        if uid not in best or h["time_seconds"] < best[uid]["time_seconds"]:
            best[uid] = h

    ranked = sorted(best.values(), key=lambda x: x["time_seconds"])

    filter_labels = {
        "all": "", "85": "85CC", "125": "125CC", "250 2T": "250CC 2T",
        "250F": "250F", "350": "350CC", "450": "450CC", "500": "500CC", "Varg": "ELECTRIC",
    }
    cl = filter_labels.get(f, "")

    # ── Build leaderboard embed ──
    medal = {0: "🥇", 1: "🥈", 2: "🥉"}
    lines = []

    for i, entry in enumerate(ranked[:15]):
        bike_d = get_bike_display(entry["bike"])
        gap = ""
        if i > 0:
            diff = entry["time_seconds"] - ranked[0]["time_seconds"]
            gap = f"  `+{diff:.3f}s`"

        icon = medal.get(i, f"`{i+1}.`")
        lines.append(f"{icon} **{entry['username']}** — `{entry['time_display']}`{gap}")
        lines.append(f"⠀ ↳ {bike_d}")
        if i < len(ranked[:15]) - 1:
            lines.append("")

    title = f"🏁  {track.upper()}"
    if cl:
        title += f"  ›  {cl}"

    embed = discord.Embed(
        title=title,
        description="\n".join(lines),
        color=DARK_EMBED,
    )
    embed.set_footer(text=f"👤 {len(best)} riders  ·  🔁 {len(times)} total laps")
    embed.timestamp = datetime.now()

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="updateleaderboards", description="Refresh and clean all public leaderboard posts in this channel")
async def update_leaderboards(interaction: discord.Interaction):
    if not interaction.channel:
        await interaction.response.send_message("This command can only be used in a server channel.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    data = load_data()
    if not data["hotlaps"]:
        await interaction.followup.send("No hotlaps recorded yet — nothing to refresh.", ephemeral=True)
        return

    deleted_count, posted_count = await refresh_all_leaderboards(interaction.channel, data)
    await interaction.followup.send(
        f"✅ Refreshed **{posted_count}** leaderboard{'s' if posted_count != 1 else ''} and removed **{deleted_count}** old bot message{'s' if deleted_count != 1 else ''}.",
        ephemeral=True,
    )


@bot.tree.command(name="pb", description="View personal bests")
@app_commands.describe(member="View another rider's PBs")
async def personal_bests(
    interaction: discord.Interaction, member: discord.Member = None,
):
    target = member or interaction.user
    data = load_data()

    user_times = [h for h in data["hotlaps"] if h["user_id"] == target.id]

    if not user_times:
        msg = (
            "No hotlaps yet — use `/hotlap` to submit your first."
            if target == interaction.user
            else f"{target.display_name} hasn't submitted any hotlaps."
        )
        await interaction.response.send_message(msg, ephemeral=True)
        return

    best_per_track = {}
    for h in user_times:
        t = h["track"]
        if t not in best_per_track or h["time_seconds"] < best_per_track[t]["time_seconds"]:
            best_per_track[t] = h

    brand_counts = {}
    for h in user_times:
        b = get_bike_brand(h["bike"])
        brand_counts[b] = brand_counts.get(b, 0) + 1
    top_brand = max(brand_counts, key=brand_counts.get)

    d = []
    for track, entry in sorted(best_per_track.items()):
        all_track = [h for h in data["hotlaps"] if h["track"].lower() == track.lower()]
        best_all = {}
        for h in all_track:
            uid = h["user_id"]
            if uid not in best_all or h["time_seconds"] < best_all[uid]:
                best_all[uid] = h["time_seconds"]
        s = sorted(best_all.values())
        try:
            rank = s.index(entry["time_seconds"]) + 1
        except ValueError:
            rank = len(s)

        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"**P{rank}**"
        bike_d = get_bike_display(entry["bike"])

        d.append(f"**{track}**")
        d.append(f"⠀ `{entry['time_display']}` — {medal} of {len(best_all)}  ·  {bike_d}")
        d.append("")

    embed = discord.Embed(
        title=f"📊  {target.display_name}'s Personal Bests",
        description="\n".join(d),
        color=BRAND_COLORS.get(top_brand, DARK_EMBED),
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.set_footer(text=f"🔁 {len(user_times)} laps  ·  🗺️ {len(best_per_track)} tracks  ·  {top_brand}")
    embed.timestamp = datetime.now()

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="tracks", description="List all tracks")
async def tracks(interaction: discord.Interaction):
    data = load_data()

    if not data["hotlaps"]:
        await interaction.response.send_message(
            "No hotlaps recorded yet — use `/hotlap`", ephemeral=True,
        )
        return

    info = {}
    for h in data["hotlaps"]:
        t = h["track"]
        if t not in info:
            info[t] = {
                "count": 0, "best": h["time_seconds"],
                "best_display": h["time_display"],
                "best_rider": h["username"], "best_bike": h["bike"],
                "riders": set(),
            }
        info[t]["count"] += 1
        info[t]["riders"].add(h["user_id"])
        if h["time_seconds"] < info[t]["best"]:
            info[t]["best"] = h["time_seconds"]
            info[t]["best_display"] = h["time_display"]
            info[t]["best_rider"] = h["username"]
            info[t]["best_bike"] = h["bike"]

    d = []
    for track, i in sorted(info.items()):
        bike_d = get_bike_display(i["best_bike"])
        d.append(f"**{track}**")
        d.append(f"⠀ 🥇 `{i['best_display']}` by **{i['best_rider']}**  ·  {bike_d}")
        d.append(f"⠀ 👤 {len(i['riders'])} riders  ·  🔁 {i['count']} laps")
        d.append("")

    embed = discord.Embed(
        title=f"🗺️  All Tracks  ({len(info)})",
        description="\n".join(d),
        color=DARK_EMBED,
    )
    embed.timestamp = datetime.now()

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="delete", description="Delete your most recent hotlap")
async def delete_last(interaction: discord.Interaction):
    data = load_data()

    user_laps = [
        (i, h) for i, h in enumerate(data["hotlaps"])
        if h["user_id"] == interaction.user.id
    ]

    if not user_laps:
        await interaction.response.send_message(
            "Nothing to delete.", ephemeral=True,
        )
        return

    idx, lap = user_laps[-1]
    data["hotlaps"].pop(idx)
    save_data(data)

    bike_d = get_bike_display(lap["bike"])
    embed = discord.Embed(
        title="🗑️  Lap Deleted",
        description=f"**{lap['track']}** — `{lap['time_display']}`\n{bike_d}",
        color=0x636366,
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

    if interaction.channel:
        await post_or_update_leaderboard(interaction.channel, lap["track"], data)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EVENTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_COMMANDS_SYNCED = False

@bot.event
async def on_ready():
    global _COMMANDS_SYNCED
    print(f"✅ {bot.user} is online!")

    if _COMMANDS_SYNCED:
        return

    try:
        global_synced = await bot.tree.sync()
        print(f"✅ Synced {len(global_synced)} global slash commands")
    except Exception as e:
        print(f"❌ Failed to sync global commands: {e}")

    for guild in bot.guilds:
        try:
            bot.tree.clear_commands(guild=guild)
            bot.tree.copy_global_to(guild=guild)
            guild_synced = await bot.tree.sync(guild=guild)
            print(f"✅ Synced {len(guild_synced)} guild slash commands to {guild.name} ({guild.id})")
        except Exception as e:
            print(f"❌ Failed to sync guild commands to {guild.name} ({guild.id}): {e}")

    _COMMANDS_SYNCED = True


if __name__ == "__main__":
    bot.run(BOT_TOKEN)
