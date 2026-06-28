#!/usr/bin/env python3
"""
download_xfinity_bills.py
Download Xfinity internet bill PDFs using the authenticated Xfinity API.

The Bearer JWT is pulled from Safari's localStorage automatically via AppleScript.
Bills are saved to ~/Downloads/Xfinity-2025-Bills/

Usage:
    python3 download_xfinity_bills.py --all
    python3 download_xfinity_bills.py --months 2025-01 2025-02 2025-06
    python3 download_xfinity_bills.py --months 2026-01 --output-dir ~/Downloads/Xfinity-2025-Bills
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, date
from pathlib import Path

import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

XFINITY_BILL_URL = "https://api.sc.xfinity.com/session/ssm/bill/pdf"
LOCALSTORAGE_KEY = "dss-myaccount-production_https://api.sc.xfinity.com/session"
DEFAULT_OUTPUT_DIR = os.path.expanduser("~/Downloads/Xfinity-2025-Bills")

MONTH_LABEL = {
    "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
    "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
    "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
}

# ---------------------------------------------------------------------------
# Safari localStorage token retrieval
# ---------------------------------------------------------------------------

APPLESCRIPT_TEMPLATE = """
tell application "Safari"
    set theResult to do JavaScript "
        (function() {{
            var raw = localStorage.getItem('{key}');
            return raw ? raw : '__NOT_FOUND__';
        }})()
    " in current tab of front window
    return theResult
end tell
"""


def get_jwt_from_safari() -> str:
    """Retrieve the Xfinity JWT token from Safari's localStorage via AppleScript."""
    script = APPLESCRIPT_TEMPLATE.format(key=LOCALSTORAGE_KEY)
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"AppleScript failed: {result.stderr.strip()}\n"
            "Make sure Safari is open and you are logged in to xfinity.com/myaccount"
        )
    raw = result.stdout.strip()
    if raw == "__NOT_FOUND__":
        raise RuntimeError(
            f"localStorage key not found: {LOCALSTORAGE_KEY}\n"
            "Open Safari, log in to xfinity.com/myaccount, then retry."
        )
    try:
        session_data = json.loads(raw)
    except json.JSONDecodeError:
        # Some versions store the JWT directly as a plain string
        return raw.strip('"')

    # Dig out the token — try common nested paths
    for path in [
        ["access_token"],
        ["token", "access_token"],
        ["session", "access_token"],
        ["data", "access_token"],
    ]:
        node = session_data
        for key in path:
            if isinstance(node, dict) and key in node:
                node = node[key]
            else:
                node = None
                break
        if node and isinstance(node, str):
            return node

    # Last resort: return the raw JSON and let the user sort it out
    raise RuntimeError(
        f"Could not locate access_token in the localStorage data.\n"
        f"Raw value (first 200 chars): {raw[:200]}"
    )


# ---------------------------------------------------------------------------
# Bill download
# ---------------------------------------------------------------------------

def month_to_statement_date(ym: str) -> str:
    """Convert '2025-01' → '01-01-2025' (first day of month, Xfinity API format)."""
    year, month = ym.split("-")
    return f"{month}-01-{year}"


def output_filename(ym: str) -> str:
    """'2025-01' → 'Xfinity-Jan2025.pdf'"""
    year, month = ym.split("-")
    return f"Xfinity-{MONTH_LABEL[month]}{year}.pdf"


def download_bill(ym: str, jwt: str, output_dir: Path) -> Path:
    """Download a single bill PDF. Returns the saved file path."""
    statement_date = month_to_statement_date(ym)
    url = f"{XFINITY_BILL_URL}?statementDate={statement_date}&signed=true"
    dest = output_dir / output_filename(ym)

    if dest.exists():
        print(f"  [skip] {dest.name} already exists")
        return dest

    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {jwt}")
    req.add_header("Accept", "application/pdf")
    req.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15")

    print(f"  [fetch] {ym} → {dest.name} ...", end=" ", flush=True)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read()
        if not content.startswith(b"%PDF"):
            raise ValueError(f"Response is not a PDF (starts with: {content[:20]})")
        dest.write_bytes(content)
        print(f"OK ({len(content)//1024} KB)")
        return dest
    except urllib.error.HTTPError as e:
        print(f"FAILED — HTTP {e.code}: {e.reason}")
        raise
    except Exception as e:
        print(f"FAILED — {e}")
        raise


# ---------------------------------------------------------------------------
# Month range helpers
# ---------------------------------------------------------------------------

def all_months_since_jan_2025() -> list[str]:
    """Return all YYYY-MM strings from 2025-01 through the current month."""
    months = []
    current = date.today()
    d = date(2025, 1, 1)
    while d <= current:
        months.append(f"{d.year:04d}-{d.month:02d}")
        if d.month == 12:
            d = date(d.year + 1, 1, 1)
        else:
            d = date(d.year, d.month + 1, 1)
    return months


def validate_months(months: list[str]) -> list[str]:
    valid = []
    for m in months:
        try:
            datetime.strptime(m, "%Y-%m")
            valid.append(m)
        except ValueError:
            print(f"  [warn] Invalid month format '{m}' — expected YYYY-MM, skipping")
    return valid


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Download Xfinity bill PDFs using the authenticated Safari session."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--all", action="store_true",
        help="Download all months from Jan 2025 through the current month"
    )
    group.add_argument(
        "--months", nargs="+", metavar="YYYY-MM",
        help="Specific month(s) to download, e.g. 2025-01 2025-06"
    )
    parser.add_argument(
        "--output-dir", default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to save PDFs (default: {DEFAULT_OUTPUT_DIR})"
    )
    parser.add_argument(
        "--token", metavar="JWT",
        help="Provide JWT token directly (skips Safari AppleScript lookup)"
    )
    args = parser.parse_args()

    output_dir = Path(os.path.expanduser(args.output_dir))
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine months
    if args.all:
        months = all_months_since_jan_2025()
    else:
        months = validate_months(args.months)

    if not months:
        print("No valid months to download.")
        sys.exit(1)

    print(f"Target months: {', '.join(months)}")
    print(f"Output directory: {output_dir}")

    # Get JWT
    if args.token:
        jwt = args.token
        print("Using provided JWT token.")
    else:
        print("Retrieving JWT from Safari localStorage...")
        try:
            jwt = get_jwt_from_safari()
            print(f"  Token retrieved ({len(jwt)} chars)")
        except RuntimeError as e:
            print(f"\nERROR: {e}")
            sys.exit(1)

    # Download
    success, skipped, failed = 0, 0, 0
    for ym in months:
        try:
            path = download_bill(ym, jwt, output_dir)
            if "skip" in str(path):
                skipped += 1
            else:
                success += 1
            time.sleep(0.5)  # gentle rate limiting
        except Exception:
            failed += 1

    print(f"\nDone. Downloaded: {success}  Skipped: {skipped}  Failed: {failed}")
    if failed:
        print("Re-run to retry failed months, or check that your Safari session is still active.")


if __name__ == "__main__":
    main()
