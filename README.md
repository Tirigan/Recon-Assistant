# Recon Assistant

A simple Python-based recon toolkit built while learning bug bounty and offensive security fundamentals.

---

## 📌 Overview

This project contains a collection of small tools used during the reconnaissance phase of security testing.
The goal is to better understand how common recon techniques work under the hood by building them from scratch.

---

## 🛠️ Tools Included

### 🔍 Subdomain Scanner (`recon.py`)

* Checks common subdomains using HTTP and HTTPS
* Filters valid responses
* Helps identify exposed services

---

### 🌐 Port Scanner (`port_scanner.py`)

* Scans common ports on a target
* Identifies open services
* Uses Python sockets for low-level network interaction

---

### 📂 Directory Brute Forcer (`dir_bruteforce.py`)

* Discovers hidden directories and endpoints
* Uses a wordlist for path enumeration
* Identifies interesting responses (200, 301, 302, 403)

---

### ⚔️ HTTP Decapitator (`http_decapitator.py`)

* Experimental tool for testing HTTP behavior
* Used for learning and experimenting with request handling

---

## 📁 Project Structure

```
recon-assistant/
│
├── recon.py
├── port_scanner.py
├── dir_bruteforce.py
├── http_decapitator.py
│
├
```
