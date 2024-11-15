from qiskit import QuantumCircuit
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import Text, Scrollbar, END, Menu, messagebox, filedialog
from ttkthemes import ThemedTk
import os


class ArchitectureModel:
    def __init__(self):
        self.structural_view = []
        self.computational_view = []
        self.integration_view = []
        self.physical_view = []
        self.actors = []

    def add_to_view(self, view_name, component):
        if view_name == "StructuralView":
            self.structural_view.append(component)
        elif view_name == "ComputationalView":
            self.computational_view.append(component)
        elif view_name == "IntegrationView":
            self.integration_view.append(component)
        elif view_name == "PhysicalView":
            self.physical_view.append(component)

    def add_actor(self, actor_name):
        self.actors.append(actor_name)

    def visualize(self, image_label, selected_view=None):
        # Create a Qiskit Quantum Circuit for gates visualization
        qc = QuantumCircuit(2, 2)

        # Adding elements based on different views
        views = {
            "StructuralView": self.structural_view,
            "ComputationalView": self.computational_view,
            "IntegrationView": self.integration_view,
            "PhysicalView": self.physical_view,
        }

        fig, ax = plt.subplots(figsize=(8, 4))

        # Loop through all views and their components
        for view_name, components in views.items():
            if selected_view is None or selected_view == view_name:
                for component in components:
                    if "QuantumGate" in component:
                        # Example handling QuantumGate components
                        if "Hadamard" in component:
                            qc.h(0)
                        elif "CNOT" in component:
                            qc.cx(0, 1)
                    elif "QuantumChannel" in component:
                        # Represent QuantumChannel - as an arrow
                        ax.annotate('', xy=(0.6, 0.3), xytext=(0.8, 0.3),
                                    arrowprops=dict(facecolor='black', arrowstyle='->'))
                        ax.text(0.7, 0.32, 'Quantum Channel', fontsize=12, ha='center', va='center')
                    elif "QuantumBus" in component:
                        # Represent QuantumBus - dashed line
                        ax.plot([0.5, 0.8], [0.5, 0.5], 'k--', lw=2)
                        ax.text(0.65, 0.52, 'Quantum Bus', fontsize=12, ha='center', va='center')
                    elif "QuantumState" in component:
                        # Represent QuantumState - Text label
                        ax.text(0.5, 0.8, 'Quantum State', fontsize=12, ha='center', va='center', color='green')
                    elif "QuantumSubsystem" in component:
                        # Represent QuantumSubsystem - Draw a rectangle around the label
                        ax.add_patch(plt.Rectangle((0.55, 0.6), 0.2, 0.2, color='purple', fill=True))
                        ax.text(0.65, 0.7, 'Quantum Subsystem', fontsize=12, ha='center', va='center', color='white')

        # Draw the Qiskit circuit as usual
        qc.draw(output="mpl", ax=ax)

        # Integrate the quantum circuit visualization into Tkinter
        canvas = FigureCanvasTkAgg(fig, master=image_label)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)


def parse_dsl(text: str, model: ArchitectureModel):
    """
    Parses QADL script to extract architectural components and add them to the model.
    """
    lines = text.strip().split("\n")
    current_view = None

    for line in lines:
        line = line.strip()

        if line.startswith("@startQADL") or line.startswith("@endQADL"):
            continue
        elif line.endswith("View {"):
            current_view = line.replace(" {", "").strip()
            if current_view not in ["StructuralView", "ComputationalView", "IntegrationView", "PhysicalView"]:
                raise SyntaxError(f"Invalid view name '{current_view}'")
        elif line == "}":
            current_view = None
        else:
            tokens = line.split()
            if len(tokens) < 2:
                raise SyntaxError("Incomplete command")
            command = tokens[0]

            if command == "Actor":
                model.add_actor(tokens[1])
            elif command in [
                "Qubit", "QuantumGate", "QuantumCircuit", "QuantumAlgorithm",
                "ControlSystem", "QubitType", "QuantumChannel", "QuantumBus",
                "QuantumState", "QuantumSubsystem"
            ]:
                model.add_to_view(current_view, " ".join(tokens))
            elif command == "Measure":
                if len(tokens) == 4 and tokens[2] == "to":
                    measure_command = f"{tokens[0]} {tokens[1]} {tokens[2]} {tokens[3]}"
                    model.add_to_view(current_view, measure_command)
                else:
                    raise SyntaxError("Incorrect syntax for 'Measure' command")
            elif command == "QubitConnection":
                if len(tokens) == 3:
                    connection_command = f"{tokens[0]} {tokens[1]} {tokens[2]}"
                    model.add_to_view(current_view, connection_command)
                else:
                    raise SyntaxError("Incorrect syntax for 'QubitConnection' command")
            elif command in ["ErrorCorrection", "FaultTolerance", "QuantumCompiler", "QuantumMemory"]:
                model.add_to_view(current_view, " ".join(tokens))
            else:
                raise SyntaxError(f"Unknown command '{command}'")


