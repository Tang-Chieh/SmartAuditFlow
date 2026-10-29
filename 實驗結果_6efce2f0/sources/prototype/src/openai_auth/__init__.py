"""Authentication helpers for OpenAI API and ChatGPT plan credentials."""

from .client import (
    DEFAULT_AUTH_MODE,
    AuthMode,
    OpenAIClientProvider,
)
from .login import login_with_chatgpt
from .credentials import (
    DEFAULT_OAUTH_CREDENTIAL_FILE,
    CHATGPT_DIRECT_SCOPE,
    OAuthCredentialError,
    OAuthCredentialManager,
    OAuthCredentialRecord,
)

__all__ = [
    "AuthMode",
    "DEFAULT_AUTH_MODE",
    "DEFAULT_OAUTH_CREDENTIAL_FILE",
    "CHATGPT_DIRECT_SCOPE",
    "OAuthCredentialError",
    "OAuthCredentialManager",
    "OAuthCredentialRecord",
    "OpenAIClientProvider",
    "login_with_chatgpt",
]
