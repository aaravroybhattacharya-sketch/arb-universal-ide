import sys
import os
import re
import shutil
import subprocess
import threading
import webbrowser
import tkinter as tk
from tkinter import messagebox, ttk
from llama_cpp import Llama
from huggingface_hub import hf_hub_download

if os.name == "nt":
    import winreg

# Global model cache & lock to prevent duplicate loads
llm_engine = None
model_lock = threading.Lock()

# --- Initialize UI Window ---
root = tk.Tk()
root.title("ARB Multi-Language AI Compiler (Offline Embedded)")
root.geometry("1150x680")
root.configure(bg="#1e1e1e")

if os.path.exists("arb_icon.ico"):
    root.iconbitmap("arb_icon.ico")

# --- Top Navigation Bar ---
top_bar = tk.Frame(root, bg="#252526", height=50)
top_bar.pack(fill=tk.X, side=tk.TOP)

title_label = tk.Label(
    top_bar,
    text="📝 ARB AI Universal IDE (Local)",
    font=("Segoe UI", 12, "bold"),
    fg="#ffffff",
    bg="#252526"
)
title_label.pack(side=tk.LEFT, padx=20, pady=10)

lang_label = tk.Label(
    top_bar,
    text="Target Language:",
    fg="#aaaaaa",
    bg="#252526",
    font=("Segoe UI", 10)
)
lang_label.pack(side=tk.LEFT, padx=(20, 5))

language_var = tk.StringVar(value="Python")
lang_dropdown = ttk.Combobox(
    top_bar,
    textvariable=language_var,
    state="readonly",
    width=15,
    font=("Segoe UI", 10)
)
lang_dropdown["values"] = (
    "Python",
    "C",
    "C++",
    "C#",
    "Java",
    "JavaScript",
    "TypeScript",
    "HTML & CSS"
)
lang_dropdown.pack(side=tk.LEFT, padx=5)

# --- Main Split Window Layout ---
main_frame = tk.Frame(root, bg="#1e1e1e")
main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

# LEFT SIDE: Editor Panel
editor_frame = tk.Frame(main_frame, bg="#1e1e1e")
editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

editor_label = tk.Label(
    editor_frame,
    text="Write Plain English Logic Here:",
    fg="#aaaaaa",
    bg="#1e1e1e",
    font=("Segoe UI", 10)
)
editor_label.pack(anchor=tk.W, pady=(0, 5))

code_input = tk.Text(
    editor_frame,
    wrap=tk.WORD,
    undo=True,
    font=("Consolas", 12),
    bg="#2d2d2d",
    fg="#ffffff",
    insertbackground="white"
)
code_input.pack(fill=tk.BOTH, expand=True)

# RIGHT SIDE: Output Screen Terminal Panel
output_frame = tk.Frame(main_frame, bg="#1e1e1e")
output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

output_label = tk.Label(
    output_frame,
    text="AI Compiler & Execution Log Output:",
    fg="#aaaaaa",
    bg="#1e1e1e",
    font=("Segoe UI", 10)
)
output_label.pack(anchor=tk.W, pady=(0, 5))

terminal_output = tk.Text(
    output_frame,
    wrap=tk.WORD,
    font=("Consolas", 11),
    bg="#121212",
    fg="#00ff00",
    state=tk.DISABLED
)
terminal_output.pack(fill=tk.BOTH, expand=True)


# --- Thread-Safe UI Helpers ---
def update_terminal(text):
    """Safely updates the custom terminal UI on the main Tkinter thread."""
    def _append():
        terminal_output.config(state=tk.NORMAL)
        terminal_output.insert(tk.END, text)
        terminal_output.see(tk.END)
        terminal_output.config(state=tk.DISABLED)
    root.after(0, _append)


def reset_ui_state(show_popup=None):
    """Safely re-enables the Run button and optionally displays a popup on the main thread."""
    def _reset():
        run_button.config(state=tk.NORMAL, text="⚡ Compile & Execute Logic")
        if show_popup:
            title, msg, is_error = show_popup
            if is_error:
                messagebox.showerror(title, msg)
            else:
                messagebox.showinfo(title, msg)
    root.after(0, _reset)


