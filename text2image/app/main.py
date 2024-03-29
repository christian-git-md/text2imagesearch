from fastapi import FastAPI, File, UploadFile, Form

from app.handlers import handle_text_query, handle_image_upload

app = FastAPI()


@app.post("/")
@app.post("/query-text/")
async def query_text(text: str = Form(...)):
    response = handle_text_query(text)
    return response


@app.post("/add-image/")
async def add_image(image_url: str = Form(...)):
    response = handle_image_upload(image_url)
    return response
