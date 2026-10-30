"""Read-only release checks for the canonical domain and Netlify probe blocking.

The generated site, rather than the templates alone, is the verification target.
This script runs after the existing build commands in GitHub Actions.
"""
from __future__ import annotations

import logging
import subprocess
import sys
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://yourpetshealthlog.com"
OLD_HOST = "yourpetshealthlog.netlify.app"
LOGGER = logging.getLogger("security-audit")

BLOCKED = {
    "/.env", "/.env.bak", "/.env.backup", "/.env.example",
    "/.env.development", "/.env.dev", "/.env.save",
    "/api/.env", "/app/.env", "/admin/.env", "/backend/.env",
    "/core/.env", "/server/.env", "/src/.env",
    "/.git/*", "/wp-admin/*", "/wp-login.php", "/xmlrpc.php",
    "/phpinfo.php",
}


def verify() -> None:
    """Reject mixed SEO origins, unsafe tracked paths, and missing CDN rules."""
    netlify = tomllib.loads((ROOT / "netlify.toml").read_text("utf-8"))
    redirects = {rule["from"]: rule for rule in netlify.get("redirects", [])}
    for route in BLOCKED:
        rule = redirects.get(route)
        if not rule or rule.get("status") != 404 or rule.get("force") is not True:
            raise AssertionError(f"Sensitive route is not forced to 404: {route}")
        if rule.get("to") != "/404.html":
            raise AssertionError(f"Sensitive route has unexpected target: {route}")

    global_headers = next(
        h["values"] for h in netlify.get("headers", [])
        if h.get("for") == "/*"
    )
    if "default-src 'self'" not in global_headers.get("Content-Security-Policy", ""):
        raise AssertionError("Restrictive Content Security Policy missing")
    if global_headers.get("X-Frame-Options") != "DENY":
        raise AssertionError("Clickjacking defense missing")
    if "max-age=" not in global_headers.get("Strict-Transport-Security", ""):
        raise AssertionError("HSTS missing")

    pages = [
        ROOT / "index.html",
        ROOT / "app/index.html",
        ROOT / "packs/index.html",
        *(ROOT / "care").glob("*.html"),
        *(ROOT / "pets").glob("*.html"),
        *(ROOT / name for name in ("about.html", "privacy.html",
                                    "terms.html", "accessibility.html")),
    ]
    for page in pages:
        content = page.read_text("utf-8")
        if OLD_HOST in content:
            raise AssertionError(f"Legacy SEO origin in {page.relative_to(ROOT)}")
        if 'rel="canonical" href="' not in content:
            raise AssertionError(f"Missing canonical in {page.relative_to(ROOT)}")
        if f'rel="canonical" href="{DOMAIN}' not in content:
            raise AssertionError(f"Unexpected canonical in {page.relative_to(ROOT)}")

    for sitemap in (ROOT / "sitemap.xml", ROOT / "species-sitemap.xml"):
        xml = ET.parse(sitemap).getroot()
        locs = [el.text for el in xml.iter() if el.tag.endswith("}loc")]
        if not locs or any(not (url or "").startswith(DOMAIN + "/") for url in locs):
            raise AssertionError(f"Invalid canonical URLs in {sitemap.name}")
    robots = (ROOT / "robots.txt").read_text("utf-8")
    for name in ("sitemap.xml", "species-sitemap.xml"):
        if f"Sitemap: {DOMAIN}/{name}" not in robots:
            raise AssertionError(f"Incorrect robots.txt sitemap: {name}")

    tracked = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    ).stdout.decode("utf-8").split("\0")
    for path in filter(None, tracked):
        name = Path(path).name
        if name == ".env" or name.startswith(".env.") or path.startswith(".git/"):
            raise AssertionError(f"Sensitive file is tracked: {path}")
    LOGGER.info(
        "PASS: %d generated pages, two sitemaps, security headers, "
        "and %d blocked probe paths.", len(pages), len(BLOCKED)
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        verify()
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError,
            ET.ParseError, AssertionError) as error:
        LOGGER.exception("Security and canonical verification failed: %s", error)
        sys.exit(1)
