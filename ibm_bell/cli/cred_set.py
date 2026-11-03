"""CLI for securely storing an IBM Quantum token in Windows Credential Manager.

The script prompts the user for the token using hidden input (``getpass``) and
stores it via :func:`ibm_bell.cred_manager.store_token`.  No token is echoed to
stdout or written to any file.
"""

import getpass
import sys

from ibm_bell.cred_manager import retrieve_token, store_token


def main() -> None:
    """Store the IBM Quantum token if not already present.

    * If a token is already stored, the script prints a notice and exits with
      status 0.
    * Otherwise it prompts for the token (hidden), saves it, and confirms.
    """
    if retrieve_token():
        print("IBM Quantum token already stored in Credential Manager.")
        sys.exit(0)

    token = getpass.getpass("Enter IBM Quantum token (input hidden): ")
    if not token:
        print("No token entered – aborting.")
        sys.exit(1)
    # Store securely
    store_token(token)
    print("Token stored successfully in Credential Manager.")
    sys.exit(0)

if __name__ == "__main__":
    main()
