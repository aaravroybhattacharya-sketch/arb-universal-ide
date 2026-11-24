import json
import os
import re
import shutil
import subprocess
import sys
import threading
import urllib.error
import urllib.request
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from llama_cpp import Llama
    from huggingface_hub import hf_hub_download
    HAS_LLAMA_CPP = True
except ImportError:
    HAS_LLAMA_CPP = False
    Llama = None
    hf_hub_download = None


EMBEDDED_MODELS = {
    "Qwen 2.5 Coder 7B": (
        "Qwen/Qwen2.5-Coder-7B-Instruct-GGUF",
        "qwen2.5-coder-7b-instruct-q4_k_m.gguf",
    ),
    "Qwen 2.5 Coder 3B": (
        "Qwen/Qwen2.5-Coder-3B-Instruct-GGUF",
        "qwen2.5-coder-3b-instruct-q4_k_m.gguf",
    ),
    "Qwen 2.5 Coder 1.5B": (
        "Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF",
        "qwen2.5-coder-1.5b-instruct-q4_k_m.gguf",
    ),
}

workspace_dir = os.path.abspath(
    os.path.join(os.path.expanduser("~"), "ARB_Workspace")
)
os.makedirs(workspace_dir, exist_ok=True)

undo_history = []
llm_engine = None
loaded_model_name = None
model_lock = threading.Lock()


root = tk.Tk()
root.title("ARB Universal IDE")
root.geometry("1280x800")
root.configure(bg="#1e1e1e")

top_bar = tk.Frame(root, bg="#252526", height=46)
top_bar.pack(fill=tk.X)
top_bar.pack_propagate(False)

main_frame = tk.Frame(root, bg="#1e1e1e")
main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

sidebar = tk.Frame(main_frame, bg="#252526", width=210)
sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
sidebar.pack_propagate(False)

editor = tk.Frame(main_frame, bg="#252526")
editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

terminal_frame = tk.Frame(main_frame, bg="#252526", width=360)
terminal_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))
terminal_frame.pack_propagate(False)


tk.Label(
    top_bar,
    text="Backend:",
    fg="#aaaaaa",
    bg="#252526",
).pack(side=tk.LEFT, padx=(10, 4))

backend_var = tk.StringVar(value="Embedded (GGUF)")
backend_dropdown = ttk.Combobox(
    top_bar,
    textvariable=backend_var,
    state="readonly",
    width=18,
    values=(
        "Embedded (GGUF)",
        "Ollama (Local API)",
        "LM Studio (Local API)",
    ),
)
backend_dropdown.pack(side=tk.LEFT)

tk.Label(
    top_bar,
    text="Model:",
    fg="#aaaaaa",
    bg="#252526",
).pack(side=tk.LEFT, padx=(10, 4))

model_var = tk.StringVar(value="Qwen 2.5 Coder 7B")
model_dropdown = ttk.Combobox(
    top_bar,
    textvariable=model_var,
    state="readonly",
    width=24,
    values=list(EMBEDDED_MODELS),
)
model_dropdown.pack(side=tk.LEFT)

refresh_models_button = tk.Button(
    top_bar,
    text="Refresh",
    bg="#333333",
    fg="#ffffff",
    relief=tk.FLAT,
)
refresh_models_button.pack(side=tk.LEFT, padx=4)

tk.Label(
    top_bar,
    text="Language:",
    fg="#aaaaaa",
    bg="#252526",
).pack(side=tk.LEFT, padx=(10, 4))

language_var = tk.StringVar(value="Python")
language_dropdown = ttk.Combobox(
    top_bar,
    textvariable=language_var,
    state="readonly",
    width=13,
    values=("Python", "C", "C++", "C#", "Java",
            "JavaScript", "TypeScript", "HTML & CSS"),
)
language_dropdown.pack(side=tk.LEFT)

