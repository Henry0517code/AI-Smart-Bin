import argparse
import time

import serial


def parse_args():
    parser = argparse.ArgumentParser(description="Send low-level motor commands over serial.")
    parser.add_argument("--port", default="/dev/ttyACM0", help="Serial port (default: /dev/ttyACM0)")
    parser.add_argument("--baud", type=int, default=115200, help="Serial baud rate (default: 115200)")
    parser.add_argument("--delay", type=float, default=3.0, help="Arduino reset wait time in seconds (default: 3.0)")
    return parser.parse_args()


def read_serial_line(ser):
    raw = ser.readline()
    if not raw:
        return None
    decoded = raw.decode("utf-8", errors="replace").strip()
    print(f"received: {decoded!r}")
    return decoded


def send_command(ser, command: int):
    ser.write(f"{command}\n".encode("utf-8"))
    ser.flush()
    print(f"sent: {command}")


def main():
    args = parse_args()

    with serial.Serial(args.port, args.baud, timeout=3) as ser:
        time.sleep(args.delay)
        ser.reset_input_buffer()

        print(f"connected: {args.port} @ {args.baud}")
        print("enter a motor position/command, or q to quit")

        while True:
            raw = input("go to> ").strip()

            if raw.lower() in {"q", "quit", "exit"}:
                break
            if not raw:
                continue

            try:
                command = int(raw)
            except ValueError:
                print("please enter an integer command")
                continue

            send_command(ser, command)
            while True:
                line = read_serial_line(ser)
                if line is None:
                    break


if __name__ == "__main__":
    main()
