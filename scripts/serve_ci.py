"""Small production-like static server for Lighthouse CI.

Netlify compresses text assets and serves versioned static files with cache headers.
Python's stock http.server does neither, which makes local Lighthouse materially
slower than the deployed site. This server keeps the audit representative.
"""

from __future__ import annotations

import gzip
import mimetypes
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
HOST = "127.0.0.1"
PORT = 4173

COMPRESSIBLE = (
    "text/",
    "application/javascript",
    "application/json",
    "application/xml",
    "image/svg+xml",
)


class ProductionLikeHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args: object) -> None:
        return

    def _target(self) -> Path | None:
        request_path = unquote(urlsplit(self.path).path)
        relative = request_path.lstrip("/")
        target = (ROOT / relative).resolve()
        try:
            target.relative_to(ROOT)
        except ValueError:
            return None
        if target.is_dir():
            target = target / "index.html"
        return target

    def _cache_control(self, request_path: str) -> str:
        if request_path.startswith(("/styles/", "/assets/")):
            return "public, max-age=31536000, immutable"
        if request_path.startswith("/downloads/"):
            return "public, max-age=86400"
        return "public, max-age=0, must-revalidate"

    def _serve(self, include_body: bool) -> None:
        target = self._target()
        if target is None or not target.is_file():
            self.send_error(404)
            return

        data = target.read_bytes()
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        accept_encoding = self.headers.get("Accept-Encoding", "").lower()
        compressed = "gzip" in accept_encoding and (
            content_type.startswith(COMPRESSIBLE[0]) or content_type in COMPRESSIBLE[1:]
        )
        if compressed:
            data = gzip.compress(data, compresslevel=6)

        request_path = urlsplit(self.path).path
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", self._cache_control(request_path))
        self.send_header("Vary", "Accept-Encoding")
        self.send_header("X-Content-Type-Options", "nosniff")
        if compressed:
            self.send_header("Content-Encoding", "gzip")
        self.end_headers()
        if include_body:
            self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        self._serve(include_body=True)

    def do_HEAD(self) -> None:  # noqa: N802 - stdlib handler API
        self._serve(include_body=False)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), ProductionLikeHandler)
    print(f"Steady Paws Lighthouse server listening on http://{HOST}:{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
