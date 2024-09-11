import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog
from pathlib import Path
import logging

# Function to create a new output directory for each run based on mode and timestamp
def create_output_directory(base_output_dir, mode):
    # Create a unique subdirectory for each run based on timestamp and mode
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_output_dir = Path(base_output_dir) / f"{mode}_run_{timestamp}"
    run_output_dir.mkdir(parents=True, exist_ok=True)
    return run_output_dir

# Function to setup logging for the run
def setup_logging(run_output_dir):
    log_file = run_output_dir / "run.log"
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')
    logging.info("Logging initialized for run.")
    return log_file

# Function to handle mode selection and run the corresponding function
def run_selected_mode(mode, config_path):
    # Let the user select or create an output folder for the run
    base_output_dir = select_output_folder()
    if not base_output_dir:
        return

    # Create a new output directory for the run
    run_output_dir = create_output_directory(base_output_dir, mode)

    # Setup logging for the run in the new output directory
    log_file = setup_logging(run_output_dir)
    logging.info(f"Running in {mode} mode.")
    
    # Placeholder for running the mode-specific functionality
    try:
        # Here, insert actual functionality for running each mode
        if mode == 'elec':
            logging.info("Running electric mode...")
            # Call the corresponding function and pass the run_output_dir
            # run_elec_solo(config_path=config_path, output_dir=run_output_dir)
        elif mode == 'h2':
            logging.info("Running hydrogen mode...")
            # run_h2_solo(config_path=config_path, output_dir=run_output_dir)
        elif mode == 'gs-combo':
            logging.info("Running grid-storage combo mode...")
            # run_gs_combo(config_path=config_path, output_dir=run_output_dir)
        elif mode == 'unified-combo':
            logging.info("Running unified electric-hydrogen mode...")
            # run_unified_res_elec_h2(config_path=config_path, output_dir=run_output_dir)
        else:
            raise ValueError("Unknown mode selected.")
        
        # Log success and output directory
        logging.info(f"Run for {mode} mode completed successfully.")
        messagebox.showinfo("Success", f"Run completed successfully.\nLog file: {log_file}\nOutput directory: {run_output_dir}")
    
    except Exception as e:
        logging.error(f"Error occurred during {mode} run: {str(e)}")
        messagebox.showerror("Error", f"An error occurred during {mode} run: {str(e)}")

# Function to select or create an output folder
def select_output_folder():
    folder_selected = filedialog.askdirectory()
    if not folder_selected:
        messagebox.showerror("Error", "No output folder selected.")
        return None
    return Path(folder_selected)

# Function to load and display the configuration TOML file (if needed)
def load_config_file():
    filepath = filedialog.askopenfilename(filetypes=[("TOML files", "*.toml")])
    if filepath:
        try:
            # Load the configuration file (TOML loading logic)
            return filepath
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
            return None
    return None

# Example of tkinter window creation and interaction
window = tk.Tk()
window.title("Mode Runner")

# Radio buttons for mode selection
modes = ['elec', 'h2', 'unified-combo', 'gs-combo']
mode_var = tk.StringVar()
for mode in modes:
    tk.Radiobutton(window, text=mode, variable=mode_var, value=mode).pack(anchor=tk.W)

# Function to run the selected mode on button click
def on_run_button_click():
    mode = mode_var.get()
    if mode:
        config_path = load_config_file()  # Load configuration file
        if config_path:
            run_selected_mode(mode, config_path)
    else:
        messagebox.showwarning("Warning", "Please select a mode to run.")

# Run button
run_button = tk.Button(window, text="Run", command=on_run_button_click)
run_button.pack(pady=20)

# Start the tkinter GUI loop
window.mainloop()
