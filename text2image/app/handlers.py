import json
from typing import List
from urllib.parse import urljoin, urlunparse

import requests

from app.qdrant_client_ops import qdrant_query, qdrant_upload

from appconfig import DEFAULT_COLLECTION_NAME, CLIP_SERVER_LOCATION, CLIP_SERVER_PORT
from qdrant_client.conversions import common_types as types


def make_model_serving_url() -> str:
    netloc = f"{CLIP_SERVER_LOCATION}:{CLIP_SERVER_PORT}"
    scheme = "http"
    url = urlunparse((scheme, netloc, "", "", "", ""))
    return url


def query_clip_model_text(text: str) -> List[float]:
    url = urljoin(make_model_serving_url(), "query_text")
    response = requests.post(url, data=text)
    if response.status_code == 200:
        vector = json.loads(response.text)
        return vector
    else:
        raise ConnectionError("Could not connect to ML model to create query vector.")


def query_clip_model_image(text: str) -> List[float]:
    url = urljoin(make_model_serving_url(), "query_image")
    response = requests.post(url, data=text)
    if response.status_code == 200:
        vector = json.loads(response.text)
        return vector
    else:
        raise ConnectionError("Could not connect to ML model to create image vector.")


def handle_text_query(text: str) -> List[types.ScoredPoint]:
    vector = query_clip_model_text(text)
    return qdrant_query(vector=vector, collection_name=DEFAULT_COLLECTION_NAME)


def handle_image_upload(image_url: str) -> types.UpdateResult:
    vector = query_clip_model_image(image_url)
    return qdrant_upload(
        vector=vector, image_url=image_url, collection_name=DEFAULT_COLLECTION_NAME
    )
