from typing import Any, Tuple, Union, List
from transformers import CLIPProcessor, CLIPModel
import requests
from PIL import Image

from app.typing import InferType
from fastapi.responses import JSONResponse
from asyncio import Queue


def download_image(url: str) -> Image:
    return Image.open(requests.get(url, stream=True).raw)


def run_infer_text(
    processor: CLIPProcessor, model: CLIPModel, text: str, mock_image: Image
) -> List[float]:
    inputs = processor(
        text=[text], images=mock_image, return_tensors="pt", padding=True
    )
    out = model(**inputs).text_embeds[0].tolist()
    return out


def run_infer_image(
    processor: CLIPProcessor, model: CLIPModel, download_url: str
) -> List[float]:
    image = download_image(download_url)
    inputs = processor(text=[""], images=image, return_tensors="pt", padding=True)
    out = model(**inputs).image_embeds[0].tolist()
    return out


def create_error_response(message: str) -> JSONResponse:
    error_response = {
        "error": True,
        "message": message,
    }
    return JSONResponse(status_code=500, content=error_response)


async def clip_server_loop(in_queue: Queue) -> None:
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    mock_image = Image.new("RGB", (256, 256), (0, 0, 0))
    while True:
        string, response_queue, infer_type = await in_queue.get()
        try:
            if infer_type == InferType.TEXT:
                out = run_infer_text(processor, model, string, mock_image)
            elif infer_type == InferType.IMAGE:
                out = run_infer_image(processor, model, string)
            else:
                raise TypeError(f"Invalid infer type {infer_type}")
        except Exception as e:
            out = create_error_response(str(e)).body.decode(
                "utf-8"
            )  # Adjusted to directly use the error response
        await response_queue.put(JSONResponse(content=out))
