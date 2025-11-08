import sys, subprocess
import tkinter as tk
from graphics import add_hover, show_frame
root = tk.Tk()
root.title("Face Recognition Application")
root.geometry("500x500")
menu_frame = tk.Frame(root)
settings_frame = tk.Frame(root)
frame_list = [menu_frame, settings_frame]
btn_width = 40
btn_height = 3
extra_ipady = 8

button1 = tk.Button(menu_frame,width = btn_width, height = btn_height,
                    text="Run Face Recognition", font = ('Arial', 15),
                    command=lambda: run_option("1"))
button1.pack(pady=20, ipady = extra_ipady)
button2 = tk.Button(menu_frame,width = btn_width, height = btn_height,
                    text="Build Face Encodings Database", font = ('Arial',15),
                    command=lambda: run_option("2"))
button2.pack(pady=20, ipady = extra_ipady)
settings_btn = tk.Button(menu_frame, text = "Settings",
                         font = ('Arial', 15),
                         command = lambda: show_frame(settings_frame,frame_list))
settings_btn.place(x = 400, y = 400, height = 50, width = 80)
close_btn = tk.Button(menu_frame, text = "Close", fg = "red",
                      font = ('Arial', 15),
                      command=root.destroy)
close_btn.place(x = 30, y = 400, height = 50, width = 80)
add_hover(button1, menu_frame)
add_hover(button2, menu_frame)
add_hover(settings_btn, menu_frame)
add_hover(close_btn, menu_frame)
def run_option(option):
    root.destroy()
    if option == "1":
        subprocess.run([sys.executable, "face_recognition.py"])
    elif option == "2":
        subprocess.run([sys.executable, "build_encodings.py"])
show_frame(menu_frame,frame_list)
root.mainloop()