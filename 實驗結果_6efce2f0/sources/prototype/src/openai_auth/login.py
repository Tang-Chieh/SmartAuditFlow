"""Interactive Sign in with ChatGPT bootstrap for local SCAR runs."""

from __future__ import annotations

from dataclasses import dataclass
import base64
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import queue
from pathlib import Path
import secrets
import threading
import time
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen
import webbrowser
import uuid

from .credentials import (
    CHATGPT_DIRECT_SCOPE,
    DEFAULT_OAUTH_CREDENTIAL_FILE,
    OAuthCredentialError,
    OAuthCredentialManager,
    OAuthCredentialRecord,
)


AUTHORIZATION_ENDPOINT = "https://auth.openai.com/api/accounts/authorize"
TOKEN_ENDPOINT = "https://auth.openai.com/api/accounts/oauth/token"
ISSUER = "https://auth.openai.com"
JWKS_URI = f"{ISSUER}/.well-known/jwks.json"
RESOURCE = "https://api.openai.com/v1"
CALLBACK_PATH = "/auth/callback"
DEFAULT_AGENT_NAME = "llm-judge"
HOST_ID_FILENAME = ".ext-agent-host-id"
OAUTH_SCOPES = (
    "openid",
    "profile",
    "email",
    "offline_access",
    "resource.invoke",
    CHATGPT_DIRECT_SCOPE,
)


@dataclass(frozen=True)
class _CallbackResult:
    query: Mapping[str, list[str]]


class _CallbackHandler(BaseHTTPRequestHandler):
    result_queue: "queue.Queue[_CallbackResult]"

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query, keep_blank_values=True)
        self.result_queue.put(_CallbackResult(query=query))
        body = b"SCAR OAuth sign-in received. You can close this browser tab."
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format: str, *_args: Any) -> None:
        return


def login_with_chatgpt(
    path: str | Path = DEFAULT_OAUTH_CREDENTIAL_FILE,
    *,
    agent_name: str = DEFAULT_AGENT_NAME,
    timeout_seconds: int = 600,
) -> OAuthCredentialRecord:
    """Complete the public OAuth + PKCE flow and save a credential record."""

    credential_path = Path(path).expanduser()
    manager = OAuthCredentialManager(credential_path)
    existing = _optional_existing_record(manager)
    host_id = _load_or_create_host_id(credential_path)
    client_id = existing.client_id if existing else "dynamic_agent_client"
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    verifier = secrets.token_urlsafe(64)
    challenge = _base64url(hashlib.sha256(verifier.encode("ascii")).digest())

    server = HTTPServer(("127.0.0.1", 0), _CallbackHandler)
    callback_path = CALLBACK_PATH
    redirect_uri = f"http://127.0.0.1:{server.server_port}{callback_path}"
    callback_queue: "queue.Queue[_CallbackResult]" = queue.Queue(maxsize=1)
    _CallbackHandler.result_queue = callback_queue
    server.timeout = timeout_seconds
    listener = threading.Thread(target=server.handle_request, daemon=True)
    listener.start()

    params = {
        "client_id": client_id,
        "ext_agent_host_id": host_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": " ".join(OAUTH_SCOPES),
        "resource": RESOURCE,
        "state": state,
        "nonce": nonce,
        "code_challenge_method": "S256",
        "code_challenge": challenge,
    }
    if existing is None:
        params["agent_name_hint"] = agent_name
    elif existing.id_token:
        params["id_token_hint"] = existing.id_token
    authorization_url = f"{AUTHORIZATION_ENDPOINT}?{urlencode(params)}"
    print(f"OpenAI OAuth URL: {authorization_url}")
    webbrowser.open(authorization_url)
    listener.join(timeout_seconds + 5)
    server.server_close()
    try:
        callback = callback_queue.get_nowait()
    except queue.Empty as exc:
        raise OAuthCredentialError("OAuth callback timed out") from exc

    returned_state = _one(callback.query, "state")
    if not secrets.compare_digest(returned_state or "", state):
        raise OAuthCredentialError("OAuth callback state validation failed")
    error = _one(callback.query, "error")
    if error:
        description = _one(callback.query, "error_description") or error
        raise OAuthCredentialError(f"OAuth authorization failed: {description}")
    code = _one(callback.query, "code")
    issued_client_id = _one(callback.query, "client_id")
    if client_id == "dynamic_agent_client":
        if not issued_client_id or issued_client_id == client_id:
            raise OAuthCredentialError("OAuth registration did not return an issued client_id")
        client_id = issued_client_id
    elif issued_client_id and issued_client_id != client_id:
        raise OAuthCredentialError("OAuth callback returned an unexpected client_id")
    if not code:
        raise OAuthCredentialError("OAuth callback did not contain an authorization code")

    token_payload = _exchange_code(
        client_id=client_id,
        code=code,
        verifier=verifier,
        redirect_uri=redirect_uri,
    )
    scopes = _parse_scopes(token_payload.get("scope"))
    if CHATGPT_DIRECT_SCOPE not in scopes:
        raise OAuthCredentialError(
            f"OAuth grant is missing required scope {CHATGPT_DIRECT_SCOPE!r}"
        )
    access_token = _required_string(token_payload, "access_token")
    refresh_token = _required_string(token_payload, "refresh_token")
    id_token = _required_string(token_payload, "id_token")
    expires_in = token_payload.get("expires_in")
    if isinstance(expires_in, bool) or not isinstance(expires_in, (int, float)) or expires_in <= 0:
        raise OAuthCredentialError("OAuth token response has an invalid expires_in")
    claims = _validate_id_token(id_token, client_id=client_id, nonce=nonce)
    if existing and existing.subject and claims["sub"] != existing.subject:
        raise OAuthCredentialError("OAuth identity changed during reauthorization")

    record = OAuthCredentialRecord(
        client_id=client_id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=time.time() + float(expires_in),
        scopes=tuple(sorted(scopes)),
        ext_agent_host_id=host_id,
        id_token=id_token,
        issuer=claims["iss"],
        subject=claims["sub"],
        email=claims.get("email"),
    )
    manager.save_record(record)
    print(f"Saved OAuth credential for {record.email or record.subject or 'ChatGPT account'}")
    return record


