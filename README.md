# ARB Universal IDE & AI Compiler

<p align="center">
  Turn plain-English instructions into code in the language you choose — 100% locally and offline.
</p>

<p align="center">
  <img src="https://shields.io" alt="AI Engine: Local Offline Qwen 2.5 Coder">
  <img src="https://img.shields.io/badge/Platforms-Windows%20%7C%20macOS%20%7C%20Linux-4C8EDA?style=for-the-badge" alt="Platforms: Windows, macOS, and Linux source setup">
  <a href="https://github.com/aaravroybhattacharya-sketch/arb-universal-ide/blob/main/LICENSE.md">
    <img src="https://shields.io" alt="Apache License 2.0">
  </a>
</p>

<p align="center">
  <a href="https://github.com/aaravroybhattacharya-sketch/arb-universal-ide/releases">
    <img src="https://img.shields.io/badge/Download-Windows%20Installer-0078D4?style=for-the-badge&logo=windows&logoColor=white" alt="Download the Windows installer">
  </a>
</p>

---

## What is ARB?

**ARB** is an offline, AI-powered, multi-language transpiler IDE. Describe program logic in everyday English, and ARB turns it into executable code directly on your machine. Its automated pipeline can identify and install dependencies required by your instructions.

> **Model information:** ARB embeds `llama-cpp-python` with **Qwen 2.5 Coder 7B** directly inside the application. No API keys, cloud accounts, or background servers (`localhost`) are required. On the first run, the model (~4.7 GB) is downloaded automatically and cached locally for offline use.

## Features

- **100% Offline & Unlimited:** Runs locally on your hardware with zero rate limits, subscriptions, or API keys.
- **Zero-Config Embedded AI:** Automatically downloads and caches the coding model on first launch—no separate Ollama or server setup required.
- **Write without indentation:** Describe loops, conditions, and lists in plain language.
- **Automated dependency management:** Identify and install Python packages needed by your instructions.
- **Multiple output languages:** Generate Python, C, Java, JavaScript, HTML/CSS, C++, or Go.
- **Native file export:** Save generated code with the appropriate file extension, such as `.py`, `.c`, or `.js`.

## Example

**English instructions**

```text
create a variable numbers from 1 to 5
loop through numbers
if number is even print "Even:" and the number
```

**Python output**

```python
numbers = list(range(1, 6))
for num in numbers:
    if num % 2 == 0:
        print(f"Even: {num}")
```

## Build from source

The release provides a Windows installer. You can also run the Python source on Windows, macOS, or Linux.

### Prerequisites
- Python 3.9+
- At least **8 GB RAM** and **~5 GB of free disk space** (for the one-time model download)

### 1. Clone the repository

```bash
git clone https://github.com/aaravroybhattacharya-sketch/arb-universal-ide.git
cd arb-universal-ide
```

### 2. Install dependencies and run

```bash
pip install llama-cpp-python huggingface-hub pyinstaller
python app.py
```

*(Note: No environment variables or API keys are needed. The first compilation will download the local model automatically.)*

## License

This project is licensed under the Apache License 2.0 - see the <a href="https://github.com/aaravroybhattacharya-sketch/arb-universal-ide/blob/main/LICENSE.md">License</a> file for details.

© 2026 ARB Universal IDE · Open source under the Apache License 2.0
