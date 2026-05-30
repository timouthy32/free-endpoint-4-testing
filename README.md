# free-endpoint-4-testing

A minimal **OAuth 2.0 Client Credentials + Request Inspector** API — think [httpbin.org](https://httpbin.org) but focused on auth testing.

Built with **FastAPI** + **Python 3.12**.

---

## Quick Start

### Local (Python)
```bash
pip install -r requirements.txt
uvicorn main:app --reload
# → http://localhost:8000/docs
```

### Docker
```bash
docker build -t fe4t .
docker run -p 8000:8000 fe4t
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
curl -X POST http://localhost:8000/oauth/token \
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
  "http://localhost:8000/inspect?foo=bar&baz=qux"

# POST with JSON body
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"hello": "world"}' \
  http://localhost:8000/inspect

# With path params
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/inspect/users/42/orders/7
```

**Response shape:**
```json
{
  "method": "POST",
  "url": "http://localhost:8000/inspect",
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

1. **Get token** → `POST /oauth/token` (form-data body)
2. **Inspect** → Any method to `/inspect`, set header `Authorization: Bearer {{ $json.access_token }}`

---

## Security Note

This is a **testing-only** service. Do **not** use these credentials in production.  
To add your own clients, edit the `CLIENTS` dict in `main.py`.
