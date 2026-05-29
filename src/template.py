import cv2

import serial
from picamera2 import Picamera2


def send_command(ser, command):
    ser.write(f"{command}\n".encode())
    ser.flush()
    print("sent:", command)


def read_serial_line(ser):
    raw = ser.readline()
    if not raw:
        return None
    return raw.decode("utf-8", errors="replace").strip()


def main():
    # Serial
    ser = serial.Serial("/dev/ttyACM0", 115200, timeout=1)

    # Camera
    picam2 = Picamera2()
    picam2.configure(
        picam2.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
    )
    picam2.start()

    while True:
        frame = picam2.capture_array()

        # TODO: Implement detection and moving logics here!

        cv2.imshow("Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    picam2.stop()
    ser.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()