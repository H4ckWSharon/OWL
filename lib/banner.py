"""
╔═══════════════════════════════════════════════════════════╗
║         OWL — Offensive WiFi Launcher                     ║
║         Banner & ASCII Art  — Steampunk Edition           ║
║         Created by Sharon Anil                            ║
╚═══════════════════════════════════════════════════════════╝
"""

# ── Steampunk Owl — full boot / terminal banner ───────────────────────────────
STARTUP_ASCII = r"""
[bold yellow]         ⚙   ⚙   ⚙               ⚙   ⚙   ⚙[/bold yellow]
[bold yellow]       ⚙    [/bold yellow][#6B2D8B]▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓[/bold yellow][bold yellow]    ⚙[/bold yellow]
[bold yellow]      ⚙   [/bold yellow][#6B2D8B]▓▓[/bold yellow][bold yellow]╔═══════════════════╗[/bold yellow][#6B2D8B]▓▓[/bold yellow][bold yellow]   ⚙[/bold yellow]
[bold yellow]     ⚙    [/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]║[/bold yellow][#8B4513] ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ [/bold yellow][bold yellow]║[/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]    ⚙[/bold yellow]
[bold yellow]  ⚙─┬─╔╗  [/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]║[/bold yellow][#8B4513] █  [/bold yellow][bold red]◈◈◈[/bold red][#DAA520] ▄▄▄ [/bold yellow][bold red]◈◈◈[/bold red][#8B4513]  █ [/bold yellow][bold yellow]║[/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]  ╔╗─┬─⚙[/bold yellow]
[bold yellow]  ⚙  │ ║  [/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]║[/bold yellow][#8B4513] █  [/bold yellow][bold red]◈◈◈[/bold red][#DAA520] ║⊙║ [/bold yellow][bold red]◈◈◈[/bold red][#8B4513]  █ [/bold yellow][bold yellow]║[/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]  ║ │  ⚙[/bold yellow]
[bold yellow]  ⚙  │ ╚╗ [/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]║[/bold yellow][#8B4513] ████[/bold yellow][#DAA520] ▀▄▀▄▀ [/bold yellow][#8B4513]████ [/bold yellow][bold yellow]║[/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow] ╔╝ │  ⚙[/bold yellow]
[bold yellow]  ⚙─┴──╚══[/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]║[/bold yellow][#8B4513] █████[/bold yellow][#DAA520] ─── [/bold yellow][#8B4513]█████ [/bold yellow][bold yellow]║[/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]══╝──┴─⚙[/bold yellow]
[bold yellow]  ───────╔╝[/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]╠[/bold yellow][#8B4513]███████[/bold yellow][bold yellow]⚙─⚙─⚙[/bold yellow][#8B4513]███████[/bold yellow][bold yellow]╣[/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]╚╗───────[/bold yellow]
[bold yellow]         ╔╝[/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]║[/bold yellow][#8B4513] ██[/bold yellow][bold yellow]╔══════════════════╗[/bold yellow][#8B4513]██ [/bold yellow][bold yellow]║[/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]╚╗[/bold yellow]
[bold yellow]        ╔╝ [/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]║[/bold yellow][#8B4513] ██[/bold yellow][bold yellow]║[/bold yellow][white]    XII       I   [/white][bold yellow]║[/bold yellow][#8B4513]██ [/bold yellow][bold yellow]║[/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow] ╚╗[/bold yellow]
[bold yellow]       ╔╝  [/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]║[/bold yellow][#8B4513] ██[/bold yellow][bold yellow]║[/bold yellow][white]  XI [/white][#DAA520]⚙[/bold yellow][yellow]─◉─[/yellow][#DAA520]⚙[/bold yellow][white] II  [/white][bold yellow]║[/bold yellow][#8B4513]██ [/bold yellow][bold yellow]║[/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]  ╚╗[/bold yellow]
[bold yellow]      ╔╝   [/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]║[/bold yellow][#8B4513] ██[/bold yellow][bold yellow]║[/bold yellow][white]   X          III  [/white][bold yellow]║[/bold yellow][#8B4513]██ [/bold yellow][bold yellow]║[/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]   ╚╗[/bold yellow]
[bold yellow]     ╔╝    [/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]╚═[/bold yellow][#8B4513]██[/bold yellow][bold yellow]║[/bold yellow][white]    IX      IV    [/white][bold yellow]║[/bold yellow][#8B4513]██[/bold yellow][bold yellow]═╝[/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]    ╚╗[/bold yellow]
[bold yellow]    ╔╝ [/bold yellow][#8B4513]████[/bold yellow][bold yellow]═══[/bold yellow][#8B4513]██[/bold yellow][bold yellow]╚══════════════════╝[/bold yellow][#8B4513]██[/bold yellow][bold yellow]═══[/bold yellow][#8B4513]████[/bold yellow][bold yellow] ╚╗[/bold yellow]
[bold yellow]   ╔╝  [/bold yellow][#DAA520]▌▌▌[/bold yellow][#8B4513]█████████████████████████████[/bold yellow][#DAA520]▐▐▐[/bold yellow][bold yellow]  ╚╗[/bold yellow]
[bold yellow]  ╔╝   [/bold yellow][#DAA520]▌▌▌[/bold yellow][#8B4513]██[/bold yellow][#DAA520]▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌[/bold yellow][#8B4513]██[/bold yellow][#DAA520]▐▐▐[/bold yellow][bold yellow]   ╚╗[/bold yellow]
[bold yellow]  ╚══════════════╧════════════════╧══════════════╝[/bold yellow]
[bold yellow]              [/bold yellow][#8B4513]║║║[/bold yellow][bold yellow]  [/bold yellow][#8B4513]║║║[/bold yellow][bold yellow]  [/bold yellow][#8B4513]║║║[/bold yellow][bold yellow]  [/bold yellow][#8B4513]║║║[/bold yellow][bold yellow]  [/bold yellow][#8B4513]║║║[/bold yellow]
[bold yellow]              [/bold yellow][#DAA520]╚╝╚[/bold yellow][bold yellow]  [/bold yellow][#DAA520]╚╝╚[/bold yellow][bold yellow]  [/bold yellow][#DAA520]╚╝╚[/bold yellow][bold yellow]  [/bold yellow][#DAA520]╚╝╚[/bold yellow][bold yellow]  [/bold yellow][#DAA520]╚╝╚[/bold yellow]
[bold yellow]
          [dim]Offensive WiFi Launcher v1.0  ·  Created by Sharon Anil[/dim]
        [dim yellow]"See in the dark.  Strike without a trace."[/dim yellow][/bold yellow]
"""