auto_fix_var = tk.BooleanVar(value=True)
tk.Checkbutton(
    top_bar,
    text="Auto-Fix Errors",
    variable=auto_fix_var,
    fg="#cccccc",
    bg="#252526",
    selectcolor="#1e1e1e",
    activebackground="#252526",
).pack(side=tk.LEFT, padx=(10, 5))


sidebar_header = tk.Frame(sidebar, bg="#252526")
sidebar_header.pack(fill=tk.X, padx=8, pady=8)

tk.Label(
    sidebar_header,
    text="WORKSPACE FILES",
    fg="#bbbbbb",
    bg="#252526",
    font=("Segoe UI", 9, "bold"),
).pack(side=tk.LEFT)

file_listbox = tk.Listbox(
    sidebar,
    bg="#252526",
    fg="#e0e0e0",
    selectbackground="#094771",
    selectforeground="#ffffff",
    borderwidth=0,
    highlightthickness=0,
    font=("Consolas", 10),
)
file_listbox.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

open_folder_button = tk.Button(
    sidebar,
    text="Open Folder",
    bg="#0e639c",
    fg="#ffffff",
    relief=tk.FLAT,
    pady=5,
)
open_folder_button.pack(fill=tk.X, padx=8, pady=(0, 5))

undo_button = tk.Button(
    sidebar,
    text="Undo AI Edit",
    bg="#333333",
    fg="#ffffff",
    relief=tk.FLAT,
    pady=5,
    state=tk.DISABLED,
)
undo_button.pack(fill=tk.X, padx=8, pady=(0, 8))


tk.Label(
    editor,
    text="Describe what you want to build:",
    fg="#bbbbbb",
    bg="#252526",
).pack(anchor="w", padx=10, pady=(8, 4))

prompt_text = tk.Text(
    editor,
    height=7,
    bg="#1e1e1e",
    fg="#e0e0e0",
    insertbackground="#ffffff",
    font=("Segoe UI", 11),
    borderwidth=0,
    padx=10,
    pady=10,
)
prompt_text.pack(fill=tk.X, padx=10)

generate_button = tk.Button(
    editor,
    text="Generate && Run",
    bg="#0e639c",
    fg="#ffffff",
    relief=tk.FLAT,
    pady=8,
    font=("Segoe UI", 10, "bold"),
)
generate_button.pack(fill=tk.X, padx=10, pady=10)

tk.Label(
    editor,
    text="Generated code:",
    fg="#bbbbbb",
    bg="#252526",
).pack(anchor="w", padx=10, pady=(4, 4))

code_text = tk.Text(
    editor,
    bg="#181818",
    fg="#d4d4d4",
    insertbackground="#ffffff",
    font=("Consolas", 11),
    borderwidth=0,
    padx=10,
    pady=10,
    wrap=tk.NONE,
)
code_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))


terminal_header = tk.Frame(terminal_frame, bg="#252526")
terminal_header.pack(fill=tk.X, padx=8, pady=8)

tk.Label(
    terminal_header,
    text="OUTPUT",
    fg="#bbbbbb",
    bg="#252526",
    font=("Segoe UI", 9, "bold"),
).pack(side=tk.LEFT)

clear_terminal_button = tk.Button(
    terminal_header,
    text="Clear",
    bg="#333333",
    fg="#ffffff",
    relief=tk.FLAT,
)
clear_terminal_button.pack(side=tk.RIGHT)

terminal_text = tk.Text(
    terminal_frame,
    bg="#181818",
    fg="#d4d4d4",
    font=("Consolas", 10),
    borderwidth=0,
    padx=8,
    pady=8,
    wrap=tk.WORD,
)
terminal_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))


def write_terminal(text):
    def append():
        terminal_text.configure(state=tk.NORMAL)
        terminal_text.insert(tk.END, text)
        terminal_text.see(tk.END)

    root.after(0, append)


def reset_ui():
    root.after(
        0,
        lambda: generate_button.config(
            state=tk.NORMAL,
            text="Generate && Run",
        ),
    )


