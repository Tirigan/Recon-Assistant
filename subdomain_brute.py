"""
Subdomain Brute Forcer Module
Checks a list of common subdomain prefixes against a base domain,
threaded and rate-limited.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from rate_limiter import RateLimiter

DEFAULT_SUBS = [
    "www", "mail", "dev", "test", "api",
    "staging", "admin", "portal", "vpn", "blog"
]


def _check_subdomain(domain, sub, timeout, limiter):
    subdomain = f"{sub}.{domain}"
    for protocol in ["https", "http"]:
        url = f"{protocol}://{subdomain}"
        limiter.acquire()
        try:
            response = requests.get(url, timeout=timeout, allow_redirects=False)
            if response.status_code < 400:
                return {"url": url, "status_code": response.status_code}
        except requests.exceptions.SSLError:
            continue
        except requests.exceptions.ConnectionError:
            continue
        except requests.exceptions.Timeout:
            print(f"[!] Timeout: {url}")
        except requests.exceptions.RequestException as e:
            print(f"[!] Error: {e}")
    return None


def brute_subdomains(domain, subs=None, timeout=3, threads=10, rate_limit=20):
    """
    Brute-force subdomains of a domain, multi-threaded and rate-limited
    to `rate_limit` requests/sec across all threads.

    Returns a dict:
    {
        "domain": str,
        "found": [{"url": str, "status_code": int}]
    }
    """
    subs = subs or DEFAULT_SUBS
    result = {"domain": domain, "found": []}

    limiter = RateLimiter(rate_limit)

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(_check_subdomain, domain, sub, timeout, limiter)
            for sub in subs
        ]
        for future in as_completed(futures):
            hit = future.result()
            if hit:
                result["found"].append(hit)
                print(f"[+] Found: {hit['url']} ({hit['status_code']})")

    return result


def print_report(result):
    print(f"\n[+] Scan complete. Found {len(result['found'])} subdomains.")


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Threaded subdomain brute forcer.")
    parser.add_argument("domain", help="Base domain, e.g. example.com")
    parser.add_argument("-s", "--subs-file", help="Optional path to a custom subdomain wordlist (one per line)")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Concurrent threads (default: 10)")
    parser.add_argument("-r", "--rate-limit", type=float, default=20,
                         help="Max requests/sec across all threads (default: 20)")
    parser.add_argument("--timeout", type=float, default=3, help="Per-request timeout in seconds (default: 3)")
    return parser


if __name__ == "__main__":
    args = build_arg_parser().parse_args()

    subs = DEFAULT_SUBS
    if args.subs_file:
        with open(args.subs_file, "r") as f:
            subs = f.read().splitlines()

    print(f"\n[+] Scanning {args.domain} with {args.threads} threads @ {args.rate_limit} req/s...\n")
    result = brute_subdomains(
        args.domain, subs=subs,
        timeout=args.timeout, threads=args.threads, rate_limit=args.rate_limit
    )
    print_report(result)
