import os
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from PIL import Image, ImageTk
from graphics import add_hover, show_frame

# --- Configuration ---
KNOWN_FACES_DIR = Path("faces/known")
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp")
THUMBNAIL_SIZE = (100, 100)


class PeopleManager:
    """Manages the known-people database UI: listing people, viewing/deleting images."""

    def __init__(self, people_list_frame, person_images_frame, database_frame, frame_list):
        self.people_list_frame = people_list_frame
        self.person_images_frame = person_images_frame
        self.database_frame = database_frame
        self.frame_list = frame_list

    # --- Data helpers ---

    @staticmethod
    def get_known_people():
        """Get list of people from the known faces directory."""
        if not KNOWN_FACES_DIR.exists():
            return []
        return [d.name for d in sorted(KNOWN_FACES_DIR.iterdir()) if d.is_dir()]

    @staticmethod
    def get_person_images(person_name):
        """Get list of image paths for a person."""
        person_dir = KNOWN_FACES_DIR / person_name
        if not person_dir.exists():
            return []
        return [f for f in sorted(person_dir.iterdir()) if f.suffix.lower() in IMAGE_EXTENSIONS]

    # --- Actions ---

    def delete_image(self, image_path, person_name):
        """Delete an image file and refresh the person frame."""
        if messagebox.askyesno("Confirm Delete", f"Delete {image_path.name}?"):
            try:
                os.remove(image_path)
                self.show_person_images(person_name)
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete file: {e}")

    # --- UI builders ---

    def show_person_images(self, person_name):
        """Show the images frame for a specific person."""
        frame = self.person_images_frame

        for widget in frame.winfo_children():
            widget.destroy()

        # Back button
        back_btn = tk.Button(
            frame, text="<", font=('Arial', 20),
            command=lambda: show_frame(self.people_list_frame, self.frame_list))
        back_btn.place(x=30, y=30, height=50, width=50)
        add_hover(back_btn, frame)

        # Title
        tk.Label(
            frame, text=f"Photos of {person_name}",
            font=('Arial', 16, 'bold')).place(x=100, y=40)

        images = self.get_person_images(person_name)

        if not images:
            tk.Label(
                frame, text="No images found for this person.",
                font=('Arial', 12)).place(x=150, y=150)
        else:
            self._build_image_grid(frame, images, person_name)

        show_frame(frame, self.frame_list)

    def _build_image_grid(self, frame, images, person_name):
        """Build a scrollable grid of thumbnail images."""
        canvas = tk.Canvas(frame, width=440, height=350)
        canvas.place(x=30, y=100)

        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollbar.place(x=470, y=100, height=350)
        canvas.configure(yscrollcommand=scrollbar.set)

        images_container = tk.Frame(canvas)
        canvas.create_window((0, 0), window=images_container, anchor="nw")

        frame.image_refs = []
        cols = 3

        for idx, img_path in enumerate(images):
            row, col = divmod(idx, cols)

            img_frame = tk.Frame(images_container, width=130, height=140)
            img_frame.grid(row=row, column=col, padx=10, pady=10)
            img_frame.grid_propagate(False)

            try:
                img = Image.open(img_path)
                img.thumbnail(THUMBNAIL_SIZE)
                photo = ImageTk.PhotoImage(img)
                frame.image_refs.append(photo)

                img_btn = tk.Button(
                    img_frame, image=photo,
                    command=lambda p=img_path: os.startfile(p))
                img_btn.place(x=5, y=5, width=110, height=110)
                add_hover(img_btn, img_frame)

                del_btn = tk.Button(
                    img_frame, text="X", fg="red", font=('Arial', 8, 'bold'),
                    command=lambda p=img_path, n=person_name: self.delete_image(p, n))
                del_btn.place(x=95, y=5, width=20, height=20)
                add_hover(del_btn, img_frame)
            except Exception:
                tk.Label(img_frame, text="Error", fg="red").place(x=5, y=50)

        images_container.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    def refresh_people_list(self):
        """Refresh the people list frame with current people."""
        frame = self.people_list_frame

        for widget in frame.winfo_children():
            widget.destroy()

        # Back button
        back_btn = tk.Button(
            frame, text="<", font=('Arial', 20),
            command=lambda: show_frame(self.database_frame, self.frame_list))
        back_btn.place(x=30, y=30, height=50, width=50)
        add_hover(back_btn, frame)

        # Title
        tk.Label(
            frame, text="Known People",
            font=('Arial', 16, 'bold')).place(x=100, y=40)

        people = self.get_known_people()

        if not people:
            tk.Label(
                frame,
                text="No people found in database.\nAdd folders to faces/known/",
                font=('Arial', 12)).place(x=130, y=150)
        else:
            for idx, person_name in enumerate(people):
                num_images = len(self.get_person_images(person_name))
                btn = tk.Button(
                    frame,
                    text=f"{person_name} ({num_images} photos)",
                    font=('Arial', 12),
                    command=lambda n=person_name: self.show_person_images(n))
                btn.place(x=50, y=100 + idx * 50, height=40, width=400)
                add_hover(btn, frame)

    def show_people_list(self):
        """Show the people list frame."""
        self.refresh_people_list()
        show_frame(self.people_list_frame, self.frame_list)

