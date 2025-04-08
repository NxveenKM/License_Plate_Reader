import torch
import cv2
import pytesseract
import numpy as np
import imutils

# Path to tesseract if needed (on macOS via Homebrew)
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt')  # Update path if needed
model.conf = 0.5  # Confidence threshold

def extract_text_from_plate(plate_img):
    gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    config = "--psm 8 --oem 3"
    text = pytesseract.image_to_string(thresh, config=config)
    return text.strip()

def process_frame(frame):
    results = model(frame)
    detections = results.xyxy[0].cpu().numpy()

    for det in detections:
        x1, y1, x2, y2, conf, cls = det
        x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))
        plate_img = frame[y1:y2, x1:x2]

        text = extract_text_from_plate(plate_img)
        label = text if text else "Plate"

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    return frame

def start_lpr():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Could not access webcam.")
        return

    print("📷 Starting License Plate Reader... (Press 'q' to quit)")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = imutils.resize(frame, width=800)
        output = process_frame(frame)
        cv2.imshow("YOLOv5 License Plate Reader", output)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    start_lpr()
