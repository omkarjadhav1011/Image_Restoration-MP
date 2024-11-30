from fastapi import FastAPI, UploadFile, Request
import uvicorn
from script import *
from fastapi.responses import HTMLResponse, FileResponse
import os
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from helper import get_file_extension, does_file_exist, get_file_with_extension

app = FastAPI()

static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
def main(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/upload")  # This is the endpoint for the API for the CLI
async def upload_image(file: UploadFile, request: Request):
    # if the processed_image was saved from earlier run, delete it.
    if does_file_exist("static/", "processed_image"):
        os.remove("static/" + get_file_with_extension("static", "processed_image"))

    print(file.filename)
    extension = get_file_extension(file.filename)
    data = await file.read()
    nparr = np.frombuffer(data, np.uint8)
    colorize_image(nparr, extension)

    # move file to static folder
    os.rename("processed_image."+extension, "static/processed_image." + extension)

    download_link = os.path.join(
        os.path.dirname(__file__), "static/processed_image." + extension
    )
    return FileResponse(download_link, filename="color.png")


@app.post("/upload_image")  # This is the endpoint for the API for the webapp
async def upload_image(file: UploadFile, request: Request):
    if not file.filename:
        error = "please choose a file"
        return templates.TemplateResponse(
            "upload.html", {"request": request, "error": error}
        )
    extension = get_file_extension(file.filename)

    # if the processed_image was saved from earlier run, delete it.
    if does_file_exist("static/", "processed_image"):
        os.remove("static/" + get_file_with_extension("static", "processed_image"))

    data = await file.read()
    nparr = np.frombuffer(data, np.uint8)
    colorize_image(nparr, extension)

    processed_image_path = "static/" + "processed_image." + extension

    # move file to static folder
    os.rename("processed_image." + extension, processed_image_path)

    download_link = processed_image_path

    return templates.TemplateResponse(
        "result.html", {"request": request, "download_link": download_link}
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)