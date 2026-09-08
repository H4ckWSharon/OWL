"""
OWL — Simulation Engine
Produces realistic fake output for all modules in SIM MODE.
Created by Sharon Anil
"""
import random
import string
import time
from datetime import datetime

# ─── Helpers ────────────────────────────────────────────────────────────────

def rand_mac() -> str:
    return ":".join(f"{random.randint(0, 255):02X}" for _ in range(6))

def rand_bssid() -> str:
    return rand_mac()

def rand_ssid() -> str:
    prefixes = ["NETGEAR", "Linksys", "TP-Link", "ASUS", "DLink", "Xfinity",
                "Spectrum", "ATT", "HomeNet", "Office_WiFi", "CafeNet", "StarbucksWifi"]
    suffix = "".join(random.choices(string.digits, k=random.randint(2, 5)))
    return random.choice(prefixes) + "_" + suffix

def rand_channel() -> int:
    return random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 36, 40, 44, 48, 149, 153, 157, 161])

def rand_signal() -> int:
    return random.randint(-85, -30)

def rand_enc() -> str:
    return random.choice(["WPA2", "WPA3", "WPA2/WPA3", "WPA", "OWE"])

def rand_pmf() -> str:
    return random.choice(["Required", "Optional", "Disabled"])

def rand_vendor() -> str:
    vendors = ["Apple", "Samsung", "Intel", "Realtek", "Broadcom", "Qualcomm",
               "MediaTek", "Ralink", "Atheros", "Unknown"]
    return random.choice(vendors)

def rand_reason() -> str:
    reasons = {
        "0x01": "Unspecified",
        "0x02": "Auth no longer valid",
        "0x03": "Deauth — leaving BSS",
        "0x04": "Inactivity",
        "0x05": "AP capacity exceeded",
        "0x06": "Class 2 frame from non-auth STA",
        "0x07": "Class 3 from non-assoc STA",
        "0x08": "Disassoc — leaving BSS",
        "0x0F": "4-Way Handshake timeout",
    }
    code = random.choice(list(reasons.keys()))
    return f"{code} ({reasons[code]})"

def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

# ─── RECON Simulation ────────────────────────────────────────────────────────

def sim_recon_scan(count: int = 8) -> list[dict]:
    """Return fake AP list from a RECON scan."""
    aps = []
    for _ in range(count):
        aps.append({
            "bssid": rand_bssid(),
            "ssid": rand_ssid(),
            "channel": rand_channel(),
            "signal": rand_signal(),
            "enc": rand_enc(),
            "pmf": rand_pmf(),
            "clients": random.randint(0, 12),
            "vendor": rand_vendor(),
            "wids": random.choice([True, False]),
        })
    return aps


def sim_recon_clients(bssid: str, count: int = 5) -> list[dict]:
    """Return fake client list for a given AP."""
    clients = []
    for _ in range(count):
        clients.append({
            "mac": rand_mac(),
            "channel": rand_channel(),
            "signal": rand_signal(),
            "vendor": rand_vendor(),
            "last_seen": timestamp(),
            "frames": random.randint(10, 9999),
        })
    return clients


def sim_recon_log_lines(bssid: str) -> list[tuple[str, str]]:
    """Log lines for recon operation."""
    return [
        ("cyan",    f"[{timestamp()}] [*] Starting OWL-RECON on interface wlan0mon"),
        ("cyan",    f"[{timestamp()}] [*] Target BSSID: {bssid}"),
        ("cyan",    f"[{timestamp()}] [*] Enabling monitor mode..."),
        ("green",   f"[{timestamp()}] [+] Monitor mode active on wlan0mon"),
        ("cyan",    f"[{timestamp()}] [*] Scanning all channels for beacons..."),
        ("yellow",  f"[{timestamp()}] [!] WIDS indicator detected — possible rogue AP monitoring"),
        ("cyan",    f"[{timestamp()}] [*] PMF status: {rand_pmf()} — {'Protected MgmtFrames active' if random.random() > 0.5 else 'No PMF, deauth viable'}"),
        ("green",   f"[{timestamp()}] [+] {random.randint(3, 14)} clients discovered"),
        ("green",   f"[{timestamp()}] [+] RECON complete."),
    ]


