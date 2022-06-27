from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, Path, Body, Query, File
from fastapi.responses import FileResponse
from PIL import Image, ImageFilter
import ssl
import os
from starlette.background import BackgroundTasks
import urllib.request, urllib.parse

app = FastAPI()
ssl._create_default_https_context = ssl._create_unverified_context

# List of URLs which have access to this API
origins = [
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return{"Test": "test"}

# Post request for retrieving a blurred version of an image
# The image is fetched from the URL in the post body and a blur is applied to it, the result is returned
@app.post("/get-blur")
async def get_effect(request: Request, background_tasks: BackgroundTasks):
    image = await request.json()
    id = image['id']
    cldId = image['cldId']

    img_path = 'app/bib/' + id + ".jpg"
    image_url = "https://cmp.photoprintit.com/api/photos/" + id + ".org?size=original&errorImage=false&cldId=" + cldId + "&clientVersion=0.0.0-apidoc"
    
    urllib.request.urlretrieve(image_url, img_path)
    blurImage = Image.open(img_path)
    blurImage = blurImage.filter(ImageFilter.BoxBlur(10))
    blurImage.save(img_path)

    background_tasks.add_task(remove_file, img_path)
    return FileResponse(img_path)

# Delete a file
def remove_file(path: str) -> None:
    os.unlink(path)