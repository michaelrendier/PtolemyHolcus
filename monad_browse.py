"""
monad_browse.py — the back end of a browser, minus the browser.

Ptol fetches, strips, and routes; a window (PtolemyDesktop's BrowserWindow,
later) only renders. This module is the fetch + strip half, shared by the
harness (full path) and the bare monad (minimal path).

  search_url(q)          — a query → a search URL
  fetch(url)             — minimal urllib GET, size-capped, never raises
  strip_html(body, ...)  — html2text (Aaron Swartz's lib) → strip_to_prose
  estimate_ram(nbytes)   — parse blow-up, for the ResourceGovernor's Job

Only prose is handled today. Code-type text stripping is a later increment.
"""
from __future__ import annotations

import gzip
import io
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Optional

_UA = ("Mozilla/5.0 (X11; Linux x86_64) PtolemyDesktop/0 "
       "(+https://michaelrendier.online) monad-browse")

MAX_BYTES = 5 * 1024 * 1024          # a page over 5 MB is not "the information"
PARSE_BLOWUP_HTML = 6               # HTML source → DOM/parse residents, rough
PARSE_BLOWUP_TEXT = 2


@dataclass
class Fetched:
    status: int                     # HTTP status, or 0 on transport failure
    url_final: str
    content_type: str
    body: bytes
    nbytes: int
    error: str = ''


def search_url(q: str, engine: str = 'ddg') -> str:
    qs = urllib.parse.quote_plus(q.strip())
    return {
        'ddg':   f"https://html.duckduckgo.com/html/?q={qs}",
        'wiki':  f"https://en.wikipedia.org/w/index.php?search={qs}",
        'bing':  f"https://www.bing.com/search?q={qs}",
    }.get(engine, f"https://html.duckduckgo.com/html/?q={qs}")


def fetch(url: str, timeout: float = 15.0, max_bytes: int = MAX_BYTES) -> Fetched:
    """One GET. Follows redirects (urllib default). Reads at most `max_bytes`.
    Any transport error → status 0 with `error` set; never raises."""
    req = urllib.request.Request(url, headers={
        'User-Agent': _UA,
        'Accept': 'text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.5',
        'Accept-Encoding': 'gzip',
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read(max_bytes + 1)
            ctype = resp.headers.get('Content-Type', '') or ''
            enc = (resp.headers.get('Content-Encoding', '') or '').lower()
            final = resp.geturl()
            status = getattr(resp, 'status', 200) or 200
    except urllib.error.HTTPError as e:                       # noqa: PERF203
        return Fetched(e.code, url, e.headers.get('Content-Type', '') if e.headers
                       else '', b'', 0, error=f'HTTP {e.code}')
    except Exception as e:                                     # noqa: BLE001
        return Fetched(0, url, '', b'', 0, error=str(e))

    if 'gzip' in enc:
        try:
            raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read(max_bytes + 1)
        except OSError:
            pass
    truncated = len(raw) > max_bytes
    body = raw[:max_bytes]
    return Fetched(status, final, ctype, body, len(body),
                   error='truncated' if truncated else '')


def strip_html(body: bytes, content_type: str = 'text/html',
               base_url: Optional[str] = None) -> str:
    """HTML/text → prose. html2text removes tags/scripts/style; the harness's
    own strip_to_prose then drops notation-dense / code / table lines."""
    text = body.decode('utf-8', 'replace')
    if 'html' in (content_type or '').lower() or '<' in text[:2048]:
        try:
            import html2text
            h = html2text.HTML2Text()
            h.ignore_links = True
            h.ignore_images = True
            h.ignore_emphasis = True
            h.body_width = 0
            h.skip_internal_links = True
            text = h.handle(text)
        except Exception:                                     # noqa: BLE001
            # last-ditch: crude tag scrub
            import re
            text = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', text,
                          flags=re.S | re.I)
            text = re.sub(r'<[^>]+>', ' ', text)
    try:
        from harness import strip_to_prose
        return strip_to_prose(text)
    except Exception:                                         # noqa: BLE001
        return '\n'.join(ln.strip() for ln in text.splitlines() if ln.strip())


def estimate_ram(nbytes: int, is_html: bool = True) -> int:
    """Resident-bytes estimate for the governor: source × parse blow-up."""
    return max(64 * 1024, nbytes * (PARSE_BLOWUP_HTML if is_html
                                    else PARSE_BLOWUP_TEXT))
