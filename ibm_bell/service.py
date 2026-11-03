"""Service utilities for IBM Quantum integration.

Provides a helper to obtain an authenticated ``QiskitRuntimeService`` instance.
Token resolution order:

1. Environment variable ``IBM_QUANTUM_TOKEN``.
2. Colab ``userdata`` (if running in a Colab environment).
3. Windows Credential Manager via ``keyring`` (through ``cred_manager``).

The function attempts to reuse an existing saved account; if none exists it
stores the token securely and creates a new service instance.
"""

import os
from typing import Optional

# Optional import for Colab userdata; ignored when not in Colab environment
try:
    from google.colab import userdata  # type: ignore
except Exception:
    userdata = None  # type: ignore

# Import the runtime service from Qiskit IBM Runtime package
from qiskit_ibm_runtime import QiskitRuntimeService

def get_service() -> QiskitRuntimeService:
    """Return an authenticated ``QiskitRuntimeService``.

    The function follows the token resolution order described in the module
    docstring. If a saved account is already present, ``QiskitRuntimeService``
    will reuse it; otherwise the provided token is saved and a new service is
    instantiated.
    """
    # 1. Environment variable
    token: Optional[str] = os.getenv("IBM_QUANTUM_TOKEN")

    # 2. Colab userdata (optional)
    if not token and userdata is not None:
        token = userdata.get("IBM_QUANTUM_TOKEN")  # type: ignore[attr-defined]

    # 3. Credential Manager via our helper
    if not token:
        try:
            from .cred_manager import retrieve_token
            token = retrieve_token()
        except Exception:
            token = None

    # Attempt to obtain a service using any saved account
    try:
        return QiskitRuntimeService()
    except Exception:
        # No saved account or authentication failed – ensure we have a token
        if not token:
            raise RuntimeError(
                "IBM_QUANTUM_TOKEN not found in environment, Colab userdata, or Credential Manager"
            )
        # Save the token securely and create a new service instance
        QiskitRuntimeService.save_account(
            token=token.strip(),
            channel="ibm_quantum_platform",
            overwrite=True,
        )
        return QiskitRuntimeService()
