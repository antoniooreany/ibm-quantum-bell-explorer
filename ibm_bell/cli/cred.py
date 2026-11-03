"""CLI for accessing the IBM Quantum token stored in Windows Credential Manager.

If the token is already saved, the script reports that and exits.
If no token is found, it advises the user to set the environment variable
`IBM_QUANTUM_TOKEN` or use a custom script to store it. (We keep it minimal to avoid prompting when the token already exists.)
"""
import sys

from ibm_bell.cred_manager import retrieve_token


def main() -> None:
    """Check Credential Manager for an IBM Quantum token.

    - If a token is present → print a notice and exit with status 0.
    - If absent → print guidance and exit with status 1.
    """
    if retrieve_token():
        print("IBM Quantum token already stored in Credential Manager.")
        sys.exit(0)
    print(
        "IBM Quantum token not found in Credential Manager.\n"
        "Set the token via the environment variable IBM_QUANTUM_TOKEN "
        "or use a custom script to store it."
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
