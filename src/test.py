import time

import serial
from google import genai
from PIL import Image
from picamera2 import Picamera2


def setup_serial(port="/dev/ttyACM0", baud=115200, timeout=0.1):
    ser = serial.Serial(port, baud, timeout=timeout)
    time.sleep(3)
    ser.reset_input_buffer()
    return ser


def send_command(ser, command):
    ser.write(f"{command}\n".encode())
    ser.flush()
    print("sent:", command)


def read_serial_line(ser):
    raw = ser.readline()
    if not raw:
        return None
    return raw.decode("utf-8", errors="replace").strip()


def setup_camera(width=640, height=480):
    picam2 = Picamera2()
    picam2.configure(
        picam2.create_preview_configuration(
            main={"size": (width, height), "format": "RGB888"}
        )
    )
    picam2.start()
    return picam2


def capture_frame(picam2):
    return picam2.capture_array()


def to_pil(frame):
    return Image.fromarray(frame)


def classify(client, frame):
    prompt = (
        "Look at this image. If you see a piece of waste ready to be sorted, "
        "reply with exactly one digit: 1 for glass, 2 for paper, 3 for plastic. "
        "If no waste is present (e.g. only the yellow tray), reply: none."
    )
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=[to_pil(frame), prompt],
    )
    text = response.text.strip()
    print("gemini:", text)
    return int(text) if text in ("1", "2", "3") else None


def main():
    client = genai.Client()
    ser = setup_serial()
    picam2 = setup_camera()

    try:
        while True:
            frame   = capture_frame(picam2)
            command = classify(client, frame)

            if command is None:
                time.sleep(3)
                continue

            send_command(ser, command)
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                line = read_serial_line(ser)
                if line:
                    print("received:", line)
                    if line == "Servo back to level":
                        break

            send_command(ser, 0)
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                line = read_serial_line(ser)
                if line:
                    print("received:", line)
                    if line == "Homing done, pointer = 0":
                        break

    except KeyboardInterrupt:
        pass

    finally:
        picam2.stop()
        ser.close()


if __name__ == "__main__":
    main()
