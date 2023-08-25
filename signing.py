from abc import ABC, abstractmethod

import fitz
from PIL import Image
import os
from datetime import datetime
import io

# Define constants for folder paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
UNSIGNED = os.path.join(CURRENT_DIR, "documents", "unsigned")
SIGNED = os.path.join(CURRENT_DIR, "documents", "signed")
SIGNATURES = os.path.join(CURRENT_DIR, "documents", "signatures")


class DocumentToSign:
    def __init__(self, filename: str):
        self.pdf_path = os.path.join(UNSIGNED, filename)
        self.doc = fitz.open(self.pdf_path)
        # calculate the number of pages in the document
        self.num_pages = self.doc.page_count


class ImageProcessor:
    def __init__(self, image_name="extracted_signature.png"):
        self.image_path = os.path.join(SIGNATURES, image_name)
        self.image = Image.open(self.image_path)

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
    def __init__(
        self, document_to_sign, signature_processor, signature_positions: dict
    ):
        self.doc = document_to_sign.doc
        self.signature = signature_processor.get_image()
        self.signature_positions = signature_positions
        self._embed_signatures()

    def _embed_signatures(self):
        # Convert the PIL Image to bytes in PNG format
        img_stream = io.BytesIO()
        self.signature.save(img_stream, format="PNG")
        img_data = img_stream.getvalue()

        # Calculate the aspect ratio of the signature image
        img_width, img_height = self.signature.size
        aspect_ratio = img_width / img_height

        for page_num, positions in self.signature_positions.items():
            for pos in positions:
                x, y = pos
                rect = fitz.Rect(x, y, x + img_width, y + img_height)
                if page_num < len(
                    self.doc
                ):  # Ensure we're not trying to add a signature beyond the number of pages in the doc
                    self.doc[page_num].insert_image(rect, stream=img_data)

    def save(self, output_path=None):
        if not output_path:
            base_name = os.path.basename(self.doc.name).split(".")[0]
            output_path = os.path.join(SIGNED, f"{base_name}_signed.pdf")
        self.doc.save(output_path)
        print(f"Signed document saved at: {output_path}")
        return output_path


signature_positions = {
    0: [
        (330, 90),
    ],  # First page
    1: [(330, 130)],  # Second page
    # 2: [(400, 300)]              # Third page
}
document_to_sign = DocumentToSign("Invoice.pdf")
document_to_sign = DocumentToSign("INVOICE_NAME2.pdf")
print(document_to_sign.num_pages)
signature = ImageProcessor()
signed_document = SignedDocument(
    document_to_sign, signature.resize(0.5), signature_positions
)
output_path = signed_document.save()
# make output path relative to current directory
relative_path = os.path.relpath(output_path, CURRENT_DIR)

print(relative_path)


# print(f"Signed document saved at: {output_path}")


# document_to_sign = DocumentToSign('documents\\unsigned\\Invoice.pdf')
# signature = ImageProcessor()
# signed_document = SignedDocument(document_to_sign, signature.flip(Image.FLIP_TOP_BOTTOM).resize(0.25), [(150, 100), (300, 200)])
# output_path = signed_document.save()
# print(f"Signed document saved at: {output_path}")
