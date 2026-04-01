"""
Settings manager for the Facial Recognition application.

Handles loading, saving, and validating application settings.
Provides a tkinter-based settings UI panel.
"""

import json
import logging
import tkinter as tk
from tkinter import messagebox, filedialog
from pathlib import Path

from graphics import add_hover, show_frame

# --- Settings File Location ---
SETTINGS_DIR = Path(__file__).resolve().parent
SETTINGS_FILE = SETTINGS_DIR / "settings.json"

# --- Default Settings ---
DEFAULT_SETTINGS = {
    "known_faces_dir": "faces/known",
    "db_file": "faces/encodings.pkl",
    "detection_size": 640,
    "detection_threshold": 0.1,
}

# --- Validation Constraints ---
MIN_DETECTION_SIZE = 32
MAX_DETECTION_SIZE = 2048
MIN_THRESHOLD = 0.0
MAX_THRESHOLD = 1.0

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class SettingsManager:
    """Loads, validates, and persists application settings from a JSON file."""

    def __init__(self):
        self._settings: dict = {}
        self.load()

    # --- Persistence ---

    def load(self):
        """Load settings from the JSON file, creating defaults if missing."""
        if not SETTINGS_FILE.exists():
            logging.info("Settings file not found. Creating defaults at %s", SETTINGS_FILE)
            self._settings = dict(DEFAULT_SETTINGS)
            self.save()
            return

        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            logging.error("Failed to read settings file: %s. Reverting to defaults.", exc)
            self._settings = dict(DEFAULT_SETTINGS)
            self.save()
            return

        # Merge with defaults so newly-added keys are always present
        merged = dict(DEFAULT_SETTINGS)
        merged.update(data)
        self._settings = merged

    def save(self):
        """Write current settings to the JSON file."""
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self._settings, f, indent=4)
        logging.info("Settings saved to %s", SETTINGS_FILE)

    # --- Accessors ---

    @property
    def known_faces_dir(self) -> Path:
        return Path(self._settings["known_faces_dir"])

    @property
    def db_file(self) -> Path:
        return Path(self._settings["db_file"])

    @property
    def detection_size(self) -> tuple[int, int]:
        s = self._settings["detection_size"]
        return (s, s)

    @property
    def detection_threshold(self) -> float:
        return float(self._settings["detection_threshold"])

    # --- Validation helpers ---

    @staticmethod
    def validate_directory(value: str) -> str | None:
        """Return an error message if *value* is not a valid directory path, else None."""
        value = value.strip()
        if not value:
            return "Directory path cannot be empty."
        path = Path(value)
        if path.exists() and not path.is_dir():
            return f"'{value}' exists but is not a directory."
        # Allow non-existent paths (will be created later), but check for illegal characters
        try:
            path.resolve()
        except (OSError, ValueError):
            return f"'{value}' is not a valid path."
        return None

    @staticmethod
    def validate_file_path(value: str) -> str | None:
        """Return an error message if *value* is not a usable file path, else None."""
        value = value.strip()
        if not value:
            return "File path cannot be empty."
        path = Path(value)
        if path.exists() and path.is_dir():
            return f"'{value}' is a directory, not a file."
        try:
            path.resolve()
        except (OSError, ValueError):
            return f"'{value}' is not a valid path."
        return None

    @staticmethod
    def validate_detection_size(value: str) -> str | None:
        """Return an error message if *value* is not a valid detection size, else None."""
        value = value.strip()
        if not value:
            return "Detection size cannot be empty."
        try:
            size = int(value)
        except ValueError:
            return "Detection size must be an integer."
        if size < MIN_DETECTION_SIZE or size > MAX_DETECTION_SIZE:
            return f"Detection size must be between {MIN_DETECTION_SIZE} and {MAX_DETECTION_SIZE}."
        if size % 32 != 0:
            return "Detection size must be a multiple of 32."
        return None

    @staticmethod
    def validate_threshold(value: str) -> str | None:
        """Return an error message if *value* is not a valid threshold, else None."""
        value = value.strip()
        if not value:
            return "Threshold cannot be empty."
        try:
            t = float(value)
        except ValueError:
            return "Threshold must be a number."
        if t < MIN_THRESHOLD or t > MAX_THRESHOLD:
            return f"Threshold must be between {MIN_THRESHOLD} and {MAX_THRESHOLD}."
        return None

    # --- Bulk update with validation ---

    def update(self, known_faces_dir: str, db_file: str,
               detection_size: str, detection_threshold: str) -> list[str]:
        """Validate and apply all settings at once.

        Returns a list of error messages (empty if everything is valid).
        """
        errors: list[str] = []

        err = self.validate_directory(known_faces_dir)
        if err:
            errors.append(f"Known Faces Directory: {err}")

        err = self.validate_file_path(db_file)
        if err:
            errors.append(f"Database File: {err}")

        err = self.validate_detection_size(detection_size)
        if err:
            errors.append(f"Detection Size: {err}")

        err = self.validate_threshold(detection_threshold)
        if err:
            errors.append(f"Detection Threshold: {err}")

        if errors:
            return errors

        self._settings["known_faces_dir"] = known_faces_dir.strip()
        self._settings["db_file"] = db_file.strip()
        self._settings["detection_size"] = int(detection_size.strip())
        self._settings["detection_threshold"] = float(detection_threshold.strip())
        self.save()
        return []


