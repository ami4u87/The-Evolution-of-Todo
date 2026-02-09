#!/usr/bin/env bash
# =============================================================================
# OCI VM Deployment Script for Todo Application
# Supports Ubuntu and Oracle Linux on ARM64 (Always Free tier)
# =============================================================================
set -euo pipefail

# --- Configuration -----------------------------------------------------------
REPO_URL="https://github.com/ami4u87/Hacathorn-II-The-Evolution-of-Todo.git"
APP_DIR="/opt/todo-app"
BRANCH="master"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Helper Functions --------------------------------------------------------
log_info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Deploy the Todo application on an OCI ARM64 VM.

Options:
  --domain <domain>       Domain name (e.g., todo.example.com) or leave empty for IP-only mode
  --database-url <url>    Neon PostgreSQL connection string
  --auth-secret <secret>  BETTER_AUTH_SECRET (min 32 chars)
  --groq-key <key>        Groq API key for AI chat (optional)
  --branch <branch>       Git branch to deploy (default: master)
  --repo <url>            Git repository URL (default: project repo)
  -h, --help              Show this help message

If options are not provided, the script will prompt interactively.

Examples:
  # Interactive mode
  sudo bash deploy-oci.sh

  # Non-interactive mode
  sudo bash deploy-oci.sh \\
    --domain todo.example.com \\
    --database-url "postgresql://user:pass@host/db?sslmode=require" \\
    --auth-secret "your-32-char-secret-here-change-me"
EOF
    exit 0
}

# --- Parse Arguments ---------------------------------------------------------
DOMAIN=""
DATABASE_URL=""
AUTH_SECRET=""
GROQ_KEY=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --domain)       DOMAIN="$2"; shift 2 ;;
        --database-url) DATABASE_URL="$2"; shift 2 ;;
        --auth-secret)  AUTH_SECRET="$2"; shift 2 ;;
        --groq-key)     GROQ_KEY="$2"; shift 2 ;;
        --branch)       BRANCH="$2"; shift 2 ;;
        --repo)         REPO_URL="$2"; shift 2 ;;
        -h|--help)      usage ;;
        *)              log_error "Unknown option: $1"; usage ;;
    esac
done

# --- Root Check --------------------------------------------------------------
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root (use sudo)"
    exit 1
fi

# =============================================================================
# Phase 1: Detect OS and Install Dependencies
# =============================================================================
log_info "Phase 1: Detecting OS and installing dependencies..."

detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    else
        log_error "Cannot detect OS"
        exit 1
    fi
}

OS=$(detect_os)
log_info "Detected OS: $OS"

install_docker_ubuntu() {
    log_info "Installing Docker on Ubuntu..."
    apt-get update -qq
    apt-get install -y -qq ca-certificates curl gnupg lsb-release

    # Add Docker GPG key and repo
    install -m 0755 -d /etc/apt/keyrings
    if [ ! -f /etc/apt/keyrings/docker.gpg ]; then
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        chmod a+r /etc/apt/keyrings/docker.gpg
    fi

    if [ ! -f /etc/apt/sources.list.d/docker.list ]; then
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
            > /etc/apt/sources.list.d/docker.list
    fi

    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    systemctl enable --now docker
    log_ok "Docker installed on Ubuntu"
}

install_docker_ol() {
    log_info "Installing Docker on Oracle Linux..."
    dnf install -y dnf-utils
    dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    systemctl enable --now docker
    log_ok "Docker installed on Oracle Linux"
}

install_git() {
    if command -v git &>/dev/null; then
        log_ok "Git already installed"
        return
    fi
    log_info "Installing Git..."
    case "$OS" in
        ubuntu|debian) apt-get install -y -qq git ;;
        ol|oraclelinux|centos|rhel) dnf install -y git ;;
        *) log_error "Unsupported OS for git install: $OS"; exit 1 ;;
    esac
    log_ok "Git installed"
}

# Install Docker if not present
if command -v docker &>/dev/null && docker compose version &>/dev/null; then
    log_ok "Docker and Docker Compose already installed"
else
    case "$OS" in
        ubuntu|debian)          install_docker_ubuntu ;;
        ol|oraclelinux|centos)  install_docker_ol ;;
        *)                      log_error "Unsupported OS: $OS"; exit 1 ;;
    esac
fi

install_git

# =============================================================================
# Phase 2: Open Firewall Ports (OCI blocks by default)
# =============================================================================
log_info "Phase 2: Opening firewall ports 80 and 443..."

