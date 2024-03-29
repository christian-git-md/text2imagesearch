from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import asyncio

from app.clip import clip_server_loop

from app.typing import InferType

app = FastAPI()


@app.on_event("startup")
async def load_model():
    q = asyncio.Queue()
    app.state.model_queue = q
    asyncio.create_task(clip_server_loop(q))


@app.post("/")
@app.post("/query_text")
async def homepage(request: Request):
    payload = await request.body()
    string = payload.decode("utf-8")
    response_q = asyncio.Queue()
    await request.app.state.model_queue.put((string, response_q, InferType.TEXT))
    return await response_q.get()


@app.post("/query_image")
async def homepage(request: Request):
    payload = await request.body()
    string = payload.decode("utf-8")
    response_q = asyncio.Queue()
    await request.app.state.model_queue.put((string, response_q, InferType.IMAGE))
    return await response_q.get()
