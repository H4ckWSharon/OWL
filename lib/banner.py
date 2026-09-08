"""
╔═══════════════════════════════════════════════════════════╗
║         OWL — Offensive WiFi Launcher                     ║
║         Banner & ASCII Art                                ║
║         Created by Sharon Anil                            ║
╚═══════════════════════════════════════════════════════════╝
"""

OWL_ASCII = r"""
[bold yellow]
    ██████╗ ██╗    ██╗██╗
   ██╔═══██╗██║    ██║██║
   ██║   ██║██║ █╗ ██║██║
   ██║   ██║██║███╗██║██║
   ╚██████╔╝╚███╔███╔╝███████╗
    ╚═════╝  ╚══╝╚══╝ ╚══════╝
[/bold yellow]
[dim cyan]
         (  ,  )
          )/ \(
         (/ @ \)      [/dim cyan][bold amber]See in the dark.[/bold amber][dim cyan]
          )   (       [/dim cyan][dim]Strike without a trace.[/dim][dim cyan]
         (_\_/_)
          ( Y )
          /|=|\
         (_/ \_)
[/dim cyan]"""

OWL_BANNER_FULL = r"""
[bold yellow]
  ╔══════════════════════════════════════════════════════════════════════════╗
  ║                                                                          ║
  ║   ▄██████▄   ▄█     █▄   ▄█                                             ║
  ║  ███    ███ ███     ███ ███                                              ║
  ║  ███    ███ ███     ███ ███         Offensive WiFi Launcher              ║
  ║  ███    ███ ███     ███ ███                                              ║
  ║  ███    ███ ███     ███ ███         "See in the dark.                    ║
  ║  ███    ███ ███     ███ ███          Strike without a trace."            ║
  ║  ███    ███ ███     ███ ███                                              ║
  ║   ▀██████▀   ▀███████▀  █▀                                              ║
  ║                                                                          ║
  ╚══════════════════════════════════════════════════════════════════════════╝
[/bold yellow]"""

OWL_BANNER_COMPACT = r"""
[bold yellow]  ██████╗ ██╗    ██╗██╗     [dim]|[/dim]  [cyan]Offensive WiFi Launcher v1.0[/cyan]
  ██╔══██╗██║    ██║██║     [dim]|[/dim]  [dim]"See in the dark. Strike without a trace."[/dim]
  ██║  ██║██║ █╗ ██║██║     [dim]|[/dim]
  ██████╔╝╚███╔███╔╝███████╗[dim]|[/dim]  [dim yellow]RECON · DEAUTH · FLOOD · HARVEST · PORTAL[/dim yellow]
  ╚═════╝  ╚══╝╚══╝ ╚══════╝[dim]|[/dim]  [dim]Created by Sharon Anil[/dim][/bold yellow]"""

OWL_MINI = "[bold yellow]◉ OWL[/bold yellow][dim yellow] v1.0[/dim yellow]"

STARTUP_ASCII = r"""
[bold yellow]
     .    .    .
   ,'_`--'_`--'_`.
  :  `  `  `  `  :     ██████╗ ██╗    ██╗██╗
  :  .  .  .  .  :    ██╔═══██╗██║    ██║██║
   \  `--`--`--' /     ██║   ██║██║ █╗ ██║██║
    `.__________.'     ██║   ██║██║███╗██║██║
      |  |  |  |       ╚██████╔╝╚███╔███╔╝███████╗
     (◉)      (◉)       ╚═════╝  ╚══╝╚══╝ ╚══════╝
      `--....--'
        |    |         [dim cyan]Offensive WiFi Launcher[/dim cyan]
       /|    |\        [dim]"See in the dark. Strike without a trace."[/dim]
      / |    | \
     '  '----'  '      [dim yellow]For authorized penetration testing only.[/dim yellow]
[/bold yellow]"""

TERMINAL_BOOT_LINES = [
    ("[cyan]", "[*] OWL v1.0 initializing..."),
    ("[cyan]", "[*] Loading modules: RECON, DEAUTH, FLOOD, HARVEST, PORTAL"),
    ("[green]", "[+] SIM engine loaded — demo mode active"),
    ("[cyan]", "[*] Checking Python environment..."),
    ("[green]", "[+] Python 3.x detected"),
    ("[yellow]", "[!] Real hardware ops require Linux + monitor-mode NIC"),
    ("[cyan]", "[*] Auth gate loaded — checking consent..."),
    ("[green]", "[+] Ready. Welcome to OWL."),
]

MODULE_BANNERS = {
    "recon": "[bold cyan]┌─ OWL-RECON ─── Reconnaissance & Discovery ──────────────────┐[/bold cyan]",
    "deauth": "[bold yellow]┌─ OWL-DEAUTH ── Deauthentication Attack Engine ──────────────┐[/bold yellow]",
    "flood": "[bold red]┌─ OWL-FLOOD ─── Broadcast Kill / Packet Flood ───────────────┐[/bold red]",
    "harvest": "[bold magenta]┌─ OWL-HARVEST ─ Handshake Capture Pipeline ──────────────────┐[/bold magenta]",
    "portal": "[bold green]┌─ OWL-PORTAL ── Evil Twin & Captive Portal ──────────────────┐[/bold green]",
    "settings": "[bold white]┌─ OWL-CONFIG ── Settings & Health Checks ────────────────────┐[/bold white]",
    "dashboard": "[bold yellow]┌─ OWL-DASH ──── Command Center ──────────────────────────────┐[/bold yellow]",
}