def _exchange_code(*, client_id: str, code: str, verifier: str, redirect_uri: str) -> Mapping[str, Any]:
    payload = urlencode(
        {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "code": code,
            "code_verifier": verifier,
            "redirect_uri": redirect_uri,
            "resource": RESOURCE,
        }
    ).encode("ascii")
    request = Request(
        TOKEN_ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise OAuthCredentialError(f"OAuth code exchange failed with HTTP {exc.code}") from exc
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise OAuthCredentialError("OAuth code exchange request failed") from exc
    if not isinstance(result, Mapping):
        raise OAuthCredentialError("OAuth code exchange returned an invalid response")
    return result


def _validate_id_token(id_token: str, *, client_id: str, nonce: str) -> dict[str, Any]:
    try:
        import jwt
        from jwt import PyJWKClient
    except ImportError as exc:
        raise OAuthCredentialError(
            "PyJWT with cryptography is required for OAuth ID-token validation"
        ) from exc
    try:
        signing_key = PyJWKClient(JWKS_URI).get_signing_key_from_jwt(id_token).key
        claims = jwt.decode(
            id_token,
            signing_key,
            algorithms=["RS256"],
            audience=client_id,
            issuer=ISSUER,
            options={"require": ["iss", "aud", "exp", "iat", "nonce", "sub"]},
        )
    except Exception as exc:
        raise OAuthCredentialError("OAuth ID-token validation failed") from exc
    if claims.get("nonce") != nonce:
        raise OAuthCredentialError("OAuth ID-token nonce validation failed")
    if not isinstance(claims.get("sub"), str) or not claims["sub"]:
        raise OAuthCredentialError("OAuth ID-token subject is missing")
    return claims


def _load_or_create_host_id(path: Path) -> str:
    host_path = path.with_name(HOST_ID_FILENAME)
    if host_path.exists():
        value = host_path.read_text(encoding="utf-8").strip()
        if value:
            return value
    host_path.parent.mkdir(parents=True, exist_ok=True)
    value = f"urn:uuid:{uuid.uuid4()}"
    temporary = host_path.with_name(f".{host_path.name}.tmp")
    temporary.write_text(value + "\n", encoding="utf-8")
    temporary.chmod(0o600)
    temporary.replace(host_path)
    host_path.chmod(0o600)
    return value


def _optional_existing_record(manager: OAuthCredentialManager) -> OAuthCredentialRecord | None:
    try:
        return manager.load_record()
    except OAuthCredentialError:
        return None


def _required_string(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise OAuthCredentialError(f"OAuth token response field {key!r} is required")
    return value


def _parse_scopes(value: Any) -> set[str]:
    if isinstance(value, str):
        return {item for item in value.split() if item}
    raise OAuthCredentialError("OAuth token response did not contain granted scopes")


def _one(query: Mapping[str, list[str]], key: str) -> str | None:
    values = query.get(key, [])
    return values[0] if values else None


def _base64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")
