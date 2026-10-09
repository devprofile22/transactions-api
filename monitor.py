import argparse
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

DEFAULT_URL = "http://127.0.0.1:5000/health"
TIMEOUT_SECONDS = 3
LOG_FILE = "monitor.log"


def check(url):
    """Ping the URL. Returns (is_up, message)."""
    start = time.time()
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as resp:
            ms = int((time.time() - start) * 1000)
            if resp.status == 200:
                return True, f"UP (HTTP 200, {ms} ms)"
            return False, f"DOWN (HTTP {resp.status})"
    except urllib.error.HTTPError as e:
        return False, f"DOWN (HTTP {e.code})"
    except Exception as e:
        return False, f"DOWN ({type(e).__name__})"


def report(url):
    is_up, message = check(url)
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {message}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    return is_up


def main():
    parser = argparse.ArgumentParser(description="Ping the API and report UP/DOWN")
    parser.add_argument("--url", default=DEFAULT_URL, help="URL to check")
    parser.add_argument("--watch", type=int, default=0,
                        help="keep checking every N seconds (0 = check once)")
    args = parser.parse_args()

    if args.watch > 0:
        print(f"Monitoring {args.url} every {args.watch}s. Press Ctrl+C to stop.")
        try:
            while True:
                report(args.url)
                time.sleep(args.watch)
        except KeyboardInterrupt:
            print("\nStopped.")
    else:
        sys.exit(0 if report(args.url) else 1)


if __name__ == "__main__":
    main()