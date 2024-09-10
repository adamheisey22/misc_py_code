import tkinter as tk
from tkinter import messagebox

# Mode functions
def mode1():
    messagebox.showinfo("Mode 1", "You selected Mode 1. This is where Mode 1 functionality goes.")

def mode2():
    messagebox.showinfo("Mode 2", "You selected Mode 2. This is where Mode 2 functionality goes.")

def mode3():
    messagebox.showinfo("Mode 3", "You selected Mode 3. This is where Mode 3 functionality goes.")

def mode4():
    messagebox.showinfo("Mode 4", "You selected Mode 4. This is where Mode 4 functionality goes.")

# Main application window
window = tk.Tk()
window.title("Main.py Modes")
window.geometry("300x300")

# Create label
label = tk.Label(window, text="Select a Mode:", font=('Arial', 14))
label.pack(pady=20)

# Create buttons for different modes
button_mode1 = tk.Button(window, text="Mode 1", command=mode1, width=20)
button_mode1.pack(pady=10)

button_mode2 = tk.Button(window, text="Mode 2", command=mode2, width=20)
button_mode2.pack(pady=10)

button_mode3 = tk.Button(window, text="Mode 3", command=mode3, width=20)
button_mode3.pack(pady=10)

button_mode4 = tk.Button(window, text="Mode 4", command=mode4, width=20)
button_mode4.pack(pady=10)

# Start the GUI event loop
window.mainloop()
