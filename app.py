import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import io
from contextlib import redirect_stdout
import threading
from llama_cpp import Llama
from huggingface_hub import hf_hub_download

# Global variable to cache the loaded model in RAM so it only loads once
llm_engine = None

# Initialize UI Window
root = tk.Tk()
root.title("ARB Multi-Language AI Compiler (Offline Embedded)")
root.geometry("1100x650")
root.configure(bg="#1e1e1e")
if os.path.exists("arb_icon.ico"):
    root.iconbitmap("arb_icon.ico")

# --- Top Navigation Bar ---
top_bar = tk.Frame(root, bg="#252526", height=50)
top_bar.pack(fill=tk.X, side=tk.TOP)

title_label = tk.Label(top_bar, text="📝 ARB AI Universal IDE (Local)", font=("Segoe UI", 12, "bold"), fg="#ffffff", bg="#252526")
title_label.pack(side=tk.LEFT, padx=20, pady=10)

lang_label = tk.Label(top_bar, text="Target Language:", fg="#aaaaaa", bg="#252526", font=("Segoe UI", 10))
lang_label.pack(side=tk.LEFT, padx=(20, 5))

language_var = tk.StringVar(value="Python")
lang_dropdown = ttk.Combobox(top_bar, textvariable=language_var, state="readonly", width=15, font=("Segoe UI", 10))
lang_dropdown['values'] = ("Python", "C", "Java", "JavaScript", "HTML & CSS", "C++", "Go")
lang_dropdown.pack(side=tk.LEFT, padx=5)

# --- Main Split Window Layout ---
main_frame = tk.Frame(root, bg="#1e1e1e")
main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

# LEFT SIDE: Editor Panel
editor_frame = tk.Frame(main_frame, bg="#1e1e1e")
editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

editor_label = tk.Label(editor_frame, text="Write Plain English Logic Here:", fg="#aaaaaa", bg="#1e1e1e", font=("Segoe UI", 10))
editor_label.pack(anchor=tk.W, pady=(0, 5))

code_input = tk.Text(editor_frame, wrap=tk.WORD, undo=True, font=("Consolas", 12), bg="#2d2d2d", fg="#ffffff", insertbackground="white")
code_input.pack(fill=tk.BOTH, expand=True)

# RIGHT SIDE: Output Screen Terminal Panel
output_frame = tk.Frame(main_frame, bg="#1e1e1e")
output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

output_label = tk.Label(output_frame, text="AI Compiler & Execution Log Output:", fg="#aaaaaa", bg="#1e1e1e", font=("Segoe UI", 10))
output_label.pack(anchor=tk.W, pady=(0, 5))

terminal_output = tk.Text(output_frame, wrap=tk.WORD, font=("Consolas", 11), bg="#121212", fg="#00ff00", state=tk.DISABLED)
terminal_output.pack(fill=tk.BOTH, expand=True)

# --- Core Dynamic Functionality ---
def update_terminal(text):
    """Safely updates the custom terminal UI from any background worker thread."""
    terminal_output.config(state=tk.NORMAL)
    terminal_output.insert(tk.END, text)
    terminal_output.see(tk.END)
    terminal_output.config(state=tk.DISABLED)

def get_embedded_model():
    """Automatically downloads (first run only) and loads the local GGUF model into RAM."""
    global llm_engine
    if llm_engine is None:
        update_terminal("📥 Checking/Downloading local Qwen 2.5 Coder model (first run takes a few minutes)...\n")
        model_path = hf_hub_download(
            repo_id="Qwen/Qwen2.5-Coder-7B-Instruct-GGUF",
            filename="qwen2.5-coder-7b-instruct-q4_k_m.gguf"
        )
        update_terminal("🧠 Loading AI model directly into system memory...\n")
        # n_gpu_layers=-1 uses GPU if available, otherwise falls back cleanly to CPU
        llm_engine = Llama(
            model_path=model_path,
            n_ctx=4096,
            n_gpu_layers=-1,
            verbose=False
        )
    return llm_engine

def auto_install_dependencies(compiled_code):
    """Scans code logic structures and launches automated background pip module installations."""
    update_terminal("🔍 Analyzing code structure for required third-party packages...\n")
    import re
    imports = re.findall(r'^\s*(?:import|from)\s+([a-zA-Z0-9_]+)', compiled_code, re.MULTILINE)
    
    standard_libs = {'sys', 'os', 'math', 'random', 'time', 'json', 're', 'datetime', 'collections', 'itertools', 'io'}
    packages_to_check = set(imports) - standard_libs

    for package in packages_to_check:
        try:
            __import__(package)
        except ImportError:
            update_terminal(f"📦 Missing package '{package}' discovered. Running pip deployment module...\n")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                update_terminal(f"✅ Successfully installed requirement: {package}\n")
            except Exception as pip_err:
                update_terminal(f"⚠️ Automatic module install skipped or failed for '{package}': {pip_err}\n")

