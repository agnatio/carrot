from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os

from signing import Document, ImageProcessor, PDFSigner, SIGNATURES, SIGNED

app = FastAPI()
dir_path = os.path.dirname(os.path.realpath(__file__))
templates = Jinja2Templates(directory=os.path.join(dir_path, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(dir_path, "static")), name="static")
app.mount("/documents", StaticFiles(directory=os.path.join(dir_path, "documents")), name="documents")
app.mount("/documents/unsigned", StaticFiles(directory=os.path.join(dir_path, "documents", "unsigned")), name="unsigned")
app.mount("/documents/signed", StaticFiles(directory=os.path.join(dir_path, "documents", "signed")), name="signed")



@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/signatures")
async def signatures(request: Request):
    signatures = [s for s in os.listdir(os.path.join(dir_path, "documents", "signatures")) if s.endswith('.png')]
    return templates.TemplateResponse("signatures.html", {"request": request, "signatures": signatures})

@app.get("/documents")
async def list_documents(request: Request):
    # Scan the documents directory for PDF files
    pdf_files = [f for f in os.listdir(os.path.join(dir_path, "documents", "unsigned")) if f.endswith('.pdf')]

    # Return the list of PDF files to the template
    return templates.TemplateResponse("documents.html", {"request": request, "pdf_files": pdf_files})

# @app.get("/documents/unsigned/{filename}")
# async def get_document(filename: str):
#     print(filename)
#     print("debug")
#     return FileResponse(os.path.join(dir_path, "documents", "unsigned", filename))

@app.get("/scan/{filename}")
async def get_document(request: Request, filename: str):
    print(filename)
    signatures = [s for s in os.listdir(os.path.join(dir_path, "documents", "signatures")) if s.endswith('.png')]
    return templates.TemplateResponse("scan.html", {"request": request, "filename": filename, "signatures": signatures})


@app.get("/sign_document/")
async def sign_document(request: Request, filename: str = None, signature: str = None):
    print(filename)
    print(signature)
    file_to_sign = Document(filename)
    document_to_sign = PDFSigner(file_to_sign)
    signature = os.path.join(SIGNATURES, signature)
    signature_processor = ImageProcessor(signature)
    processed_signature = signature_processor.save_processed_image()
    res = document_to_sign.add_signature(os.path.join(SIGNATURES, signature), [(330, 90), (330, 180)])
    return templates.TemplateResponse("sign.html", {"request": request, "filename": filename, "signature": processed_signature, "res": res})

# @app.get("/signed/{path:path}")
# async def signed(path: str):
#     return FileResponse(os.path.join(SIGNED, path))


@app.get("/sign")
async def signatures(request: Request):
    return "Working on that..."
                

if __name__ == '__main__':

    uvicorn.run(app, host="localhost", port=8080)


