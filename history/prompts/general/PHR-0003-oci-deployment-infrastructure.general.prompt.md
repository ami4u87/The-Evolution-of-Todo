---
id: 3
title: OCI Deployment Infrastructure
stage: general
date: 2026-02-09
surface: agent
model: claude-opus-4-6
feature: none
branch: master
user: ami4u87
command: implement
labels: ["deployment", "oci", "docker", "caddy", "production"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - docker/frontend/Dockerfile
  - caddy/Caddyfile
  - docker-compose.prod.yml
  - .dockerignore
  - scripts/deploy-oci.sh
  - docs/oci-deployment.md
tests:
  - none
---

## Prompt

Implement the following plan:

# Oracle Cloud Infrastructure (OCI) Deployment Plan

## Context

The user signed up for Oracle Cloud and wants to deploy their Todo application (FastAPI + Next.js + Neon PostgreSQL) on OCI's Always Free ARM VM. The project already has production Dockerfiles (`docker/backend/Dockerfile`, `docker/frontend/Dockerfile`) and K8s deployment configs, but no simple VM-based production deployment. We need a Docker Compose production setup with Caddy reverse proxy for automatic HTTPS.

## Deliverables

1. Modify `docker/frontend/Dockerfile` - Add ARG/ENV for NEXT_PUBLIC_API_URL
2. Create `caddy/Caddyfile` - Reverse proxy config with auto-HTTPS
3. Create `docker-compose.prod.yml` - Production compose (no local DB, Caddy proxy)
4. Create `.dockerignore` at project root
5. Create `scripts/deploy-oci.sh` - Automated OCI VM deployment script
6. Create `docs/oci-deployment.md` - Deployment guide

## Response snapshot

Implemented all 6 deliverables:

1. **docker/frontend/Dockerfile**: Added `ARG NEXT_PUBLIC_API_URL=http://localhost:8000` and `ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL` before the build step so Next.js inlines the correct API URL at build time.

2. **caddy/Caddyfile**: Reverse proxy config using `{$DOMAIN}` env var for auto-HTTPS. Routes `/api/*` and `/health` to backend:8000, everything else to frontend:3000. Includes security headers and gzip/zstd compression.

3. **docker-compose.prod.yml**: Three services (backend, frontend, caddy). Backend uses `.env.production`, frontend gets `NEXT_PUBLIC_API_URL` as build arg. Only Caddy exposes ports 80/443. Uses `todo-prod-network` bridge. No local PostgreSQL (uses external Neon).

4. **.dockerignore**: Excludes .git/, node_modules/, k8s/, helm/, docs/, specs/, history/, subagents/ from Docker build context.

5. **scripts/deploy-oci.sh**: Full automated deployment script with 9 phases: OS detection, Docker install, firewall config (iptables for Ubuntu, firewalld for Oracle Linux), repo clone/pull, interactive config collection, domain vs IP detection, .env.production creation, container build/start, health checks.

6. **docs/oci-deployment.md**: Step-by-step guide covering OCI Console setup, security list rules, SSH access, deploy script usage (interactive and non-interactive), DNS setup, management commands, and troubleshooting.

## Outcome

- ✅ Impact: Complete production deployment infrastructure for OCI Always Free ARM VM
- 🧪 Tests: No automated tests; manual verification via health checks documented
- 📁 Files: 1 modified, 5 created
- 🔁 Next prompts: Test deployment on actual OCI VM, configure DNS, verify HTTPS
- 🧠 Reflection: Key gotchas handled — OCI iptables blocking, NEXT_PUBLIC_* build-time inlining, Caddy IP vs domain HTTPS behavior

## Evaluation notes (flywheel)

- Failure modes observed: None during implementation (infrastructure code, not runtime)
- Graders run and results (PASS/FAIL): N/A — deployment scripts require target environment
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Deploy to actual OCI VM and validate end-to-end
