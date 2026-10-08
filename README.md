# GPU-Accelerated Facial Recognition

A real-time face recognition app I built in Python. Point a webcam at a room and it labels the people it knows. It also comes with a small desktop GUI, so adding people or changing settings doesn't mean digging through folders by hand.

<!-- Add a demo here: ![Demo](assets/demo.gif) -->

## How it works

Running face detection on every frame is wasteful, so I track **people** instead:

1. **YOLOv8** detects and tracks every person in the frame, giving each one a stable track ID.
2. For a person who isn't identified yet, **InsightFace** finds the face inside their crop and computes an ArcFace embedding.
3. The embedding is compared against the known faces. A match means an L2 distance below `1.0` between normalised embeddings, which is roughly a cosine similarity above 0.5.
4. Once someone is recognised, the name sticks to their track ID. The expensive face step therefore runs **once per person, not once per frame**.

## The app

- **Run Face Recognition**: starts the webcam view. Press `q` to quit.
- **Manage known people**: add or delete people, browse their photos and delete individual ones.
- **Build database**: recomputes the embeddings from `faces/known/` with one click.
- **Settings**: change the paths and the detection parameters. They are validated and saved to `settings.json`.

## Getting started

Install [PyTorch](https://pytorch.org/get-started/locally/) for your CUDA version first, then:

```bash
pip install -r requirements.txt
python main.py
```

1. Add a person from the GUI and put a few photos of them in `faces/known/<Name>/`.
2. Click **Build Face Encodings Database**.
3. Click **Run Face Recognition**.

YOLOv8 uses the GPU automatically. To run InsightFace on the GPU as well, set `INSIGHTFACE_CTX_ID=0` before starting the app.

## Built with

Python · OpenCV · PyTorch · YOLOv8 (Ultralytics) · InsightFace · Tkinter

## What I'd improve next

- Re-check identities from time to time, instead of locking in the first match for a track
- Make the photo viewer work outside Windows (it currently uses `os.startfile`)
