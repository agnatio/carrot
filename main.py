from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

import signing

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuration Dictionary for Mount Paths and Directories
MOUNT_CONFIG = {
    "/static": "static",
    "/documents": "documents",
    "/documents/unsigned": "documents/unsigned",
    "/documents/signed": "documents/signed",
    "/documents/update_signature": "documents/update_signature",
}
# Get the directory path of the current file
dir_path = os.path.dirname(os.path.realpath(__file__))

# Centralized directory path logic
get_full_path = lambda subdir: os.path.join(dir_path, subdir)
print(get_full_path("templates"))

# Initialize FastAPI app and templates
app = FastAPI()
templates = Jinja2Templates(directory=get_full_path("templates"))

# Iterate over MOUNT_CONFIG to mount each path
for mount_path, directory in MOUNT_CONFIG.items():
    app.mount(
        mount_path, StaticFiles(directory=get_full_path(directory)), name=directory
    )
    print(f"Mounted {mount_path} to {directory}")


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/signatures")
async def signatures(request: Request):
    signatures = [
        s
        for s in os.listdir(os.path.join(dir_path, "documents", "signatures"))
        if s.endswith(".png")
    ]
    print(f"{signatures}")
    return templates.TemplateResponse(
        "signatures.html", {"request": request, "signatures": signatures}
    )


@app.get("/update_signature/{signature}")
async def edit_signature(request: Request, signature: str):
    return templates.TemplateResponse(
        "signature_edit.html", {"request": request, "signature": signature}
    )


@app.post("/update_signature/{signature}")
async def update_signature(
    request: Request, signature: str, param1: str = Form(...), param2: str = Form(...)
):
    # Handle form data and update the signature
    # For now, just redirect back to the edit page
    return RedirectResponse(url=f"/update_signature/{signature}")


@app.get("/documents")
async def list_documents(request: Request):
    # Scan the documents directory for PDF files
    pdf_files = [
        f
        for f in os.listdir(os.path.join(dir_path, "documents", "unsigned"))
        if f.endswith(".pdf")
    ]

    # Return the list of PDF files to the template
    return templates.TemplateResponse(
        "documents.html", {"request": request, "pdf_files": pdf_files}
    )


@app.get("/scan/{filename}")
async def get_document(request: Request, filename: str):
    print(filename)
    doc_to_sign = signing.DocumentToSign(filename)
    print(doc_to_sign.num_pages)
    signatures = [
        s
        for s in os.listdir(os.path.join(dir_path, "documents", "signatures"))
        if s.endswith(".png")
    ]
    return templates.TemplateResponse(
        "scan.html",
        {
            "request": request,
            "filename": filename,
            "signatures": signatures,
            "num_pages": doc_to_sign.num_pages,
        },
    )


@app.get("/sign_document/")
async def sign_document(request: Request, filename: str = None, signature: str = None):
    print(filename)
    doc_to_sign = signing.DocumentToSign(filename)
    print(signature)
    signature = signing.ImageProcessor(signature)

    print(f"{type(doc_to_sign)} AND {type(signature)}")

    signature_positions = {
        0: [
            (330, 90),
        ],  # First page
        1: [(330, 130)],  # Second page
        # 2: [(400, 300)]              # Third page
    }

    signed_document = signing.SignedDocument(
        doc_to_sign, signature.flip().resize(0.5), signature_positions
    )
    output_path = signed_document.save()
    # relative_path = os.path.relpath(output_path, CURRENT_DIR)
    relative_path = os.path.basename(output_path)

    return templates.TemplateResponse(
        "sign.html", {"request": request, "res": relative_path}
    )


@app.get("/sign")
async def sign_docuemnt(request: Request):
    return "Working on that..."


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
