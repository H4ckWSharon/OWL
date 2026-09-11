"""
╔═══════════════════════════════════════════════════════════╗
║         OWL — Offensive WiFi Launcher                     ║
║         Banner & ASCII Art  — Steampunk Edition           ║
║         Created by Sharon Anil                            ║
╚═══════════════════════════════════════════════════════════╝
"""

# ── Steampunk Owl — full boot / terminal banner ───────────────────────────────
# All inline color segments use [/] (Rich universal close) so each line
# written individually to RichLog never has an unmatched closing tag.
STARTUP_ASCII = (
    "[bold yellow]         ⚙   ⚙   ⚙               ⚙   ⚙   ⚙[/]\n"
    "[bold yellow]       ⚙    [/][#6B2D8B]▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓[/][bold yellow]    ⚙[/]\n"
    "[bold yellow]      ⚙   [/][#6B2D8B]▓▓[/][bold yellow]╔═══════════════════╗[/][#6B2D8B]▓▓[/][bold yellow]   ⚙[/]\n"
    "[bold yellow]     ⚙    [/][#6B2D8B]▓[/][bold yellow]║[/][#8B4513] ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ [/][bold yellow]║[/][#6B2D8B]▓[/][bold yellow]    ⚙[/]\n"
    "[bold yellow]  ⚙─┬─╔╗  [/][#6B2D8B]▓[/][bold yellow]║[/][#8B4513] █  [/][bold red]◈◈◈[/] [#DAA520]▄▄▄[/] [bold red]◈◈◈[/][#8B4513]  █ [/][bold yellow]║[/][#6B2D8B]▓[/][bold yellow]  ╔╗─┬─⚙[/]\n"
    "[bold yellow]  ⚙  │ ║  [/][#6B2D8B]▓[/][bold yellow]║[/][#8B4513] █  [/][bold red]◈◈◈[/] [#DAA520]║⊙║[/] [bold red]◈◈◈[/][#8B4513]  █ [/][bold yellow]║[/][#6B2D8B]▓[/][bold yellow]  ║ │  ⚙[/]\n"
    "[bold yellow]  ⚙  │ ╚╗ [/][#6B2D8B]▓[/][bold yellow]║[/][#8B4513] ████[/] [#DAA520]▀▄▀▄▀[/] [#8B4513]████ [/][bold yellow]║[/][#6B2D8B]▓[/][bold yellow] ╔╝ │  ⚙[/]\n"
    "[bold yellow]  ⚙─┴──╚══[/][#6B2D8B]▓[/][bold yellow]║[/][#8B4513] █████[/] [#DAA520]───[/] [#8B4513]█████ [/][bold yellow]║[/][#6B2D8B]▓[/][bold yellow]══╝──┴─⚙[/]\n"
    "[bold yellow]  ───────╔╝[/][#6B2D8B]▓[/][bold yellow]╠[/][#8B4513]███████[/][bold yellow]⚙─⚙─⚙[/][#8B4513]███████[/][bold yellow]╣[/][#6B2D8B]▓[/][bold yellow]╚╗───────[/]\n"
    "[bold yellow]         ╔╝[/][#6B2D8B]▓[/][bold yellow]║[/][#8B4513] ██[/][bold yellow]╔══════════════════╗[/][#8B4513]██ [/][bold yellow]║[/][#6B2D8B]▓[/][bold yellow]╚╗[/]\n"
    "[bold yellow]        ╔╝ [/][#6B2D8B]▓[/][bold yellow]║[/][#8B4513] ██[/][bold yellow]║[/][white]    XII       I   [/][bold yellow]║[/][#8B4513]██ [/][bold yellow]║[/][#6B2D8B]▓[/][bold yellow] ╚╗[/]\n"
    "[bold yellow]       ╔╝  [/][#6B2D8B]▓[/][bold yellow]║[/][#8B4513] ██[/][bold yellow]║[/][white]  XI [/][#DAA520]⚙[/][yellow]─◉─[/][#DAA520]⚙[/][white] II  [/][bold yellow]║[/][#8B4513]██ [/][bold yellow]║[/][#6B2D8B]▓[/][bold yellow]  ╚╗[/]\n"
    "[bold yellow]      ╔╝   [/][#6B2D8B]▓[/][bold yellow]║[/][#8B4513] ██[/][bold yellow]║[/][white]   X          III  [/][bold yellow]║[/][#8B4513]██ [/][bold yellow]║[/][#6B2D8B]▓[/][bold yellow]   ╚╗[/]\n"
    "[bold yellow]     ╔╝    [/][#6B2D8B]▓[/][bold yellow]╚═[/][#8B4513]██[/][bold yellow]║[/][white]    IX      IV    [/][bold yellow]║[/][#8B4513]██[/][bold yellow]═╝[/][#6B2D8B]▓[/][bold yellow]    ╚╗[/]\n"
    "[bold yellow]    ╔╝ [/][#8B4513]████[/][bold yellow]═══[/][#8B4513]██[/][bold yellow]╚══════════════════╝[/][#8B4513]██[/][bold yellow]═══[/][#8B4513]████[/][bold yellow] ╚╗[/]\n"
    "[bold yellow]   ╔╝  [/][#DAA520]▌▌▌[/][#8B4513]█████████████████████████████[/][#DAA520]▐▐▐[/][bold yellow]  ╚╗[/]\n"
    "[bold yellow]  ╔╝   [/][#DAA520]▌▌▌[/][#8B4513]██[/][#DAA520]▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌[/][#8B4513]██[/][#DAA520]▐▐▐[/][bold yellow]   ╚╗[/]\n"
    "[bold yellow]  ╚══════════════╧════════════════╧══════════════╝[/]\n"
    "[#8B4513]              ║║║  ║║║  ║║║  ║║║  ║║║[/]\n"
    "[#DAA520]              ╚╝╚  ╚╝╚  ╚╝╚  ╚╝╚  ╚╝╚[/]\n"
    "\n"
    "[dim]          Offensive WiFi Launcher v1.0  ·  Created by Sharon Anil[/]\n"
    '[dim yellow]        "See in the dark.  Strike without a trace."[/]\n'
)

