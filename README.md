# Recon Toolkit

A lightweight, multi-threaded reconnaissance toolkit written in Python. It chains together port scanning, subdomain enumeration, HTTP header grabbing, and directory brute-forcing into a single automated workflow, then exports the findings in formats other tools can consume.

Built as a hands-on project while transitioning from IT support into cybersecurity — every module is written from scratch to understand exactly how threading, rate-limiting, and basic recon techniques work under the hood.

> ⚠️ **Authorized use only.** This toolkit sends real network traffic (port connections, HTTP requests, brute-force scans) to whatever target you point it at. Only use it against systems you own, or have **explicit written permission** to test (e.g. your own lab, a CTF box, or a bug-bounty program's in-scope assets). Scanning systems without authorization may be illegal in your jurisdiction.

## Features

- **Port Scanner** — threaded TCP connect scan against common ports
- **Subdomain Brute Forcer** — checks a wordlist of prefixes against a base domain over HTTP/S
- **HTTP Header Grabber** — fetches status code and response headers for a URL
- **Directory Brute Forcer** — checks a wordlist of paths against a base URL
- **Toolkit Orchestrator** — runs all of the above against a target in sequence and writes a consolidated JSON + text report
- **Findings Export** — normalizes the orchestrator's output into plain-text target lists ready to feed into other tools (`nmap`, `gobuster`, `ffuf`, etc.)
- **Shared rate limiter** — every module uses the same thread-safe token-bucket limiter, so you control requests/sec across all threads instead of hammering a target

## Project structure

```
.
├── port_scanner.py       # TCP port scanner
├── subdomain_brute.py    # Subdomain enumeration over HTTP/S
├── http_headers.py       # HTTP header/status grabber
├── dir_bruteforce.py     # Directory/path brute forcer
├── rate_limiter.py       # Shared token-bucket rate limiter
├── toolkit.py            # Orchestrates all modules into one scan
├── findings_export.py    # Exports results.json into plain target lists
├── wordlists/
│   └── common.txt        # Wordlist used by dir_bruteforce.py (add your own)
└── output/                # Created automatically — results.json, report.txt, exports/
```

Every module can also be run standalone from the command line — `toolkit.py` just wires them together.

## Requirements

- Python 3.8+
- [`requests`](https://pypi.org/project/requests/)

```bash
pip install requests
```

## Usage

### Run the full toolkit

```bash
python3 toolkit.py example.com
```

This will, in order:
1. Port scan the target
2. Brute-force subdomains
3. Grab HTTP headers for the base domain and every live subdomain found
4. Brute-force directories on each live host (unless `--no-dir-brute` is passed)

Results are written to `output/results.json` (machine-readable) and `output/report.txt` (human-readable).

**Options:**

| Flag | Description | Default |
|---|---|---|
| `-w, --wordlist` | Wordlist for directory brute-forcing | `wordlists/common.txt` |
| `--no-dir-brute` | Skip the directory brute-force step | off |
| `-t, --threads` | Concurrent threads per module | `10` |
| `-r, --rate-limit` | Max requests/sec per module, across all threads | `20` |

```bash
python3 toolkit.py example.com -w wordlists/common.txt -t 20 -r 15
python3 toolkit.py example.com --no-dir-brute
```

### Export findings for other tools

Once you have a `results.json`, turn it into plain target lists:

```bash
python3 findings_export.py output/results.json -o output/exports
```

This produces:

- `live_hosts.txt` — every host that responded, one per line (feed to `nmap -iL`)
- `open_ports.txt` — `ip:port  # service` for each open port
- `subdomains.txt` — discovered subdomains
- `discovered_paths.txt` — full URLs found during directory brute-forcing

### Run a single module

Every module works on its own too:

```bash
python3 port_scanner.py example.com -t 20 -r 50
python3 subdomain_brute.py example.com -s wordlists/subdomains.txt
python3 http_headers.py https://example.com
python3 dir_bruteforce.py https://example.com -w wordlists/common.txt
```

Run any module with `-h` to see its full option list.

## Sample output

```
[+] Scan complete.
[+] JSON results: output/results.json
[+] Text report:  output/report.txt

[+] Exporting findings from output/results.json -> output/exports

  live_hosts.txt         2 entries
  open_ports.txt         3 entries
  subdomains.txt         2 entries
  discovered_paths.txt   5 entries
```

## Roadmap

- [ ] SSL/TLS certificate inspection module
- [ ] Basic vulnerability fingerprinting against `discovered_paths.txt`
- [ ] HTML report generation
- [ ] Config file support (YAML/JSON) instead of CLI-only flags

## Disclaimer

This project is for educational purposes and authorized security testing only. The author is not responsible for misuse of this software. Always get permission before scanning a target.


## 📬 Notes

Still early in the learning process, but this project represents a hands-on approach to understanding how recon tools work internally.
