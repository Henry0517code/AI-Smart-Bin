import argparse

import cv2
from picamera2 import Picamera2


def parse_args():
    parser = argparse.ArgumentParser(description="Show the PiCamera feed in a cv2 window.")
    parser.add_argument("--width", type=int, default=640, help="Capture width (default: 640)")
    parser.add_argument("--height", type=int, default=480, help="Capture height (default: 480)")
    return parser.parse_args()


def main():
    args = parse_args()
    picam2 = Picamera2()

    config = picam2.create_preview_configuration(
        main={"size": (args.width, args.height), "format": "RGB888"}
    )
    picam2.configure(config)

    try:
        picam2.start()

        while True:
            frame = picam2.capture_array()
            cv2.imshow("PiCam Feed", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:
                break

    except KeyboardInterrupt:
        pass

    finally:
        picam2.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
