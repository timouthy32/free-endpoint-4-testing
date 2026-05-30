# free-endpoint-4-testing

A minimal **OAuth 2.0 Client Credentials + Request Inspector** API — think [httpbin.org](https://httpbin.org) but focused on auth testing.

Built with **FastAPI** + **Python 3.12**.

---

## 🚀 Quick Start

### Option 1 — Docker Compose (recommended, no Python needed)

> **Requirements:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows / macOS) or Docker Engine + Compose plugin (Linux).

**1. Clone the repository**
```bash
git clone https://github.com/timouthy32/free-endpoint-4-testing.git
cd free-endpoint-4-testing
```

**2. Start the service**
```bash
docker compose up -d
```

The API is now running at **http://localhost:8085**

**3. Open the interactive docs**

Visit → [http://localhost:8085/docs](http://localhost:8085/docs)

**4. Stop the service**
```bash
docker compose down
```

**5. View logs**
```bash
docker compose logs -f
```

**6. Rebuild after code changes**
```bash
docker compose up -d --build
```

---

### Option 2 — Local Python

> **Requirements:** Python 3.12+

```bash
git clone https://github.com/timouthy32/free-endpoint-4-testing.git
cd free-endpoint-4-testing
pip install -r requirements.txt
uvicorn main:app --reload --port 8085
# → http://localhost:8085/docs
```

---

## Endpoints

| Method | Path | Auth required | Description |
|--------|------|---------------|-------------|
| `POST` | `/oauth/token` | ❌ | Get a Bearer token |
| `GET/POST/PUT/PATCH/DELETE` | `/inspect` | ✅ | Echo request back |
| `GET/POST/PUT/PATCH/DELETE` | `/inspect/{path}` | ✅ | Echo with path params |
| `GET` | `/health` | ❌ | Health check |
| `GET` | `/docs` | ❌ | Swagger UI |
| `GET` | `/redoc` | ❌ | ReDoc UI |

---

## Step 1 — Get a Token

```bash
curl -X POST http://localhost:8085/oauth/token \
  -d "grant_type=client_credentials" \
  -d "client_id=test_client" \
  -d "client_secret=super_secret"
```

**Response:**
```json
{
  "access_token": "abc123...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### Pre-configured clients

| `client_id` | `client_secret` |
|-------------|------------------|
| `test_client` | `super_secret` |
| `demo_app` | `demo_password` |

---

## Step 2 — Inspect a Request

```bash
TOKEN="abc123..."

# GET with query params
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8085/inspect?foo=bar&baz=qux"

# POST with JSON body
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"hello": "world"}' \
  http://localhost:8085/inspect

# With path params
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8085/inspect/users/42/orders/7
```

**Response shape:**
```json
{
  "method": "POST",
  "url": "http://localhost:8085/inspect",
  "path": "/inspect",
  "path_params": {},
  "query_params": {},
  "headers": { "content-type": "application/json", "...": "..." },
  "body": { "hello": "world" },
  "client": "127.0.0.1"
}
```

---

## n8n Integration

Use the **HTTP Request** node twice:

1. **Get token** → `POST http://<host>:8085/oauth/token` with form-data body
2. **Inspect** → Any method to `http://<host>:8085/inspect`, set header `Authorization: Bearer {{ $json.access_token }}`

> If n8n runs in Docker on the same machine, replace `localhost` with your host machine IP or use `host.docker.internal` (Docker Desktop).

---

## Security Note

This is a **testing-only** service. Do **not** expose port 8085 publicly or use these credentials in production.  
To add your own clients, edit the `CLIENTS` dict in `main.py` and rebuild with `docker compose up -d --build`.
