# 📝 ARB Universal IDE & AI Compiler

<p align="center">
  <img src="https://shields.io" alt="Model Used">
  <img src="https://shields.io" alt="Platform Support">
  <img src="https://shields.io" alt="License">
</p>

<p align="center">
  <b>Programming, simplified. Write instructions row-by-row in plain English. No complex indentation. No syntax boilerplate.</b>
</p>

<p align="center">
  <a href="https://github.com">
    <img src="https://shields.io📥_Download-Windows_Installer-007acc?style=for-the-badge&logo=windows" alt="Download Installer" height="40">
  </a>
</p>

---

## ⚡ What is ARB?

**ARB** is an AI-driven, multi-language transpiler IDE. It allows you to write programmatic logic using standard English phrasing. The engine parses your unstructured pseudo-code block by block, automatically figures out and installs any required dependencies via an **Automated Pipeline**, and outputs executable script blocks targeting the language of your choice.

### 🚀 Key Features

* **Zero-Indentation Logic:** Express loops, conditional flows, and array states using pure conversational structuring.
* **Auto-Dependency Management:** If your plain-English code calls for data sheets or web scraping, ARB instantly identifies, fetches, and installs packages like `pandas` or `requests` silently before execution.
* **Multi-Language Architecture:** Write once in English, and compile cleanly into **Python, C, Java, JavaScript, HTML & CSS, C++, or Go**.
* **Direct File Export:** Saves output natively using the matching language extensions (e.g., `.py`, `.c`, `.js`) instead of custom runtime formats.

---

## 💻 Language Comparison Showcase

| Target Language | Your English Input Code | Compiled Production Output |
| :--- | :--- | :--- |
| **Python** | `create a variable numbers from 1 to 5`<br>`loop through numbers`<br>`if number is even print "Even:" and the number` | `numbers = list(range(1, 6))`<br>`for num in numbers:`<br>`    if num % 2 == 0:`<br>`        print(f"Even: {num}")` |
| **JavaScript** | `declare user score as 100`<br>`if score is greater than 50 print "Passed"` | `let userScore = 100;`<br>`if (userScore > 50) {`<br>`    console.log("Passed");`<br>`}` |

---

## 📦 How to Build Natively from Source

If you prefer running or tweaking the Python source code directly instead of utilizing our downloadable `Setup.exe` installer, follow these quick configuration steps:

### 1. Clone the Workspace Environment
```bash
git clone https://github.com
cd YOUR_REPO_NAME
```

### 2. Set Up Your API Key Credentials
ARB uses an OpenAI-compatible ecosystem interface runner. Get your free secret key token from your console dashboard and apply it securely to your machine terminal paths:

**Windows PowerShell:**
```powershell
\$env:GROQ_API_KEY="your_api_key_string_here"
```

**Linux / Mac Terminal:**
```bash
export GROQ_API_KEY="your_api_key_string_here"
```

### 3. Launch the App Window Engine
```bash
pip install groq pyinstaller
python app.py
```

---

## 🛠️ Free Licensing Deployment Info

This ecosystem application configuration framework is distributed entirely as open-source code architecture under the **MIT License**. Check out our live developer portfolio page links to test active roadmap updates!
