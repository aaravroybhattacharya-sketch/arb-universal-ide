# ARB Universal IDE & AI Compiler

<p align="center">
  Turn plain-English instructions into multi-language code 100% locally and offline using the embedded Qwen 2.5 Coder 7B model [https://shields.io].
</p>

## Overview
**ARB** is an offline, AI-powered transpiler IDE that converts everyday English descriptions into executable code across languages like Python, C, Java, JavaScript, and more. It embeds `llama-cpp-python` with the Qwen 2.5 Coder 7B model (~4.7 GB) directly, requiring no API keys, cloud accounts, or external servers.

## Key Features
- **Offline & Private:** Zero rate limits, subscriptions, or cloud dependencies.
- **Automated Pipeline:** Handles code generation, dependency identification/installation, and native file export (`.py`, `.c`, `.js`, etc.).
- **Plain English Input:** Write logic without strict indentations.

## Quick Install

Via PyPI:
```bash
pip install arb-universal-ide
```

From Source (Windows, macOS, or Linux with Python 3.9+ and 8GB+ RAM):
```bash
git clone https://github.com
cd arb-universal-ide
pip install llama-cpp-python huggingface-hub pyinstaller
python app.py
```

## License
Licensed under the Apache License 2.0. See the repository for full details.
