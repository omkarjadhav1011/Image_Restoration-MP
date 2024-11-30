from fastapi import FastAPI, UploadFile, Request
import uvicorn
import numpy as np
import os
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from script import colorize_image
from helper import get_file_extension, does_file_exist, get_file_with_extension

app = FastAPI()

# Setup static files and templates
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def main(request: Request):
    """
    Render the main upload page
    """
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/upload_image")
async def upload_image(file: UploadFile, request: Request):
    """
    Handle image upload and colorization for web interface
    
    Args:
        file (UploadFile): Uploaded image file
        request (Request): FastAPI request object
    
    Returns:
        TemplateResponse: Rendered result page with colorized image
    """
    # Validate file upload
    if not file.filename:
        error = "Please choose a file"
        return templates.TemplateResponse(
            "upload.html", {"request": request, "error": error}
        )
    
    # Get file extension
    extension = get_file_extension(file.filename)

    # Remove previous processed image if exists
    if does_file_exist("static/", "processed_image"):
        os.remove("static/" + get_file_with_extension("static", "processed_image"))

    # Read file data
    data = await file.read()
    nparr = np.frombuffer(data, np.uint8)
    
    # Colorize image
    colorize_image(nparr, extension)

    # Set processed image path
    processed_image_path = "static/" + "processed_image." + extension

    # Move file to static folder
    os.rename("processed_image." + extension, processed_image_path)

    # Return result template with download link
    return templates.TemplateResponse(
        "result.html", {"request": request, "download_link": processed_image_path}
    )

@app.get("/download")
async def download_image(request: Request):
    """
    Provide download functionality for processed image
    
    Returns:
        FileResponse: Downloadable processed image
    """
    # Find the processed image
    processed_image = get_file_with_extension("static", "processed_image")
    
    if processed_image:
        download_link = os.path.join(static_path, processed_image)
        return FileResponse(download_link, filename="colorized_image.png")
    
    # If no image found, return to upload page
    return templates.TemplateResponse("upload.html", {"request": request, "error": "No image available"})

if __name__ == "__main__":
    # Run the application
    uvicorn.run(app, host="127.0.0.1", port=8080)