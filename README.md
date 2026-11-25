# ARB Universal IDE v2.0.0

**Build real software with plain words—100% locally and offline.**

ARB Universal IDE turns plain-English instructions into working, multi-file code across **8 programming languages** with zero API keys, cloud accounts, or rate limits.

🌐 **Website:** [arb-universal-ide.vercel.app](https://arb-universal-ide.vercel.app)  
📦 **Latest Release:** [Download v2.0.0 Windows Installer](https://github.com)  
🐍 **PyPI:** [arb-universal-ide](https://pypi.org)

---

## ✨ What's New in v2.0.0

* **Multi-Backend & Multi-Model AI:** Switch between the built-in **Embedded GGUF** runtime (`Qwen 2.5 Coder 1.5B, 3B, 7B`) or connect directly to your local **Ollama** (`localhost:11434`) and **LM Studio** (`localhost:1234`) servers with one-click model discovery.
* **Project Workspaces & Multi-File Generation:** Open any project directory in the sidebar file explorer. ARB reads existing project files for context and generates or edits multi-file projects automatically.
* **Self-Healing Auto-Fix Loop:** When generated code hits a compiler or runtime error, ARB automatically feeds the traceback back to the AI to repair syntax and import bugs.
* **One-Click Undo Checkpoints:** Snapshots affected workspace files before every AI edit so you can revert changes safely in one click.
* **8 Supported Languages:** Python, C, C++, C#, Java, JavaScript, TypeScript, and HTML & CSS.

---

## 🚀 Installation

### Option 1: Windows Standalone Installer (Recommended)
1. Download **`ARB_Universal_IDE.exe`** from the [Releases Page](https://github.com).
2. Run the installer and launch **ARB Universal IDE** from your Start Menu or Desktop.

### Option 2: Run via Python (Windows, macOS & Linux)
```bash
pip install arb-universal-ide
```
*(Note: If you use **Ollama** or **LM Studio** as your backend, `llama-cpp-python` is optional and no C++ compiler is required.)*

---

## 🛠 How It Works
1. **Choose your AI Backend:** Select **Embedded (GGUF)** for zero-setup offline coding, or pick **Ollama / LM Studio** to use models already installed on your machine.
2. **Describe your project:** Open a workspace folder (`~/ARB_Workspace` by default) and write what you want to build in plain English.
3. **Generate, Run & Auto-Fix:** Click **Generate & Run** to write files, install missing Python packages, compile, execute in the built-in terminal, and auto-repair errors.

---

## 📄 License
Open-source under the **Apache 2.0 License**.