def safe_workspace_path(relative_path):
    if not isinstance(relative_path, str):
        return None

    clean_path = relative_path.strip()
    clean_path = clean_path.replace("/", os.sep).replace("\\", os.sep)
    clean_path = clean_path.lstrip("/\\")

    full_path = os.path.abspath(
        os.path.join(workspace_dir, os.path.normpath(clean_path))
    )
    workspace = os.path.abspath(workspace_dir)

    try:
        if os.path.commonpath((workspace, full_path)) != workspace:
            return None
    except ValueError:
        return None

    return full_path


def refresh_file_tree():
    file_listbox.delete(0, tk.END)
    os.makedirs(workspace_dir, exist_ok=True)

    for base_directory, directories, filenames in os.walk(workspace_dir):
        directories[:] = [
            directory
            for directory in directories
            if not directory.startswith(".")
            and directory not in {
                "__pycache__",
                "node_modules",
                "bin",
                "obj",
            }
        ]

        for filename in sorted(filenames):
            full_path = os.path.join(base_directory, filename)
            relative_path = os.path.relpath(full_path, workspace_dir)
            file_listbox.insert(tk.END, relative_path)


def open_workspace_folder():
    global workspace_dir

    selected_directory = filedialog.askdirectory(
        initialdir=workspace_dir,
        title="Select Project Workspace",
    )

    if selected_directory:
        workspace_dir = os.path.abspath(selected_directory)
        refresh_file_tree()
        write_terminal(
            "Switched workspace to: "
            + workspace_dir
            + "\n"
        )


def open_selected_file(event=None):
    selection = file_listbox.curselection()
    if not selection:
        return

    relative_path = file_listbox.get(selection[0])
    full_path = safe_workspace_path(relative_path)

    if not full_path:
        return

    try:
        with open(full_path, "r", encoding="utf-8",
                  errors="replace") as file_handle:
            content = file_handle.read()

        code_text.delete("1.0", tk.END)
        code_text.insert("1.0", content)
    except OSError as error:
        write_terminal("Could not open file: " + str(error) + "\n")


def save_workspace_snapshot(relative_paths):
    snapshot = {}

    for relative_path in relative_paths:
        full_path = safe_workspace_path(relative_path)

        if full_path and os.path.isfile(full_path):
            with open(full_path, "r", encoding="utf-8",
                      errors="replace") as file_handle:
                snapshot[relative_path] = file_handle.read()
        else:
            snapshot[relative_path] = None

    undo_history.append(snapshot)
    root.after(0, lambda: undo_button.config(state=tk.NORMAL))


def undo_last_edit():
    if not undo_history:
        messagebox.showinfo(
            "Nothing to Undo",
            "No previous AI file changes to revert.",
        )
        return

    snapshot = undo_history.pop()

    for relative_path, old_content in snapshot.items():
        full_path = safe_workspace_path(relative_path)

        if not full_path:
            continue

        if old_content is None:
            if os.path.isfile(full_path):
                os.remove(full_path)
        else:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as file_handle:
                file_handle.write(old_content)

    refresh_file_tree()
    write_terminal("Reverted the last AI file edit.\n")

    if not undo_history:
        undo_button.config(state=tk.DISABLED)


def parse_multi_file_output(raw_text, default_filename):
    pattern = re.compile(
        r"===FILE:\s*(.+?)\s*===\r?\n"
        r"(.*?)"
        r"(?=\r?\n===FILE:|\Z)",
        re.DOTALL,
    )

    matches = pattern.findall(raw_text)
    generated_files = {}

    for filename, content in matches:
        filename = filename.strip().replace("\\", "/").lstrip("/")
        content = re.sub(
            r"^```[a-zA-Z0-9_+-]*\s*\n|```$",
            "",
            content.strip(),
            flags=re.MULTILINE,
        ).strip()

        if filename:
            generated_files[filename] = content

    if not generated_files:
        content = re.sub(
            r"^```[a-zA-Z0-9_+-]*\s*\n|```$",
            "",
            raw_text.strip(),
            flags=re.MULTILINE,
        ).strip()
        generated_files[default_filename] = content

    return generated_files


