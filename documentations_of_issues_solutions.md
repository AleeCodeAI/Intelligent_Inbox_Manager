# Docker Compose Setup & Key Lessons Learned

## Overview
Successfully deployed a full-stack application (FastAPI backend + React frontend) using Docker Compose, connecting to external services (PostgreSQL, n8n, Langfuse) on a shared network.

---

## Key Lessons Learned

### 1. Database Connection: Container Name vs localhost

**The Problem:**
- Backend kept failing with: `FATAL: database "inbox-manager-production" does not exist`
- PostgreSQL container was running, but the database itself didn't exist

**The Lesson:**
- **A running PostgreSQL container ≠ database exists**
- You must explicitly create the database even if the container is running

**The Solution:**
```powershell
# Connect to PostgreSQL container
docker exec -it shared-postgres psql -U postgres

# Create the database
CREATE DATABASE "inbox-manager-production";
\q
```

**The Bigger Lesson - Container Communication:**
- Local development uses `localhost:5432`
- Docker containers must use the **container name**: `shared-postgres:5432`
- These need to be overridden in docker-compose.yml:

```yaml
environment:
  # Local: postgresql://postgres:password@localhost:5432/dbname
  # Docker: postgresql://postgres:password@shared-postgres:5432/dbname
  - POSTGRESQL_URL=postgresql://postgres:alee00@shared-postgres:5432/inbox-manager-production
```

---

### 2. Port Mapping: Host Ports vs Container Ports

**The Confusion:**
- n8n was running on host port `5679`
- Backend couldn't connect using `localhost:5679`

**The Lesson:**
- **Host port** (5679): What you use in your browser `http://localhost:5679`
- **Container port** (5678): What containers use to talk to each other
- Inside Docker networks, use `container-name:container-port`

**Example from our setup:**
```yaml
environment:
  # Wrong (only works on host machine)
  - N8N_WEBHOOK_URL=http://localhost:5679/webhook/fetch-emails
  
  # Correct (works inside Docker network)
  - N8N_WEBHOOK_URL=http://shared-n8n:5678/webhook/fetch-emails
```

**Port Mapping Table:**

| Service | Host Port | Container Port | When to use |
|---------|-----------|----------------|--------------|
| PostgreSQL | 5434 | 5432 | Browser: `localhost:5434`<br>Containers: `shared-postgres:5432` |
| n8n | 5679 | 5678 | Browser: `localhost:5679`<br>Containers: `shared-n8n:5678` |
| Langfuse | 3100 | 3000 | Browser: `localhost:3100`<br>Containers: `shared-langfuse:3000` |
| Backend | 8000 | 8000 | Both use same port |
| Frontend | 5173 | 80 | Browser: `localhost:5173`<br>Containers: N/A |

---

### 3. Environment Variables: .env vs docker-compose.yml

**The Pattern:**
- **Keep secrets in `.env` files** (API keys, passwords)
- **Override only what changes** in docker-compose.yml

**Our Setup:**
```yaml
backend:
  env_file:
    - backend/.env  # Loads everything (API keys, local URLs)
  environment:
    # Only override URLs that need Docker container names
    - POSTGRESQL_URL=postgresql://postgres:alee00@shared-postgres:5432/inbox-manager-production
    - LANGFUSE_HOST=http://shared-langfuse:3000
    - N8N_GET_EMAILS_WEBHOOK_URL=http://shared-n8n:5678/webhook/fetch-emails
    # API keys stay in .env file - no need to override
```

**Why this works:**
- Local development: Uses `localhost` URLs from `.env`
- Docker: Overrides URLs to use container names
- API keys: Same everywhere, no override needed

---

### 4. FastAPI Needs Uvicorn, Not python -m

**The Mistake:**
```dockerfile
CMD ["uv", "run", "python", "-m", "your_backend_module"]  # Wrong placeholder
```

**The Correction:**
```dockerfile
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Why:**
- FastAPI is an ASGI framework, needs an ASGI server (uvicorn)
- `python -m` only works for scripts/modules, not FastAPI apps
- Format: `uvicorn file:app_instance`

---

### 5. Docker Warnings Don't Mean Failure

**The Warning:**
```
level=warning msg="The \"LANGFUSE_PUBLIC_KEY\" variable is not set"
```

**The Reality:**
- Backend was running perfectly despite warnings
- Warnings came from Docker Compose, not the application
- Application got keys from `backend/.env` via `env_file`

**Lesson:** Don't panic at warnings - check if the application is actually working:
```powershell
docker compose ps  # Check if containers are Up
docker compose logs backend  # Check application logs
```

---

## Complete Working Configuration

### docker-compose.yml
```yaml
services:
  backend:
    build: ./backend
    container_name: inbox_manager_backend
    ports:
      - "8000:8000"
    env_file:
      - backend/.env
    environment:
      # Override URLs for Docker communication
      - POSTGRESQL_URL=postgresql://postgres:password@shared-postgres:5432/inbox-manager-production
      - LANGFUSE_HOST=http://shared-langfuse:3000
      - N8N_GET_EMAILS_WEBHOOK_URL=http://shared-n8n:5678/webhook/fetch-emails
      # ... other n8n webhooks
    networks:
      - infra-network

  frontend:
    build: ./frontend
    container_name: inbox_manager_frontend
    ports:
      - "5173:80"
    networks:
      - infra-network

networks:
  infra-network:
    external: true
```

### Database Setup Commands
```powershell
# 1. Create the database
docker exec -it shared-postgres psql -U postgres
CREATE DATABASE "inbox-manager-production";
\q

# 2. Create tables
docker compose exec backend uv run python -m database.init_db
```

### Useful Commands
```powershell
# Rebuild and start
docker compose up --build -d

# Check status
docker compose ps

# Follow backend logs
docker compose logs -f backend

# Access database
docker exec -it shared-postgres psql -U postgres -d inbox-manager-production

# Test container communication
docker compose exec backend curl http://shared-n8n:5678/healthz
```

---

## Summary: Key Principles

1. **Containers communicate via container names, not localhost**
2. **Running container ≠ database exists** - create databases explicitly
3. **Host ports (5679) ≠ Container ports (5678)** - use container ports for inter-container communication
4. **Override only what changes** - keep secrets in .env files
5. **FastAPI needs uvicorn** - not python -m
6. **Docker warnings aren't application errors** - verify with logs

---

## Current Status ✅

- **Frontend:** Running on `http://localhost:5173`
- **Backend API:** Running on `http://localhost:8000`
- **Database:** Created with all tables
- **Services:** Backend can communicate with PostgreSQL, n8n, and Langfuse via container names
- **n8n:** Accessible at `http://localhost:5679` (host) and `http://shared-n8n:5678` (containers)