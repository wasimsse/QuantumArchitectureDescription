# helper_functions.py

from PIL import Image, ImageTk
import tkinter as tk

def load_icon(filepath):
    try:
        image = Image.open(filepath)
        image = image.resize((32, 32), Image.LANCZOS)  # Resize to appropriate size for toolbar
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"Icon load error: {e}")
        # Return a placeholder image (or you can return a text label as a fallback)
        return tk.PhotoImage(width=32, height=32)
