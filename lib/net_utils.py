"""
OWL — Network Utilities
NIC detection, channel ops, interface helpers.
Created by Sharon Anil
"""

from __future__ import annotations
import os
import platform
import re
import shutil
import subprocess
from pathlib import Path

IS_LINUX = platform.system() == "Linux"
IS_ROOT  = (os.geteuid() == 0) if IS_LINUX else False


# ─── Interface discovery ──────────────────────────────────────────────────────

def list_all_interfaces() -> list[str]:
    """All network interfaces on the system."""
    if IS_LINUX:
        try:
            return os.listdir("/sys/class/net")
        except Exception:
            pass
    return []


def list_wifi_interfaces() -> list[str]:
    """Wireless interfaces (checks /wireless, /phy80211, interface type, or iw)."""
    ifaces = []
    for iface in list_all_interfaces():
        if iface == "lo":
            continue
        # Check 1: sysfs wireless or phy80211 node
        if (Path(f"/sys/class/net/{iface}/wireless").exists() or
            Path(f"/sys/class/net/{iface}/phy80211").exists()):
            ifaces.append(iface)
            continue
        # Check 2: type in (801, 802, 803) (ARPHRD_IEEE80211*)
        try:
            t = Path(f"/sys/class/net/{iface}/type").read_text().strip()
            if t in ("801", "802", "803"):
                ifaces.append(iface)
                continue
        except Exception:
            pass
        # Check 3: Standard wireless interface naming prefixes
        if iface.startswith(("wlan", "wlp", "wlo", "wlx", "mon", "wifi")):
            ifaces.append(iface)
    return sorted(list(set(ifaces)))


def get_interface_info(iface: str) -> dict:
    """Return dict with mode, mac, driver, channel, txpower."""
    info: dict = {
        "interface": iface,
        "mode": "unknown",
        "mac": "",
        "driver": "",
        "channel": 0,
        "txpower": 0,
        "monitor": False,
        "injection": False,
        "exists": False,
    }
    if not IS_LINUX:
        return info

    # Check existence
    if not Path(f"/sys/class/net/{iface}").exists():
        return info
    info["exists"] = True

    # MAC
    try:
        info["mac"] = Path(f"/sys/class/net/{iface}/address").read_text().strip()
    except Exception:
        pass

    # Driver
    try:
        driver_path = Path(f"/sys/class/net/{iface}/device/driver")
        if driver_path.exists():
            info["driver"] = driver_path.resolve().name
    except Exception:
        pass

    # Check sysfs type for monitor mode (802 = PRISM, 803 = RADIOTAP)
    try:
        t = Path(f"/sys/class/net/{iface}/type").read_text().strip()
        if t in ("802", "803"):
            info["mode"] = "monitor"
            info["monitor"] = True
    except Exception:
        pass

    # Mode via iw
    if info["mode"] == "unknown" and shutil.which("iw"):
        try:
            out = subprocess.check_output(
                ["iw", "dev", iface, "info"],
                stderr=subprocess.DEVNULL, text=True, timeout=2.0
            )
            for line in out.splitlines():
                s = line.strip()
                if s.startswith("type "):
                    info["mode"] = s.split()[-1].lower()
                    info["monitor"] = info["mode"] == "monitor"
                elif s.startswith("channel "):
                    m = re.search(r"channel (\d+)", s)
                    if m:
                        info["channel"] = int(m.group(1))
                elif s.startswith("txpower "):
                    m = re.search(r"txpower ([\d.]+)", s)
                    if m:
                        info["txpower"] = float(m.group(1))
        except Exception:
            pass

    # Fallback mode via iwconfig (especially for Realtek RTL8812au, etc.)
    if info["mode"] == "unknown" and shutil.which("iwconfig"):
        try:
            out = subprocess.check_output(
                ["iwconfig", iface],
                stderr=subprocess.DEVNULL, text=True, timeout=2.0
            )
            m = re.search(r"Mode:(\w+)", out, re.IGNORECASE)
            if m:
                info["mode"] = m.group(1).lower()
                info["monitor"] = info["mode"] == "monitor"
        except Exception:
            pass

    # Injection test (quick — check aireplay-ng exists when monitor is active)
    info["injection"] = info["monitor"] and shutil.which("aireplay-ng") is not None

    return info