class SettingsTab:
    """Builds and manages the Settings UI inside a given tkinter frame."""

    LABEL_FONT = ('Arial', 11)
    ENTRY_FONT = ('Arial', 11)
    TITLE_FONT = ('Arial', 16, 'bold')
    HINT_FONT = ('Arial', 9)

    def __init__(self, settings_frame: tk.Frame, menu_frame: tk.Frame,
                 frame_list: list[tk.Frame], settings_manager: SettingsManager):
        self.frame = settings_frame
        self.menu_frame = menu_frame
        self.frame_list = frame_list
        self.settings = settings_manager

        # Tk variables for entries
        self._var_known_dir = tk.StringVar()
        self._var_db_file = tk.StringVar()
        self._var_det_size = tk.StringVar()
        self._var_threshold = tk.StringVar()

        self._build_ui()
        self._load_current_values()

    # --- UI Construction ---

    def _build_ui(self):
        frame = self.frame

        # Back button
        back_btn = tk.Button(
            frame, text="<", font=('Arial', 20),
            command=lambda: show_frame(self.menu_frame, self.frame_list))
        back_btn.place(x=30, y=30, height=50, width=50)
        add_hover(back_btn, frame)

        # Title
        tk.Label(frame, text="Settings", font=self.TITLE_FONT).place(x=100, y=40)

        y_offset = 100
        row_height = 70

        # --- Known Faces Directory ---
        tk.Label(frame, text="Known Faces Directory:", font=self.LABEL_FONT).place(x=30, y=y_offset)
        dir_entry = tk.Entry(frame, textvariable=self._var_known_dir, font=self.ENTRY_FONT, width=30)
        dir_entry.place(x=30, y=y_offset + 25, width=370, height=28)
        browse_dir_btn = tk.Button(
            frame, text="...", font=('Arial', 10),
            command=self._browse_directory)
        browse_dir_btn.place(x=410, y=y_offset + 25, width=40, height=28)
        add_hover(browse_dir_btn, frame)
        tk.Label(frame, text="Folder containing known person sub-folders",
                 font=self.HINT_FONT, fg="gray").place(x=30, y=y_offset + 55)

        y_offset += row_height

        # --- Database File ---
        tk.Label(frame, text="Database File (.pkl):", font=self.LABEL_FONT).place(x=30, y=y_offset)
        db_entry = tk.Entry(frame, textvariable=self._var_db_file, font=self.ENTRY_FONT, width=30)
        db_entry.place(x=30, y=y_offset + 25, width=370, height=28)
        browse_file_btn = tk.Button(
            frame, text="...", font=('Arial', 10),
            command=self._browse_file)
        browse_file_btn.place(x=410, y=y_offset + 25, width=40, height=28)
        add_hover(browse_file_btn, frame)
        tk.Label(frame, text="Path to the face encodings pickle file",
                 font=self.HINT_FONT, fg="gray").place(x=30, y=y_offset + 55)

        y_offset += row_height

        # --- Detection Size ---
        tk.Label(frame, text="Detection Size:", font=self.LABEL_FONT).place(x=30, y=y_offset)
        det_entry = tk.Entry(frame, textvariable=self._var_det_size, font=self.ENTRY_FONT, width=10)
        det_entry.place(x=30, y=y_offset + 25, width=120, height=28)
        tk.Label(frame, text=f"Integer, multiple of 32  ({MIN_DETECTION_SIZE}–{MAX_DETECTION_SIZE})",
                 font=self.HINT_FONT, fg="gray").place(x=160, y=y_offset + 28)

        y_offset += row_height

        # --- Detection Threshold ---
        tk.Label(frame, text="Detection Threshold:", font=self.LABEL_FONT).place(x=30, y=y_offset)
        thr_entry = tk.Entry(frame, textvariable=self._var_threshold, font=self.ENTRY_FONT, width=10)
        thr_entry.place(x=30, y=y_offset + 25, width=120, height=28)
        tk.Label(frame, text=f"Float  ({MIN_THRESHOLD}–{MAX_THRESHOLD})",
                 font=self.HINT_FONT, fg="gray").place(x=160, y=y_offset + 28)

        y_offset += row_height + 10

        # --- Action Buttons ---
        save_btn = tk.Button(
            frame, text="Save Settings", font=('Arial', 13),
            command=self._on_save)
        save_btn.place(x=30, y=y_offset, height=40, width=200)
        add_hover(save_btn, frame)

        reset_btn = tk.Button(
            frame, text="Reset to Defaults", font=('Arial', 13),
            command=self._on_reset)
        reset_btn.place(x=250, y=y_offset, height=40, width=200)
        add_hover(reset_btn, frame)

    # --- Helpers ---

    def _load_current_values(self):
        """Populate entry fields from the current settings."""
        self._var_known_dir.set(self.settings._settings["known_faces_dir"])
        self._var_db_file.set(self.settings._settings["db_file"])
        self._var_det_size.set(str(self.settings._settings["detection_size"]))
        self._var_threshold.set(str(self.settings._settings["detection_threshold"]))

    def _browse_directory(self):
        """Open a folder-picker dialog for the known faces directory."""
        chosen = filedialog.askdirectory(title="Select Known Faces Directory")
        if chosen:
            self._var_known_dir.set(chosen)

    def _browse_file(self):
        """Open a file-picker dialog for the database file."""
        chosen = filedialog.asksaveasfilename(
            title="Select Database File",
            defaultextension=".pkl",
            filetypes=[("Pickle files", "*.pkl"), ("All files", "*.*")])
        if chosen:
            self._var_db_file.set(chosen)

    # --- Callbacks ---

    def _on_save(self):
        """Validate inputs and save settings."""
        errors = self.settings.update(
            known_faces_dir=self._var_known_dir.get(),
            db_file=self._var_db_file.get(),
            detection_size=self._var_det_size.get(),
            detection_threshold=self._var_threshold.get(),
        )
        if errors:
            messagebox.showerror("Invalid Settings", "\n".join(errors))
        else:
            messagebox.showinfo("Settings Saved", "All settings have been saved successfully.")
            self._load_current_values()  # refresh in case values were stripped

    def _on_reset(self):
        """Reset all fields to default values."""
        if messagebox.askyesno("Reset Settings", "Reset all settings to their defaults?"):
            self.settings._settings = dict(DEFAULT_SETTINGS)
            self.settings.save()
            self._load_current_values()
            messagebox.showinfo("Settings Reset", "Settings have been reset to defaults.")