# ─── DEAUTH Simulation ───────────────────────────────────────────────────────

def sim_deauth_frames(bssid: str, client: str, count: int, reason: str) -> list[tuple[str, str]]:
    """Simulate sending deauth frames and return log lines."""
    logs = []
    logs.append(("cyan",   f"[{timestamp()}] [*] OWL-DEAUTH starting..."))
    logs.append(("cyan",   f"[{timestamp()}] [*] Target AP : {bssid}"))
    logs.append(("cyan",   f"[{timestamp()}] [*] Target STA: {client or 'FF:FF:FF:FF:FF:FF (broadcast)'}"))
    logs.append(("cyan",   f"[{timestamp()}] [*] Reason    : {reason}"))
    spoofed_src = rand_mac()
    logs.append(("magenta",f"[{timestamp()}] [~] Spoofed src MAC: {spoofed_src}"))
    for i in range(1, count + 1):
        seq = random.randint(1, 4095)
        logs.append((
            "green" if i % 7 != 0 else "yellow",
            f"[{timestamp()}] [>] Frame #{i:04d}  seq={seq:04d}  "
            f"src={spoofed_src}  dst={client or 'FF:FF:FF:FF:FF:FF'}  "
            f"AP={bssid}  reason={reason.split()[0]}"
        ))
        if i % 20 == 0:
            logs.append(("cyan", f"[{timestamp()}] [*] Sent {i}/{count} frames..."))
    logs.append(("green", f"[{timestamp()}] [+] DEAUTH complete — {count} frames transmitted."))
    return logs


# ─── FLOOD Simulation ────────────────────────────────────────────────────────

def sim_flood_tick(bssid: str, packet_num: int) -> tuple[str, str]:
    """Single flood tick log entry."""
    src = rand_mac()
    dst = "FF:FF:FF:FF:FF:FF"
    ch  = rand_channel()
    reason = f"0x{random.randint(1, 7):02X}"
    col = random.choice(["magenta", "green", "yellow"])
    return (col,
        f"[{timestamp()}] [FLOOD] #{packet_num:05d}  "
        f"ch={ch:3d}  src={src}  "
        f"→ {dst}  AP={bssid}  rsn={reason}"
    )


def sim_flood_burst(bssid: str, count: int) -> list[tuple[str, str]]:
    logs = [("cyan", f"[{timestamp()}] [*] OWL-FLOOD starting on {bssid}")]
    logs.append(("cyan", f"[{timestamp()}] [*] Mode: adaptive burst, channel-hopping ENABLED"))
    for i in range(1, count + 1):
        logs.append(sim_flood_tick(bssid, i))
    logs.append(("red", f"[{timestamp()}] [!] FLOOD STOP — {count} packets sent."))
    return logs


# ─── HARVEST Simulation ──────────────────────────────────────────────────────

def sim_harvest_log(bssid: str, ssid: str) -> list[tuple[str, str]]:
    client = rand_mac()
    logs = [
        ("cyan",    f"[{timestamp()}] [*] OWL-HARVEST started for {ssid} ({bssid})"),
        ("cyan",    f"[{timestamp()}] [*] Listening for 4-Way Handshake / PMKID..."),
        ("yellow",  f"[{timestamp()}] [!] Client {client} detected, sending chaser deauth..."),
        ("magenta", f"[{timestamp()}] [~] Deauth sent to {client} (re-association chaser)"),
        ("cyan",    f"[{timestamp()}] [*] Waiting for client reconnect..."),
        ("green",   f"[{timestamp()}] [+] EAPOL M1 captured from {bssid}"),
        ("green",   f"[{timestamp()}] [+] EAPOL M2 captured from {client}"),
        ("green",   f"[{timestamp()}] [+] EAPOL M3 captured from {bssid}"),
        ("green",   f"[{timestamp()}] [+] EAPOL M4 captured from {client}"),
        ("green",   f"[{timestamp()}] [✓] 4-WAY HANDSHAKE CAPTURED!"),
        ("cyan",    f"[{timestamp()}] [*] Saving to capture_{ssid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.cap"),
        ("cyan",    f"[{timestamp()}] [*] PMKID also extracted — dual-mode capture ready"),
        ("green",   f"[{timestamp()}] [+] Auto-switching to next target..."),
    ]
    return logs


