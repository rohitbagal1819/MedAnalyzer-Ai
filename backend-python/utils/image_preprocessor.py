"""
Image Preprocessor — OpenCV image preprocessing for OCR
Grayscale conversion, binarization, denoising.
"""

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None


class ImagePreprocessor:
    """Preprocesses images for better OCR accuracy."""

    def preprocess(self, image_path):
        """
        Preprocess an image for OCR.
        Steps: Load → Grayscale → Denoise → Binarize → Deskew
        Returns: Preprocessed numpy array or None if cv2 unavailable
        """
        if cv2 is None:
            return None

        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                return None

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Denoise
            denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)

            # Adaptive thresholding for binarization
            binary = cv2.adaptiveThreshold(
                denoised, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )

            # Optional: slight blur to remove noise artifacts
            cleaned = cv2.medianBlur(binary, 3)

            return cleaned

        except Exception as e:
            print(f"Image preprocessing error: {e}")
            return None

    def resize_for_ocr(self, img, target_dpi=300):
        """Resize image to optimal DPI for OCR."""
        if cv2 is None or img is None:
            return img

        # Assume 72 DPI input, scale to target DPI
        scale = target_dpi / 72.0
        width = int(img.shape[1] * scale)
        height = int(img.shape[0] * scale)

        if width > 0 and height > 0:
            return cv2.resize(img, (width, height), interpolation=cv2.INTER_CUBIC)
        return img

    def remove_borders(self, img):
        """Remove black borders from scanned documents."""
        if cv2 is None or img is None:
            return img

        try:
            contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest)
                return img[y:y+h, x:x+w]
        except:
            pass

        return img
