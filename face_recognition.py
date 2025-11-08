from ultralytics import YOLO
import cv2
import pickle
import numpy as np
from insightface.app import FaceAnalysis
import os
import logging
import torch
ctx_id = int(os.environ.get("INSIGHTFACE_CTX_ID", "-1"))
app = FaceAnalysis(name="buffalo_l")
try:
    app.prepare(ctx_id=ctx_id, det_size=(640, 640), det_thresh=0.1)
except Exception as ex:
    logging.warning("prepare(ctx_id=%s) failed: %s. Falling back to CPU (ctx_id=-1).", ctx_id, ex)
    ctx_id = -1
    app.prepare(ctx_id=ctx_id, det_size=(640, 640), det_thresh=0.1)

with open("faces/encodings.pkl", "rb") as f:
    db = pickle.load(f)
known_encodings = db["encodings"]
known_names = db["names"]

model = YOLO("yolov8m.pt")
if torch.cuda.is_available():
    model.to("cuda")
else:
    model.to("cpu")
cap = cv2.VideoCapture(0)

track_history = {}

while True:
    ret, frame = cap.read()
    if not ret:
        break

    annotated_frame = frame.copy()
    results = model.track(frame, classes=[0], verbose=False, imgsz=640, persist=True)

    if results[0].boxes is not None and results[0].boxes.id is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
        track_ids = results[0].boxes.id.cpu().numpy().astype(int)

        for box, track_id in zip(boxes, track_ids):
            x1, y1, x2, y2 = box

            name = "Unknown"
            face_box_trbl = None

            if track_id in track_history and track_history[track_id]["face_box"] is not None and track_history[track_id]["name"] != "Unknown":
                data = track_history[track_id]
                name = data["name"]
                face_box_trbl = data["face_box"]
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

                        if min_dist < 1.0:
                            name = known_names[best_match_index]

                track_history[track_id] = {"name": name, "face_box": face_box_trbl}

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

    cv2.imshow("Facial detection & recognition", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()