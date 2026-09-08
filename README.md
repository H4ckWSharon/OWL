<div align="center">

<!-- Animated typing banner -->
<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=18&duration=3000&pause=1000&color=F5A623&center=true&vCenter=true&width=500&lines=See+in+the+dark.;Strike+without+a+trace.;Offensive+WiFi+Launcher+v1.0;For+authorized+testing+ONLY." alt="OWL tagline" />

```
    ██████╗ ██╗    ██╗██╗
   ██╔═══██╗██║    ██║██║
   ██║   ██║██║ █╗ ██║██║       Offensive WiFi Launcher v1.0
   ██║   ██║██║███╗██║██║       "See in the dark. Strike without a trace."
   ╚██████╔╝╚███╔███╔╝███████╗
    ╚═════╝  ╚══╝╚══╝ ╚══════╝   Created by Sharon Anil
```

![Python](https://img.shields.io/badge/Python-3.10%2B-yellow?style=for-the-badge&logo=python&logoColor=white&labelColor=1a1a2e)
![Platform](https://img.shields.io/badge/Platform-Kali%20%7C%20Parrot%20%7C%20Debian-orange?style=for-the-badge&logo=linux&logoColor=white&labelColor=1a1a2e)
![License](https://img.shields.io/badge/License-Auth%20Testing%20Only-red?style=for-the-badge&labelColor=1a1a2e)
![Version](https://img.shields.io/badge/Version-1.0-f5a623?style=for-the-badge&labelColor=1a1a2e)
![Stars](https://img.shields.io/github/stars/H4ckWSharon/OWL?style=for-the-badge&labelColor=1a1a2e&color=f5a623)

</div>

---

<div align="center">

> ⚠️ **For authorized penetration testing and security research ONLY.**
> Unauthorized network access is illegal. The creator bears no liability for misuse.

</div>

---

## 🦉 What is OWL?

**OWL** is a **terminal-based** offensive WiFi toolkit built with Python + [Textual](https://github.com/Textualize/textual). It provides a rich, keyboard-driven TUI (Terminal User Interface) for WiFi reconnaissance, deauthentication, packet flooding, handshake capture, and evil-twin attacks — all from a single, powerful CLI interface.

```
 ┌──────────────────────────────────────────────────────────────┐
 │  OWL — Command Center                                        │
 │                                                              │
 │  [1] OWL-RECON    [2] OWL-DEAUTH   [3] OWL-FLOOD            │
 │  [4] OWL-HARVEST  [5] OWL-PORTAL   [6] SETTINGS             │
 │                                                              │
 │  Mode: [LIVE]    Interface: wlan0mon    Channel: 6           │
 └──────────────────────────────────────────────────────────────┘
```

---

## ⚡ Features

<div align="center">

| Module | Description |
|:---|:---|
| 🔍 **OWL-RECON** | Live AP scan · client discovery · PMF detection · WIDS risk check · CSV export |
| 💥 **OWL-DEAUTH** | Targeted deauth · reason-code selector + fuzzer · MAC spoofing · seq spoofing · burst mode |
| 🌊 **OWL-FLOOD** | Broadcast deauth flood · channel-hopping · adaptive burst pacing · real-time pkt/s counter |
| 🎯 **OWL-HARVEST** | 4-Way Handshake + PMKID capture · auto-chaser · hashcat/aircrack integration · PSK display |
| 🕸️ **OWL-PORTAL** | Evil twin AP · captive portal HTML editor · credential logger · hostapd/dnsmasq config gen |
| ⚙️ **SETTINGS** | Health checks · YAML config editor · interface assignment · evidence export · about |

</div>

---

## 📋 Requirements

- **Python 3.10+**
- **Kali Linux / Parrot OS / Debian / Ubuntu** *(for live mode)*
- Monitor-mode capable WiFi adapter *(e.g., Alfa AWUS036ACH, TP-Link WN722N v1)*
- Root privileges *(for live mode — SIM mode works without root)*

### Python Dependencies

```
rich>=13.7.0
textual>=0.47.0
pyyaml>=6.0.1
click>=8.1.7
scapy>=2.5.0   # Linux only
```

---

## 🚀 Quick Install

### Kali / Parrot / Debian *(Recommended)*

```bash
# Clone the repository
git clone https://github.com/H4ckWSharon/OWL.git
cd OWL

# Full install (aircrack-ng + Python deps + CLI launcher)
sudo bash install.sh

# Launch in live mode (requires root + monitor NIC)
sudo owl

# Launch in SIM mode (no root, no hardware needed)
owl
```

### Manual Install *(any Linux)*

```bash
pip3 install rich textual pyyaml click scapy
sudo python3 owl.py
```

---

## 🎮 Controls

<div align="center">

| Key | Action |
|:---:|:---|
| `1` – `6` | Switch modules |
| `Ctrl+T` | Toggle terminal panel |
| `Ctrl+S` | Toggle SIM / LIVE mode |
| `Ctrl+A` | About OWL |
| `Ctrl+E` | Export evidence |
| `q` | Quit OWL |

</div>

---

## 🖥️ SIM Mode

Toggle **SIM MODE** in the sidebar or press `Ctrl+S` to run fully simulated operations — **no hardware required**. All modules produce realistic, animated output for demo or training purposes.

```bash
owl         # runs SIM mode automatically (no root / no NIC required)
```

---

## 📡 Live Mode *(Linux + root)*

Live mode requires the full aircrack-ng suite and a monitor-mode capable NIC.

| Requirement | Purpose |
|:---|:---|
| `airmon-ng` | Enable monitor mode |
| `aireplay-ng` | Deauth / flood attacks |
| `airodump-ng` | Packet capture / PCAP |
| `hostapd` | Evil twin AP (OWL-PORTAL) |
| `dnsmasq` | Captive portal DNS (OWL-PORTAL) |
| `hashcat` / `aircrack-ng` | PSK cracking (OWL-HARVEST) |

Check tool availability under **SETTINGS → TOOL DETECTION** inside OWL.

---

## 🗂️ Project Structure

```
OWL/
├── owl.py                  ← Main TUI application (entry point)
├── install.sh              ← Kali/Parrot/Debian installer
├── uninstall.sh            ← Uninstaller
├── requirements.txt        ← Python dependencies
├── lib/
│   ├── banner.py           ← ASCII art & text constants
│   ├── sim_engine.py       ← SIM mode simulation engine
│   ├── live_engine.py      ← Live mode (aircrack-ng / hostapd wrappers)
│   ├── net_utils.py        ← NIC detection & channel helpers
│   └── store.py            ← State management (consent, config)
└── config/
    └── default.yaml        ← Default configuration template
```

---

## ⚖️ Legal

OWL is designed **exclusively** for **authorized penetration testing** and security research.

**You must:**
- Own the target networks, **OR**
- Have **explicit written permission** from the network owner

Unauthorized use is illegal under:
- 🇺🇸 Computer Fraud and Abuse Act (CFAA)
- 🇬🇧 Computer Misuse Act 1990
- 🇪🇺 EU Directive on Attacks Against Information Systems
- and equivalent laws in your jurisdiction.

**The creator (Sharon Anil) assumes zero liability for misuse.**

---

<div align="center">

```
      (  ,  )
       )/ \(
      (/ @ \)      See in the dark.
       )   (       Strike without a trace.
      (_\_/_)
       ( Y )
       /|=|\
      (_/ \_)
```

**CREATED BY [SHARON ANIL](https://github.com/H4ckWSharon)**
OWL v1.0 · *"See in the dark. Strike without a trace."*

![Visitors](https://visitor-badge.laobi.icu/badge?page_id=H4ckWSharon.OWL&style=for-the-badge)

</div>