# ── Compact sidebar / small area banner ──────────────────────────────────────
OWL_ASCII = (
    "[bold yellow]     ⚙  [/][#6B2D8B]▓▓▓▓▓▓▓▓▓▓▓[/][bold yellow]  ⚙[/]\n"
    "[#6B2D8B]      ▓[/][bold yellow]╔═══════════╗[/][#6B2D8B]▓[/]\n"
    "[bold yellow]  ⚙──┤[/][#6B2D8B]▓[/][bold yellow]║[/][#8B4513]█[/][bold red]◈[/][#DAA520]▄▄▄[/][bold red]◈[/][#8B4513]█[/][bold yellow]║[/][#6B2D8B]▓[/][bold yellow]├──⚙[/]\n"
    "[#6B2D8B]     ▓[/][bold yellow]║[/][#8B4513]█[/][bold red]◈[/][#DAA520]║⊙║[/][bold red]◈[/][#8B4513]█[/][bold yellow]║[/][#6B2D8B]▓[/]\n"
    "[bold yellow]  ⚙──┤[/][#6B2D8B]▓[/][bold yellow]╠[/][#8B4513]███[/][bold yellow]⚙─⚙[/][#8B4513]███[/][bold yellow]╣[/][#6B2D8B]▓[/][bold yellow]├──⚙[/]\n"
    "[#6B2D8B]      ▓[/][bold yellow]║[/][#8B4513]██[/][bold yellow]╔═══════╗[/][#8B4513]██[/][bold yellow]║[/][#6B2D8B]▓[/]\n"
    "[#6B2D8B]      ▓[/][bold yellow]║[/][#8B4513]██[/][bold yellow]║[/][white]X [/][yellow]◉[/][white] III[/][bold yellow]║[/][#8B4513]██[/][bold yellow]║[/][#6B2D8B]▓[/]\n"
    "[#6B2D8B]      ▓[/][bold yellow]╚[/][#8B4513]██[/][bold yellow]╚═══════╝[/][#8B4513]██[/][bold yellow]╝[/][#6B2D8B]▓[/]\n"
    "[#DAA520]       ▌[/][#8B4513]███████████[/][#DAA520]▐[/]\n"
    "[#8B4513]       ║╝ ║╝ ║╝ ║╝ ║╝[/]\n"
)

