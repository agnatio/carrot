
# FastAPI Document Signing Application

This application provides endpoints for managing and signing documents using the FastAPI framework.

## Features

1. **Static File Serving**: Serves static files like templates, documents, and signatures.
2. **Document Management**: Lists and displays documents available for signing.
3. **Signature Management**: Lists available signatures and provides an interface for updating them.
4. **Document Signing**: Allows users to sign a document using a selected signature.

## Setup

### Prerequisites

- Python 3.6+
- FastAPI
- Uvicorn
- Any additional dependencies can be installed using `pip install -r requirements.txt` (You'll need to create this file)

### Running the Application

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-dir>
   ```

2. Install the required packages:
   ```
   pip install fastapi[all] uvicorn
   ```

3. Run the application:
   ```
   uvicorn main:app --reload
   ```

   This will start the FastAPI server on `localhost` at port `8000`.

## Endpoints

- **GET `/`**: Home page displaying the main interface.
- **GET `/signatures`**: Lists available signatures for signing.
- **GET & POST `/update_signature/{signature}`**: Displays and updates the selected signature.
- **GET `/documents`**: Lists available documents for signing.
- **GET `/scan/{filename}`**: Scans a specific document and prepares it for signing.
- **GET `/sign_document/`**: Signs a selected document using a given signature.
- **GET `/sign`**: Placeholder endpoint for future development.

## Directory Structure

- **/static**: Contains static assets like CSS, JS, and images.
- **/documents**: Contains all document-related files.
  - **/unsigned**: Contains documents that are yet to be signed.
  - **/signed**: Contains signed documents.
  - **/update_signature**: Contains signatures that need updates.
- **/templates**: Contains Jinja2 templates for rendering HTML pages.

## Future Improvements

- Add authentication and authorization to protect endpoints.
- Integrate with a database for better management of documents and signatures.
- Enhance the user interface for a smoother user experience.