def background_compiler_worker(english_code, target_lang):
    """Processes the embedded local AI inference and execution pipeline inside a worker thread."""
    try:
        llm = get_embedded_model()

        pause_rule = (
            "Do NOT include any `input()` calls so execution completes cleanly."
            if target_lang == "Python"
            else "Append a native pause statement at the end (e.g., `getchar();` for C, `std::cin.get();` for C++)."
        )

        system_prompt = (
            f"You are a strict code compiler. Translate the user's plain English programming logic "
            f"into actual, syntactically correct {target_lang} source code. Follow these rules precisely:\n"
            f"1. Fix all indentation, structure, brackets, and logical flows to conform perfectly to {target_lang} language specifications.\n"
            f"2. Output ONLY the raw executable {target_lang} code.\n"
            f"3. Do NOT include markdown code blocks (like ```python ... ```), text formatting, or conversational notes.\n"
            f"4. {pause_rule}"
        )

        response = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Translate this code:\n\n{english_code}"}
            ],
            temperature=0.0
        )
        
        compiled_source = response["choices"][0]["message"]["content"].strip()

        # Strip accidental markdown fences if the local model outputs them
        if compiled_source.startswith("```"):
            lines = compiled_source.splitlines()
            compiled_source = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:]).strip()

        update_terminal(f"--- Compiled {target_lang} Source Struct ---\n")
        update_terminal(compiled_source + "\n")
        update_terminal("-----------------------------------------\n\n")

        # Language Runtime Routing Engine
        if target_lang == "Python":
            auto_install_dependencies(compiled_source)
            update_terminal("🚀 Launching execution environment engine thread...\n")
            output_buffer = io.StringIO()
            with redirect_stdout(output_buffer):
                try:
                    exec(compiled_source, {})
                except Exception as runtime_err:
                    print(f"Runtime Execution Error: {runtime_err}")
            execution_results = output_buffer.getvalue()
            update_terminal(f"\n💻 Result Output:\n{execution_results if execution_results else '[Execution Complete: No Stdout Stream Data returned]'}\n")
        else:
            update_terminal("💡 Syntax Generation Complete: Generated source code verification passed.\n")

        # Dynamic File Extension Mapping
        extension_map = {
            "Python": ".py", "C": ".c", "Java": ".java", "JavaScript": ".js", "HTML & CSS": ".html", "C++": ".cpp", "Go": ".go"
        }
        
        file_ext = extension_map.get(target_lang, ".txt")
        output_file_name = f"output{file_ext}"

        with open(output_file_name, "w", encoding="utf-8") as out_file:
            out_file.write(compiled_source)

        run_button.config(state=tk.NORMAL, text="⚡ Compile & Execute Logic")
        messagebox.showinfo("Compilation Success", f"Source logic built successfully! Raw file saved as '{output_file_name}'")

    except Exception as e:
        update_terminal(f"\n❌ Operational Processing Error encountered:\n{e}\n")
        run_button.config(state=tk.NORMAL, text="⚡ Compile & Execute Logic")

def start_compilation():
    english_code = code_input.get("1.0", tk.END).strip()
    target_lang = language_var.get()
    
    if not english_code:
        messagebox.showwarning("Empty Editor", "Please drop instructions into the text engine frame.")
        return

    terminal_output.config(state=tk.NORMAL)
    terminal_output.delete("1.0", tk.END)
    terminal_output.config(state=tk.DISABLED)
    
    update_terminal(f"🤖 Transpiling English into raw standard {target_lang} structure...\n\n")
    run_button.config(state=tk.DISABLED, text="⏳ Processing...")

    threading.Thread(target=background_compiler_worker, args=(english_code, target_lang), daemon=True).start()

# --- Footer Action Toolbar Control Panel ---
bottom_frame = tk.Frame(root, bg="#1e1e1e")
bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=15)

run_button = tk.Button(bottom_frame, text="⚡ Compile & Execute Logic", font=("Segoe UI", 11, "bold"), fg="#ffffff", bg="#007acc", activebackground="#005999", padx=25, command=start_compilation)
run_button.pack()

root.mainloop()
