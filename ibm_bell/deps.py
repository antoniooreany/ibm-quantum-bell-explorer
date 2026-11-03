import subprocess
import sys
from typing import List


def install(packages: List[str]):
    """Idempotent installer used in notebooks and package import time.
    Installs missing packages via pip. Raises RuntimeError if installation fails.
    """
    for pkg in packages:
        try:
            __import__(pkg.replace('-', '_'))
        except ImportError:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', pkg])
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Failed to install package {pkg}: {e}")