open_firewall_ubuntu() {
    # OCI Ubuntu images use iptables with a REJECT rule that blocks traffic
    # even when Security List allows it. Insert ACCEPT before the REJECT.
    if iptables -L INPUT -n --line-numbers | grep -q "REJECT"; then
        REJECT_LINE=$(iptables -L INPUT -n --line-numbers | grep "REJECT" | head -1 | awk '{print $1}')
        # Check if rules already exist
        if ! iptables -C INPUT -p tcp --dport 80 -j ACCEPT 2>/dev/null; then
            iptables -I INPUT "$REJECT_LINE" -p tcp --dport 80 -j ACCEPT
            log_ok "Opened port 80 (iptables)"
        fi
        if ! iptables -C INPUT -p tcp --dport 443 -j ACCEPT 2>/dev/null; then
            iptables -I INPUT "$REJECT_LINE" -p tcp --dport 443 -j ACCEPT
            log_ok "Opened port 443 (iptables)"
        fi
        # Persist rules
        if command -v netfilter-persistent &>/dev/null; then
            netfilter-persistent save
        elif [ -f /etc/iptables/rules.v4 ]; then
            iptables-save > /etc/iptables/rules.v4
        fi
    else
        log_ok "No iptables REJECT rule found, ports should be open"
    fi
}

open_firewall_ol() {
    if command -v firewall-cmd &>/dev/null; then
        firewall-cmd --permanent --add-port=80/tcp 2>/dev/null || true
        firewall-cmd --permanent --add-port=443/tcp 2>/dev/null || true
        firewall-cmd --reload
        log_ok "Opened ports 80, 443 (firewalld)"
    else
        log_warn "firewalld not found, skipping"
    fi
}

case "$OS" in
    ubuntu|debian)          open_firewall_ubuntu ;;
    ol|oraclelinux|centos)  open_firewall_ol ;;
esac

# =============================================================================
# Phase 3: Clone or Pull Repository
# =============================================================================
log_info "Phase 3: Setting up application code..."

if [ -d "$APP_DIR/.git" ]; then
    log_info "Repository exists, pulling latest changes..."
    cd "$APP_DIR"
    git fetch origin
    git checkout "$BRANCH"
    git pull origin "$BRANCH"
    log_ok "Repository updated"
else
    log_info "Cloning repository..."
    git clone -b "$BRANCH" "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
    log_ok "Repository cloned to $APP_DIR"
fi

# =============================================================================
# Phase 4: Collect Configuration
# =============================================================================
log_info "Phase 4: Collecting configuration..."

# Database URL
if [ -z "$DATABASE_URL" ]; then
    echo ""
    echo -e "${YELLOW}Enter your Neon PostgreSQL connection string${NC}"
    echo "  Format: postgresql://user:password@host/dbname?sslmode=require"
    echo "  Get it from: https://console.neon.tech"
    read -rp "  DATABASE_URL: " DATABASE_URL
fi

if [ -z "$DATABASE_URL" ]; then
    log_error "DATABASE_URL is required"
    exit 1
fi

# Auth secret
if [ -z "$AUTH_SECRET" ]; then
    echo ""
    echo -e "${YELLOW}Enter BETTER_AUTH_SECRET (min 32 characters)${NC}"
    echo "  Generate one with: openssl rand -base64 32"
    read -rp "  AUTH_SECRET: " AUTH_SECRET
fi

