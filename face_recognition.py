import os
import logging
import pickle
from pathlib import Path

import cv2
import numpy as np
import torch
from ultralytics import YOLO
from insightface.app import FaceAnalysis
from settings_tab import SettingsManager

# --- Configuration (loaded from settings.json) ---
settings = SettingsManager()
ENCODINGS_FILE = settings.db_file
YOLO_MODEL = "yolov8m.pt"
DETECTION_SIZE = settings.detection_size
DETECTION_THRESHOLD = settings.detection_threshold
RECOGNITION_THRESHOLD = 1.0
MAX_TRACK_AGE = 30  # Remove tracks not seen for this many frames

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# --- Face Analysis Setup ---
ctx_id = int(os.environ.get("INSIGHTFACE_CTX_ID", "-1"))
app = FaceAnalysis(name="buffalo_l")
try:
    app.prepare(ctx_id=ctx_id, det_size=DETECTION_SIZE, det_thresh=DETECTION_THRESHOLD)
except Exception as ex:
    logging.warning("prepare(ctx_id=%s) failed: %s. Falling back to CPU (ctx_id=-1).", ctx_id, ex)
    ctx_id = -1
    app.prepare(ctx_id=ctx_id, det_size=DETECTION_SIZE, det_thresh=DETECTION_THRESHOLD)

# --- Load Known Faces Database ---
if not ENCODINGS_FILE.exists():
    logging.error("Encodings file not found: %s. Run build_encodings.py first.", ENCODINGS_FILE)
    raise FileNotFoundError(f"Encodings file not found: {ENCODINGS_FILE}")

with open(ENCODINGS_FILE, "rb") as f:
    db = pickle.load(f)
known_encodings = db["encodings"]
known_names = db["names"]
logging.info("Loaded %d known face encodings.", len(known_encodings))

# --- YOLO Model Setup ---
model = YOLO(YOLO_MODEL)
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
logging.info("YOLO model loaded on %s.", device)

# --- Video Capture ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    logging.error("Could not open video capture device.")
    raise RuntimeError("Could not open video capture device.")

# Track history: {track_id: {"name": str, "face_box": tuple, "last_seen": int}}
track_history = {}
frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    annotated_frame = frame.copy()
    results = model.track(frame, classes=[0], verbose=False, imgsz=640, persist=True)

    # Track IDs seen in this frame (for cleanup)
    current_track_ids = set()

    if results[0].boxes is not None and results[0].boxes.id is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
        track_ids = results[0].boxes.id.cpu().numpy().astype(int)

        for box, track_id in zip(boxes, track_ids):
            current_track_ids.add(track_id)
            x1, y1, x2, y2 = box

            name = "Unknown"
            face_box_trbl = None

            if track_id in track_history and track_history[track_id]["face_box"] is not None and track_history[track_id]["name"] != "Unknown":
                data = track_history[track_id]
                name = data["name"]
                face_box_trbl = data["face_box"]
                # Update last seen
                track_history[track_id]["last_seen"] = frame_count
            else:
                person_crop = frame[y1:y2, x1:x2]
                if person_crop.size > 0:
                    faces = app.get(person_crop)

                    if faces:
                        face = faces[0]
                        bbox = face.bbox.astype(int)
                        face_box_trbl = (bbox[1], bbox[2], bbox[3], bbox[0])
                        face_enc = face.embedding
                        face_enc = face_enc / np.linalg.norm(face_enc)
                        distances = np.linalg.norm(np.array(known_encodings) - face_enc, axis=1)
                        min_dist = np.min(distances)
                        best_match_index = np.argmin(distances)

                        if min_dist < RECOGNITION_THRESHOLD:
                            name = known_names[best_match_index]

                track_history[track_id] = {
                    "name": name,
                    "face_box": face_box_trbl,
                    "last_seen": frame_count
                }

            if face_box_trbl is not None:
                top, right, bottom, left = face_box_trbl

                abs_top = y1 + top
                abs_right = x1 + right
                abs_bottom = y1 + bottom
                abs_left = x1 + left

                cv2.rectangle(
                    annotated_frame,
                    (abs_left, abs_top),
                    (abs_right, abs_bottom),
                    (0, 255, 0),
                    2
                )
                cv2.putText(
                    annotated_frame,
                    name,
                    (abs_left, abs_top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )
            else:
                cv2.rectangle(
                    annotated_frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 0, 255),
                    2
                )
                cv2.putText(
                    annotated_frame,
                    "Searching for face...",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2
                )

    # Clean up old tracks that haven't been seen recently
    stale_ids = [
        tid for tid, data in track_history.items()
        if frame_count - data.get("last_seen", 0) > MAX_TRACK_AGE
    ]
    for tid in stale_ids:
        del track_history[tid]

    cv2.imshow("Facial detection & recognition", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()