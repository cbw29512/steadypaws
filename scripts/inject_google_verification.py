"""Inject Google Search Console verification into the generated homepage."""

from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


def main() -> int:
    token = os.environ.get("GOOGLE_SITE_VERIFICATION", "").strip()
    if not token:
        print("Google site verification token not configured; skipping injection.")
        return 0

    if not re.fullmatch(r"[A-Za-z0-9_-]+", token):
        raise RuntimeError("GOOGLE_SITE_VERIFICATION contains unsupported characters")

    html = INDEX.read_text(encoding="utf-8")
    meta = f'<meta name="google-site-verification" content="{token}">'
    pattern = re.compile(r'<meta\s+name=["\']google-site-verification["\'][^>]*>', re.I)

    if pattern.search(html):
        html = pattern.sub(meta, html, count=1)
    elif "</head>" in html:
        html = html.replace("</head>", f"  {meta}\n</head>", 1)
    else:
        raise RuntimeError("Generated index.html is missing </head>")

    INDEX.write_text(html, encoding="utf-8")
    print("Injected Google Search Console verification meta tag.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
