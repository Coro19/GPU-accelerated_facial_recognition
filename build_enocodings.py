import os
import pickle
import logging
from pathlib import Path
import cv2
import numpy as np
from insightface.app import FaceAnalysis

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

known_dir = Path("faces/known")
db_file = Path("faces/encodings.pkl")

ctx_id = int(os.environ.get("INSIGHTFACE_CTX_ID", "-1"))
app = FaceAnalysis(name="buffalo_l")
try:
    app.prepare(ctx_id=ctx_id, det_size=(640, 640), det_thresh=0.1)
except Exception as ex:
    logging.warning("prepare(ctx_id=%s) failed: %s. Falling back to CPU (ctx_id=-1).", ctx_id, ex)
    ctx_id = -1
    app.prepare(ctx_id=ctx_id, det_size=(640, 640), det_thresh=0.1)

all_encodings = []
all_names = []

if not known_dir.exists():
    logging.error("Known directory %s does not exist.", known_dir)
else:
    for person_dir in sorted(known_dir.iterdir()):
        if not person_dir.is_dir():
            continue
        name = person_dir.name
        for pattern in ("*.jpg", "*.jpeg", "*.png", "*.bmp"):
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

db_file.parent.mkdir(parents=True, exist_ok=True)

payload = {"encodings": [e.tolist() for e in all_encodings], "names": all_names}
with open(db_file, "wb") as f:
    pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)

logging.info("Database successfully saved to %s", db_file)
