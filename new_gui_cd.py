"""
BlueSky Graphical User Interface.

Built using the built-in Python tkinter package.

Created on Wed Sept 10 2024 by Adam Heisey
"""

import argparse
import logging
import toml
import csv
import tkinter as tk
import ast
from tkinter import messagebox, filedialog
from tkinter import ttk
import subprocess
from pathlib import Path
import datetime
from definitions import PROJECT_ROOT, OUTPUT_ROOT

# Specify default config path
default_config_path = Path(PROJECT_ROOT, 'src/integrator', 'run_config.toml')


def load_toml_file():
    """Function to load and display TOML file content in the GUI"""
    filepath = filedialog.askopenfilename(filetypes=[('TOML files', '*.toml')])
    if filepath:
        try:
            with open(filepath, 'r') as src:
                config = toml.load(src)
            return config, filepath
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load file: {str(e)}')
            return None, None
    return None, None


def load_csv_file():
    """Function to load and display CSV file content in the GUI"""
    filepath = filedialog.askopenfilename(filetypes=[('CSV files', '*.csv')])
    if filepath:
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            data = list(reader)
        return data, filepath
    return None, None


def convert_value(value, original_type):
    """Function to maintain the original type for config values"""
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


def edit_toml_file():
    """Function to display and allow edits for a TOML file"""
    config, filepath = load_toml_file()

    if config and filepath:
        edit_window = tk.Toplevel(window)
        edit_window.title(f'Edit {Path(filepath).name}')

        # Window size
        edit_window.geometry('800x600')

        canvas = tk.Canvas(edit_window)
        scrollbar = tk.Scrollbar(edit_window, orient='vertical', command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        entries = []

        # Create an entry widget for each key-value pair in the config
        for key, value in config.items():
            frame = tk.Frame(scroll_frame)
            frame.pack(padx=10, pady=5, fill='x', expand=True)

            # Create a key label
            label = tk.Label(frame, text=f'{key}: ', anchor='w')
            label.pack(side=tk.LEFT, fill='x', padx=5)

            # Create a value label - adjust width
            entry = tk.Entry(frame, width=60)
            entry.insert(tk.END, str(value))
            entry.pack(side=tk.RIGHT, padx=5)

            # Store reference to entries in dict
            entries.append((key, entry, type(value)))

        def save_changes():
            """Update the config with new values from the entry widgets"""
            for key, entry, original_type in entries:
                new_value = entry.get()
                config[key] = convert_value(new_value, original_type)

            if filepath:
                try:
                    # Save changes back to the TOML file using toml
                    with open(filepath, 'w') as f:
                        toml.dump(config, f)
                    messagebox.showinfo('Success', f"Config file '{Path(filepath).name}' saved successfully!")
                    edit_window.destroy()
                except Exception as e:
                    messagebox.showerror('Error', f'Failed to save file: {str(e)}')
            else:
                messagebox.showerror('Error', 'No file selected to save')

        # Add a save button at the bottom of the window
        save_button = tk.Button(edit_window, text='Save Changes', command=save_changes)
        save_button.pack(pady=10)


def run_selected_mode(mode, config_path=default_config_path):
    """Function to run the main.py script with selected mode and config file"""
    output_dir = OUTPUT_ROOT / f"{mode}_run_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Call main.py with the selected mode and config file
    try:
        subprocess.run(
            ['python', 'main.py', '--mode', mode, '--config', str(config_path)],
            check=True
        )
        messagebox.showinfo('Success', f"{mode.capitalize()} mode has finished running. See results in '{output_dir}'.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror('Error', f'An error occurred while running the mode: {str(e)}')


def on_run_button_click():
    """Function to update the progress bar and display messages"""
    mode = mode_var.get()
    if mode:
        progress_bar.start(10)  # Start the progress bar
        status_label.config(text=f'Running {mode} mode... Please wait.')
        window.update()  # Force update the GUI

        # Run the selected mode
        try:
            run_selected_mode(mode)
            status_label.config(text=f'{mode.capitalize()} mode finished successfully!')
        except Exception as e:
            messagebox.showerror('Error', f'An error occurred: {str(e)}')
        finally:
            progress_bar.stop()  # Stop the progress bar
            status_label.config(text='Ready to run another mode')
            run_button.config(state=tk.NORMAL)  # Re-enable the Run button
    else:
        messagebox.showwarning('Warning', 'Please select a mode to run.')


# Command-line argument parser
def setup_argparse():
    parser = argparse.ArgumentParser(description='Run the model in different modes with a specified config.')
    parser.add_argument('--config', help='Specify the path to the config file (TOML or CSV).', required=False)
    return parser.parse_args()


def Close():
    window.destroy()


# Create GUI window
window = tk.Tk()
window.title('BlueSky Model Runner')
window.geometry('800x600')

# Add a label
label = tk.Label(window, text='Select Mode to Run:')
label.pack(pady=10)

# Add buttons for mode selection
mode_var = tk.StringVar()

modes = ['elec', 'h2', 'residential', 'unified-combo', 'gs-combo', 'standalone']
for mode in modes:
    tk.Radiobutton(window, text=mode, variable=mode_var, value=mode).pack(anchor=tk.W)

# Add a run button
run_button = tk.Button(window, text='Run', command=on_run_button_click)
run_button.pack(pady=20)

# Add a progress bar
progress_bar = ttk.Progressbar(window, mode='indeterminate')
progress_bar.pack(pady=10)

# Add a status label
status_label = tk.Label(window, text='Ready to run a mode')
status_label.pack(pady=10)

# Add a button to edit config (TOML or CSV)
edit_toml_button = tk.Button(window, text='Edit Config (TOML)', command=edit_toml_file)
edit_toml_button.pack(pady=5)

# Button for closing
exit_button = tk.Button(window, text='Exit', command=Close)
exit_button.pack(pady=20)

# Run the GUI
window.mainloop()
