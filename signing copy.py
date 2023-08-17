import fitz
from PIL import Image
import os

# Define constants for folder paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
UNSIGNED = os.path.join(CURRENT_DIR, 'documents', 'unsigned')
SIGNED = os.path.join(CURRENT_DIR, 'documents', 'signed')
SIGNATURES = os.path.join(CURRENT_DIR, 'documents', 'signatures')

class Document:
    def __init__(self, doc_name):
        self.unsigned = os.path.join(UNSIGNED, doc_name)
        self.signed = os.path.join(SIGNED, f"{os.path.splitext(doc_name)[0]}_signed.pdf")

class ImageProcessor:
    def __init__(self, image_path):
        self.image_path = image_path

    def flip_and_shrink(self, shrink_percentage=20):
        with Image.open(self.image_path) as img:
            flipped_img = img.transpose(Image.FLIP_TOP_BOTTOM)
            new_width = int(flipped_img.width * (1 - (shrink_percentage / 100)))
            new_height = int(flipped_img.height * (1 - (shrink_percentage / 100)))
            resized_img = flipped_img.resize((new_width, new_height))
            return resized_img

    def save_processed_image(self, output_path=None):
        flipped_image = self.flip_and_shrink()
        if not output_path:
            output_path = os.path.join(CURRENT_DIR, "temp_flipped_signature.png")
        flipped_image.save(output_path)
        return output_path

class PDFSigner:
    def __init__(self, document):
        self.unsigned_pdf_path = document.unsigned
        self.signed_pdf_path = document.signed

    def add_signature(self, image_path, coordinates_list):
        doc = fitz.open(self.unsigned_pdf_path)
        signature = fitz.open(image_path)
        img_width, img_height = signature[0].rect.width, signature[0].rect.height
        aspect_ratio = img_width / img_height

        desired_width = 200
        desired_height = desired_width / aspect_ratio

        for page_num, coordinates in enumerate(coordinates_list):
            x, y = coordinates
            rect = fitz.Rect(x, y, x + desired_width, y + desired_height)
            if page_num < len(doc):  # Ensure we're not trying to add a signature beyond the number of pages in the doc
                doc[page_num].insert_image(rect, filename=image_path)

        try:
            doc.save(self.signed_pdf_path)
            doc.close()
            print(f"Successfully signed {self.signed_pdf_path}")
        except Exception as e:
            print(f"Error signing {self.signed_pdf_path}: {e}")
        file_name = os.path.basename(self.signed_pdf_path)
        return file_name

if __name__ == '__main__':
    doc = Document('invoice.pdf')
    img_processor = ImageProcessor(os.path.join(SIGNATURES, 'extracted_signature.png'))
    processed_signature = img_processor.save_processed_image()
    signer = PDFSigner(doc)
    signer.add_signature(processed_signature, [(330, 90), (330, 180)])
