import sys, subprocess
import tkinter as tk
root = tk.Tk()
root.title("Face Recognition Options")
root.geometry("500x500")
btn_width = 40
btn_height = 3
extra_ipady = 8
def _winfo_rgb_normalized(root, color):
    r, g, b = root.winfo_rgb(color)
    return (r >> 8, g >> 8, b >> 8)

def _rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb
def lighten_color(root, color, factor=0.08):
    r, g, b = _winfo_rgb_normalized(root, color)
    nr = min(255, int(r + (255 - r) * factor))
    ng = min(255, int(g + (255 - g) * factor))
    nb = min(255, int(b + (255 - b) * factor))
    return _rgb_to_hex((nr, ng, nb))
def add_hover(widget, root, factor = 0.08, bd_increase = 2, hover_relief = "raised"):
    orig_bg = widget.cget("bg")
    orig_relief = widget.cget("relief")
    orig_bd = widget.cget("bd")
    try:
        hover_bg = lighten_color(root, orig_bg, factor)
    except tk.TclError:
        hover_bg = orig_bg

    def on_enter(_ev):
        widget.configure(bg=hover_bg, relief=hover_relief, bd=int(orig_bd) + bd_increase, cursor="hand2")

    def on_leave(_ev):
        widget.configure(bg=orig_bg, relief=orig_relief, bd=orig_bd, cursor="")

    widget.bind("<Enter>", on_enter, add="+")
    widget.bind("<Leave>", on_leave, add="+")
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
add_hover(button1, root)
add_hover(button2, root)
add_hover(settings_btn, root)
add_hover(close_btn, root)
def run_option(option):
    root.destroy()
    if option == "1":
        subprocess.run([sys.executable, "face_recognition.py"])
    elif option == "2":
        subprocess.run([sys.executable, "build_encodings.py"])
root.mainloop()