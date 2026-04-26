"""QR code scanner backed by OpenCV's QRCodeDetector."""

import cv2
import numpy as np


class QRScanner:
    def __init__(self):
        self.cap = None
        self.qr_detector = cv2.QRCodeDetector()

    def start_camera(self, camera_index: int = 0) -> bool:
        try:
            self.cap = cv2.VideoCapture(camera_index)
            if not self.cap.isOpened():
                return False
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
            return True
        except Exception as exc:
            print(f"[scanner] start_camera failed: {exc}")
            return False

    def stop_camera(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.cap = None

    def get_frame(self):
        if not self.cap or not self.cap.isOpened():
            return None
        ok, frame = self.cap.read()
        return frame if ok else None

    def scan_qr_code(self, frame):
        if frame is None:
            return []
        try:
            data, _bbox, _ = self.qr_detector.detectAndDecode(frame)
            if data:
                return [{"data": data, "type": "QR"}]

            # Fallback: try preprocessed frame for low-contrast / noisy captures.
            processed = self._preprocess(frame)
            data, _bbox, _ = self.qr_detector.detectAndDecode(processed)
            if data:
                return [{"data": data, "type": "QR"}]
        except Exception as exc:
            print(f"[scanner] detect failed: {exc}")
        return []

    @staticmethod
    def _preprocess(frame):
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2)
            kernel = np.ones((3, 3), np.uint8)
            morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel)
            return morph
        except Exception:
            return frame
