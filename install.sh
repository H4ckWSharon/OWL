#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  OWL — Offensive WiFi Launcher                                               ║
# ║  Installer for Kali Linux / Parrot OS / Debian / Ubuntu                     ║
# ║  Created by Sharon Anil                                                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
# Usage:  sudo bash install.sh
# Uninstall: sudo bash uninstall.sh

set -e

# ── Colors ─────────────────────────────────────────────────────────────────────
AMBER='\033[0;33m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

owl_banner() {
cat << 'EOF'

    ██████╗ ██╗    ██╗██╗
   ██╔═══██╗██║    ██║██║
   ██║   ██║██║ █╗ ██║██║       Offensive WiFi Launcher v1.0
   ██║   ██║██║███╗██║██║       "See in the dark. Strike without a trace."
   ╚██████╔╝╚███╔███╔╝███████╗
    ╚═════╝  ╚══╝╚══╝ ╚══════╝   Created by Sharon Anil

EOF
}

info()    { echo -e "${CYAN}[*]${NC} $*"; }
success() { echo -e "${GREEN}[+]${NC} $*"; }
warn()    { echo -e "${AMBER}[!]${NC} $*"; }
error()   { echo -e "${RED}[✗]${NC} $*"; exit 1; }
step()    { echo -e "\n${BOLD}${AMBER}──────────────────────────────────────────${NC}"; echo -e "${BOLD}$*${NC}"; }

# ── Check root ────────────────────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
    error "OWL installer requires root. Run: sudo bash install.sh"
fi

owl_banner

step "Step 1/6 — Detecting system"
OS_ID=$(grep -oP '(?<=^ID=).+' /etc/os-release 2>/dev/null | tr -d '"' || echo "unknown")
OS_PRETTY=$(grep -oP '(?<=^PRETTY_NAME=).+' /etc/os-release 2>/dev/null | tr -d '"' || echo "Linux")
ARCH=$(uname -m)
KERNEL=$(uname -r)

info "OS:     $OS_PRETTY"
info "Kernel: $KERNEL"
info "Arch:   $ARCH"

case "$OS_ID" in
    kali|parrot|debian|ubuntu|linuxmint|mx)
        info "Supported distro detected: $OS_ID"
        ;;
    *)
        warn "Distro '$OS_ID' not officially tested. Proceeding anyway..."
        ;;
esac

OWL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
info "OWL directory: $OWL_DIR"

step "Step 2/6 — Updating package lists"
apt-get update -qq || warn "apt update failed — continuing..."

step "Step 3/6 — Installing system dependencies"
SYSTEM_PKGS=(
    python3
    python3-pip
    python3-venv
    aircrack-ng
    hashcat
    hostapd
    dnsmasq
    iw
    wireless-tools
    net-tools
    curl
    wget
    git
)

info "Installing: ${SYSTEM_PKGS[*]}"
apt-get install -y --no-install-recommends "${SYSTEM_PKGS[@]}" 2>&1 \
    | grep -E "^(Setting up|Reading|Unpacking|Get:|Err:|W:)" \
    || true

# Optional tools
OPTIONAL_PKGS=(hcxdumptool hcxtools tcpdump wireshark-common nmap)
for pkg in "${OPTIONAL_PKGS[@]}"; do
    apt-get install -y --no-install-recommends "$pkg" 2>/dev/null && \
        info "Installed optional: $pkg" || warn "Optional $pkg not available — skipping"
done

success "System dependencies installed."

step "Step 4/6 — Installing Python dependencies"

PY=$(command -v python3)
info "Python: $($PY --version)"

# Modern Debian/Parrot/Ubuntu enforce PEP 668 — system pip is restricted.
# We create a dedicated virtualenv at /opt/owl-venv instead.
OWL_VENV="/opt/owl-venv"
info "Creating virtual environment at $OWL_VENV ..."
$PY -m venv "$OWL_VENV"

VENV_PY="$OWL_VENV/bin/python3"
VENV_PIP="$OWL_VENV/bin/pip"

info "Upgrading pip inside venv..."
"$VENV_PIP" install --upgrade pip --quiet

info "Installing OWL Python dependencies into venv..."
"$VENV_PIP" install \
    "rich>=13.7.0" \
    "textual>=0.47.0" \
    "pyyaml>=6.0.1" \
    "click>=8.1.7" \
    "scapy>=2.5.0" \
    --quiet

success "Python dependencies installed into $OWL_VENV"

step "Step 5/6 — Creating CLI launcher"

# Create /usr/local/bin/owl — uses the venv Python
cat > /usr/local/bin/owl << OWLEOF
#!/usr/bin/env bash
# OWL CLI launcher — Created by Sharon Anil
# Uses dedicated venv at /opt/owl-venv to avoid PEP 668 restrictions
cd "$OWL_DIR"
exec "$OWL_VENV/bin/python3" "$OWL_DIR/owl.py" "\$@"
OWLEOF

chmod +x /usr/local/bin/owl
success "CLI launcher created: /usr/local/bin/owl"

# Create owl-recon, owl-deauth etc. shortcuts
for mod in recon deauth flood harvest portal; do
    cat > "/usr/local/bin/owl-$mod" << MODEOF
#!/usr/bin/env bash
cd "$OWL_DIR"
exec "$OWL_VENV/bin/python3" "$OWL_DIR/owl.py" --module $mod "\$@"
MODEOF
    chmod +x "/usr/local/bin/owl-$mod"
done
success "Module shortcuts created: owl-recon, owl-deauth, owl-flood, owl-harvest, owl-portal"

step "Step 6/6 — Final checks"

# Verify Python can import textual (use venv Python)
if "$VENV_PY" -c "import textual, rich, yaml" 2>/dev/null; then
    success "Python imports: OK (venv)"
else
    error "Python import check failed. Try: $VENV_PIP install rich textual pyyaml"
fi

# Verify aircrack suite
for tool in airmon-ng aireplay-ng airodump-ng; do
    if command -v "$tool" &>/dev/null; then
        success "Found: $tool"
    else
        warn "Missing: $tool — live ops will be unavailable"
    fi
done

# Ensure wireless tools available
if command -v iw &>/dev/null; then
    success "Found: iw (wireless interface management)"
fi

echo ""
echo -e "${AMBER}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${AMBER}║${NC}  ${BOLD}OWL v1.0 — Installation Complete!${NC}                          ${AMBER}║${NC}"
echo -e "${AMBER}║${NC}                                                              ${AMBER}║${NC}"
echo -e "${AMBER}║${NC}  Run as root for live mode:                                 ${AMBER}║${NC}"
echo -e "${AMBER}║${NC}    ${CYAN}sudo owl${NC}                                               ${AMBER}║${NC}"
echo -e "${AMBER}║${NC}                                                              ${AMBER}║${NC}"
echo -e "${AMBER}║${NC}  Run in SIM mode (no root required):                        ${AMBER}║${NC}"
echo -e "${AMBER}║${NC}    ${CYAN}owl${NC}                                                    ${AMBER}║${NC}"
echo -e "${AMBER}║${NC}                                                              ${AMBER}║${NC}"
echo -e "${AMBER}║${NC}  ${DIM}Created by Sharon Anil · For authorized use only${NC}         ${AMBER}║${NC}"
echo -e "${AMBER}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
