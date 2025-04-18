# Zula Account Checker (Request-Based, Captcha Solving)

<img src="https://i.imgur.com/XJXdczd.png">

This tool checks Zula game accounts via HTTP requests and retrieves detailed account info such as rank, nickname, level, KD, registration date, and total ZA transaction history.
It uses [CapSolver](https://capsolver.com/) to bypass Turnstile (Cloudflare) challenges.

---

### 🔍 Features

- ✅ Full request-based login (no browser automation)
- 🧠 Captcha solved via CapSolver (Turnstile support)
- 📊 Fetches payment history and calculates total ZA used
- 🧾 Collects profile data: username, rank, level, KD, registration date
- 🔐 Checks email and phone verification status
- 🧵 Multi-threaded (50 concurrent threads)
- 🌐 Proxy support ready (just uncomment related lines)

---

### ⚙️ Requirements

Install required Python libraries:
```python
pip install tls-client beautifulsoup4 requests loguru
```
This tool uses tls-client for TLS fingerprinting (Chrome 120), mimicking real browser behavior.

---

### 🧩 CapSolver Setup

You need a CapSolver API key to use this tool.
Get your key from https://dashboard.capsolver.com

Paste it into the script:
```python
api_key = "CAPSOLVER-KEY"
```

---

### 📁 Usage

Prepare accounts.txt in the following format:
```
email1@example.com:password1
email2@example.com:password2
```

Run the script:
```
python main.py
```

--- 

### 💾 Output

If login is successful and ZA > 0, the tool will:

- Print account summary to console
- Append full details to success.txt
- If captcha or login fails after 3 attempts:
- Account will be saved in error.txt

---

### 📌 Notes

Proxy support is included but commented out. To enable it:
```
proxy = random.choice(open("proxy.txt").readlines()).strip()
session.proxies = {'http': 'http://' + proxy, 'https': 'http://' + proxy}
```
Captcha-solving and verification logic is fully request-based (no Selenium, Puppeteer, etc.)

---

### ⚠️ Disclaimer
This tool is for educational and ethical research purposes only.
The developer is not responsible for any misuse.
Always comply with your local laws and the terms of service of the platform.

---

### :rose: Special Thanks

[itzgonza](https://github.com/itzgonza) for contributions and support
