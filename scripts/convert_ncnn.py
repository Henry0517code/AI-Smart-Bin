import argparse
import shutil

from ultralytics import YOLO


parser = argparse.ArgumentParser()
parser.add_argument("--input", help="Path to input .pt model")
parser.add_argument("--output", help="Destination path for the exported NCNN model directory")
args = parser.parse_args()

model = YOLO(args.input)
result = model.export(format="ncnn")

if args.output:
    shutil.move(str(result), args.output)