def fetch_external_models(backend_name):
    try:
        if "Ollama" in backend_name:
            url = "http://localhost:11434/api/tags"
        else:
            url = "http://localhost:1234/v1/models"

        request = urllib.request.Request(url)

        with urllib.request.urlopen(request, timeout=2) as response:
            data = json.loads(response.read().decode("utf-8"))

        if "Ollama" in backend_name:
            return [
                item["name"]
                for item in data.get("models", [])
                if "name" in item
            ]

        return [
            item["id"]
            for item in data.get("data", [])
            if "id" in item
        ]

    except (
        OSError,
        urllib.error.URLError,
        json.JSONDecodeError,
        TimeoutError,
    ):
        return []


def sync_model_dropdown(event=None):
    backend_name = backend_var.get()

    if "Embedded" in backend_name:
        model_names = list(EMBEDDED_MODELS)
        model_dropdown["values"] = model_names

        if model_var.get() not in model_names:
            model_var.set(model_names[0])

        return

    model_names = fetch_external_models(backend_name)

    if model_names:
        model_dropdown["values"] = model_names

        if model_var.get() not in model_names:
            model_var.set(model_names[0])

        write_terminal(
            "Found "
            + str(len(model_names))
            + " model(s) in "
            + backend_name
            + ".\n"
        )
    else:
        model_dropdown["values"] = ["No local models found"]
        model_var.set("No local models found")
        write_terminal(
            "Could not connect to "
            + backend_name
            + ". Make sure it is running locally.\n"
        )


def build_workspace_context(maximum_characters=6000):
    allowed_extensions = {
        ".py",
        ".c",
        ".cpp",
        ".h",
        ".cs",
        ".java",
        ".js",
        ".ts",
        ".html",
        ".css",
        ".json",
    }

    chunks = []
    total_characters = 0

    for base_directory, directories, filenames in os.walk(workspace_dir):
        directories[:] = [
            directory
            for directory in directories
            if not directory.startswith(".")
            and directory not in {
                "__pycache__",
                "node_modules",
                "bin",
                "obj",
            }
        ]

        for filename in sorted(filenames):
            extension = os.path.splitext(filename)[1].lower()

            if extension not in allowed_extensions:
                continue

            full_path = os.path.join(base_directory, filename)
            relative_path = os.path.relpath(full_path, workspace_dir)

            try:
                with open(full_path, "r", encoding="utf-8",
                          errors="replace") as file_handle:
                    content = file_handle.read()

                chunk = (
                    "--- EXISTING FILE: "
                    + relative_path
                    + " ---\n"
                    + content
                    + "\n"
                )

                if total_characters + len(chunk) > maximum_characters:
                    break

                chunks.append(chunk)
                total_characters += len(chunk)

            except OSError:
                continue

    return "\n".join(chunks)


def get_embedded_model(model_label):
    global llm_engine, loaded_model_name

    if model_label not in EMBEDDED_MODELS:
        raise ValueError("Unknown embedded model")

    if not HAS_LLAMA_CPP:
        raise RuntimeError(
            "llama-cpp-python is not installed. "
            "Choose Ollama or LM Studio."
        )

    repository, filename = EMBEDDED_MODELS[model_label]

    with model_lock:
        if (
            llm_engine is None
            or loaded_model_name != model_label
        ):
            write_terminal(
                "Downloading/loading "
                + model_label
                + "...\n"
            )

            model_path = hf_hub_download(
                repo_id=repository,
                filename=filename,
            )

            llm_engine = Llama(
                model_path=model_path,
                n_ctx=8192,
                n_gpu_layers=-1,
                verbose=False,
            )
            loaded_model_name = model_label

    return llm_engine


