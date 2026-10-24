# ARB Universal IDE & AI Compiler

<p align="center">
  Turn plain-English instructions into code in the language you choose.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/AI%20provider-Groq-F55036?style=for-the-badge&logo=groq&logoColor=white" alt="AI provider: Groq">
  <img src="https://img.shields.io/badge/Platforms-Windows%20%7C%20macOS%20%7C%20Linux-4C8EDA?style=for-the-badge" alt="Platforms: Windows, macOS, and Linux source setup">
  <a href="https://opensource.org/license/mit">
    <img src="https://img.shields.io/badge/License-MIT-2ea44f?style=for-the-badge" alt="MIT License">
  </a>
</p>

<p align="center">
  <a href="https://github.com/aaravroybhattacharya-sketch/arb-universal-ide/releases/tag/v1.0.0">
    <img src="https://img.shields.io/badge/Download-Windows%20Installer-0078D4?style=for-the-badge&logo=windows&logoColor=white" alt="Download the Windows installer">
  </a>
</p>

---

## What is ARB?

**ARB** is an AI-powered, multi-language transpiler IDE. Describe program logic in everyday English, and ARB turns it into executable code. Its automated pipeline can identify and install dependencies required by your instructions.

> **Model information:** The published setup uses a `GROQ_API_KEY`, which identifies Groq as the AI provider. The repository does not document the specific model ID, so it is not listed as a model name here.

## Features

- **Write without indentation:** Describe loops, conditions, and lists in plain language.
- **Automated dependency management:** Identify and install packages needed by your instructions.
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

### 1. Clone the repository

```bash
git clone https://github.com/aaravroybhattacharya-sketch/arb-universal-ide.git
cd arb-universal-ide
```

### 2. Configure your Groq API key

Create an API key in your Groq account and set it in your terminal. Keep the key private.

**Windows PowerShell**

```powershell
$env:GROQ_API_KEY="your_api_key"
```

**macOS / Linux**

```bash
export GROQ_API_KEY="your_api_key"
```

### 3. Install dependencies and run

```bash
pip install groq pyinstaller
python app.py
```

## License

ARB is distributed under the **MIT License**. See the [MIT License text](https://opensource.org/license/mit).
