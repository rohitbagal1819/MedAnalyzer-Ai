"""
OCR Agent — Tesseract + OpenCV pipeline
Extracts raw text from images and PDFs.
"""

import os
import sys

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None

try:
    import pytesseract
    # Configure Tesseract path for Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except ImportError:
    pytesseract = None

from utils.image_preprocessor import ImagePreprocessor
from utils.pdf_extractor import PDFExtractor


class OCRAgent:
    """Extracts text from medical report images and PDFs using Tesseract OCR."""

    def __init__(self):
        self.preprocessor = ImagePreprocessor()
        self.pdf_extractor = PDFExtractor()
        # Tesseract config for medical documents
        self.tess_config = '--oem 3 --psm 6 -l eng'

    def extract_text(self, file_path, file_type='image'):
        """
        Extract text from a file.
        Args:
            file_path: Path to the file
            file_type: 'pdf' or 'image'
        Returns:
            Extracted raw text string
        """
        try:
            print("  [OCR] Using local Tesseract OCR...")
            if file_type == 'pdf':
                text = self._extract_from_pdf(file_path)
            else:
                text = self._extract_from_image(file_path)

            if text and len(text.strip()) > 10:
                print(f"  [OCR] Successfully extracted {len(text)} characters")
                return text
            else:
                print("  [OCR] Tesseract returned very little text, trying alternative config...")
                return self._extract_with_alt_config(file_path)
        except Exception as e:
            print(f"  [OCR Error] {e}")
            return ""

    def _extract_from_image(self, image_path):
        """Extract text from a single image file."""
        if pytesseract is None:
            print("  [OCR] pytesseract not installed!")
            return ""

        if cv2 is not None:
            # Preprocess image for better OCR
            processed = self.preprocessor.preprocess(image_path)
            if processed is not None:
                text = pytesseract.image_to_string(processed, config=self.tess_config)
                if text and len(text.strip()) > 10:
                    return text.strip()

        # Try without preprocessing (raw image)
        text = pytesseract.image_to_string(image_path, config=self.tess_config)
        return text.strip()

    def _extract_with_alt_config(self, file_path):
        """Try alternative Tesseract configs for difficult images."""
        if pytesseract is None:
            return ""

        alt_configs = [
            '--oem 3 --psm 4 -l eng',  # Assume single column
            '--oem 3 --psm 3 -l eng',  # Fully automatic page segmentation
            '--oem 3 --psm 11 -l eng', # Sparse text
        ]

        for config in alt_configs:
            try:
                text = pytesseract.image_to_string(file_path, config=config)
                if text and len(text.strip()) > 20:
                    print(f"  [OCR] Alternative config worked: {config}")
                    return text.strip()
            except Exception:
                continue

        return ""

    def _extract_from_pdf(self, pdf_path):
        """Extract text from a PDF file."""
        # First try direct text extraction (for text-based PDFs)
        direct_text = self.pdf_extractor.extract_text_direct(pdf_path)
        if direct_text and len(direct_text.strip()) > 50:
            print("  [OCR] PDF has embedded text, extracted directly")
            return direct_text.strip()

        # If direct extraction fails, convert pages to images and OCR
        print("  [OCR] PDF is scanned/image-based, converting to images for OCR...")
        images = self.pdf_extractor.pdf_to_images(pdf_path)
        all_text = []

        for img_path in images:
            text = self._extract_from_image(img_path)
            if text:
                all_text.append(text)
            # Clean up temp image
            try:
                os.remove(img_path)
            except:
                pass

        return '\n\n'.join(all_text)
