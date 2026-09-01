"""Add local-only personalization/print support to generated care worksheets."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARE_DIR = ROOT / "care"
SCRIPT = '<script src="/assets/care-personalization-print1.js" defer></script>'
OLD_CARE_STYLE = '/styles/care.css?v=20260901-pawphoto1'
NEW_CARE_STYLE = '/styles/care.css?v=20260901-printphoto1'


def main() -> int:
    pages = sorted(CARE_DIR.glob("*.html"))
    if not pages:
        raise RuntimeError("No generated care worksheets found")

    updated = 0
    for path in pages:
        html = path.read_text(encoding="utf-8")
        if OLD_CARE_STYLE in html:
            html = html.replace(OLD_CARE_STYLE, NEW_CARE_STYLE)
        if SCRIPT not in html:
            if "</head>" not in html:
                raise RuntimeError(f"Missing </head> in {path}")
            html = html.replace("</head>", f"  {SCRIPT}\n</head>", 1)
        path.write_text(html, encoding="utf-8")
        updated += 1

    print(f"Enhanced {len(pages)} accessible care worksheets for local photo/name printing ({updated} updated)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
