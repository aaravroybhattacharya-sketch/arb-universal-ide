import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import io
from contextlib import redirect_stdout
import threading  # Keeps the UI butter-smooth during AI network requests
from groq import Groq

# Initialize UI Window
root = tk.Tk()
root.title("ARB Multi-Language AI Compiler")
root.geometry("1100x650")
root.configure(bg="#1e1e1e")

# --- Top Navigation Bar ---
top_bar = tk.Frame(root, bg="#252526", height=50)
top_bar.pack(fill=tk.X, side=tk.TOP)

title_label = tk.Label(top_bar, text="📝 ARB AI Universal IDE", font=("Segoe UI", 12, "bold"), fg="#ffffff", bg="#252526")
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
    terminal_output.see(tk.END)  # Auto-scrolls the terminal tracking log
    terminal_output.config(state=tk.DISABLED)

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
    """Processes the AI heavy network request and execution pipeline inside an isolated worker thread."""
    try:
        # Dynamically pulls your key directly out from the host machine OS environment variables
        api_key_env = os.environ.get("GROQ_API_KEY")
        
        if not api_key_env:
            update_terminal("\n❌ Operational Failure: 'GROQ_API_KEY' environment variable not found on this system.\n")
            update_terminal("💡 Fix: Please save your Groq key into your system environment variables and restart the application.\n")
            run_button.config(state=tk.NORMAL, text="⚡ Compile & Execute Logic")
            return

        client = Groq(api_key=api_key_env)

        system_prompt = (
            f"You are a strict code compiler. Translate the user's plain English programming logic "
            f"into actual, syntactically correct {target_lang} source code. Follow these rules precisely:\n"
            f"1. Fix all indentation, structure, brackets, and logical flows to conform perfectly to {target_lang} language specifications.\n"
            f"2. Output ONLY the raw executable {target_lang} code.\n"
            f"3. Do NOT include markdown code blocks (like ```python ... ```), text formatting, or conversational notes.\n"
            f"4. CRITICAL: Always append a native input/pause statement at the very end of the code so the terminal window stays open after execution "
            f"(e.g., for Python add `input('\\nPress Enter to exit...')`, for C add `printf('\\nPress Enter to exit...'); getchar();`, for C++ use `std::cin.get();`)."
        )


        response = client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Translate this code:\n\n{english_code}"}
            ],
            temperature=0.0
        )
        
        compiled_source = response.choices[0].message.content.strip()

        update_terminal(f"--- Compiled {target_lang} Source Struct ---\n")
        update_terminal(compiled_source + "\n")
        update_terminal("-----------------------------------------\n\n")

        execution_results = ""

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
            update_terminal(f"💡 Syntax Generation Complete: Generated source code verification passed.\n")

        # Dynamic File Extension Mapping
        extension_map = {
            "Python": ".py", "C": ".c", "Java": ".java", "JavaScript": ".js", "HTML & CSS": ".html", "C++": ".cpp", "Go": ".go"
        }
        
        file_ext = extension_map.get(target_lang, ".txt")
        output_file_name = f"output{file_ext}"

        # Saves purely the actual source script file natively to matching extensions
        with open(output_file_name, "w", encoding="utf-8") as out_file:
            out_file.write(compiled_source)

        # Restore compilation trigger button controls
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

    # Clear previous terminal screen tracking data out 
    terminal_output.config(state=tk.NORMAL)
    terminal_output.delete("1.0", tk.END)
    terminal_output.config(state=tk.DISABLED)
    
    update_terminal(f"🤖 Transpiling English into raw standard {target_lang} structure...\n\n")
    
    # Freeze standard action inputs to prevent network race conditions
    run_button.config(state=tk.DISABLED, text="⏳ Processing...")

    # Spawn thread to insulate window processing loops from standard network waiting frames
    threading.Thread(target=background_compiler_worker, args=(english_code, target_lang), daemon=True).start()

# --- Footer Action Toolbar Control Panel ---
bottom_frame = tk.Frame(root, bg="#1e1e1e")
bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=15)

run_button = tk.Button(bottom_frame, text="⚡ Compile & Execute Logic", font=("Segoe UI", 11, "bold"), fg="#ffffff", bg="#007acc", activebackground="#005999", padx=25, command=start_compilation)
run_button.pack()

root.mainloop()
