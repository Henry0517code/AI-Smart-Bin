import argparse

import cv2
from ultralytics import YOLO


parser = argparse.ArgumentParser()
parser.add_argument("--model", required=True, help="Path to YOLO model (e.g. yolo26n_ncnn_model)")
parser.add_argument("--source", default=0, help="Camera index or video file path (default: 0)")
args = parser.parse_args()

model = YOLO(args.model, task="classify")

source = int(args.source) if str(args.source).isdigit() else args.source
cap = cv2.VideoCapture(source)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)
    r = results[0]
    print(r.names[r.probs.top1])
    annotated = r.plot()

    cv2.imshow("Inference", annotated)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
