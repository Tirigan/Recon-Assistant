import requests

url = input("Enter base URL (e.g. https://example.com): ")
wordlist = input("Enter wordlist path: ")

print(f"\n[+] Scanning {url}...\n")

with open(wordlist, "r") as file:
    paths = file.read().splitlines()

for path in paths:
    full_url = f"{url}/{path}"
    
    try:
        response = requests.get(full_url, timeout=3)
        
        if response.status_code in [200, 301, 302, 403]:
            print(f"[+] Found: {full_url} ({response.status_code})")
    
    except:
        pass
