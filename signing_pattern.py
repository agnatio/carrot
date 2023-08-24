from abc import ABC, abstractmethod

import fitz
from PIL import Image
import os
from datetime import datetime
import io

# Define constants for folder paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
UNSIGNED = os.path.join(CURRENT_DIR, 'documents', 'unsigned')
SIGNED = os.path.join(CURRENT_DIR, 'documents', 'signed')
SIGNATURES = os.path.join(CURRENT_DIR, 'documents', 'signatures')

# --- Strategy Pattern for Image Transformations ---

class TransformStrategy(ABC):
    @abstractmethod
    def execute(self, image: Image) -> Image:
        pass

class FlipStrategy(TransformStrategy):
    def __init__(self, mode=Image.FLIP_TOP_BOTTOM):
        self.mode = mode

    def execute(self, image: Image) -> Image:
        return image.transpose(self.mode)

class ShrinkStrategy(TransformStrategy):
    def __init__(self, percentage=20):
        self.percentage = percentage

    def execute(self, image: Image) -> Image:
        new_width = int(image.width * (1 - (self.percentage / 100)))
        new_height = int(image.height * (1 - (self.percentage / 100)))
        return image.resize((new_width, new_height))

# --- Image Processor ---

class ImageProcessor:
    def __init__(self, image_path):
        self.image = Image.open(image_path)

    def apply(self, strategy: TransformStrategy):
        self.image = strategy.execute(self.image)
        return self

    def save(self, output_path=None) -> str:
        if not output_path:
            output_directory = os.path.join(CURRENT_DIR, "documents", "update_signature")
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(output_directory, f"processed_signature_{current_time}.png")
        self.image.save(output_path)
        return output_path

class PDFSigner:
    def __init__(self, pdf_path, signature_path):
        self.pdf_path = pdf_path
        self.signature_path = signature_path
        self.doc = fitz.open(self.pdf_path)

    def place_signature(self, page_num, rect_coords, output_path=None):
        """
        Places the signature onto the specified page and rectangle of the PDF.

        :param page_num: Page number (0-indexed) on which to place the signature.
        :param rect_coords: (x0, y0, x1, y1) coordinates defining the rectangle where the signature will be placed.
        :param output_path: Path to save the signed PDF. If None, it will save with '_signed' appended to original name.
        """
        page = self.doc[page_num]
        rect = fitz.Rect(*rect_coords)

        # Scale signature to fit the rect
        signature_img = Image.open(self.signature_path)
        signature_img = signature_img.resize((int(rect.width), int(rect.height)))

        # Convert signature back to PNG byte data for insertion into PDF
        img_stream = io.BytesIO()
        signature_img.save(img_stream, format="PNG")
        img_data = img_stream.getvalue()

        # Insert the signature into the PDF
        page.insert_image(rect, stream=img_data, overlay=True)

        # Save the signed PDF
        if not output_path:
            base_name = os.path.basename(self.pdf_path).split('.')[0]
            dir_name = os.path.dirname(self.pdf_path)
            output_path = os.path.join(dir_name, f"{base_name}_signed.pdf")
        
        self.doc.save(output_path)
        return output_path


# Test the strategies and image processor
test_image_path = os.path.join(SIGNATURES, 'extracted_signature.png')
processor = ImageProcessor(test_image_path)
processor.apply(FlipStrategy()).apply(ShrinkStrategy(30)).save()
