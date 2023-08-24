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

import fitz
from PIL import Image
import os

# Constants
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SIGNED = os.path.join(CURRENT_DIR, 'documents', 'signed')

class DocumentToSign:
    def __init__(self, pdf_path=os.path.join(CURRENT_DIR, 'documents', 'unsigned', 'sample.pdf')):
        self.pdf_path = pdf_path
        self.doc = fitz.open(self.pdf_path)

class ImageProcessor:
    def __init__(self, image_path=os.path.join(CURRENT_DIR, 'documents', 'signatures', 'extracted_signature.png')):
        self.image = Image.open(image_path)

    def flip(self, mode=Image.FLIP_TOP_BOTTOM):
        self.image = self.image.transpose(mode)
        return self

    def resize(self, coefficient=1):
        new_width = int(self.image.width * coefficient)
        new_height = int(self.image.height * coefficient)
        self.image = self.image.resize((new_width, new_height))
        return self

    def get_image(self):
        return self.image


class SignedDocument:
    def __init__(self, document_to_sign, signature_processor, signature_positions: dict):
        self.doc = document_to_sign.doc
        self.signature = signature_processor.get_image()
        self.signature_positions = signature_positions
        self._embed_signatures()

    def _embed_signatures(self):
        for page_num, positions in self.signature_positions.items():
            page = self.doc[page_num]
            for pos in positions:
                rect = fitz.Rect(pos[0], pos[1], pos[0] + self.signature.width, pos[1] + self.signature.height)
                img_stream = io.BytesIO()
                self.signature.save(img_stream, format="PNG")
                img_data = img_stream.getvalue()
                page.insert_image(rect, stream=img_data, overlay=True)

    def save(self, output_path=None):
        if not output_path:
            base_name = os.path.basename(self.doc.name).split('.')[0]
            output_path = os.path.join(SIGNED, f"{base_name}_signed.pdf")
        self.doc.save(output_path)
        return output_path


signature_positions = {
    0: [(330, 90), ],  # First page
    1: [(330, 130)],             # Second page
    # 2: [(400, 300)]              # Third page
}
document_to_sign = DocumentToSign('documents\\unsigned\\Invoice.pdf')
signature = ImageProcessor()
signed_document = SignedDocument(document_to_sign, signature.flip(Image.FLIP_TOP_BOTTOM).resize(0.24), signature_positions)
output_path = signed_document.save()
print(f"Signed document saved at: {output_path}")


# document_to_sign = DocumentToSign('documents\\unsigned\\Invoice.pdf')
# signature = ImageProcessor()
# signed_document = SignedDocument(document_to_sign, signature.flip(Image.FLIP_TOP_BOTTOM).resize(0.25), [(150, 100), (300, 200)])
# output_path = signed_document.save()
# print(f"Signed document saved at: {output_path}")