def sim_crack_log(filename: str) -> list[tuple[str, str]]:
    psk = "".join(random.choices(string.ascii_letters + string.digits, k=random.randint(8, 16)))
    logs = [
        ("cyan",    f"[{timestamp()}] [*] Launching hashcat on {filename}..."),
        ("cyan",    f"[{timestamp()}] [*] Mode: PMKID (22000), wordlist: rockyou.txt"),
        ("yellow",  f"[{timestamp()}] [!] GPU acceleration not available, using CPU"),
        ("cyan",    f"[{timestamp()}] [*] Progress: 12.3%  Speed: 2.1 MH/s  ETA: 00:04:22"),
        ("cyan",    f"[{timestamp()}] [*] Progress: 45.7%  Speed: 2.3 MH/s  ETA: 00:02:08"),
        ("cyan",    f"[{timestamp()}] [*] Progress: 78.2%  Speed: 2.4 MH/s  ETA: 00:00:51"),
        ("green",   f"[{timestamp()}] [✓] PSK CRACKED: \"{psk}\""),
        ("green",   f"[{timestamp()}] [+] Result saved to cracked_{filename}.txt"),
    ]
    return logs, psk


# ─── PORTAL Simulation ───────────────────────────────────────────────────────

def sim_portal_start(ssid: str) -> list[tuple[str, str]]:
    logs = [
        ("cyan",    f"[{timestamp()}] [*] OWL-PORTAL starting evil twin for \"{ssid}\""),
        ("cyan",    f"[{timestamp()}] [*] Generating hostapd config..."),
        ("green",   f"[{timestamp()}] [+] hostapd config written to /tmp/owl_hostapd.conf"),
        ("cyan",    f"[{timestamp()}] [*] Starting rogue AP on wlan1 (channel 6)"),
        ("green",   f"[{timestamp()}] [+] Rogue AP live: SSID=\"{ssid}\" (open/no-auth)"),
        ("cyan",    f"[{timestamp()}] [*] Starting DHCP server on 192.168.99.1/24"),
        ("green",   f"[{timestamp()}] [+] DHCP ready — pool: 192.168.99.100-200"),
        ("cyan",    f"[{timestamp()}] [*] DNS spoof active — all queries → 192.168.99.1"),
        ("cyan",    f"[{timestamp()}] [*] Captive portal HTTP server started on :80"),
        ("green",   f"[{timestamp()}] [+] Portal LIVE. Waiting for victims..."),
    ]
    return logs


def sim_portal_credential() -> dict:
    first = random.choice(["john", "alice", "bob", "sarah", "mike", "emma", "admin", "user"])
    pwd = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(6, 12)))
    return {
        "timestamp": timestamp(),
        "ip": f"192.168.99.{random.randint(101, 200)}",
        "mac": rand_mac(),
        "username": first,
        "password": pwd,
        "user_agent": random.choice([
            "iPhone; CPU iPhone OS 17_0",
            "Android 14; Samsung SM-G998B",
            "Windows NT 10.0; Win64; x64",
            "Macintosh; Intel Mac OS X 14_0",
        ])
    }


# ─── Dashboard Simulation ────────────────────────────────────────────────────

def sim_nic_status() -> dict:
    return {
        "interface": "wlan0",
        "monitor_mode": random.choice([True, False]),
        "injection": random.choice([True, False]),
        "driver": random.choice(["ath9k_htc", "rt2800usb", "rtl8812au", "mt76"]),
        "chipset": random.choice(["AR9271", "RT3070", "RTL8812AU", "MT7612U"]),
        "channels_2g": "1-13",
        "channels_5g": "36-161",
    }


def sim_recent_sessions(count: int = 6) -> list[dict]:
    modules = ["RECON", "DEAUTH", "FLOOD", "HARVEST", "PORTAL"]
    statuses = ["complete", "running", "stopped", "failed"]
    sessions = []
    for i in range(count):
        mod = random.choice(modules)
        sessions.append({
            "id": f"SES-{random.randint(1000, 9999)}",
            "module": mod,
            "target": rand_bssid(),
            "ssid": rand_ssid(),
            "status": random.choice(statuses),
            "started": f"{random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}",
            "packets": random.randint(0, 50000),
        })
    return sessions
