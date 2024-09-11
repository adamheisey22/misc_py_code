import argparse
import logging
import toml
import csv
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk  # For progress bar
from pathlib import Path
from definitions import PROJECT_ROOT, OUTPUT_ROOT
from src.integrator.utilities import make_output_dir, setup_logger
from src.integrator.runner import run_elec_solo, run_h2_solo
from src.integrator.gs_elec_hyd_res import run_gs_combo
from src.integrator.unified_elec_hyd_res import run_unified_res_elec_h2

# Specify default config path
default_config_path = Path(PROJECT_ROOT, 'src/integrator', 'run_config.toml')

# Function to load and display TOML file content in the GUI
def load_toml_file():
    filepath = filedialog.askopenfilename(filetypes=[("TOML files", "*.toml")])
    if filepath:
        with open(filepath, 'r') as src:
            config = toml.load(src)
        return config, filepath
    return None, None

# Function to load and display CSV file content in the GUI
def load_csv_file():
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if filepath:
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            data = list(reader)
        return data, filepath
    return None, None

# Function to display and allow edits for a TOML file
def edit_toml_file():
    config, filepath = load_toml_file()
    if config:
        edit_window = tk.Toplevel(window)
        edit_window.title(f"Edit {Path(filepath).name}")

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

        # Create an entry widget for each key-value pair in the config
        for key, value in config.items():
            frame = tk.Frame(scroll_frame)
            frame.pack(padx=10, pady=5, fill="x", expand=True)

            # Create a label for the key
            label = tk.Label(frame, text=f"{key}: ", anchor="w")
            label.pack(side=tk.LEFT, fill="x", padx=5)

            # Create an entry for the value with increased width
            entry = tk.Entry(frame, width=60)  # Adjust width here
            entry.insert(tk.END, str(value))
            entry.pack(side=tk.RIGHT, padx=5)

            # Store reference to entries to retrieve the values later
            entry._key = key
            frame._entry = entry

        def save_changes():
            # Update the config with new values from the entry widgets
            for child in scroll_frame.winfo_children():
                for frame in child.winfo_children():
                    if hasattr(frame, '_entry'):
                        key = frame._entry._key
                        config[key] = frame._entry.get()

            # Save changes back to the TOML file using toml
            with open(filepath, 'w') as f:
                toml.dump(config, f)
            messagebox.showinfo("Success", f"Config file '{Path(filepath).name}' saved successfully!")
            edit_window.destroy()

        # Add a save button at the bottom of the window
        save_button = tk.Button(edit_window, text="Save Changes", command=save_changes)
        save_button.pack(pady=10)

# Function to handle mode selection and run the corresponding function
def run_selected_mode(mode, config_path=default_config_path):
    # Initial setup of output directory and logger
    OUTPUT_ROOT.mkdir(exist_ok=True)
    output_dir = make_output_dir(OUTPUT_ROOT)
    logger = setup_logger(output_dir)
    logger = logging.getLogger(__name__)
    logger.info('Starting Logging')

    # Open the default config file
    with open(config_path, 'r') as src:
        config = toml.load(src)

    logger.info(f'Model running in: {mode} mode')
    if mode == 'elec':
        run_elec_solo(config_path=config_path)
    elif mode == 'h2':
        HYDROGEN_ROOT = PROJECT_ROOT / 'src/models/hydrogen'
        data_path = HYDROGEN_ROOT / 'inputs/single_region'
        run_h2_solo(data_path=data_path, config_path=config_path)
    elif mode == 'gs-combo':
        run_gs_combo(config_path=config_path)
    elif mode == 'unified-combo':
        run_unified_res_elec_h2(config_path=config_path)
    else:
        logger.error('Unknown op mode... exiting')
        messagebox.showerror("Error", "Unknown mode selected")

# Function to update the progress bar and display messages
def on_run_button_click():
    mode = mode_var.get()
    if mode:
        progress_bar.start(10)  # Start the progress bar
        status_label.config(text=f"Running {mode} mode... Please wait.")
        window.update()  # Force update the GUI

        # Run the selected mode
        try:
            run_selected_mode(mode)
            status_label.config(text=f"{mode.capitalize()} mode finished successfully!")
            messagebox.showinfo("Success", f"{mode.capitalize()} mode has finished running.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            progress_bar.stop()  # Stop the progress bar
            status_label.config(text="Ready to run another mode")
            run_button.config(state=tk.NORMAL)  # Re-enable the Run button
    else:
        messagebox.showwarning("Warning", "Please select a mode to run.")

# Command-line argument parser
def setup_argparse():
    parser = argparse.ArgumentParser(description="Run the model in different modes with a specified config.")
    parser.add_argument("--config", help="Specify the path to the config file (TOML or CSV).", required=False)
    return parser.parse_args()

# Create GUI window
window = tk.Tk()
window.title("Model Runner")

# Add a label
label = tk.Label(window, text="Select Mode to Run:")
label.pack(pady=10)

# Add radio buttons for mode selection
mode_var = tk.StringVar()

modes = ['elec', 'h2', 'unified-combo', 'gs-combo']
for mode in modes:
    tk.Radiobutton(window, text=mode, variable=mode_var, value=mode).pack(anchor=tk.W)

# Add a run button
run_button = tk.Button(window, text="Run", command=on_run_button_click)
run_button.pack(pady=20)

# Add a progress bar
progress_bar = ttk.Progressbar(window, mode='indeterminate')
progress_bar.pack(pady=10)

# Add a status label
status_label = tk.Label(window, text="Ready to run a mode")
status_label.pack(pady=10)

# Add a button to edit config (TOML or CSV)
edit_toml_button = tk.Button(window, text="Edit Config (TOML)", command=edit_toml_file)
edit_toml_button.pack(pady=5)

# Start the GUI event loop
window.mainloop()
