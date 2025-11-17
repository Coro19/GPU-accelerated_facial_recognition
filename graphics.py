import tkinter as tk
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
def show_frame(frame,frame_list):
    for f in frame_list:
        f.pack_forget()
    frame.pack(fill="both", expand=True)