# ── Compact sidebar / small area banner ──────────────────────────────────────
OWL_ASCII = r"""
[bold yellow]     ⚙  [/bold yellow][#6B2D8B]▓▓▓▓▓▓▓▓▓▓▓[/bold yellow][bold yellow]  ⚙[/bold yellow]
[bold yellow]      [/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]╔═══════════╗[/bold yellow][#6B2D8B]▓[/bold yellow]
[bold yellow]  ⚙──┤[/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]║[/bold yellow][#8B4513]█[/bold yellow][bold red]◈[/bold red][#DAA520]▄▄▄[/bold yellow][bold red]◈[/bold red][#8B4513]█[/bold yellow][bold yellow]║[/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]├──⚙[/bold yellow]
[bold yellow]     [/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]║[/bold yellow][#8B4513]█[/bold yellow][bold red]◈[/bold red][#DAA520]║⊙║[/bold yellow][bold red]◈[/bold red][#8B4513]█[/bold yellow][bold yellow]║[/bold yellow][#6B2D8B]▓[/bold yellow]
[bold yellow]  ⚙──┤[/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]╠[/bold yellow][#8B4513]███[/bold yellow][bold yellow]⚙─⚙[/bold yellow][#8B4513]███[/bold yellow][bold yellow]╣[/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]├──⚙[/bold yellow]
[bold yellow]      [/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]║[/bold yellow][#8B4513]██[/bold yellow][bold yellow]╔═══════╗[/bold yellow][#8B4513]██[/bold yellow][bold yellow]║[/bold yellow][#6B2D8B]▓[/bold yellow]
[bold yellow]      [/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]║[/bold yellow][#8B4513]██[/bold yellow][bold yellow]║[/bold yellow][white]X [/white][yellow]◉[/yellow][white] III[/white][bold yellow]║[/bold yellow][#8B4513]██[/bold yellow][bold yellow]║[/bold yellow][#6B2D8B]▓[/bold yellow]
[bold yellow]      [/bold yellow][#6B2D8B]▓[/bold yellow][bold yellow]╚[/bold yellow][#8B4513]██[/bold yellow][bold yellow]╚═══════╝[/bold yellow][#8B4513]██[/bold yellow][bold yellow]╝[/bold yellow][#6B2D8B]▓[/bold yellow]
[bold yellow]       [/bold yellow][#DAA520]▌[/bold yellow][#8B4513]███████████[/bold yellow][#DAA520]▐[/bold yellow]
[bold yellow]       [/bold yellow][#8B4513]║╝ ║╝ ║╝ ║╝ ║╝[/bold yellow]
"""

