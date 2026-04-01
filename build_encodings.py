import os
import pickle
import logging
from pathlib import Path

import cv2
import numpy as np
from insightface.app import FaceAnalysis
from settings_tab import SettingsManager

# --- Configuration (loaded from settings.json) ---
settings = SettingsManager()
KNOWN_DIR = settings.known_faces_dir
DB_FILE = settings.db_file
DETECTION_SIZE = settings.detection_size
DETECTION_THRESHOLD = settings.detection_threshold
IMAGE_PATTERNS = ("*.jpg", "*.jpeg", "*.png", "*.bmp")

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

# --- Build Encodings ---
all_encodings = []
all_names = []

if not KNOWN_DIR.exists():
    logging.error("Known directory %s does not exist.", KNOWN_DIR)
else:
    for person_dir in sorted(KNOWN_DIR.iterdir()):
        if not person_dir.is_dir():
            continue
        name = person_dir.name
        for pattern in IMAGE_PATTERNS:
            for img_path in sorted(person_dir.glob(pattern)):
                logging.info("Processing %s for %s", img_path, name)
                img = cv2.imread(str(img_path))
                if img is None:
                    logging.warning("Could not read picture at %s", img_path)
                    continue

                faces = app.get(img)
                if not faces:
                    logging.warning("Did not find face at %s", img_path)
                    continue

                for face in faces:
                    embedding = np.asarray(face.embedding, dtype=np.float32)
                    norm = np.linalg.norm(embedding)
                    if norm < 1e-8:
                        logging.warning("Embedding norm too small for %s, skipping.", img_path)
                        continue
                    embedding = embedding / norm
                    all_encodings.append(embedding)
                    all_names.append(name)

logging.info("%d embeddings collected.", len(all_encodings))

# --- Save Database ---
DB_FILE.parent.mkdir(parents=True, exist_ok=True)
payload = {"encodings": [e.tolist() for e in all_encodings], "names": all_names}
with open(DB_FILE, "wb") as f:
    pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)

logging.info("Database successfully saved to %s", DB_FILE)
