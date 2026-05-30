import secrets
import time
from typing import Any

from fastapi import FastAPI, Request, Header, HTTPException, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# ── In-memory token store {token: expires_at} ──────────────────────────────
_tokens: dict[str, float] = {}
TOKEN_TTL = 3600  # seconds

# ── Allowed clients ─────────────────────────────────────────────────────────
CLIENTS: dict[str, str] = {
    "test_client": "super_secret",
    "demo_app":    "demo_password",
}

app = FastAPI(
    title="Free Endpoint 4 Testing",
    description="Minimal OAuth 2.0 Client Credentials + request inspector.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helper ───────────────────────────────────────────────────────────────────
def _verify_token(authorization: str = Header(...)):
    """Dependency: extract and validate Bearer token."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    exp = _tokens.get(token)
    if exp is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    if time.time() > exp:
        _tokens.pop(token, None)
        raise HTTPException(status_code=401, detail="Token expired")
    return token


# ── OAuth 2.0 – Client Credentials Grant ────────────────────────────────────
@app.post(
    "/oauth/token",
    summary="Get an access token",
    tags=["Auth"],
    response_description="Bearer access token (expires in 3600 s)",
)
async def token(
    grant_type: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...),
):
    """
    **OAuth 2.0 Client Credentials Grant**

    | Field | Value |
    |---|---|
    | `grant_type` | `client_credentials` |
    | `client_id` | `test_client` or `demo_app` |
    | `client_secret` | `super_secret` or `demo_password` |

    Returns a random opaque Bearer token valid for **1 hour**.
    """
    if grant_type != "client_credentials":
        raise HTTPException(status_code=400, detail="unsupported_grant_type")
    expected = CLIENTS.get(client_id)
    if expected is None or expected != client_secret:
        raise HTTPException(status_code=401, detail="invalid_client")

    token_value = secrets.token_urlsafe(32)
    _tokens[token_value] = time.time() + TOKEN_TTL

    return {
        "access_token": token_value,
        "token_type": "Bearer",
        "expires_in": TOKEN_TTL,
    }


# ── Request Inspector ────────────────────────────────────────────────────────
async def _inspect(request: Request, _token: str = Depends(_verify_token)) -> dict[str, Any]:
    """Shared logic for all /inspect routes."""
    # Safe headers dict (lower-cased keys, skip the Authorization value)
    headers = {k: v for k, v in request.headers.items() if k.lower() != "authorization"}

    # Body — try JSON first, then raw text
    body_raw = await request.body()
    try:
        body = await request.json()
    except Exception:
        body = body_raw.decode("utf-8", errors="replace") or None

    return {
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "path_params": dict(request.path_params),
        "query_params": dict(request.query_params),
        "headers": headers,
        "body": body,
        "client": request.client.host if request.client else None,
    }


@app.get("/inspect", summary="Inspect a GET request", tags=["Inspector"])
@app.post("/inspect", summary="Inspect a POST request", tags=["Inspector"])
@app.put("/inspect", summary="Inspect a PUT request", tags=["Inspector"])
@app.patch("/inspect", summary="Inspect a PATCH request", tags=["Inspector"])
@app.delete("/inspect", summary="Inspect a DELETE request", tags=["Inspector"])
async def inspect(request: Request, _token: str = Depends(_verify_token)):
    """
    **Echo back everything in the request** — headers, query params, body (JSON or text).

    Requires a valid `Authorization: Bearer <token>` header.
    """
    return await _inspect(request, _token)


@app.api_route(
    "/inspect/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    summary="Inspect any path",
    tags=["Inspector"],
)
async def inspect_path(path: str, request: Request, _token: str = Depends(_verify_token)):
    """Same as `/inspect` but captures any **path parameters** you append."""
    return await _inspect(request, _token)


# ── Health ───────────────────────────────────────────────────────────────────
@app.get("/health", tags=["Utility"], summary="Health check")
async def health():
    return {"status": "ok", "active_tokens": len(_tokens)}


# ── Landing page ──────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    return HTMLResponse(status_code=302, headers={"Location": "/docs"})
