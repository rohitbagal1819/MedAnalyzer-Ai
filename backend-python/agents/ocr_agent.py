"""
OCR Agent — Text extraction from medical reports
Primary: Gemini Vision AI (reads any format, understands medical context)
Fallback: Tesseract OCR (if Gemini fails)
"""

import os


class OCRAgent:
    """Extracts text from medical report images/PDFs using Gemini Vision AI."""

    def __init__(self, gemini_client=None):
        """
        Args:
            gemini_client: GeminiClient instance for Vision OCR
        """
        self.gemini_client = gemini_client

    def extract_text(self, file_path, file_type='image'):
        """
        Extract text from a medical report file.
        Uses Gemini Vision as primary, Tesseract as fallback.
        """
        text = ''

        # Primary: Gemini Vision AI
        if self.gemini_client:
            try:
                if file_type == 'pdf':
                    text = self._extract_pdf_with_gemini(file_path)
                else:
                    text = self.gemini_client.extract_from_image(file_path)

                if text and len(text.strip()) > 20:
                    print(f"  [OCR] Gemini Vision extracted {len(text)} characters")
                    return text
                else:
                    print(f"  [OCR] Gemini Vision returned insufficient text, trying fallback...")
            except Exception as e:
                print(f"  ⚠ Gemini Vision failed: {e}, trying Tesseract fallback...")

        # Fallback: Tesseract OCR
        text = self._tesseract_fallback(file_path, file_type)
        return text

    def _extract_pdf_with_gemini(self, file_path):
        """Extract text from PDF using Gemini. Convert pages to images first."""
        try:
            # Try pdf2image for PDF → image conversion
            from pdf2image import convert_from_path
            images = convert_from_path(file_path, first_page=1, last_page=5, dpi=200)

            all_text = []
            for i, img in enumerate(images):
                temp_path = file_path + f'_page_{i}.png'
                img.save(temp_path, 'PNG')
                page_text = self.gemini_client.extract_from_image(temp_path)
                if page_text:
                    all_text.append(page_text)
                try:
                    os.remove(temp_path)
                except:
                    pass

            return '\n\n'.join(all_text)
        except ImportError:
            print("  [OCR] pdf2image not available, using Tesseract for PDF")
            return self._tesseract_fallback(file_path, 'pdf')
        except Exception as e:
            print(f"  ⚠ PDF extraction error: {e}")
            return self._tesseract_fallback(file_path, 'pdf')

    def _tesseract_fallback(self, file_path, file_type):
        """Tesseract OCR fallback when Gemini is unavailable."""
        text = ''

        if file_type == 'pdf':
            text = self._extract_pdf_tesseract(file_path)
        else:
            text = self._extract_image_tesseract(file_path)

        print(f"  [OCR] Tesseract extracted {len(text)} characters")
        return text

    def _extract_image_tesseract(self, file_path):
        """Extract text from image using Tesseract."""
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
            return text
        except ImportError:
            print("  ⚠ pytesseract not installed")
            return ''
        except Exception as e:
            print(f"  ⚠ Tesseract image error: {e}")
            return ''

    def _extract_pdf_tesseract(self, file_path):
        """Extract text from PDF using Tesseract."""
        try:
            import pytesseract
            from pdf2image import convert_from_path
            images = convert_from_path(file_path, first_page=1, last_page=5, dpi=200)
            all_text = []
            for img in images:
                page_text = pytesseract.image_to_string(img)
                all_text.append(page_text)
            return '\n\n'.join(all_text)
        except ImportError:
            # Try pdfplumber as last resort
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    return '\n\n'.join(page.extract_text() or '' for page in pdf.pages[:5])
            except ImportError:
                print("  ⚠ No PDF extraction library available")
                return ''
        except Exception as e:
            print(f"  ⚠ Tesseract PDF error: {e}")
            return ''