OWL_BANNER_FULL = r"""
[bold yellow]╔═══════════════════════════════════════════════════════════════════╗
║  ⚙  ⚙   ◉  OWL — OFFENSIVE WiFi LAUNCHER v1.0  ◉   ⚙  ⚙  ║
║                                                                 ║
║     [/bold yellow][bold red]◈◈[/bold red][#8B4513]▄[/bold yellow][#DAA520]▄▄▄[/bold yellow][bold red]◈◈[/bold red][bold yellow]     See in the dark.                          ║
║     [/bold yellow][bold red]◈◈[/bold red][#DAA520]║⊙║[/bold yellow][bold red]◈◈[/bold red][bold yellow]     Strike without a trace.                   ║
║     [/bold yellow][#8B4513]███[/bold yellow][#DAA520]⚙─⚙[/bold yellow][#8B4513]███[/bold yellow][bold yellow]   ───────────────────────────── ║
║     [/bold yellow][#8B4513]██[/bold yellow][bold yellow]╔[/bold yellow][white]X ◉ III[/white][bold yellow]╗[/bold yellow][#8B4513]██[/bold yellow][bold yellow]   RECON · DEAUTH · FLOOD         ║
║     [/bold yellow][#DAA520]▌▌[/bold yellow][#8B4513]███████████[/bold yellow][#DAA520]▐▐[/bold yellow][bold yellow]   HARVEST · PORTAL · SETTINGS    ║
║     [/bold yellow][#8B4513]║║ ║║ ║║ ║║[/bold yellow][bold yellow]        Created by Sharon Anil           ║
╚═══════════════════════════════════════════════════════════════════╝[/bold yellow]
"""

OWL_BANNER_COMPACT = r"""
[bold yellow]⚙ [/bold yellow][bold red]◈[/bold red][bold yellow] OWL ─── [/bold yellow][#DAA520]OFFENSIVE WiFi LAUNCHER[/bold yellow][bold yellow] ─── [/bold yellow][bold red]◈[/bold red][bold yellow] ⚙
  [dim]RECON · DEAUTH · FLOOD · HARVEST · PORTAL · v1.0[/dim]
  [dim]"See in the dark. Strike without a trace."[/dim][/bold yellow]
"""

OWL_MINI = "[bold yellow]⚙ OWL[/bold yellow][dim yellow] v1.0[/dim yellow]"

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
    "recon":     "[bold cyan]⚙─ OWL-RECON ─── Reconnaissance & Discovery ────────────────⚙[/bold cyan]",
    "deauth":    "[bold yellow]⚙─ OWL-DEAUTH ── Deauthentication Attack Engine ─────────────⚙[/bold yellow]",
    "flood":     "[bold red]⚙─ OWL-FLOOD ─── Broadcast Kill / Packet Flood ──────────────⚙[/bold red]",
    "harvest":   "[bold magenta]⚙─ OWL-HARVEST ─ Handshake Capture Pipeline ─────────────────⚙[/bold magenta]",
    "portal":    "[bold green]⚙─ OWL-PORTAL ── Evil Twin & Captive Portal ─────────────────⚙[/bold green]",
    "settings":  "[bold white]⚙─ OWL-CONFIG ── Settings & Health Checks ───────────────────⚙[/bold white]",
    "dashboard": "[bold yellow]⚙─ OWL-DASH ──── Command Center ─────────────────────────────⚙[/bold yellow]",
}

