import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
from ttkthemes import ThemedTk
from PIL import Image, ImageTk
import os
import sys

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.helper_functions import load_icon
from parser.qadl_parser import parse_qadl
from executor.qadl_executor import execute_circuit

class QcSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QcSimulator GUI with Qiskit")
        self.filename = None
        self.create_widgets()

    def create_widgets(self):
        self.create_menu()
        self.create_toolbar()

        # Create a frame to hold the editor and visualization side by side
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        self.create_text_editor()
        self.create_output_display()
        self.create_status_bar()

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        
        # File Menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Edit Menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Clear", command=self.clear_text)
        edit_menu.add_command(label="Cut", command=lambda: self.script_input.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: self.script_input.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self.script_input.event_generate("<<Paste>>"))
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        
        # Settings Menu
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Settings", command=self.show_settings)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)

        # Help Menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Help Contents", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)

    def create_toolbar(self):
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        new_icon = load_icon("../icons/new_file.png")
        open_icon = load_icon("../icons/open_file.png")
        save_icon = load_icon("../icons/save_file.png")
        run_icon = load_icon("../icons/run.png")
        clear_icon = load_icon("../icons/clear.png")
        screenshot_icon = load_icon("../icons/screenshot.png")

        tk.Button(toolbar, image=new_icon, command=self.new_file).grid(row=0, column=0, padx=2, pady=2)
        tk.Button(toolbar, image=open_icon, command=self.open_file).grid(row=0, column=1, padx=2, pady=2)
        tk.Button(toolbar, image=save_icon, command=self.save_file).grid(row=0, column=2, padx=2, pady=2)
        tk.Button(toolbar, image=run_icon, command=self.run_qadl).grid(row=0, column=3, padx=2, pady=2)
        tk.Button(toolbar, image=clear_icon, command=self.clear_text).grid(row=0, column=4, padx=2, pady=2)
        tk.Button(toolbar, image=screenshot_icon, command=self.take_screenshot).grid(row=0, column=5, padx=2, pady=2)

        # Keep references to the images to prevent garbage collection
        toolbar.images = [new_icon, open_icon, save_icon, run_icon, clear_icon, screenshot_icon]
        toolbar.pack(side=tk.TOP, fill=tk.X)

    def create_text_editor(self):
        self.editor_frame = tk.Frame(self.main_frame)
        self.editor_frame.grid(row=0, column=0, sticky='nsew')

        self.script_input = scrolledtext.ScrolledText(self.editor_frame, height=30, width=80)
        self.script_input.pack(expand=True, fill=tk.BOTH)
        self.script_input.bind('<KeyRelease>', self.apply_syntax_highlighting)

    def create_output_display(self):
        self.output_frame = tk.Frame(self.main_frame)
        self.output_frame.grid(row=0, column=1, sticky='nsew')

        self.output_display = scrolledtext.ScrolledText(self.output_frame, height=30, width=80)
        self.output_display.pack(expand=True, fill=tk.BOTH)

    def create_status_bar(self):
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, message):
        self.status_bar.config(text=message)

    def clear_text(self):
        self.script_input.delete('1.0', tk.END)
        self.output_display.delete('1.0', tk.END)
        self.update_status("Cleared")

    def new_file(self):
        self.script_input.delete('1.0', tk.END)
        self.output_display.delete('1.0', tk.END)
        self.filename = None
        self.update_status("New File")

    def open_file(self):
        self.filename = filedialog.askopenfilename(defaultextension=".qadl", filetypes=[("QADL Files", "*.qadl"), ("All Files", "*.*")])
        if self.filename:
            with open(self.filename, "r") as file:
                self.script_input.delete('1.0', tk.END)
                self.script_input.insert(tk.END, file.read())
            self.update_status(f"Opened {os.path.basename(self.filename)}")

    def save_file(self):
        if self.filename:
            with open(self.filename, "w") as file:
                file.write(self.script_input.get("1.0", tk.END))
            self.update_status(f"Saved {os.path.basename(self.filename)}")
        else:
            self.save_file_as()

    def save_file_as(self):
        self.filename = filedialog.asksaveasfilename(defaultextension=".qadl", filetypes=[("QADL Files", "*.qadl"), ("All Files", "*.*")])
        if self.filename:
            with open(self.filename, "w") as file:
                file.write(self.script_input.get("1.0", tk.END))
            self.update_status(f"Saved As {os.path.basename(self.filename)}")

    def run_qadl(self):
        script = self.script_input.get("1.0", tk.END)
        self.output_display.delete('1.0', tk.END)  # Clear previous output
        try:
            circuit_def = parse_qadl(script)
            circuit_name = execute_circuit(circuit_def)
            
            if os.path.exists("quantum_circuit.png"):
                img = Image.open("quantum_circuit.png")
                img = img.resize((800, 600), Image.LANCZOS)
                img = ImageTk.PhotoImage(img)
                self.output_display.image_create(tk.END, image=img)
                self.output_display.image = img
                self.update_status(f"Executed {circuit_name}")
        except SyntaxError as se:
            self.output_display.insert(tk.END, f"Syntax Error: {se}\n")
            self.update_status("Syntax Error")
        except Exception as e:
            self.output_display.insert(tk.END, f"Error: {e}\n")
            self.update_status("Error")

    def take_screenshot(self):
        try:
            screenshot_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")])
            if screenshot_path:
                self.root.update_idletasks()
                self.root.after(1000, lambda: self.root.grab().save(screenshot_path))
                self.update_status(f"Screenshot saved as {screenshot_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to take screenshot: {e}")

    def show_about(self):
        messagebox.showinfo("About", "QcSimulator Editor with Qiskit Integration\nDesigned for Quantum Circuit Visualization")

    def show_help(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("QcSimulator Help and Demo")
        help_text = scrolledtext.ScrolledText(help_window, height=30, width=100)
        help_text.pack(expand=True, fill=tk.BOTH)

        try:
            with open("../QcSimulator_Help_Demo.qadl", "r") as help_file:
                help_text.insert(tk.END, help_file.read())
        except Exception as e:
            help_text.insert(tk.END, f"Error loading help file: {e}")

    def show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        
        tk.Label(settings_window, text="Font Size:").pack()
        font_size = tk.Spinbox(settings_window, from_=8, to=48)
        font_size.pack()
        
        tk.Label(settings_window, text="Theme:").pack()
        themes = ["default", "equilux", "clam", "alt", "classic"]
        theme = tk.StringVar(value="default")
        tk.OptionMenu(settings_window, theme, *themes).pack()
        
        tk.Button(settings_window, text="Apply", command=lambda: self.apply_settings(font_size.get(), theme.get())).pack()

    def apply_settings(self, font_size, theme):
        self.script_input.config(font=("Arial", int(font_size)))
        self.output_display.config(font=("Arial", int(font_size)))
        self.root.set_theme(theme)
        messagebox.showinfo("Settings", "Settings Applied")

    def apply_syntax_highlighting(self, event=None):
        for tag in self.script_input.tag_names():
            self.script_input.tag_remove(tag, '1.0', tk.END)
        keywords = ['Circuit', 'qubit', 'gate', 'measure', 'node', 'edge', 'flow']
        for keyword in keywords:
            start = '1.0'
            while True:
                start = self.script_input.search(keyword, start, stopindex=tk.END)
                if not start:
                    break
                end = f"{start}+{len(keyword)}c"
                self.script_input.tag_add(keyword, start, end)
                self.script_input.tag_config(keyword, foreground='blue')
                start = end

if __name__ == "__main__":
    root = ThemedTk(theme="equilux")  # Choose a modern theme
    app = QcSimulatorApp(root)
    root.mainloop()
