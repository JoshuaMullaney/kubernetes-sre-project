import urllib.request
import urllib.error
import time
import datetime

# ─── Configuration ────────────────────────────────────────────────────────────
APP_URL        = "http://127.0.0.1:59734"
CHECK_INTERVAL = 15          # seconds between checks
WARN_TIMEOUT   = 3.0         # seconds before WARN
CRITICAL_TIMEOUT = 6.0       # seconds before CRITICAL
# ──────────────────────────────────────────────────────────────────────────────

def check_health(url):
    """
    Attempt an HTTP GET to the app's root endpoint.
    Returns (status_label, http_code, response_time_ms)
    """
    start = time.time()
    try:
        with urllib.request.urlopen(url, timeout=CRITICAL_TIMEOUT) as response:
            elapsed = (time.time() - start) * 1000
            code = response.status

            if elapsed > WARN_TIMEOUT * 1000:
                return "WARN", code, elapsed
            else:
                return "OK", code, elapsed

    except urllib.error.HTTPError as e:
        elapsed = (time.time() - start) * 1000
        return "WARN", e.code, elapsed

    except Exception:
        elapsed = (time.time() - start) * 1000
        return "CRITICAL", 0, elapsed


def format_line(status, code, elapsed):
    """Format a status line with timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    icons = {"OK": "✅", "WARN": "⚠️ ", "CRITICAL": "❌"}
    icon = icons.get(status, "?")

    if code == 0:
        detail = "No response"
    else:
        detail = f"HTTP {code}"

    return f"[{timestamp}]  {icon}  {status:<8}  {detail}    {elapsed:.0f}ms    {APP_URL}"


def run():
    print("=" * 70)
    print("  Kubernetes App Health Monitor")
    print(f"  Target : {APP_URL}")
    print(f"  Interval: every {CHECK_INTERVAL}s")
    print(f"  Thresholds — WARN: >{WARN_TIMEOUT}s  |  CRITICAL: timeout at {CRITICAL_TIMEOUT}s")
    print("=" * 70)
    print()

    ok_count       = 0
    warn_count     = 0
    critical_count = 0

    try:
        while True:
            status, code, elapsed = check_health(APP_URL)

            if status == "OK":
                ok_count += 1
            elif status == "WARN":
                warn_count += 1
            else:
                critical_count += 1

            print(format_line(status, code, elapsed))

            # Print a rolling summary every 5 checks
            total = ok_count + warn_count + critical_count
            if total % 5 == 0:
                print()
                print(f"  ── Summary after {total} checks: "
                      f"OK={ok_count}  WARN={warn_count}  CRITICAL={critical_count} ──")
                print()

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        total = ok_count + warn_count + critical_count
        print()
        print("=" * 70)
        print(f"  Monitor stopped.  Total checks: {total}")
        print(f"  OK={ok_count}  WARN={warn_count}  CRITICAL={critical_count}")
        print("=" * 70)


if __name__ == "__main__":
    run()