# --- Toolchain / PATH Verification & Auto-Installer ---
def refresh_windows_path():
    """Reloads the Windows System and User PATH from the Registry into the current Python process."""
    if os.name != "nt":
        return

    paths = []
    registry_locations = [
        (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
        (winreg.HKEY_CURRENT_USER, r"Environment"),
    ]

    for root_key, sub_key in registry_locations:
        try:
            with winreg.OpenKey(root_key, sub_key) as key:
                val, _ = winreg.QueryValueEx(key, "Path")
                if val:
                    expanded = os.path.expandvars(val)
                    paths.extend(expanded.split(";"))
        except FileNotFoundError:
            continue

    current_paths = os.environ.get("PATH", "").split(";")
    merged = []
    for p in paths + current_paths:
        p = p.strip()
        if p and p not in merged:
            merged.append(p)
    os.environ["PATH"] = ";".join(merged)


def install_missing_toolchains(missing_items):
    """Installs missing compilers/runtimes via winget in a background thread."""
    def _worker():
        root.after(0, lambda: run_button.config(state=tk.DISABLED, text="📦 Installing Toolchains..."))
        update_terminal("\n🛠️ Starting automated toolchain installation via winget...\n")

        installed_ids = set()

        for name, cmd, winget_id in missing_items:
            if winget_id in installed_ids:
                update_terminal(f"ℹ️ {name} is covered by already-installed package ({winget_id}).\n")
                continue

            update_terminal(f"\n📥 Installing {name} ({winget_id})... Please wait (may take 1-3 minutes)...\n")
            try:
                proc = subprocess.run(
                    [
                        "winget", "install",
                        "--id", winget_id,
                        "-e", "--silent",
                        "--accept-package-agreements",
                        "--accept-source-agreements"
                    ],
                    capture_output=True,
                    text=True
                )
                if proc.returncode == 0:
                    update_terminal(f"✅ Successfully installed {name}!\n")
                    installed_ids.add(winget_id)
                else:
                    update_terminal(f"⚠️ winget returned code {proc.returncode} for {name}:\n{proc.stderr or proc.stdout}\n")
            except Exception as e:
                update_terminal(f"❌ Failed to install {name}: {e}\n")

        update_terminal("\n🔄 Refreshing system PATH environment variables...\n")
        refresh_windows_path()

        update_terminal("\n🔎 Re-checking System Toolchain PATH Diagnostics:\n")
        tools = [
            ("Python", sys.executable),
            ("GCC (C)", "gcc"),
            ("G++ (C++)", "g++"),
            (".NET SDK (C#)", "dotnet"),
            ("JDK (Java)", "javac"),
            ("Node.js (JS/TS)", "node"),
        ]
        for label, binary in tools:
            found = shutil.which(binary)
            status = f"✅ {label}: Found ({found})" if found else f"⚠️ {label}: Still not found (try restarting the IDE)"
            update_terminal(f"  {status}\n")

        update_terminal("\n✅ Setup check complete!\n")
        reset_ui_state()

    threading.Thread(target=_worker, daemon=True).start()


def check_toolchain_availability(target_lang):
    """Verifies that the required compiler or runtime exists in the system PATH."""
    refresh_windows_path()
    requirements = {
        "Python": [(sys.executable, "Python interpreter")],
        "C": [("gcc", "GCC / MinGW C Compiler")],
        "C++": [("g++", "G++ / MinGW C++ Compiler")],
        "C#": [("dotnet", ".NET SDK (dotnet)")],
        "Java": [("javac", "Java JDK Compiler (javac)"), ("java", "Java Runtime (java)")],
        "JavaScript": [("node", "Node.js Runtime")],
        "TypeScript": [("node", "Node.js Runtime"), ("npx", "NPX Package Runner")],
        "HTML & CSS": []
    }

    missing = []
    for binary, label in requirements.get(target_lang, []):
        if not shutil.which(binary):
            missing.append(f"• {label} ('{binary}' not found in PATH)")

    if missing:
        return False, (
            f"❌ Missing System Toolchain for {target_lang}:\n"
            + "\n".join(missing)
            + "\n\nPlease install the missing toolchain or restart the IDE to refresh PATH."
        )
    return True, ""


def check_all_toolchains_on_startup():
    """Checks all compilers on launch and offers to auto-install missing ones."""
    refresh_windows_path()

    # Format: (Display Name, Executable Name, Winget Package ID)
    tools = [
        ("Python", sys.executable, "Python.Python.3.12"),
        ("GCC (C)", "gcc", "BrechtSanders.WinLibs.POSIX.UCRT"),
        ("G++ (C++)", "g++", "BrechtSanders.WinLibs.POSIX.UCRT"),
        (".NET SDK (C#)", "dotnet", "Microsoft.DotNet.SDK.8"),
        ("JDK (Java)", "javac", "EclipseAdoptium.Temurin.21.JDK"),
        ("Node.js (JS/TS)", "node", "OpenJS.NodeJS.LTS"),
    ]

    status_lines = ["🔎 System Toolchain PATH Diagnostics:\n"]
    missing_tools = []

    for name, cmd, winget_id in tools:
        path = shutil.which(cmd)
        if path:
            status_lines.append(f"  ✅ {name}: Found ({path})\n")
        else:
            status_lines.append(f"  ⚠️ {name}: Not found in PATH\n")
            missing_tools.append((name, cmd, winget_id))

    update_terminal("".join(status_lines))

    if missing_tools:
        if os.name != "nt" or not shutil.which("winget"):
            update_terminal("\n⚠️ 'winget' is not available on this system. Please install missing tools manually.\n")
            return

        missing_names = ", ".join(item[0] for item in missing_tools)
        ask = messagebox.askyesno(
            "Missing Compilers & Runtimes",
            f"The following toolchains are missing from your PATH:\n\n{missing_names}\n\n"
            "Would you like ARB IDE to automatically download and install all of them now using winget?"
        )
        if ask:
            install_missing_toolchains(missing_tools)
        else:
            update_terminal("\n⏭️ Skipped automatic installation. Only installed languages can be executed.\n")
    else:
        update_terminal("\n🎉 All toolchains are installed and ready!\n")


# --- Core Embedded AI & Execution Pipeline ---
def get_embedded_model():
    """Thread-safe lazy loader for the local GGUF model."""
    global llm_engine
    with model_lock:
        if llm_engine is None:
            update_terminal("📥 Checking/Downloading local Qwen 2.5 Coder model (~4.7 GB on first run)...\n")
            model_path = hf_hub_download(
                repo_id="Qwen/Qwen2.5-Coder-7B-Instruct-GGUF",
                filename="qwen2.5-coder-7b-instruct-q4_k_m.gguf"
            )
            update_terminal("🧠 Loading AI model directly into system memory...\n")
            llm_engine = Llama(
                model_path=model_path,
                n_ctx=4096,
                n_gpu_layers=-1,
                verbose=False
            )
    return llm_engine


def auto_install_dependencies(compiled_code):
    """Scans Python code for third-party imports and installs missing packages."""
    update_terminal("🔍 Analyzing Python imports for third-party dependencies...\n")
    imports = re.findall(r'^\s*(?:import|from)\s+([a-zA-Z0-9_]+)', compiled_code, re.MULTILINE)

    stdlib = getattr(sys, "stdlib_module_names", {
        'sys', 'os', 'math', 'random', 'time', 'json', 're', 'datetime',
        'collections', 'itertools', 'io', 'pathlib', 'subprocess', 'threading'
    })
    packages_to_check = set(imports) - stdlib

    pypi_alias = {
        "cv2": "opencv-python",
        "PIL": "Pillow",
        "sklearn": "scikit-learn",
        "yaml": "PyYAML",
        "bs4": "beautifulsoup4"
    }

    for package in packages_to_check:
        try:
            __import__(package)
        except ImportError:
            pip_name = pypi_alias.get(package, package)
            update_terminal(f"📦 Missing package '{package}'. Installing '{pip_name}' via pip...\n")
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", pip_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                update_terminal(f"✅ Successfully installed: {pip_name}\n")
            except Exception as pip_err:
                update_terminal(f"⚠️ Automatic install failed for '{pip_name}': {pip_err}\n")


def execute_compiled_artifact(target_lang, source_file, compiled_source):
    """Compiles and executes the generated source file in an isolated subprocess."""
    exe_suffix = ".exe" if os.name == "nt" else ""
    timeout_sec = 25

    try:
        if target_lang == "Python":
            auto_install_dependencies(compiled_source)
            update_terminal("🚀 Running Python script in isolated subprocess...\n")
            res = subprocess.run(
                [sys.executable, source_file],
                capture_output=True, text=True, timeout=timeout_sec
            )
            return res.stdout, res.stderr, res.returncode

        elif target_lang == "C":
            bin_file = f"output_c{exe_suffix}"
            update_terminal(f"🔨 Compiling {source_file} with gcc...\n")
            comp = subprocess.run(
                ["gcc", source_file, "-o", bin_file],
                capture_output=True, text=True, timeout=timeout_sec
            )
            if comp.returncode != 0:
                return "", f"GCC Compilation Error:\n{comp.stderr}", comp.returncode
            update_terminal(f"🚀 Executing ./{bin_file}...\n")
            res = subprocess.run(
                [os.path.abspath(bin_file)],
                capture_output=True, text=True, timeout=timeout_sec
            )
            return res.stdout, res.stderr, res.returncode

        elif target_lang == "C++":
            bin_file = f"output_cpp{exe_suffix}"
            update_terminal(f"🔨 Compiling {source_file} with g++...\n")
            comp = subprocess.run(
                ["g++", source_file, "-o", bin_file],
                capture_output=True, text=True, timeout=timeout_sec
            )
            if comp.returncode != 0:
                return "", f"G++ Compilation Error:\n{comp.stderr}", comp.returncode
            update_terminal(f"🚀 Executing ./{bin_file}...\n")
            res = subprocess.run(
                [os.path.abspath(bin_file)],
                capture_output=True, text=True, timeout=timeout_sec
            )
            return res.stdout, res.stderr, res.returncode

        elif target_lang == "C#":
            cs_proj_dir = os.path.abspath("arb_cs_proj")
            if not os.path.exists(cs_proj_dir):
                update_terminal("🏗️ Initializing .NET C# console workspace...\n")
                init_res = subprocess.run(
                    ["dotnet", "new", "console", "-o", cs_proj_dir, "--force"],
                    capture_output=True, text=True, timeout=timeout_sec
                )
                if init_res.returncode != 0:
                    return "", f".NET Project Init Error:\n{init_res.stderr}", init_res.returncode

            shutil.copyfile(source_file, os.path.join(cs_proj_dir, "Program.cs"))
            update_terminal("🔨 Building & running C# project with dotnet...\n")
            res = subprocess.run(
                ["dotnet", "run", "--project", cs_proj_dir],
                capture_output=True, text=True, timeout=timeout_sec
            )
            return res.stdout, res.stderr, res.returncode

        elif target_lang == "Java":
            class_name = os.path.splitext(source_file)[0]
            update_terminal(f"🔨 Compiling {source_file} with javac...\n")
            comp = subprocess.run(
                ["javac", source_file],
                capture_output=True, text=True, timeout=timeout_sec
            )
            if comp.returncode != 0:
                return "", f"Javac Compilation Error:\n{comp.stderr}", comp.returncode
            update_terminal(f"🚀 Executing java {class_name}...\n")
            res = subprocess.run(
                ["java", class_name],
                capture_output=True, text=True, timeout=timeout_sec
            )
            return res.stdout, res.stderr, res.returncode

        elif target_lang == "JavaScript":
            update_terminal(f"🚀 Executing {source_file} with Node.js...\n")
            res = subprocess.run(
                ["node", source_file],
                capture_output=True, text=True, timeout=timeout_sec
            )
            return res.stdout, res.stderr, res.returncode

        elif target_lang == "TypeScript":
            update_terminal(f"🚀 Transpiling & executing {source_file} with tsx...\n")
            npx_cmd = "npx.cmd" if os.name == "nt" else "npx"
            res = subprocess.run(
                [npx_cmd, "-y", "tsx", source_file],
                capture_output=True, text=True, timeout=timeout_sec
            )
            return res.stdout, res.stderr, res.returncode

        elif target_lang == "HTML & CSS":
            abs_html = os.path.abspath(source_file)
            webbrowser.open(f"file://{abs_html}")
            return f"🌐 Opened {abs_html} in your default web browser.", "", 0

    except subprocess.TimeoutExpired:
        return "", f"⏱️ Execution timed out after {timeout_sec} seconds (possible infinite loop).", 1


def background_compiler_worker(english_code, target_lang):
    """Processes local AI inference, compilation, and execution inside a worker thread."""
    try:
        # 1. Verify system toolchain before doing heavy inference
        ok, err_msg = check_toolchain_availability(target_lang)
        if not ok:
            update_terminal(f"\n{err_msg}\n")
            reset_ui_state(("Missing Toolchain", err_msg, True))
            return

        # 2. Load model and generate source code
        llm = get_embedded_model()

        system_prompt = (
            f"You are a strict code compiler. Translate the user's plain English programming logic "
            f"into complete, runnable, syntactically correct {target_lang} source code. Rules:\n"
            f"1. Conform strictly to {target_lang} syntax and include all necessary imports/using/headers and main entry points.\n"
            f"2. Output ONLY raw executable {target_lang} code.\n"
            f"3. Do NOT include markdown code fences (```), explanations, or notes.\n"
            f"4. Do NOT include blocking interactive input calls (like input(), scanf(), cin, Console.ReadLine(), Scanner) so automated execution completes cleanly."
        )

        response = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Translate this logic into {target_lang}:\n\n{english_code}"}
            ],
            temperature=0.0
        )

        compiled_source = response["choices"][0]["message"]["content"].strip()

        # Strip accidental markdown fences if emitted
        if compiled_source.startswith("```"):
            lines = compiled_source.splitlines()
            compiled_source = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:]).strip()

        update_terminal(f"--- Compiled {target_lang} Source ---\n")
        update_terminal(compiled_source + "\n")
        update_terminal("-------------------------------------\n\n")

        # 3. Determine output filename (handle Java public class naming)
        extension_map = {
            "Python": ".py",
            "C": ".c",
            "C++": ".cpp",
            "C#": ".cs",
            "Java": ".java",
            "JavaScript": ".js",
            "TypeScript": ".ts",
            "HTML & CSS": ".html"
        }

        if target_lang == "Java":
            match = re.search(r'public\s+class\s+([A-Za-z_][A-Za-z0-9_]*)', compiled_source)
            base_name = match.group(1) if match else "Main"
            output_file_name = f"{base_name}.java"
        else:
            output_file_name = f"output{extension_map.get(target_lang, '.txt')}"

        with open(output_file_name, "w", encoding="utf-8") as out_file:
            out_file.write(compiled_source)

        # 4. Compile and run
        stdout, stderr, returncode = execute_compiled_artifact(
            target_lang, output_file_name, compiled_source
        )

        if stdout:
            update_terminal(f"\n💻 Program Output:\n{stdout}\n")
        if stderr:
            update_terminal(f"\n⚠️ Compiler / Runtime Diagnostics:\n{stderr}\n")
        if not stdout and not stderr:
            update_terminal("\n💻 Execution Complete (No stdout returned).\n")

        if returncode == 0:
            reset_ui_state((
                "Build & Run Success",
                f"Source built and executed cleanly!\nSaved as '{output_file_name}'.",
                False
            ))
        else:
            reset_ui_state((
                "Build / Runtime Error",
                f"Process exited with code {returncode}. Check the terminal log for details.",
                True
            ))

    except Exception as e:
        update_terminal(f"\n❌ Operational Processing Error:\n{e}\n")
        reset_ui_state(("Error", str(e), True))


def start_compilation():
    english_code = code_input.get("1.0", tk.END).strip()
    target_lang = language_var.get()

    if not english_code:
        messagebox.showwarning("Empty Editor", "Please enter plain English instructions in the editor.")
        return

    terminal_output.config(state=tk.NORMAL)
    terminal_output.delete("1.0", tk.END)
    terminal_output.config(state=tk.DISABLED)

    update_terminal(f"🤖 Transpiling English into {target_lang}...\n\n")
    run_button.config(state=tk.DISABLED, text="⏳ Processing...")

    threading.Thread(
        target=background_compiler_worker,
        args=(english_code, target_lang),
        daemon=True
    ).start()


# --- Footer Action Toolbar ---
bottom_frame = tk.Frame(root, bg="#1e1e1e")
bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=15)

run_button = tk.Button(
    bottom_frame,
    text="⚡ Compile & Execute Logic",
    font=("Segoe UI", 11, "bold"),
    fg="#ffffff",
    bg="#007acc",
    activebackground="#005999",
    padx=25,
    command=start_compilation
)
run_button.pack()

# Run initial PATH diagnostic check & auto-installer prompt on launch
check_all_toolchains_on_startup()

root.mainloop()
