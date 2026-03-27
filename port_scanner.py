import socket

target = input("Enter IP or domain: ")

ports = [21, 22, 25, 53, 80, 110, 139, 143, 443, 445, 8080]

for port in ports:
    s = socket.socket()
    s.settimeout(1)
    
    try:
        s.connect((target, port))
        print(f"[+] Port {port} is open")
    except:
        pass
    
    s.close()
