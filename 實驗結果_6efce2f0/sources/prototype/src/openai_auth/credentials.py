"""Load and refresh Sign in with ChatGPT OAuth credentials."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import tempfile
import threading
import time
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_OAUTH_CREDENTIAL_FILE = (
    Path.home() / ".config" / "scar" / "openai-chatgpt.json"
)
TOKEN_ENDPOINT = "https://auth.openai.com/api/accounts/oauth/token"
RESOURCE = "https://api.openai.com/v1"
DEFAULT_REFRESH_SKEW_SECONDS = 5 * 60
CHATGPT_DIRECT_SCOPE = "chatgpt.tokens.use.direct"


logger = logging.getLogger("oauth")


class OAuthCredentialError(ValueError):
    """Raised when OAuth credentials cannot be loaded or refreshed."""


@dataclass(frozen=True)
class OAuthCredentialRecord:
    """Persisted OAuth credentials and non-secret metadata."""

    client_id: str
    access_token: str
    refresh_token: str
    expires_at: float
    scopes: tuple[str, ...] = ()
    ext_agent_host_id: str | None = None
    id_token: str | None = None
    issuer: str | None = None
    subject: str | None = None
    email: str | None = None

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "OAuthCredentialRecord":
        client_id = _required_string(payload, "client_id")
        access_token = _required_string(payload, "access_token")
        refresh_token = _required_string(payload, "refresh_token")
        expires_at = _expires_at(payload)
        scopes = _scopes(payload.get("scopes", payload.get("scope", ())))
        return cls(
            client_id=client_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            scopes=scopes,
            ext_agent_host_id=_optional_string(payload.get("ext_agent_host_id")),
            id_token=_optional_string(payload.get("id_token")),
            issuer=_optional_string(payload.get("issuer")),
            subject=_optional_string(payload.get("subject")),
            email=_optional_string(payload.get("email")),
        )

    def to_mapping(self) -> dict[str, Any]:
        """Return a JSON-safe representation without derived secret output."""

        return {
            "client_id": self.client_id,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at,
            "scopes": list(self.scopes),
            "ext_agent_host_id": self.ext_agent_host_id,
            "id_token": self.id_token,
            "issuer": self.issuer,
            "subject": self.subject,
            "email": self.email,
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }


RefreshRequester = Callable[[OAuthCredentialRecord], Mapping[str, Any]]


class OAuthCredentialManager:
    """Provide one current access token and serialize refresh operations.

    The manager is intended to be shared by all judge threads in one process.
    It refreshes only when the token is within ``refresh_skew_seconds`` of
    expiry and atomically replaces the persisted access/refresh-token pair.
    """

    def __init__(
        self,
        path: str | Path = DEFAULT_OAUTH_CREDENTIAL_FILE,
        *,
        refresh_skew_seconds: int = DEFAULT_REFRESH_SKEW_SECONDS,
        clock: Callable[[], float] = time.time,
        refresh_requester: RefreshRequester | None = None,
    ) -> None:
        if refresh_skew_seconds < 0:
            raise ValueError("refresh_skew_seconds must not be negative")
        self.path = Path(path).expanduser()
        self.refresh_skew_seconds = refresh_skew_seconds
        self._clock = clock
        self._refresh_requester = refresh_requester or _refresh_with_openai
        self._refresh_lock = threading.Lock()

    def get_valid_access_token(self) -> str:
        """Return an access token, refreshing the persisted pair when needed."""

        record = self._load()
        self._validate_plan_scope(record)
        remaining_seconds = record.expires_at - self._clock()
        if self._is_valid(record):
            logger.debug(
                "credential check: valid, expires_in=%ds",
                max(0, int(remaining_seconds)),
            )
            return record.access_token

        logger.info(
            "credential check: %s, expires_in=%ds",
            "expired" if remaining_seconds <= 0 else "expiring_soon",
            max(0, int(remaining_seconds)),
        )

        with self._refresh_lock:
            # Another thread may have refreshed while this thread waited.
            record = self._load()
            self._validate_plan_scope(record)
            if self._is_valid(record):
                logger.debug("refresh skipped: another thread refreshed the credential")
                return record.access_token
            logger.info("token refresh started")
            refreshed = self._refresh_requester(record)
            updated = _updated_record(record, refreshed, now=self._clock())
            self._save(updated)
            logger.info("token refresh completed; credential pair persisted")
            return updated.access_token

    def load_record(self) -> OAuthCredentialRecord:
        """Load the current record for diagnostics and login tooling."""

        return self._load()

    def save_record(self, record: OAuthCredentialRecord) -> None:
        """Atomically persist a validated credential record."""

        self._save(record)

    @staticmethod
    def _validate_plan_scope(record: OAuthCredentialRecord) -> None:
        if CHATGPT_DIRECT_SCOPE not in record.scopes:
            raise OAuthCredentialError(
                "OAuth credential is missing the ChatGPT plan scope "
                f"{CHATGPT_DIRECT_SCOPE!r}; sign in again with plan usage enabled"
            )

    def _is_valid(self, record: OAuthCredentialRecord) -> bool:
        return record.expires_at > self._clock() + self.refresh_skew_seconds

    def _load(self) -> OAuthCredentialRecord:
        if not self.path.exists():
            raise OAuthCredentialError(
                "OAuth credential file does not exist: "
                f"{self.path}. Run the ChatGPT OAuth login flow first."
            )
        try:
            mode = self.path.stat().st_mode
            if mode & 0o077:
                raise OAuthCredentialError(
                    f"OAuth credential file must be owner-only (0600): {self.path}"
                )
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except OAuthCredentialError:
            raise
        except (OSError, json.JSONDecodeError) as exc:
            raise OAuthCredentialError(
                f"cannot read OAuth credential file: {self.path}"
            ) from exc
        if not isinstance(payload, Mapping):
            raise OAuthCredentialError("OAuth credential file must contain a JSON object")
        try:
            return OAuthCredentialRecord.from_mapping(payload)
        except (TypeError, ValueError) as exc:
            raise OAuthCredentialError("OAuth credential file has an invalid schema") from exc

    def _save(self, record: OAuthCredentialRecord) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temporary_path = Path(handle.name)
                os.chmod(handle.fileno(), 0o600)
                json.dump(record.to_mapping(), handle, ensure_ascii=False, indent=2)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, self.path)
            os.chmod(self.path, 0o600)
        except OSError as exc:
            raise OAuthCredentialError(
                f"cannot atomically save OAuth credential file: {self.path}"
            ) from exc
        finally:
            if temporary_path is not None and temporary_path.exists():
                try:
                    temporary_path.unlink()
                except OSError:
                    pass


def _refresh_with_openai(record: OAuthCredentialRecord) -> Mapping[str, Any]:
    form = urlencode(
        {
            "grant_type": "refresh_token",
            "client_id": record.client_id,
            "refresh_token": record.refresh_token,
            "resource": RESOURCE,
        }
    ).encode("ascii")
    request = Request(
        TOKEN_ENDPOINT,
        data=form,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise OAuthCredentialError(
            f"OAuth token refresh failed with HTTP {exc.code}"
        ) from exc
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise OAuthCredentialError("OAuth token refresh request failed") from exc
    if not isinstance(payload, Mapping):
        raise OAuthCredentialError("OAuth token refresh returned an invalid response")
    return payload


def _updated_record(
    old: OAuthCredentialRecord,
    payload: Mapping[str, Any],
    *,
    now: float,
) -> OAuthCredentialRecord:
    access_token = _required_string(payload, "access_token")
    refresh_token = _optional_string(payload.get("refresh_token")) or old.refresh_token
    expires_in = payload.get("expires_in")
    if isinstance(expires_in, bool) or not isinstance(expires_in, (int, float)):
        raise OAuthCredentialError("OAuth token refresh did not return expires_in")
    if expires_in <= 0:
        raise OAuthCredentialError("OAuth token refresh returned an invalid expires_in")
    scopes = _scopes(payload.get("scope", old.scopes))
    return OAuthCredentialRecord(
        client_id=_optional_string(payload.get("client_id")) or old.client_id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=now + float(expires_in),
        scopes=scopes or old.scopes,
        ext_agent_host_id=old.ext_agent_host_id,
        id_token=old.id_token,
        issuer=old.issuer,
        subject=old.subject,
        email=old.email,
    )


def _required_string(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise OAuthCredentialError(f"OAuth credential field {key!r} is required")
    return value


def _optional_string(value: Any) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def _expires_at(payload: Mapping[str, Any]) -> float:
    value = payload.get("expires_at")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value > 0:
            return float(value)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
        except ValueError:
            pass
    raise OAuthCredentialError("OAuth credential field 'expires_at' is required")


def _scopes(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return tuple(item for item in value.split() if item)
    if isinstance(value, (list, tuple)) and all(isinstance(item, str) for item in value):
        return tuple(item for item in value if item)
    if value in (None, ()):
        return ()
    raise OAuthCredentialError("OAuth credential scopes must be a string or list")
