import argparse
import textwrap

import cv2
from PIL import Image
from google import genai


parser = argparse.ArgumentParser()
parser.add_argument("--prompt", default="What objects are in this image? Be concise.", help="Prompt to send with the image")
parser.add_argument("--model", default="gemini-2.0-flash", help="Gemini model name")
parser.add_argument("--source", default=0, help="Camera index or video file path (default: 0)")
args = parser.parse_args()

client = genai.Client()
source = int(args.source) if str(args.source).isdigit() else args.source
cap = cv2.VideoCapture(source)

response_text = "Press ENTER to query Gemini. Press Q to quit."
paused = False
display_frame = None


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


while cap.isOpened():
    if not paused:
        ret, frame = cap.read()
        if not ret:
            break
        display_frame = frame.copy()

    draw_text_box(display_frame, response_text)
    cv2.imshow("Gemini", display_frame)
    key = cv2.waitKey(1) & 0xFF

    if key == 13 and not paused:  # Enter — capture and query
        paused = True
        response_text = "Querying Gemini..."
        pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        response = client.models.generate_content(model=args.model, contents=[pil_img, args.prompt])
        response_text = response.text.strip()
        print(response_text)

    elif key == ord(" "):  # Space — resume preview
        paused = False
        response_text = "Press ENTER to query Gemini. Press Q to quit."

    elif key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
