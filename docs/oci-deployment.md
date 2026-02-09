# OCI Deployment Guide

Deploy the Todo application on Oracle Cloud Infrastructure (OCI) Always Free ARM VM with Docker Compose and Caddy reverse proxy.

## Architecture

```
Internet → Caddy (:80/:443) → Frontend (:3000) / Backend (:8000)
                                                      ↓
                                              Neon PostgreSQL (external)
```

- **Caddy** handles TLS termination and reverse proxying
- **Frontend** (Next.js) serves the UI
- **Backend** (FastAPI) serves the API
- **Database** runs on Neon (external, not on the VM)

## Prerequisites

- Oracle Cloud account (Always Free tier works)
- Neon PostgreSQL database (free tier: https://console.neon.tech)
- (Optional) A domain name pointed to your server IP
- (Optional) Groq API key for AI chat (free: https://console.groq.com/keys)

## Step 1: Create OCI VM

1. Log into [OCI Console](https://cloud.oracle.com/)
2. Go to **Compute > Instances > Create Instance**
3. Configure:
   - **Name**: `todo-app`
   - **Image**: Ubuntu 22.04 (or Oracle Linux 9)
   - **Shape**: VM.Standard.A1.Flex (ARM) — 1 OCPU, 6 GB RAM (Always Free)
   - **Network**: Create new VCN or use existing
   - **SSH Key**: Add your public key
4. Click **Create**

## Step 2: Configure Security List

OCI blocks all inbound traffic by default. You must open ports 80 and 443.

1. Go to **Networking > Virtual Cloud Networks**
2. Click your VCN > **Security Lists** > Default Security List
3. Add **Ingress Rules**:

| Source CIDR | Protocol | Dest Port | Description |
|-------------|----------|-----------|-------------|
| 0.0.0.0/0   | TCP      | 80        | HTTP        |
| 0.0.0.0/0   | TCP      | 443       | HTTPS       |

4. Click **Save**

> **Important**: Even after adding Security List rules, OCI Ubuntu VMs have iptables rules that block traffic. The deploy script handles this automatically.

## Step 3: SSH into the VM

```bash
ssh -i ~/.ssh/your_key ubuntu@<your-vm-ip>
```

For Oracle Linux:
```bash
ssh -i ~/.ssh/your_key opc@<your-vm-ip>
```

## Step 4: Run the Deploy Script

### Option A: Interactive Mode

```bash
curl -fsSL https://raw.githubusercontent.com/ami4u87/Hacathorn-II-The-Evolution-of-Todo/master/scripts/deploy-oci.sh | sudo bash
```

The script will prompt for:
- Neon DATABASE_URL
- BETTER_AUTH_SECRET
- Domain name (optional)
- Groq API key (optional)

### Option B: Non-Interactive Mode

```bash
curl -fsSL https://raw.githubusercontent.com/ami4u87/Hacathorn-II-The-Evolution-of-Todo/master/scripts/deploy-oci.sh -o deploy.sh
sudo bash deploy.sh \
  --domain todo.example.com \
  --database-url "postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require" \
  --auth-secret "$(openssl rand -base64 32)" \
  --groq-key "gsk_your_groq_key_here"
```

### Option C: Already Cloned

If you've already cloned the repo:
```bash
cd /opt/todo-app  # or wherever you cloned it
sudo bash scripts/deploy-oci.sh --domain todo.example.com
```

## Step 5: Verify Deployment

```bash
# Check all containers are running
docker compose -f /opt/todo-app/docker-compose.prod.yml ps

# Test health endpoint
curl http://your-domain-or-ip/health

# Test frontend
curl http://your-domain-or-ip/

# View logs
docker compose -f /opt/todo-app/docker-compose.prod.yml logs -f
```

## DNS Setup (for HTTPS)

If using a domain name:

1. Get your VM's public IP from OCI Console
2. Add a DNS A record:
   - **Name**: `todo` (or `@` for root domain)
   - **Type**: A
   - **Value**: Your VM's public IP
3. Wait for DNS propagation (usually 1-5 minutes)
4. Caddy will automatically provision a Let's Encrypt certificate

## Management Commands

```bash
cd /opt/todo-app

# View status
docker compose -f docker-compose.prod.yml ps

# View logs (all services)
docker compose -f docker-compose.prod.yml logs -f

# View logs (specific service)
docker compose -f docker-compose.prod.yml logs -f backend

# Restart all services
docker compose -f docker-compose.prod.yml restart

# Stop all services
docker compose -f docker-compose.prod.yml down

# Rebuild and restart (after code changes)
git pull origin master
docker compose -f docker-compose.prod.yml up -d --build

# Update just one service
docker compose -f docker-compose.prod.yml up -d --build backend
```

## Updating the Application

```bash
cd /opt/todo-app
git pull origin master
docker compose -f docker-compose.prod.yml up -d --build
```

## Troubleshooting

### Ports Not Accessible

**Symptom**: Can't reach the server on port 80/443 from outside.

**Cause**: OCI Ubuntu VMs have iptables rules that block ports even with Security List rules.

**Fix**:
```bash
# Check iptables rules
sudo iptables -L INPUT -n --line-numbers

# Manually add rules before the REJECT line
REJECT_LINE=$(sudo iptables -L INPUT -n --line-numbers | grep "REJECT" | head -1 | awk '{print $1}')
sudo iptables -I INPUT $REJECT_LINE -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT $REJECT_LINE -p tcp --dport 443 -j ACCEPT

# Persist
sudo netfilter-persistent save
```

### Caddy Can't Get Certificate

**Symptom**: HTTPS not working, Caddy logs show ACME errors.

**Causes**:
- DNS not pointing to this server yet
- Ports 80/443 not accessible from internet
- Rate limit hit (Let's Encrypt)

**Fix**:
```bash
# Check DNS
dig +short todo.example.com

# Check Caddy logs
docker compose -f docker-compose.prod.yml logs caddy

# Verify port is open
curl -I http://your-ip/
```

### Backend Can't Connect to Database

**Symptom**: Backend container keeps restarting.

**Fix**:
```bash
# Check backend logs
docker compose -f docker-compose.prod.yml logs backend

# Verify DATABASE_URL in .env.production
cat .env.production | grep DATABASE_URL

# Test connection directly
docker compose -f docker-compose.prod.yml exec backend python -c "
from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    print(conn.execute(text('SELECT 1')).scalar())
"
```

### Frontend Shows "localhost:8000" Errors

**Symptom**: Frontend tries to reach `localhost:8000` instead of your domain.

**Cause**: `NEXT_PUBLIC_API_URL` was not set at build time.

**Fix**:
```bash
# Rebuild with correct API URL
export NEXT_PUBLIC_API_URL=https://your-domain.com
docker compose -f docker-compose.prod.yml up -d --build frontend
```

### Out of Disk Space

The Always Free ARM VM has limited storage.

```bash
# Check disk usage
df -h

# Clean up Docker (remove unused images/volumes)
docker system prune -af
docker volume prune -f
```

### Checking Container Health

```bash
# Detailed container status
docker compose -f docker-compose.prod.yml ps

# Inspect a specific container
docker inspect todo-backend | jq '.[0].State.Health'
```

## Resource Usage

The Always Free ARM VM (1 OCPU, 6 GB RAM) comfortably runs all three containers:

| Container | CPU | RAM (typical) |
|-----------|-----|---------------|
| Backend   | Low | ~100-200 MB   |
| Frontend  | Low | ~100-200 MB   |
| Caddy     | Minimal | ~20 MB    |
| **Total** | | **~320-420 MB** |

## Security Notes

- `.env.production` has `chmod 600` (owner-read-only)
- Caddy adds security headers (X-Content-Type-Options, X-Frame-Options, Referrer-Policy)
- Only Caddy ports (80/443) are exposed to the host; backend and frontend are internal only
- Backend runs as non-root user inside container
- Frontend runs as non-root user inside container
