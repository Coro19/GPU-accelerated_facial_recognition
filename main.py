import sys, subprocess
import tkinter as tk
root = tk.Tk()
root.title("Face Recognition Options")
root.geometry("500x500")
btn_width = 40
btn_height = 3
extra_ipady = 8
button1 = tk.Button(root,width = btn_width, height = btn_height,
                    text="Run Face Recognition", font = ('Arial', 15),
                    command=lambda: run_option("1"))
button1.pack(pady=20, ipady = extra_ipady)
button2 = tk.Button(root,width = btn_width, height = btn_height,
                    text="Build Face Encodings Database", font = ('Arial',15),
                    command=lambda: run_option("2"))
button2.pack(pady=20, ipady = extra_ipady)
settings_btn = tk.Button(root, text = "Settings",
                         font = ('Arial', 15))
settings_btn.place(x = 400, y = 400, height = 50, width = 80)
close_btn = tk.Button(root, text = "Close", fg = "red",
                      font = ('Arial', 15),
                      command=root.destroy)
close_btn.place(x = 30, y = 400, height = 50, width = 80)
def run_option(option):
    root.destroy()
    if option == "1":
        subprocess.run([sys.executable, "face_recognition.py"])
    elif option == "2":
        subprocess.run([sys.executable, "build_encodings.py"])
root.mainloop()