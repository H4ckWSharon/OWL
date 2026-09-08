#!/usr/bin/env bash
# OWL — Uninstaller
# Created by Sharon Anil

set -e
if [[ $EUID -ne 0 ]]; then echo "Run as root: sudo bash uninstall.sh"; exit 1; fi

echo "[*] Removing OWL CLI launchers..."
rm -f /usr/local/bin/owl
rm -f /usr/local/bin/owl-recon
rm -f /usr/local/bin/owl-deauth
rm -f /usr/local/bin/owl-flood
rm -f /usr/local/bin/owl-harvest
rm -f /usr/local/bin/owl-portal

echo "[*] Removing OWL state file..."
rm -f "$HOME/.owl_state.json"
rm -f "$HOME/.owl_config.yaml"

echo "[+] OWL uninstalled. System tools (aircrack-ng, etc.) preserved."
echo "[+] Remove OWL directory manually if desired."
