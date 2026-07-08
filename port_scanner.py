"""
Port Scanner Module
Scans a target for open TCP ports, threaded and rate-limited.
"""

import argparse
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

from rate_limiter import RateLimiter

COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    139: "NetBIOS",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    8080: "HTTP-Proxy"
}


def resolve_target(target):
    """Resolve a hostname to an IP. Returns None if it fails."""
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        return None


def _check_port(ip, port, service, timeout, limiter):
    limiter.acquire()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        if sock.connect_ex((ip, port)) == 0:
            return {"port": port, "service": service}
    except socket.error:
        pass
    finally:
        sock.close()
    return None


def scan_ports(target, ports=None, timeout=1, threads=10, rate_limit=50):
    """
    Scan a target for open ports, multi-threaded and rate-limited to
    `rate_limit` connection attempts/sec across all threads.

    Returns a dict:
    {
        "target": str,
        "ip": str or None,
        "open_ports": [{"port": int, "service": str}],
        "error": str or None
    }
    """
    ports = ports or COMMON_PORTS
    result = {"target": target, "ip": None, "open_ports": [], "error": None}

    ip = resolve_target(target)
    if ip is None:
        result["error"] = "Could not resolve hostname."
        return result

    result["ip"] = ip
    limiter = RateLimiter(rate_limit)

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(_check_port, ip, port, service, timeout, limiter)
            for port, service in ports.items()
        ]
        for future in as_completed(futures):
            hit = future.result()
            if hit:
                result["open_ports"].append(hit)
                print(f"[+] Port {hit['port']} OPEN ({hit['service']})")

    # Keep port order deterministic in output regardless of thread completion order
    result["open_ports"].sort(key=lambda x: x["port"])

    return result


def print_report(result):
    if result["error"]:
        print(f"[-] {result['error']}")
        return
    print(f"\n[+] Resolved {result['target']} -> {result['ip']}")
    if not result["open_ports"]:
        print("[-] No open ports found among ports checked.")


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Threaded TCP port scanner.")
    parser.add_argument("target", help="IP address or domain to scan")
    parser.add_argument("-p", "--ports", help="Comma-separated list of ports, e.g. 22,80,443 "
                                                "(default: common ports list)")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Concurrent threads (default: 10)")
    parser.add_argument("-r", "--rate-limit", type=float, default=50,
                         help="Max connection attempts/sec across all threads (default: 50)")
    parser.add_argument("--timeout", type=float, default=1, help="Per-port connect timeout in seconds (default: 1)")
    return parser


if __name__ == "__main__":
    args = build_arg_parser().parse_args()

    ports = COMMON_PORTS
    if args.ports:
        selected = [int(p.strip()) for p in args.ports.split(",")]
        ports = {p: COMMON_PORTS.get(p, "unknown") for p in selected}

    print(f"\n[+] Scanning {args.target} with {args.threads} threads @ {args.rate_limit} conn/s...\n")
    result = scan_ports(
        args.target, ports=ports,
        timeout=args.timeout, threads=args.threads, rate_limit=args.rate_limit
    )
    print_report(result)
    print("\n[+] Scan complete.")
