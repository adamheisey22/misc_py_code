import tkinter as tk
from tkinter import messagebox

# This function will be called when the button is clicked
def on_button_click():
    user_input = entry.get()
    messagebox.showinfo("Information", f"You entered: {user_input}")

# Create the main window
window = tk.Tk()
window.title("Basic GUI Program")
window.geometry("300x200")

# Create a label
label = tk.Label(window, text="Enter something:")
label.pack(pady=10)

# Create a text entry field
entry = tk.Entry(window)
entry.pack(pady=10)

# Create a button
button = tk.Button(window, text="Submit", command=on_button_click)
button.pack(pady=10)

# Start the GUI event loop
window.mainloop()
