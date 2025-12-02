# Document Aligner

A lightweight tool to automatically deskew and rotate scanned or photographed documents. Provides both a simple GUI (Tkinter) and a headless CLI for batch processing.

## Features
- Auto rotation using adaptive threshold + minAreaRect
- Edge/Hough lines fallback when text is faint
- Displays applied rotation angle
- Scales large images to fit an 800x800 preview canvas
- GUI or CLI modes with identical alignment logic

## Why
Crooked scans waste time when reading, OCRing, or sharing. This tool removes skew in one click or one command.

## Installation
Make sure you are in your virtual environment, then install dependencies:
```bash
pip install opencv-python Pillow
```
(NumPy ships with OpenCV; Tkinter comes with standard Python on Windows.)

## Usage
### GUI Mode
```bash
cd "./Document_Aligner"
"D:/ML projects/.venv/Scripts/python.exe" doc_align.py --gui
```
1. Click `Load Image`.
2. View aligned result with angle overlay.
3. (Save functionality can be added later.)

### CLI (Headless) Mode
Process and save an aligned copy:
```bash
"D:/ML projects/.venv/Scripts/python.exe" doc_align.py --input input_scan.jpg --output aligned_scan.jpg
```
Console output example:
```
[INFO] Processed 'input_scan.jpg' | rotation applied: 2.31 deg
[INFO] Saved aligned image to: aligned_scan.jpg
```
If the angle is 0.00 degrees, the page was already straight, or skew detection was not triggered.

## How It Works
1. Adaptive threshold isolates foreground (text/edges).
2. Foreground pixel coordinates -> minimum area bounding box -> rotation angle.
3. If insufficient foreground, Canny + Hough lines estimate the dominant text orientation.
4. Image rotated with a replication border to avoid clipping.

## Troubleshooting
| Issue | Cause | Fix |
|-------|-------|-----|
| Blank white preview | Image loaded but foreground too faint | Try higher-contrast scan or ensure text exists; fallback now uses edges. |
| Angle always 0.00 | Page already straight or detection failed | Test with an intentionally rotated page; check lighting. |
| No window appears | Window behind other apps | Check taskbar; run with `--gui` again. |

## Roadmap / Ideas
- Batch processing of an entire folder (`--folder`)
- Auto cropping margins
- Save button in GUI
- Confidence score for detected angle
- OCR integration after alignment

## Tech Stack
Python, OpenCV, Tkinter, Pillow.

## License
Personal/learning use. Add a license if you plan to distribute.

## Contributing
Open to enhancements. Suggestions welcome.

---
Made for quick, hassle-free document cleanup.
