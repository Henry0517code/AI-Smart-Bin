import argparse
import textwrap

import cv2
from PIL import Image
from picamera2 import Picamera2
from google import genai


def parse_args():
    parser = argparse.ArgumentParser(description="Query Gemini with a live Picamera2 frame.")
    parser.add_argument("--prompt", default="What objects are in this image? Be concise.", help="Prompt to send with the image")
    parser.add_argument("--model", default="gemini-2.0-flash", help="Gemini model name")
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


def draw_text_box(frame, text, max_width=60):
    lines = []
    for paragraph in text.splitlines():
        lines.extend(textwrap.wrap(paragraph, max_width) or [""])
    overlay = frame.copy()
    box_h = len(lines) * 22 + 16
    cv2.rectangle(overlay, (0, 0), (frame.shape[1], box_h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    for i, line in enumerate(lines):
        cv2.putText(frame, line, (8, 20 + i * 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 1, cv2.LINE_AA)


def main():
    args = parse_args()
    client = genai.Client()
    picam2 = None

    try:
        picam2 = start_camera(args.width, args.height)

        paused = False
        display_frame = None
        status = "Press ENTER to query Gemini. SPACE to resume. Q to quit."

        while True:
            if not paused:
                frame = picam2.capture_array()
                display_frame = frame.copy()

            draw_text_box(display_frame, status)
            cv2.imshow("Gemini", display_frame)
            key = cv2.waitKey(1) & 0xFF

            if key == 13 and not paused:  # Enter — capture and query
                paused = True
                status = "Querying Gemini..."
                pil_img = Image.fromarray(frame)  # Picamera2 RGB888 — no conversion needed
                response = client.models.generate_content(model=args.model, contents=[pil_img, args.prompt])
                status = response.text.strip()
                print(status)

            elif key == ord(" "):  # Space — resume preview
                paused = False
                status = "Press ENTER to query Gemini. SPACE to resume. Q to quit."

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
