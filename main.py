import sys, subprocess
import tkinter as tk
from graphics import add_hover, show_frame
root = tk.Tk()
root.title("Face Recognition Application")
root.geometry("500x500")
menu_frame = tk.Frame(root)
settings_frame = tk.Frame(root)
database_frame = tk.Frame(root)
frame_list = [menu_frame, settings_frame, database_frame]
btn_width = 40
btn_height = 3
extra_ipady = 8
run_build_encs_btn = tk.Button(database_frame, width = btn_width, height = btn_height,
                              text="Build Face Encodings Database",
                              font = ('Arial', 15),
                              command=lambda: subprocess.run([sys.executable, "face_recognition.py"]))
run_build_encs_btn.pack(pady=20, ipady = extra_ipady)
add_hover(run_build_encs_btn, database_frame)
run_build_encs_btn.place(x = 50, y = 100, height = 70, width = 400)
back_button_settings = tk.Button(settings_frame, text="<",
                        font = ('Arial', 20), width=btn_width, height=btn_height,
                        command=lambda: show_frame(menu_frame,frame_list))
back_button_settings.pack(pady=20, ipady = extra_ipady)
add_hover(back_button_settings, settings_frame)
back_button_settings.place(x = 30, y = 30, height = 50, width = 50)
back_button_database = tk.Button(database_frame, text="<",
                        font = ('Arial', 20), width=btn_width, height=btn_height,
                        command=lambda: show_frame(menu_frame,frame_list))
back_button_database.pack(pady=20, ipady = extra_ipady)
add_hover(back_button_database, settings_frame)
back_button_database.place(x = 30, y = 30, height = 50, width = 50)
button1 = tk.Button(menu_frame,width = btn_width, height = btn_height,
                    text="Run Face Recognition", font = ('Arial', 15),
                    command=lambda: run_option("1"))
button1.pack(pady=20, ipady = extra_ipady)
button2 = tk.Button(menu_frame,width = btn_width, height = btn_height,
                    text="Access Face Encodings Database", font = ('Arial',15),
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
    if option == "1":
        root.destroy()
        subprocess.run([sys.executable, "face_recognition.py"])
    elif option == "2":
        show_frame(database_frame,frame_list)
    elif option == "3":
        show_frame(settings_frame,frame_list)
show_frame(menu_frame,frame_list)
root.mainloop()