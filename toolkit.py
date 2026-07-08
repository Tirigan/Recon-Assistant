"""
Recon Toolkit Orchestrator
============================
Chains the individual recon modules into a single workflow and writes
a consolidated results file (JSON + human-readable txt) that other
tools can consume.

Workflow:
  1. Port scan the base domain
  2. Brute-force subdomains
  3. For every live host found (base domain + subdomains that responded
     on HTTP/S), grab headers and optionally brute-force directories
  4. Dump everything to output/results.json and output/report.txt

Usage:
  python3 toolkit.py example.com
  python3 toolkit.py example.com -w wordlists/common.txt -t 20 -r 15
  python3 toolkit.py example.com --no-dir-brute
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "modules"))

from port_scanner import scan_ports
from subdomain_brute import brute_subdomains
from http_headers import get_headers
from dir_bruteforce import brute_dirs

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
DEFAULT_WORDLIST = os.path.join(os.path.dirname(__file__), "wordlists", "common.txt")


def run(domain, wordlist_path=None, do_dir_brute=True, threads=10, rate_limit=20):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    results = {
        "target": domain,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "settings": {"threads": threads, "rate_limit": rate_limit},
        "port_scan": None,
        "subdomains": None,
        "http_recon": []  # one entry per live host: headers + dir brute results
    }

    # 1. Port scan
    print(f"\n[*] Step 1/4 - Port scanning {domain}")
    results["port_scan"] = scan_ports(domain, threads=threads, rate_limit=rate_limit * 2)
    if results["port_scan"]["error"]:
        print(f"[-] {results['port_scan']['error']}")
    else:
        print(f"[+] {len(results['port_scan']['open_ports'])} open port(s) found")

    # 2. Subdomain brute force
    print(f"\n[*] Step 2/4 - Brute-forcing subdomains of {domain}")
    results["subdomains"] = brute_subdomains(domain, threads=threads, rate_limit=rate_limit)
    print(f"[+] {len(results['subdomains']['found'])} subdomain(s) found")

    # Build the list of live hosts to hit with HTTP recon:
    # the base domain (both protocols) + every subdomain that responded
    hosts_to_check = [f"https://{domain}", f"http://{domain}"]
    hosts_to_check += [entry["url"] for entry in results["subdomains"]["found"]]

    # 3. Header grab (+ optional dir brute) on each live host
    print(f"\n[*] Step 3/4 - Grabbing headers on {len(hosts_to_check)} host(s)")
    checked_bases = set()
    for host_url in hosts_to_check:
        header_result = get_headers(host_url)
        if header_result["error"]:
            continue  # host not actually live, skip

        base = host_url.split("://", 1)[1]
        if base in checked_bases:
            continue
        checked_bases.add(base)

        entry = {
            "host": host_url,
            "headers": header_result,
            "dir_brute": None
        }

        # 4. Dir brute force (only against hosts that actually responded)
        if do_dir_brute:
            wl = wordlist_path or DEFAULT_WORDLIST
            if os.path.exists(wl):
                print(f"    [*] Step 4/4 - Brute-forcing dirs on {host_url}")
                entry["dir_brute"] = brute_dirs(host_url, wl, threads=threads, rate_limit=rate_limit)
            else:
                print(f"    [-] Wordlist not found at {wl}, skipping dir brute for {host_url}")

        results["http_recon"].append(entry)
        print(f"[+] {host_url} -> {header_result['status_code']}")

    # Write outputs
    json_path = os.path.join(OUTPUT_DIR, "results.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)

    txt_path = os.path.join(OUTPUT_DIR, "report.txt")
    write_text_report(results, txt_path)

    print(f"\n[+] Scan complete.")
    print(f"[+] JSON results: {json_path}")
    print(f"[+] Text report:  {txt_path}")

    return results


def write_text_report(results, path):
    lines = []
    lines.append(f"Recon Report for {results['target']}")
    lines.append(f"Scanned at: {results['scanned_at']}")
    lines.append("=" * 50)

    lines.append("\n[Port Scan]")
    ps = results["port_scan"]
    if ps["error"]:
        lines.append(f"  Error: {ps['error']}")
    else:
        lines.append(f"  IP: {ps['ip']}")
        for p in ps["open_ports"]:
            lines.append(f"  OPEN {p['port']} ({p['service']})")
        if not ps["open_ports"]:
            lines.append("  No open ports found.")

    lines.append("\n[Subdomains]")
    for s in results["subdomains"]["found"]:
        lines.append(f"  {s['url']} ({s['status_code']})")
    if not results["subdomains"]["found"]:
        lines.append("  None found.")

    lines.append("\n[HTTP Recon]")
    for entry in results["http_recon"]:
        lines.append(f"\n  Host: {entry['host']}")
        lines.append(f"  Status: {entry['headers']['status_code']}")
        for k, v in entry["headers"]["headers"].items():
            lines.append(f"    {k}: {v}")
        if entry["dir_brute"] and entry["dir_brute"]["found"]:
            lines.append("  Found paths:")
            for d in entry["dir_brute"]["found"]:
                lines.append(f"    {d['url']} ({d['status_code']})")

    with open(path, "w") as f:
        f.write("\n".join(lines))


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Recon Toolkit Orchestrator")
    parser.add_argument("domain", help="Target domain, e.g. example.com")
    parser.add_argument("-w", "--wordlist", default=None,
                         help="Path to wordlist for dir brute force (default: wordlists/common.txt)")
    parser.add_argument("--no-dir-brute", action="store_true", help="Skip directory brute forcing")
    parser.add_argument("-t", "--threads", type=int, default=10,
                         help="Concurrent threads for brute-force steps (default: 10)")
    parser.add_argument("-r", "--rate-limit", type=float, default=20,
                         help="Max requests/sec per module, across all threads (default: 20)")
    return parser


if __name__ == "__main__":
    print("=" * 50)
    print(" Recon Toolkit - Orchestrator")
    print("=" * 50)

    args = build_arg_parser().parse_args()

    run(
        args.domain,
        wordlist_path=args.wordlist,
        do_dir_brute=not args.no_dir_brute,
        threads=args.threads,
        rate_limit=args.rate_limit
    )
