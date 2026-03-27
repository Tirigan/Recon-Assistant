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
├── wordlists/
├── results/
│
├── README.md
└── venv/
```

---

## ⚙️ Setup

### 1. Clone the repository

```
git clone <your-repo-url>
cd recon-assistant
```

### 2. Create and activate virtual environment

```
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```
pip install requests
```

---

## ▶️ Usage

### Subdomain Scanner

```
python recon.py
```

---

### Port Scanner

```
python port_scanner.py
```

---

### Directory Brute Forcer

```
python dir_bruteforce.py
```

---

## 📄 Wordlists

Wordlists should be placed in the `wordlists/` directory.

Recommended:

* SecLists (common industry wordlists)

---

## 📊 Results

Scan results can be stored in the `results/` directory for later analysis.

---

## 🧠 Purpose

This project is part of my hands-on learning in:

* Bug bounty methodology
* Reconnaissance techniques
* Python scripting for security

---

## 🚀 Future Improvements

* [ ] Add multithreading for faster scans
* [ ] Integrate larger wordlists
* [ ] Save and organize results automatically
* [ ] Add CLI arguments (e.g. `-d`, `-w`)
* [ ] Improve error handling and logging

---

## ⚠️ Disclaimer

This project is for educational purposes only.
Only use these tools on systems you own or have permission to test.

---

## 📬 Notes

Still early in the learning process, but this project represents a hands-on approach to understanding how recon tools work internally.
