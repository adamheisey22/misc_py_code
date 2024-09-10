import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import logging
import tomllib

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

# Create the main window
root = tk.Tk()
root.title("Model Runner")

# Mode selection
mode_var = tk.StringVar()
debug_var = tk.BooleanVar()

ttk.Label(root, text="Select Mode:").grid(row=0, column=0, padx=10, pady=10)
modes = ['elec', 'h2', 'unified-combo', 'gs-combo']
mode_menu = ttk.OptionMenu(root, mode_var, modes[0], *modes)
mode_menu.grid(row=0, column=1, padx=10, pady=10)

# Debug checkbox
debug_checkbox = ttk.Checkbutton(root, text="Enable Debug", variable=debug_var)
debug_checkbox.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

# Run button
run_button = ttk.Button(root, text="Run", command=run_model)
run_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Start the GUI loop
root.mainloop()
