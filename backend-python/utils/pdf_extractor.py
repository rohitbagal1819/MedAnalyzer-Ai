"""
PDF Extractor — PyMuPDF PDF to image converter
Extracts text directly or converts pages to images for OCR.
"""

import os
import tempfile

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


class PDFExtractor:
    """Extracts content from PDF files."""

    def extract_text_direct(self, pdf_path):
        """
        Extract text directly from PDF (for text-based PDFs).
        Returns extracted text or empty string.
        """
        if fitz is None:
            return ''

        try:
            doc = fitz.open(pdf_path)
            text_parts = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    text_parts.append(text)

            doc.close()
            return '\n\n'.join(text_parts)

        except Exception as e:
            print(f"PDF direct text extraction error: {e}")
            return ''

    def pdf_to_images(self, pdf_path, dpi=300):
        """
        Convert PDF pages to images for OCR processing.
        Returns list of temporary image file paths.
        """
        if fitz is None:
            return []

        image_paths = []

        try:
            doc = fitz.open(pdf_path)
            temp_dir = tempfile.mkdtemp()

            for page_num in range(len(doc)):
                page = doc[page_num]

                # Render page to image
                zoom = dpi / 72  # Default PDF DPI is 72
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)

                # Save as PNG
                img_path = os.path.join(temp_dir, f'page_{page_num + 1}.png')
                pix.save(img_path)
                image_paths.append(img_path)

            doc.close()

        except Exception as e:
            print(f"PDF to image conversion error: {e}")

        return image_paths

    def get_page_count(self, pdf_path):
        """Get the number of pages in a PDF."""
        if fitz is None:
            return 0

        try:
            doc = fitz.open(pdf_path)
            count = len(doc)
            doc.close()
            return count
        except:
            return 0
