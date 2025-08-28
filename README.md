# 🔎 Advanced Python Port Scanner

A fast, multithreaded port scanner written in **Python**, with support for:
- Custom or full port ranges
- Optional proxy support (HTTP CONNECT tunneling)
- Colored CLI output
- Estimated scan time calculation

---

## 🚀 Features
- Scan **all ports** or define custom ports/ranges.
- Use **proxies** for stealth (HTTP CONNECT supported).
- **Threaded scanning** with up to 100 workers.
- Shows **estimated time to complete**.
- Clean, **colorized output** using `colorama`.

---

## 📦 Installation
Clone the repository:
```bash
git clone https://github.com/thehackerthathacks/port-scanner.git
cd port-scanner
```

### Install requirements:
```bash
pip install -r requirements.txt
```

### Usage
python scanner.py --target <TARGET> [OPTIONS]