class QADLEditor(ThemedTk):
    def __init__(self):
        super().__init__(theme="arc")
        self.title("QADL Editor with Dropdown Menus")
        self.geometry("1200x700")

        # Menu bar setup
        menubar = Menu(self)
        self.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Script", command=self.save_script)
        file_menu.add_command(label="Save Image", command=self.save_image)

        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear Script", command=self.clear_script)
        edit_menu.add_command(label="Clear Image", command=self.clear_image)
        edit_menu.add_command(label="Copy Script", command=self.copy_script)

        view_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        self.view_var = tk.StringVar(value="All Views")
        views = ["All Views", "StructuralView", "ComputationalView", "IntegrationView", "PhysicalView"]
        for view in views:
            view_menu.add_radiobutton(label=view, variable=self.view_var, value=view)

        main_frame = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=5)
        main_frame.pack(fill=tk.BOTH, expand=True)

        editor_frame = tk.Frame(main_frame)
        main_frame.add(editor_frame, stretch="always")

        self.line_numbers = tk.Text(
            editor_frame, width=4, padx=3, takefocus=0, border=0, background="lightgrey", state="disabled"
        )
        self.line_numbers.pack(side=tk.LEFT, fill="y")

        self.editor = Text(editor_frame, wrap="word")
        self.editor.pack(fill=tk.BOTH, expand=True)
        self.editor.bind("<KeyRelease>", self.update_line_numbers)

        scrollbar = Scrollbar(editor_frame, command=self.editor.yview)
        self.editor.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        preview_frame = tk.Frame(main_frame)
        main_frame.add(preview_frame, stretch="always")

        self.image_label = tk.Label(preview_frame)
        self.image_label.pack(expand=True)

        update_button = tk.Button(self, text="Update Preview", command=self.update_preview)
        update_button.pack(side=tk.TOP, pady=5)

    def clear_script(self):
        self.editor.delete("1.0", END)

    def clear_image(self):
        self.image_label.config(image=None)

    def copy_script(self):
        self.clipboard_clear()
        self.clipboard_append(self.editor.get("1.0", END))

    def save_script(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.editor.get("1.0", END))

    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path and os.path.exists("quantum_architecture.png"):
            os.rename("quantum_architecture.png", file_path)

    def update_line_numbers(self, event=None):
        line_numbers = "\n".join(str(i) for i in range(1, int(self.editor.index("end").split(".")[0])))
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", "end")
        self.line_numbers.insert("1.0", line_numbers)
        self.line_numbers.config(state="disabled")

    def update_preview(self):
        try:
            dsl_script = self.editor.get("1.0", END)
            architecture_model = ArchitectureModel()
            parse_dsl(dsl_script, architecture_model)

            selected_view = None if self.view_var.get() == "All Views" else self.view_var.get()
            architecture_model.visualize(self.image_label, selected_view)

        except SyntaxError as e:
            messagebox.showerror("Syntax Error", f"Syntax Error: {e}")


if __name__ == "__main__":
    app = QADLEditor()
    app.mainloop()