def get_chipset(iface: str) -> str:
    """Try to get chipset info."""
    if not IS_LINUX:
        return "Unknown"
    try:
        # Try usb info
        for path in Path("/sys/bus/usb/devices").iterdir():
            id_vendor  = path / "idVendor"
            id_product = path / "idProduct"
            if id_vendor.exists() and id_product.exists():
                v = id_vendor.read_text().strip()
                p = id_product.read_text().strip()
                return f"USB {v}:{p}"
    except Exception:
        pass
    # PCI
    if shutil.which("lspci"):
        try:
            out = subprocess.check_output(
                ["lspci", "-v"], stderr=subprocess.DEVNULL, text=True
            )
            for line in out.splitlines():
                if "wireless" in line.lower() or "wifi" in line.lower() or "802.11" in line.lower():
                    return line.split(":", 2)[-1].strip()
        except Exception:
            pass
    return "Unknown"


# ─── Channel helpers ──────────────────────────────────────────────────────────

CHANNELS_24 = list(range(1, 14))
CHANNELS_50 = [36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108,
               112, 116, 120, 124, 128, 132, 136, 140, 149,
               153, 157, 161, 165]
ALL_CHANNELS = CHANNELS_24 + CHANNELS_50


def channel_to_freq(ch: int) -> int:
    """Convert channel number to MHz frequency."""
    if 1 <= ch <= 13:
        return 2407 + ch * 5
    if ch == 14:
        return 2484
    if ch >= 36:
        return 5000 + ch * 5
    return 0


def freq_to_channel(freq: int) -> int:
    """Convert MHz frequency to channel."""
    if 2412 <= freq <= 2472:
        return (freq - 2407) // 5
    if freq == 2484:
        return 14
    if freq >= 5180:
        return (freq - 5000) // 5
    return 0


def set_channel(iface: str, channel: int) -> bool:
    """Set interface channel via iw. Returns success."""
    if not IS_LINUX or not shutil.which("iw"):
        return False
    try:
        r = subprocess.run(
            ["iw", "dev", iface, "set", "channel", str(channel)],
            capture_output=True,
        )
        return r.returncode == 0
    except Exception:
        return False


# ─── Tool version detection ───────────────────────────────────────────────────

def get_tool_version(tool: str) -> str:
    """Try to get version string for a tool."""
    flags = {
        "airmon-ng":   ["--version"],
        "aireplay-ng": ["--version"],
        "airodump-ng": ["--version"],
        "hashcat":     ["--version"],
        "hostapd":     ["-v"],
        "python3":     ["--version"],
        "iw":          ["--version"],
    }
    flag = flags.get(tool, ["--version"])
    try:
        out = subprocess.check_output(
            [tool] + flag, stderr=subprocess.STDOUT, text=True, timeout=3
        )
        for line in out.splitlines():
            if line.strip():
                return line.strip()[:60]
    except Exception:
        pass
    return "n/a"


# ─── System info ──────────────────────────────────────────────────────────────

def get_system_info() -> dict:
    """Return OS, kernel, hostname."""
    info: dict = {
        "os": platform.system(),
        "distro": "",
        "kernel": platform.release(),
        "hostname": "",
        "arch": platform.machine(),
        "python": platform.python_version(),
    }
    try:
        import socket
        info["hostname"] = socket.gethostname()
    except Exception:
        pass
    if IS_LINUX:
        try:
            if Path("/etc/os-release").exists():
                for line in Path("/etc/os-release").read_text().splitlines():
                    if line.startswith("PRETTY_NAME="):
                        info["distro"] = line.split("=", 1)[1].strip().strip('"')
                        break
        except Exception:
            pass
    return info
