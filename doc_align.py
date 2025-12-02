import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import argparse
import os
import sys
from typing import Tuple


def rotate_document(image) -> Tuple[np.ndarray, float]:
	"""Deskew a document using adaptive threshold + minAreaRect, with edge/Hough fallback.
	Returns rotated image and applied angle in degrees (angle=0 if none)."""
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	try:
		binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
			cv2.THRESH_BINARY_INV, 15, 9)
	except Exception:
		_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

	coords = np.column_stack(np.where(binary > 0))
	# Fallback if too few foreground pixels detected
	if len(coords) < 100:
		edges = cv2.Canny(gray, 50, 150)
		lines = cv2.HoughLines(edges, 1, np.pi / 180, 150)
		if lines is not None:
			angles = []
			for ln in lines[:30]:
				rho, theta = ln[0]
				deg = theta * 180 / np.pi
				if deg > 90:
					deg -= 180
				angles.append(deg)
			if angles:
				angle = float(np.mean(angles))
				(h, w) = image.shape[:2]
				center = (w // 2, h // 2)
				M = cv2.getRotationMatrix2D(center, angle, 1.0)
				rot = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
				return rot, angle
		return image, 0.0

	rect = cv2.minAreaRect(coords)
	angle = rect[2]
	if angle < 45:
		angle = -angle
	else:
		angle = 90 - angle
	(h, w) = image.shape[:2]
	center = (w // 2, h // 2)
	M = cv2.getRotationMatrix2D(center, angle, 1.0)
	rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
	return rotated, float(angle)


def load_image():
	filepath = filedialog.askopenfilename()
	if not filepath:
		return
	image = cv2.imread(filepath)
	if image is None:
		messagebox.showerror("Error", "Failed to read image.")
		return
	aligned_image, angle = rotate_document(image)
	print(f"[INFO] Loaded '{os.path.basename(filepath)}' | rotation applied: {angle:.2f} deg")
	display_image(aligned_image, angle, os.path.basename(filepath))


def display_image(cv_img, angle: float = 0.0, title: str = ""):
	# Scale to fit canvas while keeping aspect ratio
	CANVAS_W, CANVAS_H = 800, 800
	(h, w) = cv_img.shape[:2]
	scale = min(CANVAS_W / w, CANVAS_H / h, 1.0)
	if scale < 1.0:
		cv_img = cv2.resize(cv_img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

	display = cv_img.copy()
	info = f"Angle: {angle:.2f} deg" + (f" | {title}" if title else "")
	cv2.putText(display, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 3)
	cv2.putText(display, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)
	display = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
	img = Image.fromarray(display)
	img = ImageTk.PhotoImage(img)
	canvas.delete("all")
	canvas.create_image(0, 0, anchor=tk.NW, image=img)
	canvas.image = img
	if 'status_var' in globals():
		status_var.set(info)


def run_gui():
	print("[INFO] Starting GUI mode ...")
	app = tk.Tk()
	app.title("Document Aligner")
	app.geometry("800x900")

	global canvas, status_var
	canvas = tk.Canvas(app, width=800, height=800, bg="#FFFFFF")
	canvas.pack()
	status_var = tk.StringVar(value="Ready. Click 'Load Image'.")
	status_label = tk.Label(app, textvariable=status_var, anchor="w")
	status_label.pack(fill=tk.X, padx=8, pady=4)

	button_frame = tk.Frame(app)
	button_frame.pack(fill=tk.X, side=tk.BOTTOM)

	load_btn = tk.Button(button_frame, text="Load Image", command=load_image)
	load_btn.pack(side=tk.LEFT, padx=10, pady=10)

	print("[INFO] GUI ready. Click 'Load Image' to select a file.")
	app.mainloop()
	print("[INFO] GUI closed.")


def run_cli(input_path: str, output_path: str):
	if not os.path.isfile(input_path):
		print(f"[ERROR] Input file not found: {input_path}")
		sys.exit(1)
	image = cv2.imread(input_path)
	if image is None:
		print(f"[ERROR] Failed to read image: {input_path}")
		sys.exit(1)
	aligned, angle = rotate_document(image)
	print(f"[INFO] Processed '{os.path.basename(input_path)}' | rotation applied: {angle:.2f} deg")
	if output_path:
		cv2.imwrite(output_path, aligned)
		print(f"[INFO] Saved aligned image to: {output_path}")


def parse_args():
	parser = argparse.ArgumentParser(description="Document Aligner - auto deskew & rotate scanned pages")
	parser.add_argument("--input", type=str, help="Path to input image (activates headless CLI mode)")
	parser.add_argument("--output", type=str, help="Optional path to save aligned image (CLI mode)")
	parser.add_argument("--gui", action="store_true", help="Force GUI mode even if --input provided")
	return parser.parse_args()


def main():
	args = parse_args()
	if args.input and not args.gui:
		run_cli(args.input, args.output or "aligned_output.png")
	else:
		run_gui()


if __name__ == "__main__":
	main()