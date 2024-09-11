import tkinter as tk
from tkinter import messagebox, filedialog
from pathlib import Path
import tomlkit
import ast
import os
import logging

# Helper function to convert string input back to the original type
def convert_value(value, original_type):
    if original_type == list:
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value  # If conversion fails, return the string
    if original_type == bool:
        return value.lower() in ['true', '1', 'yes']
    elif original_type == int:
        try:
            return int(value)
        except ValueError:
            return value  # Return as string if conversion fails
    elif original_type == float:
        try:
            return float(value)
        except ValueError:
            return value  # Return as string if conversion fails
    else:
        return value

# Function to select or create an output folder
def select_output_folder():
    folder_selected = filedialog.askdirectory()
    if not folder_selected:
        messagebox.showerror("Error", "No output folder selected.")
        return None
    return Path(folder_selected)

# Setup logging to the specified log file
def setup_logging(output_folder):
    log_file = output_folder / "config_edit.log"
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')
    logging.info("Logging initialized.")

# Function to display and allow edits for a TOML file
def edit_toml_file():
    config, filepath = load_toml_file()

    if config and filepath:
        # Let the user select or create an output folder
        output_folder = select_output_folder()
        if not output_folder:
            return

        # Create output folder if it doesn't exist
        output_folder.mkdir(parents=True, exist_ok=True)

        # Setup logging for the session
        setup_logging(output_folder)
        logging.info(f"Editing config file: {filepath}")

        edit_window = tk.Toplevel(window)
        edit_window.title(f"Edit {Path(filepath).name}")

        # Set the size of the window (e.g., 800x600)
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

        # Create a dictionary to store key-entry pairs
        entries = []

        # Create an entry widget for each key-value pair in the config
        for key, value in config.items():
            frame = tk.Frame(scroll_frame)
            frame.pack(padx=10, pady=5, fill="x", expand=True)

            # Create a label for the key
            label = tk.Label(frame, text=f"{key}: ", anchor="w")
            label.pack(side=tk.LEFT, fill="x", padx=5)

            # Create an entry for the value with increased width
            entry = tk.Entry(frame, width=60)
            entry.insert(tk.END, str(value))  # Insert the current value as a string
            entry.pack(side=tk.RIGHT, padx=5)

            # Store the key, entry reference, and original type in a tuple
            entries.append((key, entry, type(value)))

        def save_changes():
            # Update the config with new values from the entry widgets
            for key, entry, original_type in entries:
                new_value = entry.get()
                logging.info(f"Updating {key}: {new_value}")
                config[key] = convert_value(new_value, original_type)

            # Save the updated TOML configuration to the output folder
            output_file = output_folder / f"{Path(filepath).stem}_modified.toml"

            # Ensure the filepath is valid before saving
            try:
                with open(output_file, 'w') as f:
                    f.write(tomlkit.dumps(config))
                messagebox.showinfo("Success", f"Config file saved to '{output_file}'")
                logging.info(f"Config file saved to '{output_file}'")
                edit_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
                logging.error(f"Failed to save file: {str(e)}")

        # Add a save button at the bottom of the window
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

# Example of tkinter window creation
window = tk.Tk()
window.title("Config Editor")

# Button to trigger the edit function
edit_button = tk.Button(window, text="Edit TOML File", command=edit_toml_file)
edit_button.pack(pady=20)

window.mainloop()
