import requests

domain = input("Enter Domain: ").strip()

subs = [
    "www",
    "mail",
    "dev",
    "test",
    "api",
    "staging",
    "admin",
    "portal",
    "vpn",
    "blog"
]

print(f"\n[+] Scanning {domain}...\n")

found = []

for sub in subs:
    subdomain = f"{sub}.{domain}"

    for protocol in ["https", "http"]:
        url = f"{protocol}://{subdomain}"

        try:
            response = requests.get(
                url,
                timeout=3,
                allow_redirects=False
            )

            if response.status_code < 400:
                print(f"[+] Found: {url} ({response.status_code})")
                found.append(url)
                break

        except requests.exceptions.SSLError:
            continue

        except requests.exceptions.ConnectionError:
            continue

        except requests.exceptions.Timeout:
            print(f"[!] Timeout: {url}")

        except requests.exceptions.RequestException as e:
            print(f"[!] Error: {e}")


print(f"\n[+] Scan complete. Found {len(found)} subdomains.")