def generate(messages):
    backend_name = backend_var.get()
    selected_model = model_var.get()

    if "Embedded" in backend_name:
        model = get_embedded_model(selected_model)
        response = model.create_chat_completion(
            messages=messages,
            temperature=0.0,
        )
        return response["choices"][0]["message"]["content"].strip()

    if "Ollama" in backend_name:
        payload = json.dumps({
            "model": selected_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.0,
            },
        }).encode("utf-8")

        request = urllib.request.Request(
            "http://localhost:11434/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
        )

        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))

        return data["message"]["content"].strip()

    if "LM Studio" in backend_name:
        payload = json.dumps({
            "model": selected_model,
            "messages": messages,
            "temperature": 0.0,
        }).encode("utf-8")

        request = urllib.request.Request(
            "http://localhost:1234/v1/chat/completions",
            data=payload,
            headers={"Content-Type": "application/json"},
        )

        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))

        return data["choices"][0]["message"]["content"].strip()

    raise ValueError("Unsupported backend: " + backend_name)


def check_toolchain(language):
    checks = {
        "C": "gcc",
        "C++": "g++",
        "C#": "dotnet",
        "Java": "javac",
        "JavaScript": "node",
        "TypeScript": "npx",
    }

    executable = checks.get(language)

    if executable and shutil.which(executable) is None:
        return (
            False,
            language
            + " toolchain not found: "
            + executable,
        )

    return True, ""


