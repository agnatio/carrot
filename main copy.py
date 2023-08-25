from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

import signing_pattern2

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()
dir_path = os.path.dirname(os.path.realpath(__file__))
templates = Jinja2Templates(directory=os.path.join(dir_path, "templates"))
app.mount(
    "/static", StaticFiles(directory=os.path.join(dir_path, "static")), name="static"
)
app.mount(
    "/documents",
    StaticFiles(directory=os.path.join(dir_path, "documents")),
    name="documents",
)
app.mount(
    "/documents/unsigned",
    StaticFiles(directory=os.path.join(dir_path, "documents", "unsigned")),
    name="unsigned",
)
app.mount(
    "/documents/signed",
    StaticFiles(directory=os.path.join(dir_path, "documents", "signed")),
    name="signed",
)
app.mount(
    "/documents/update_signature",
    StaticFiles(directory=os.path.join(dir_path, "documents", "update_signature")),
    name="update_signature",
)


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
    doc_to_sign = signing_pattern2.DocumentToSign(filename)
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
    doc_to_sign = signing_pattern2.DocumentToSign(filename)
    print(signature)
    signature = signing_pattern2.ImageProcessor(signature)

    print(f"{type(doc_to_sign)} AND {type(signature)}")

    signature_positions = {
        0: [
            (330, 90),
        ],  # First page
        1: [(330, 130)],  # Second page
        # 2: [(400, 300)]              # Third page
    }

    signed_document = signing_pattern2.SignedDocument(
        doc_to_sign, signature.flip().resize(0.5), signature_positions
    )
    output_path = signed_document.save()
    # relative_path = os.path.relpath(output_path, CURRENT_DIR)
    relative_path = os.path.basename(output_path)

    return templates.TemplateResponse(
        "sign.html", {"request": request, "res": relative_path}
    )
    # file_to_sign = Document(filename)
    # document_to_sign = PDFSigner(file_to_sign)
    # signature = os.path.join(SIGNATURES, signature)
    # signature_processor = ImageProcessor(signature)
    # processed_signature = signature_processor.save_processed_image()
    # res = document_to_sign.add_signature(os.path.join(SIGNATURES, signature), [(330, 90), (330, 180)])
    # return templates.TemplateResponse("sign.html", {"request": request, "filename": filename, "signature": processed_signature, "res": res})


# @app.get("/signed/{path:path}")
# async def signed(path: str):
#     return FileResponse(os.path.join(SIGNED, path))


@app.get("/sign")
async def signatures(request: Request):
    return "Working on that..."


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
