import asyncio
import websockets
from io import BytesIO
import pygame
from PIL import Image

frame_queue = asyncio.Queue(maxsize=1)

async def stream_frame(screen):
    image_data = pygame.image.tostring(screen, "RGB")
    image = Image.frombytes("RGB", screen.get_size(), image_data)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    if not frame_queue.full():
        await frame_queue.put(buffer.read())

async def send_frame(websocket):
    while True:
        frame_data = await frame_queue.get()

        await websocket.send(frame_data)


async def serve_stream():
     return await websockets.serve(send_frame, "localhost", 8765)  # WebSocket-сервер

