import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import logging
import tomllib
import threading
import time

# Assuming these functions are defined in your imported modules
from definitions import PROJECT_ROOT, OUTPUT_ROOT
from src.integrator.utilities import make_output_dir, setup_logger
from src.integrator.runner import run_elec_solo, run_h2_solo
from src.integrator.gs_elec_hyd_res import run_gs_combo
from src.integrator.unified_elec_hyd_res import run_unified_res_elec_h2

# Specify config path
default_config_path = Path(PROJECT_ROOT, 'src/integrator', 'run_config.toml')

# GUI Function to handle mode execution
def run_model():
    selected_mode = mode_var.get()
    debug_mode = debug_var.get()

    # Check and print the selected mode for debugging
    print(f"Selected mode: {selected_mode}")

    if not selected_mode:
        messagebox.showerror("Error", "No mode selected!")
        return

    # Disable the run button while the process is running
    run_button.config(state=tk.DISABLED)
    
    def execute_model():
        try:
            # Initial setup of output directory and logger
            output_dir = make_output_dir(OUTPUT_ROOT)
            logger = setup_logger(output_dir)
            logger = logging.getLogger(__name__)
            
            if debug_mode:
                logger.setLevel(logging.DEBUG)
                logger.debug('Logging level set to DEBUG')
            
            # If no mode is selected, use the default from the config file
            if not selected_mode:
                with open(default_config_path, 'rb') as src:
                    config = tomllib.load(src)
                selected_mode = config['default_mode']
            
            logger.info(f'Model running in: {selected_mode} mode')

            # Match the mode to run the appropriate function
            if selected_mode == 'elec':
                run_elec_solo(config_path=default_config_path)
            elif selected_mode == 'h2':
                HYDROGEN_ROOT = PROJECT_ROOT / 'src/models/hydrogen'
                data_path = HYDROGEN_ROOT / 'inputs/single_region'
                run_h2_solo(data_path=data_path, config_path=default_config_path)
            elif selected_mode == 'gs-combo':
                run_gs_combo(config_path=default_config_path)
            elif selected_mode == 'unified-combo':
                run_unified_res_elec_h2(config_path=default_config_path)
            else:
                logger.error('Unknown operation mode')
                messagebox.showerror("Error", "Unknown operation mode selected")
        finally:
            # Re-enable the run button after the process finishes
            run_button.config(state=tk.NORMAL)
    
    # Run the model execution in a separate thread to keep the GUI responsive
    threading.Thread(target=execute_model).start()

# Function to create the GUI in a separate thread
def create_gui():
    global mode_var, debug_var, run_button
    # Create the main window
    root = tk.Tk()
    root.title("Model Runner")

    # Mode selection
    modes = ['elec', 'h2', 'unified-combo', 'gs-combo']

    # Initialize the mode_var with the first option in the list as default
    mode_var = tk.StringVar(value=modes[0])  # Set default to 'elec'
    debug_var = tk.BooleanVar()

    # Display current selection for debugging
    def on_mode_change(*args):
        print(f"Mode changed to: {mode_var.get()}")

    # Link a trace to mode_var to check if it's working properly
    mode_var.trace('w', on_mode_change)

    ttk.Label(root, text="Select Mode:").grid(row=0, column=0, padx=10, pady=10)
    mode_menu = ttk.OptionMenu(root, mode_var, *modes)
    mode_menu.grid(row=0, column=1, padx=10, pady=10)

    # Debug checkbox
    debug_checkbox = ttk.Checkbutton(root, text="Enable Debug", variable=debug_var)
    debug_checkbox.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    # Run button
    run_button = ttk.Button(root, text="Run", command=run_model)
    run_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    # Start the GUI loop
    root.mainloop()

# Run the GUI in a separate thread to allow command-line interaction
gui_thread = threading.Thread(target=create_gui, daemon=True)
gui_thread.start()

# Keep the command line alive for further interaction
while True:
    # Simulate the command-line process
    user_input = input("Command Line: ")
    if user_input.lower() == 'exit':
        print("Exiting program...")
        break
    else:
        print(f"Received command: {user_input}")
