"""OpenAI client construction for API-key and ChatGPT OAuth modes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from openai import OpenAI

from .credentials import (
    DEFAULT_OAUTH_CREDENTIAL_FILE,
    OAuthCredentialManager,
)


AuthMode = Literal["oauth", "api-key"]
DEFAULT_AUTH_MODE: AuthMode = "oauth"


@dataclass(frozen=True)
class OpenAIClientProvider:
    """Lazily construct and cache the client for the selected auth mode."""

    auth_mode: AuthMode = DEFAULT_AUTH_MODE
    oauth_credential_file: str | None = None
    manager: OAuthCredentialManager | None = None
    max_retries: int = 0

    def __post_init__(self) -> None:
        if self.auth_mode not in ("oauth", "api-key"):
            raise ValueError(f"unsupported OpenAI auth mode: {self.auth_mode!r}")
        object.__setattr__(self, "_client", None)
        object.__setattr__(self, "_last_token", None)
        if self.auth_mode == "oauth" and self.manager is None:
            object.__setattr__(
                self,
                "manager",
                OAuthCredentialManager(
                    self.oauth_credential_file or DEFAULT_OAUTH_CREDENTIAL_FILE
                ),
            )

    def get_client(self) -> OpenAI:
        """Return a client using the current credential."""

        # Keep credential/login imports usable in environments that only run
        # the OAuth bootstrap. The SDK is needed only when judge inference
        # actually constructs an OpenAI client.
        from openai import OpenAI

        if self.auth_mode == "api-key":
            client = getattr(self, "_client")
            if client is None:
                client = OpenAI(max_retries=self.max_retries)
                object.__setattr__(self, "_client", client)
            return client

        assert self.manager is not None
        token = self.manager.get_valid_access_token()
        client = getattr(self, "_client")
        if client is None or getattr(self, "_last_token") != token:
            client = OpenAI(
                api_key=token,
                base_url="https://api.openai.com/v1",
                max_retries=self.max_retries,
            )
            object.__setattr__(self, "_client", client)
            object.__setattr__(self, "_last_token", token)
        return client