if [ ${#AUTH_SECRET} -lt 32 ]; then
    log_error "AUTH_SECRET must be at least 32 characters"
    exit 1
fi

# Domain
if [ -z "$DOMAIN" ]; then
    echo ""
    echo -e "${YELLOW}Enter your domain name (or press Enter for IP-only HTTP mode)${NC}"
    echo "  Example: todo.example.com"
    read -rp "  DOMAIN: " DOMAIN
fi

# Groq key (optional)
if [ -z "$GROQ_KEY" ]; then
    echo ""
    echo -e "${YELLOW}Enter Groq API key for AI chat (optional, press Enter to skip)${NC}"
    echo "  Get one free at: https://console.groq.com/keys"
    read -rp "  GROQ_KEY: " GROQ_KEY
fi

# =============================================================================
# Phase 5: Detect Domain vs IP and Set URLs
# =============================================================================
log_info "Phase 5: Configuring URLs..."

if [ -n "$DOMAIN" ]; then
    # Real domain - Caddy will auto-provision HTTPS
    CADDY_DOMAIN="$DOMAIN"
    PUBLIC_URL="https://$DOMAIN"
    API_URL="https://$DOMAIN"
    CORS_ORIGINS="https://$DOMAIN"
    log_ok "Domain mode: $DOMAIN (HTTPS via Caddy)"
else
    # No domain - HTTP only on port 80
    CADDY_DOMAIN=":80"
    # Detect public IP
    PUBLIC_IP=$(curl -s -4 ifconfig.me || curl -s -4 icanhazip.com || echo "YOUR_SERVER_IP")
    PUBLIC_URL="http://$PUBLIC_IP"
    API_URL="http://$PUBLIC_IP"
    CORS_ORIGINS="http://$PUBLIC_IP"
    log_ok "IP mode: $PUBLIC_IP (HTTP only)"
fi

# =============================================================================
# Phase 6: Create .env.production
# =============================================================================
log_info "Phase 6: Creating .env.production..."

cat > "$APP_DIR/.env.production" <<ENVEOF
# =============================================================================
# Production Environment - Generated by deploy-oci.sh
# Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
# =============================================================================

# Database (Neon Serverless PostgreSQL)
DATABASE_URL=$DATABASE_URL

# Authentication
BETTER_AUTH_SECRET=$AUTH_SECRET
JWT_ALGORITHM=HS256

# API Configuration
API_PREFIX=/api
DEBUG=false

# CORS
CORS_ORIGINS=$CORS_ORIGINS

# AI Chat (Groq - optional)
AI_PROVIDER=groq
GROQ_API_KEY=${GROQ_KEY:-not-configured}
GROQ_MODEL=llama-3.3-70b-versatile
ENVEOF

chmod 600 "$APP_DIR/.env.production"
log_ok ".env.production created"

# =============================================================================
# Phase 7: Build and Start Containers
# =============================================================================
log_info "Phase 7: Building and starting containers..."

cd "$APP_DIR"

# Export build-time variables
export NEXT_PUBLIC_API_URL="$API_URL"
export CADDY_DOMAIN="$CADDY_DOMAIN"

# Build and start
docker compose -f docker-compose.prod.yml up -d --build

log_ok "Containers started"

# =============================================================================
# Phase 8: Health Check
# =============================================================================
log_info "Phase 8: Running health checks..."

# Wait for services to stabilize
log_info "Waiting 15 seconds for services to start..."
sleep 15

HEALTH_OK=true

# Check backend health
if curl -sf "http://localhost:80/health" > /dev/null 2>&1; then
    log_ok "Backend health check passed"
else
    log_warn "Backend health check failed (may still be starting)"
    HEALTH_OK=false
fi

# Check frontend
if curl -sf "http://localhost:80/" > /dev/null 2>&1; then
    log_ok "Frontend health check passed"
else
    log_warn "Frontend health check failed (may still be starting)"
    HEALTH_OK=false
fi

# Check container status
echo ""
docker compose -f docker-compose.prod.yml ps

# =============================================================================
# Phase 9: Summary
# =============================================================================
echo ""
echo "============================================================================="
echo -e "${GREEN}  Deployment Complete!${NC}"
echo "============================================================================="
echo ""
echo -e "  ${BLUE}Application URL:${NC}  $PUBLIC_URL"
echo -e "  ${BLUE}API URL:${NC}          $PUBLIC_URL/api"
echo -e "  ${BLUE}Health Check:${NC}     $PUBLIC_URL/health"
echo ""

if [ "$CADDY_DOMAIN" != ":80" ]; then
    echo -e "  ${GREEN}HTTPS:${NC} Caddy will auto-provision a TLS certificate for $DOMAIN"
    echo "         Make sure your DNS A record points to this server's IP"
    echo ""
fi

if [ "$HEALTH_OK" = false ]; then
    echo -e "  ${YELLOW}Some health checks failed. Services may still be starting.${NC}"
    echo "  Wait a minute and check again with:"
    echo "    curl $PUBLIC_URL/health"
    echo ""
fi

echo "  Management Commands:"
echo "    cd $APP_DIR"
echo "    docker compose -f docker-compose.prod.yml ps       # Status"
echo "    docker compose -f docker-compose.prod.yml logs -f   # Logs"
echo "    docker compose -f docker-compose.prod.yml restart    # Restart"
echo "    docker compose -f docker-compose.prod.yml down       # Stop"
echo "    docker compose -f docker-compose.prod.yml up -d --build  # Rebuild"
echo ""
echo "============================================================================="
