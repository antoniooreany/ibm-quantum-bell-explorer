# cred_manager.py
"""Credential manager utilities for IBM Quantum token.

Uses the cross‑platform ``keyring`` library, which on Windows stores the
secret in Windows Credential Manager. The token is never printed to stdout
or written to a file.
"""

from typing import Optional

import keyring

SERVICE_NAME = "IBM_QUANTUM"
ACCOUNT_NAME = "token"


def store_token(token: str) -> None:
    """Save *token* in Credential Manager.

    The token is stored under ``SERVICE_NAME`` / ``ACCOUNT_NAME``.
    ``keyring.set_password`` raises ``keyring.errors.PasswordSetError`` on
    failure; we let the exception propagate so the caller can handle it.
    """
    # ``keyring`` expects a plain string; we store the raw token.
    keyring.set_password(SERVICE_NAME, ACCOUNT_NAME, token)


def retrieve_token() -> Optional[str]:
    """Return the stored token or ``None`` if not present.

    The token may have been saved under the legacy name
    ``IBM_QUANTUM_TOKEN``/``IBM_QUANTUM_TOKEN`` (used by the provided PowerShell
    script) or under the newer ``IBM_QUANTUM``/``token`` identifiers.  We try both
    and return the first non‑empty result.
    """
    # New naming
    token = keyring.get_password(SERVICE_NAME, ACCOUNT_NAME)
    if token:
        return token
    # Legacy naming used by the existing ``store_ibm_token.ps1`` script
    legacy_token = keyring.get_password("IBM_QUANTUM_TOKEN", "IBM_QUANTUM_TOKEN")
    return legacy_token
