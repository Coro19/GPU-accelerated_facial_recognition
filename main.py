import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
from graphics import add_hover, show_frame
from people_manager import PeopleManager
from settings_tab import SettingsManager, SettingsTab

# --- Helper Functions ---
def run_option(option):
    """Handle menu button actions."""
    if option == "1":
        root.destroy()
        subprocess.run([sys.executable, "face_recognition.py"])
    elif option == "2":
        show_frame(database_frame, frame_list)
def close_app():
    """Close the application with confirmation."""
    if messagebox.askokcancel("Quit", "Do you really want to quit?"):
        root.destroy()

def run_build_encodings():
    """Run the build encodings script."""
    subprocess.run([sys.executable, "build_encodings.py"])
# --- Main Window Setup ---
root = tk.Tk()
root.title("Face Recognition Application")
root.geometry("500x500")
root.resizable(False, False)
# --- Frames ---
menu_frame = tk.Frame(root)
settings_frame = tk.Frame(root)
database_frame = tk.Frame(root)
people_list_frame = tk.Frame(root)
person_images_frame = tk.Frame(root)
frame_list = [menu_frame, settings_frame, database_frame, people_list_frame, person_images_frame]
# --- Settings Manager ---
settings_mgr = SettingsManager()
# --- People Manager ---
people_mgr = PeopleManager(people_list_frame, person_images_frame, database_frame, frame_list)
# --- Settings Tab ---
settings_tab = SettingsTab(settings_frame, menu_frame, frame_list, settings_mgr)
# --- Menu Frame Buttons ---
button1 = tk.Button(
    menu_frame,
    text="Run Face Recognition",
    font=('Arial', 15),
    command=lambda: run_option("1"))
button1.place(x=50, y=100, height=70, width=400)
add_hover(button1, menu_frame)
button2 = tk.Button(
    menu_frame,
    text="Access Face Encodings Database",
    font=('Arial', 15),
    command=lambda: run_option("2"))
button2.place(x=50, y=190, height=70, width=400)
add_hover(button2, menu_frame)
settings_btn = tk.Button(
    menu_frame,
    text="Settings",
    font=('Arial', 15),
    command=lambda: show_frame(settings_frame, frame_list))
settings_btn.place(x=400, y=430, height=50, width=80)
add_hover(settings_btn, menu_frame)
close_btn = tk.Button(
    menu_frame,
    text="Close",
    fg="red",
    font=('Arial', 15),
    command=lambda: close_app())
close_btn.place(x=20, y=430, height=50, width=80)
add_hover(close_btn, menu_frame)
# --- Settings Frame is built by SettingsTab ---
# --- Database Frame Buttons ---
back_button_database = tk.Button(
    database_frame,
    text="<",
    font=('Arial', 20),
    command=lambda: show_frame(menu_frame, frame_list))
back_button_database.place(x=30, y=30, height=50, width=50)
add_hover(back_button_database, database_frame)
run_build_encs_btn = tk.Button(
    database_frame,
    text="Build Face Encodings Database",
    font=('Arial', 15),
    command=run_build_encodings)
run_build_encs_btn.place(x=50, y=100, height=70, width=400)
add_hover(run_build_encs_btn, database_frame)
view_people_btn = tk.Button(
    database_frame,
    text="View/Manage Known People",
    font=('Arial', 15),
    command=people_mgr.show_people_list)
view_people_btn.place(x=50, y=190, height=70, width=400)
add_hover(view_people_btn, database_frame)
# --- Start Application ---
show_frame(menu_frame, frame_list)
root.mainloop()