OWL_BANNER_FULL = (
    "[bold yellow]╔═══════════════════════════════════════════════════════════════════╗[/]\n"
    "[bold yellow]║  ⚙  ⚙   ◉  OWL — OFFENSIVE WiFi LAUNCHER v1.0  ◉   ⚙  ⚙  ║[/]\n"
    "[bold yellow]║[/]\n"
    "[bold yellow]║     [/][bold red]◈◈[/][#8B4513]▄[/][#DAA520]▄▄▄[/][bold red]◈◈[/][bold yellow]     See in the dark.                          ║[/]\n"
    "[bold yellow]║     [/][bold red]◈◈[/][#DAA520]║⊙║[/][bold red]◈◈[/][bold yellow]     Strike without a trace.                   ║[/]\n"
    "[bold yellow]║     [/][#8B4513]███[/][#DAA520]⚙─⚙[/][#8B4513]███[/][bold yellow]   ─────────────────────────── ║[/]\n"
    "[bold yellow]║     [/][#8B4513]██[/][bold yellow]╔[/][white]X ◉ III[/][bold yellow]╗[/][#8B4513]██[/][bold yellow]   RECON · DEAUTH · FLOOD    ║[/]\n"
    "[bold yellow]║     [/][#DAA520]▌▌[/][#8B4513]███████████[/][#DAA520]▐▐[/][bold yellow]   HARVEST · PORTAL          ║[/]\n"
    "[bold yellow]║     [/][#8B4513]║║ ║║ ║║ ║║[/][bold yellow]        Created by Sharon Anil   ║[/]\n"
    "[bold yellow]╚═══════════════════════════════════════════════════════════════════╝[/]\n"
)

OWL_BANNER_COMPACT = (
    "[bold yellow]⚙ [/][bold red]◈[/][bold yellow] OWL ─── [/][#DAA520]OFFENSIVE WiFi LAUNCHER[/][bold yellow] ─── [/][bold red]◈[/][bold yellow] ⚙[/]\n"
    '[dim]  RECON · DEAUTH · FLOOD · HARVEST · PORTAL · v1.0[/]\n'
    '[dim]  "See in the dark. Strike without a trace."[/]\n'
)

OWL_MINI = "[bold yellow]⚙ OWL[/][dim yellow] v1.0[/]"

TERMINAL_BOOT_LINES = [
    ("cyan",   "[*] OWL v1.0 Steampunk Edition — initializing..."),
    ("cyan",   "[*] Loading modules: RECON, DEAUTH, FLOOD, HARVEST, PORTAL"),
    ("green",  "[+] Core engine loaded — all gears turning"),
    ("cyan",   "[*] Checking Python environment..."),
    ("green",  "[+] Python 3.x detected"),
    ("yellow", "[!] Real hardware ops require Linux + monitor-mode NIC"),
    ("cyan",   "[*] Auth gate loaded — checking consent..."),
    ("green",  "[+] Ready. Welcome, operator. OWL is watching."),
]

MODULE_BANNERS = {
    "recon":     "[bold cyan]⚙─ OWL-RECON ─── Reconnaissance & Discovery ────────────────⚙[/]",
    "deauth":    "[bold yellow]⚙─ OWL-DEAUTH ── Deauthentication Attack Engine ─────────────⚙[/]",
    "flood":     "[bold red]⚙─ OWL-FLOOD ─── Broadcast Kill / Packet Flood ──────────────⚙[/]",
    "harvest":   "[bold magenta]⚙─ OWL-HARVEST ─ Handshake Capture Pipeline ─────────────────⚙[/]",
    "portal":    "[bold green]⚙─ OWL-PORTAL ── Evil Twin & Captive Portal ─────────────────⚙[/]",
    "settings":  "[bold white]⚙─ OWL-CONFIG ── Settings & Health Checks ───────────────────⚙[/]",
    "dashboard": "[bold yellow]⚙─ OWL-DASH ──── Command Center ─────────────────────────────⚙[/]",
}
