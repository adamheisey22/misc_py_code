import tkinter as tk
from tkinter import messagebox, filedialog
from pathlib import Path
import tomlkit
import logging
import os
import datetime
import ast

# Helper function to convert string input back to the original type
def convert_value(value, original_type):
    if original_type == list:
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value
    if original_type == bool:
        return value.lower() in ['true', '1', 'yes']
    elif original_type == int:
        try:
            return int(value)
        except ValueError:
            return value
    elif original_type == float:
        try:
            return float(value)
        except ValueError:
            return value
    else:
        return value

# Create a logger for each mode run and store it in a unique directory
def setup_logger(mode):
    # Create a unique directory based on the mode and timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path(f"runs/{mode}_{timestamp}")
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create a logger
    logger = logging.getLogger(f"{mode}_logger")
    logger.setLevel(logging.INFO)

    # Create file handler for logger
    log_file = log_dir / f"{mode}_run.log"
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)

    # Create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(fh)

    return logger, log_dir

# Function to run the selected mode
def run_selected_mode(mode, config):
    logger, log_dir = setup_logger(mode)
    logger.info(f"Starting mode: {mode}")
    
    # Simulating different mode runs
    if mode == "elec":
        logger.info("Running electric mode...")
        # Simulate work
    elif mode == "h2":
        logger.info("Running hydrogen mode...")
        # Simulate work
    elif mode == "unified-combo":
        logger.info("Running unified-combo mode...")
        # Simulate work
    elif mode == "gs-combo":
        logger.info("Running gs-combo mode...")
        # Simulate work
    else:
        logger.error("Unknown mode selected.")
        messagebox.showerror("Error", "Unknown mode selected.")
        return
    
    logger.info(f"Mode {mode} finished successfully.")
    messagebox.showinfo("Success", f"{mode} mode finished. Logs stored in {log_dir}")

# Function to display and allow edits for a TOML file
def edit_toml_file():
    config, filepath = load_toml_file()
    
    if config and filepath:
        edit_window = tk.Toplevel(window)
        edit_window.title(f"Edit {Path(filepath).name}")
        
        edit_window.geometry("800x600")
        
        canvas = tk.Canvas(edit_window)
        scrollbar = tk.Scrollbar(edit_window, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        entries = []
        
        for key, value in config.items():
            frame = tk.Frame(scroll_frame)
            frame.pack(padx=10, pady=5, fill="x", expand=True)

            label = tk.Label(frame, text=f"{key}: ", anchor="w")
            label.pack(side=tk.LEFT, fill="x", padx=5)

            entry = tk.Entry(frame, width=60)
            entry.insert(tk.END, str(value))
            entry.pack(side=tk.RIGHT, padx=5)

            entries.append((key, entry, type(value)))

        def save_changes():
            for key, entry, original_type in entries:
                new_value = entry.get()
                config[key] = convert_value(new_value, original_type)

            if filepath:
                try:
                    with open(filepath, 'w') as f:
                        f.write(tomlkit.dumps(config))
                    messagebox.showinfo("Success", f"Config file '{Path(filepath).name}' saved successfully!")
                    edit_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file: {str(e)}")
            else:
                messagebox.showerror("Error", "No file selected to save.")

        save_button = tk.Button(edit_window, text="Save Changes", command=save_changes)
        save_button.pack(pady=10)
    else:
        messagebox.showerror("Error", "No file selected or file could not be loaded.")

# Function to load and display TOML file content using tomlkit
def load_toml_file():
    filepath = filedialog.askopenfilename(filetypes=[("TOML files", "*.toml")])
    if filepath:
        try:
            with open(filepath, 'r') as src:
                config = tomlkit.parse(src.read())
            return config, filepath
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
            return None, None
    return None, None

# Function to run the selected mode based on user's selection
def on_run_button_click():
    mode = mode_var.get()
    if mode:
        config, filepath = load_toml_file()
        if config:
            run_selected_mode(mode, config)
    else:
        messagebox.showwarning("Warning", "Please select a mode to run.")

# Example of tkinter window creation
window = tk.Tk()
window.title("Config Editor and Runner")

# Label for mode selection
label = tk.Label(window, text="Select Mode to Run:")
label.pack(pady=10)

# Radio buttons for mode selection
mode_var = tk.StringVar()

modes = ['elec', 'h2', 'unified-combo', 'gs-combo']
for mode in modes:
    tk.Radiobutton(window, text=mode, variable=mode_var, value=mode).pack(anchor=tk.W)

# Button to trigger the run mode
run_button = tk.Button(window, text="Run", command=on_run_button_click)
run_button.pack(pady=20)

# Button to trigger the edit function
edit_button = tk.Button(window, text="Edit TOML File", command=edit_toml_file)
edit_button.pack(pady=20)

window.mainloop()
