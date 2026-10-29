"""Logging setup shared by benchmark Evaluation entry points."""

from __future__ import annotations

import logging
import os


DEFAULT_LOG_LEVEL = "INFO"


def configure_logging(level: str | None = None) -> None:
    """Configure concise stderr logging for command-line workflows.

    Library callers remain responsible for configuring logging themselves. CLI
    entry points use this helper so stdout stays machine-readable while
    workflow diagnostics are emitted to stderr.
    """

    level_name = (level or os.environ.get("SCAR_LOG_LEVEL", DEFAULT_LOG_LEVEL)).upper()
    numeric_level = getattr(logging, level_name, None)
    if not isinstance(numeric_level, int):
        raise ValueError(
            f"unsupported SCAR_LOG_LEVEL {level_name!r}; "
            "use DEBUG, INFO, WARNING, ERROR, or CRITICAL"
        )
    logging.basicConfig(
        level=numeric_level,
        format="[%(name)s] %(message)s",
    )
    transport_level = logging.INFO if numeric_level == logging.DEBUG else logging.WARNING
    for logger_name in ("httpx", "httpcore"):
        logging.getLogger(logger_name).setLevel(transport_level)


__all__ = ["DEFAULT_LOG_LEVEL", "configure_logging"]
