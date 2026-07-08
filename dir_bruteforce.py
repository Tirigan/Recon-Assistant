"""
Directory Brute Forcer Module
Checks a wordlist of paths against a base URL, threaded and rate-limited.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from rate_limiter import RateLimiter


def load_wordlist(path):
    """Load a wordlist file. Returns (paths, error)."""
    try:
        with open(path, "r") as file:
            return file.read().splitlines(), None
    except FileNotFoundError:
        return None, "Wordlist file not found."
    except PermissionError:
        return None, "Permission denied reading wordlist."


def _check_path(base_url, path, timeout, valid_codes, limiter):
    limiter.acquire()
    full_url = f"{base_url}/{path}"
    try:
        response = requests.get(full_url, timeout=timeout, allow_redirects=False)
        if response.status_code in valid_codes:
            return {"url": full_url, "status_code": response.status_code}
    except requests.exceptions.Timeout:
        print(f"[!] Timeout: {full_url}")
    except requests.exceptions.ConnectionError:
        print(f"[!] Connection failed: {full_url}")
    except requests.exceptions.RequestException as e:
        print(f"[!] Error: {e}")
    return None


def brute_dirs(url, wordlist_path, timeout=3, valid_codes=(200, 301, 302, 403),
                threads=10, rate_limit=20):
    """
    Brute-force directories/paths on a base URL, multi-threaded and
    rate-limited to `rate_limit` requests/sec across all threads.

    Returns a dict:
    {
        "url": str,
        "found": [{"url": str, "status_code": int}],
        "error": str or None
    }
    """
    url = url.rstrip("/")
    result = {"url": url, "found": [], "error": None}

    paths, err = load_wordlist(wordlist_path)
    if err:
        result["error"] = err
        return result

    limiter = RateLimiter(rate_limit)

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(_check_path, url, path, timeout, valid_codes, limiter)
            for path in paths
        ]
        for future in as_completed(futures):
            hit = future.result()
            if hit:
                result["found"].append(hit)
                print(f"[+] Found: {hit['url']} ({hit['status_code']})")

    return result


def print_report(result):
    if result["error"]:
        print(f"[-] {result['error']}")
        return
    print(f"\n[+] {len(result['found'])} path(s) found.")


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Threaded directory/path brute forcer.")
    parser.add_argument("url", help="Base URL, e.g. https://example.com")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to wordlist file")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Concurrent threads (default: 10)")
    parser.add_argument("-r", "--rate-limit", type=float, default=20,
                         help="Max requests/sec across all threads (default: 20)")
    parser.add_argument("--timeout", type=float, default=3, help="Per-request timeout in seconds (default: 3)")
    return parser


if __name__ == "__main__":
    args = build_arg_parser().parse_args()
    print(f"\n[+] Scanning {args.url} with {args.threads} threads @ {args.rate_limit} req/s...\n")
    result = brute_dirs(
        args.url, args.wordlist,
        timeout=args.timeout, threads=args.threads, rate_limit=args.rate_limit
    )
    print_report(result)
