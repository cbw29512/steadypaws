"""Fetch pinned browser vendor assets at build time and verify their exact bytes."""

from __future__ import annotations

import base64
import hashlib
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
VENDOR_DIR = ROOT / "assets" / "vendor"
PDF_LIB_URL = "https://cdn.jsdelivr.net/npm/pdf-lib@1.17.1/dist/pdf-lib.min.js"
PDF_LIB_SHA512 = "z8IYLHO8bTgFqj+yrPyIJnzBDf7DDhWwiEsk4sY+Oe6J2M+WQequeGS7qioI5vT6rXgVRb4K1UVQC5ER7MKzKQ=="
PDF_LIB_PATH = VENDOR_DIR / "pdf-lib-1.17.1.min.js"


def main() -> int:
    VENDOR_DIR.mkdir(parents=True, exist_ok=True)
    request = Request(PDF_LIB_URL, headers={"User-Agent": "Steady-Paws-build/1.0"})
    with urlopen(request, timeout=30) as response:  # noqa: S310 - pinned HTTPS asset with digest verification
        data = response.read()

    digest = base64.b64encode(hashlib.sha512(data).digest()).decode("ascii")
    if digest != PDF_LIB_SHA512:
        raise RuntimeError("Pinned pdf-lib asset failed SHA-512 verification")

    PDF_LIB_PATH.write_bytes(data)
    print(f"Verified vendor asset: {PDF_LIB_PATH.relative_to(ROOT)} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
