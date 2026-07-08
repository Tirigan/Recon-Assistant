import requests

url = input("Enter base URL (e.g. https://example.com): ").rstrip("/")
wordlist = input("Enter wordlist path: ")

print(f"\n[+] Scanning {url}...\n")

try:
    with open(wordlist, "r") as file:
        paths = file.read().splitlines()

except FileNotFoundError:
    print("[-] Wordlist file not found.")
    exit()

except PermissionError:
    print("[-] Permission denied reading wordlist.")
    exit()


for path in paths:
    full_url = f"{url}/{path}"

    try:
        response = requests.get(
            full_url,
            timeout=3,
            allow_redirects=False
        )

        if response.status_code in [200, 301, 302, 403]:
            print(
                f"[+] Found: {full_url} "
                f"({response.status_code})"
            )

    except requests.exceptions.Timeout:
        print(f"[!] Timeout: {full_url}")

    except requests.exceptions.ConnectionError:
        print(f"[!] Connection failed: {full_url}")

    except requests.exceptions.RequestException as e:
        print(f"[!] Error: {e}")
