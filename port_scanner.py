import socket

target = input("Enter IP or domain: ").strip()

ports = {
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

print(f"\n[+] Scanning {target}...\n")

try:
    ip = socket.gethostbyname(target)
    print(f"[+] Resolved {target} -> {ip}\n")

except socket.gaierror:
    print("[-] Could not resolve hostname.")
    exit()


for port, service in ports.items():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)

    try:
        result = sock.connect_ex((ip, port))

        if result == 0:
            print(f"[+] Port {port} OPEN ({service})")

    except socket.error as e:
        print(f"[!] Error scanning port {port}: {e}")

    finally:
        sock.close()


print("\n[+] Scan complete.")
