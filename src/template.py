import time

import serial
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


def classify(frame):
    # TODO: implement with Gemini or YOLO
    # return a command int (1, 2, or 3), or None if nothing detected
    raise NotImplementedError


def main():
    ser = setup_serial()
    picam2 = setup_camera()

    try:
        while True:
            frame = capture_frame(picam2)

            # TODO: Implement detection and moving logic here!

    except KeyboardInterrupt:
        pass

    finally:
        picam2.stop()
        ser.close()


if __name__ == "__main__":
    main()
