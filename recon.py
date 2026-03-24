import requests

domain = input("Enter Domain: ")

subs = ["www", "mail", "dev", "test", "api", "staging"]

print(f"\n[+] Scanning {domain}...\n")

for sub in subs:
    https_url = f"https://{sub}.{domain}"
    http_url = f"http://{sub}.{domain}"

    try:
        response = requests.get(https_url, timeout=3)
        if response.status_code < 400:
            print(f"[+] Found: {https_url} ({response.status_code})")
    except:
        try:
            response = requests.get(http_url, timeout=3)
            if response.status_code < 400:
                print(f"[+] Found: {http_url} ({response.status_code})")
        except:
            pass