def execute_program(language, entry_file, source_code):
    timeout_seconds = 25

    try:
        if language == "Python":
            imports = re.findall(
                r"^\s*(?:from\s+([A-Za-z_]\w*)"
                r"|import\s+([A-Za-z_]\w*))",
                source_code,
                re.MULTILINE,
            )

            standard_library = {
                "os",
                "sys",
                "re",
                "json",
                "math",
                "random",
                "datetime",
                "subprocess",
                "threading",
                "tkinter",
                "urllib",
                "pathlib",
                "time",
            }

            for import_match in imports:
                package_name = (
                    import_match[0] or import_match[1]
                ).split(".")[0]

                if package_name not in standard_library:
                    try:
                        subprocess.run(
                            [
                                sys.executable,
                                "-m",
                                "pip",
                                "install",
                                package_name,
                            ],
                            cwd=workspace_dir,
                            capture_output=True,
                            text=True,
                            timeout=60,
                        )
                    except (
                        OSError,
                        subprocess.TimeoutExpired,
                    ):
                        pass

            result = subprocess.run(
                [sys.executable, entry_file],
                cwd=workspace_dir,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
            return (
                result.stdout,
                result.stderr,
                result.returncode,
            )

        if language == "C":
            binary = os.path.join(
                workspace_dir,
                "output_c" + (".exe" if os.name == "nt" else ""),
            )
            compile_result = subprocess.run(
                ["gcc", entry_file, "-o", binary],
                cwd=workspace_dir,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )

            if compile_result.returncode != 0:
                return (
                    "",
                    "GCC Error:\n" + compile_result.stderr,
                    compile_result.returncode,
                )

            result = subprocess.run(
                [binary],
                cwd=workspace_dir,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
            return (
                result.stdout,
                result.stderr,
                result.returncode,
            )

        if language == "C++":
            binary = os.path.join(
                workspace_dir,
                "output_cpp" + (".exe" if os.name == "nt" else ""),
            )
            compile_result = subprocess.run(
                ["g++", entry_file, "-o", binary],
                cwd=workspace_dir,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )

            if compile_result.returncode != 0:
                return (
                    "",
                    "G++ Error:\n" + compile_result.stderr,
                    compile_result.returncode,
                )

            result = subprocess.run(
                [binary],
                cwd=workspace_dir,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
            return (
                result.stdout,
                result.stderr,
                result.returncode,
            )

        if language == "C#":
            project_directory = os.path.join(
                workspace_dir,
                "arb_cs_proj",
            )
            os.makedirs(project_directory, exist_ok=True)

            shutil.copyfile(
                os.path.join(workspace_dir, entry_file),
                os.path.join(project_directory, "Program.cs"),
            )

            result = subprocess.run(
                ["dotnet", "run", "--project", project_directory],
                cwd=workspace_dir,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
            return (
                result.stdout,
                result.stderr,
                result.returncode,
            )

        if language == "Java":
            compile_result = subprocess.run(
                ["javac", entry_file],
                cwd=workspace_dir,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )

            if compile_result.returncode != 0:
                return (
                    "",
                    "Javac Error:\n" + compile_result.stderr,
                    compile_result.returncode,
                )

            class_name = os.path.splitext(
                os.path.basename(entry_file)
            )[0]

            result = subprocess.run(
                ["java", class_name],
                cwd=workspace_dir,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
            return (
                result.stdout,
                result.stderr,
                result.returncode,
            )

        if language == "JavaScript":
            result = subprocess.run(
                ["node", entry_file],
                cwd=workspace_dir,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
            return (
                result.stdout,
                result.stderr,
                result.returncode,
            )

        if language == "TypeScript":
            npx_command = (
                "npx.cmd"
                if os.name == "nt"
                else "npx"
            )
            result = subprocess.run(
                [npx_command, "-y", "tsx", entry_file],
                cwd=workspace_dir,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
            return (
                result.stdout,
                result.stderr,
                result.returncode,
            )

        if language == "HTML & CSS":
            absolute_html_path = os.path.abspath(
                os.path.join(workspace_dir, entry_file)
            )
            webbrowser.open(
                "file://" + absolute_html_path
            )
            return (
                "Opened "
                + absolute_html_path
                + " in browser.",
                "",
                0,
            )

    except subprocess.TimeoutExpired:
        return (
            "",
            "Timed out after "
            + str(timeout_seconds)
            + " seconds.",
            1,
        )
    except OSError as error:
        return "", str(error), 1

    return "", "Unsupported language: " + language, 1


def generation_worker(user_prompt, target_language):
    try:
        toolchain_available, toolchain_error = (
            check_toolchain(target_language)
        )

        if not toolchain_available:
            write_terminal("\n" + toolchain_error + "\n")
            reset_ui()
            return

        extensions = {
            "Python": ".py",
            "C": ".c",
            "C++": ".cpp",
            "C#": ".cs",
            "Java": ".java",
            "JavaScript": ".js",
            "TypeScript": ".ts",
            "HTML & CSS": ".html",
        }

        default_extension = extensions[target_language]
        workspace_context = build_workspace_context()

        system_prompt = (
            "You are an expert software programmer. "
            "Return only runnable source code. "
            "Use this exact format for each file:\n"
            "===FILE: relative/path===\n"
            "file contents\n"
            "Do not use Markdown code fences."
        )

        user_prompt_full = (
            "Target language: "
            + target_language
            + "\n"
            "Instruction:\n"
            + user_prompt
            + "\n\n"
            "Existing workspace:\n"
            + workspace_context
        )

        raw_output = generate([
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt_full,
            },
        ])

        generated_files = parse_multi_file_output(
            raw_output,
            "main" + default_extension,
        )

        safe_generated_files = {}

        for relative_path, content in generated_files.items():
            full_path = safe_workspace_path(relative_path)

            if full_path:
                safe_generated_files[relative_path] = content
            else:
                write_terminal(
                    "Skipped unsafe path: "
                    + relative_path
                    + "\n"
                )

        if not safe_generated_files:
            raise ValueError(
                "The model did not provide a valid output file."
            )

        save_workspace_snapshot(
            list(safe_generated_files)
        )

        written_files = []

        for relative_path, content in safe_generated_files.items():
            full_path = safe_workspace_path(relative_path)

            if not full_path:
                continue

            os.makedirs(
                os.path.dirname(full_path),
                exist_ok=True,
            )

            with open(full_path, "w", encoding="utf-8") as file_handle:
                file_handle.write(content)

            written_files.append(relative_path)

        code_text.delete("1.0", tk.END)
        code_text.insert(
            "1.0",
            next(iter(safe_generated_files.values())),
        )

        refresh_file_tree()

        entry_file = next(
            (
                filename
                for filename in written_files
                if filename.lower().endswith(default_extension)
            ),
            written_files[0],
        )

        if target_language == "Java":
            public_class_match = re.search(
                r"public\s+class\s+(\w+)",
                safe_generated_files.get(entry_file, ""),
            )

            if public_class_match:
                class_name = public_class_match.group(1)
                old_path = safe_workspace_path(entry_file)
                new_relative_path = class_name + ".java"
                new_path = safe_workspace_path(new_relative_path)

                if old_path and new_path:
                    os.makedirs(
                        os.path.dirname(new_path),
                        exist_ok=True,
                    )
                    os.replace(old_path, new_path)
                    entry_file = new_relative_path

        write_terminal("\nRunning " + entry_file + "...\n")

        stdout, stderr, return_code = execute_program(
            target_language,
            entry_file,
            safe_generated_files.get(entry_file, ""),
        )

        if stdout:
            write_terminal(stdout)

        if stderr:
            write_terminal(stderr)

        write_terminal(
            "\nExit code: "
            + str(return_code)
            + "\n"
        )

        if (
            return_code != 0
            and auto_fix_var.get()
        ):
            for retry_number in range(2):
                fix_prompt = (
                    "Fix the following "
                    + target_language
                    + " error. "
                    "Preserve runnable code and return every "
                    "file using ===FILE: path=== blocks.\n\n"
                    "Error:\n"
                    + stderr
                    + "\n\nCode:\n"
                    + next(
                        iter(safe_generated_files.values())
                    )
                )

                fixed_output = generate([
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": fix_prompt,
                    },
                ])

                fixed_files = parse_multi_file_output(
                    fixed_output,
                    entry_file,
                )

                for relative_path, content in fixed_files.items():
                    full_path = safe_workspace_path(relative_path)

                    if not full_path:
                        continue

                    os.makedirs(
                        os.path.dirname(full_path),
                        exist_ok=True,
                    )

                    with open(full_path, "w", encoding="utf-8") as file_handle:
                        file_handle.write(content)

                refresh_file_tree()

                stdout, stderr, return_code = execute_program(
                    target_language,
                    entry_file,
                    next(
                        iter(fixed_files.values())
                    ),
                )

                if stdout:
                    write_terminal(stdout)

                if stderr:
                    write_terminal(stderr)

                write_terminal(
                    "\nRetry "
                    + str(retry_number + 1)
                    + " exit code: "
                    + str(return_code)
                    + "\n"
                )

                if return_code == 0:
                    break

    except Exception as error:
        write_terminal(
            "\nOperational Error:\n"
            + str(error)
            + "\n"
        )
    finally:
        reset_ui()


def start_generation(event=None):
    prompt = prompt_text.get("1.0", tk.END).strip()

    if not prompt:
        messagebox.showwarning(
            "Missing instruction",
            "Describe what you want to build.",
        )
        return

    generate_button.config(
        state=tk.DISABLED,
        text="Working...",
    )

    write_terminal(
        "Generating "
        + language_var.get()
        + " code...\n"
    )

    threading.Thread(
        target=generation_worker,
        args=(prompt, language_var.get()),
        daemon=True,
    ).start()


backend_dropdown.bind(
    "<<ComboboxSelected>>",
    sync_model_dropdown,
)
refresh_models_button.config(
    command=sync_model_dropdown,
)
open_folder_button.config(command=open_workspace_folder)
undo_button.config(command=undo_last_edit)
file_listbox.bind(
    "<<ListboxSelect>>",
    open_selected_file,
)
generate_button.config(command=start_generation)
clear_terminal_button.config(
    command=lambda: terminal_text.delete("1.0", tk.END)
)

refresh_file_tree()
sync_model_dropdown()
root.mainloop()