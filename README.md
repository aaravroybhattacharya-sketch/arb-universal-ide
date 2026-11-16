# ARB Universal IDE & AI Compiler

<p align="center">
  Turn plain-English instructions into code in the language you choose — 100% locally and offline.
</p>

<p align="center">
  <img src="https://shields.io" alt="AI Engine: Qwen 2.5 Coder 7B">
  <img src="https://shields.io" alt="Platforms: Windows, macOS, and Linux">
  <a href="https://pypi.org/project/arb-universal-ide/2.0.0/#description">
    <img src="https://shields.io" alt="PyPI Version">
  </a>
  <a href="https://github.com">
    <img src="https://shields.io" alt="Apache License 2.0">
  </a>
</p>

<p align="center">
  <a href="https://github.com">
    <img src="https://shields.io" alt="Download Windows Installer">
  </a>
</p>

---

## What is ARB?

**ARB** is an offline, AI-powered, multi-language transpiler IDE that converts plain English instructions into executable code locally. It includes an automated dependency management pipeline and embeds `llama-cpp-python` with **Qwen 2.5 Coder 7B** (~4.7 GB model downloaded automatically on first run) with zero API keys or cloud requirements.

## Key Features

- **100% Offline & Unlimited:** Runs locally with zero rate limits or subscriptions.
- **Zero-Config Embedded AI:** Automatically caches the coding model on first launch.
- **Flexible Input & Output:** Write logic in plain language to generate Python, C, Java, JavaScript, HTML/CSS, C++, or Go, with automated dependency installation and native file exports.

## Quick Install & Usage

Install directly via PyPI:
```bash
pip install arb-universal-ide
```

Or build/run from source (requires Python 3.9+, 8+ GB RAM, and ~5 GB free space):
```bash
git clone https://github.com
cd arb-universal-ide
pip install llama-cpp-python huggingface-hub pyinstaller
python app.py
```

## License

Licensed under the Apache License 2.0. See the repository's `LICENSE.md` for full details.
