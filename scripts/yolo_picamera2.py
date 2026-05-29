import argparse
import time

import cv2
from picamera2 import Picamera2
from ultralytics import YOLO


def parse_args():
    parser = argparse.ArgumentParser(description="Run YOLO classification with Picamera2.")
    parser.add_argument("--model", required=True, help="Path to YOLO model (e.g. models/best_ncnn_model)")
    parser.add_argument("--width", type=int, default=640, help="Camera capture width (default: 640)")
    parser.add_argument("--height", type=int, default=480, help="Camera capture height (default: 480)")
    return parser.parse_args()


def start_camera(width: int, height: int):
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(
        main={"size": (width, height), "format": "RGB888"}
    )
    picam2.configure(config)
    picam2.start()
    return picam2


def main():
    args = parse_args()
    model = YOLO(args.model, task="classify")
    picam2 = None

    try:
        picam2 = start_camera(args.width, args.height)

        paused = False
        display_frame = None

        while True:
            if not paused:
                frame = picam2.capture_array()
                display_frame = frame.copy()

            cv2.imshow("Inference", display_frame)

            key = cv2.waitKey(1) & 0xFF

            # Enter -> infer and freeze result
            if key == 13 and not paused:
                results = model(frame, verbose=False)
                r = results[0]

                print(r.names[r.probs.top1])

                display_frame = r.plot()
                paused = True

            # Space -> resume live preview
            elif key == ord(" "):
                paused = False

            # q -> quit
            elif key == ord("q"):
                break

    except KeyboardInterrupt:
        pass

    finally:
        if picam2 is not None:
            picam2.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
