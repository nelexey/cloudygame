import pygame
import asyncio
from io import BytesIO
from PIL import Image
import websockets

WIDTH, HEIGHT = 640, 480
SQUARE_SIZE = 50
FPS = 120

pygame.init()
screen = pygame.Surface((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Позиция и направление квадрата
x_pos = 0
x_direction = 1  # 1 для вправо, -1 для влево


frame_queue = asyncio.Queue(maxsize=1) # Стек для одного кадра


async def update_game():
    """Обновляет игровой цикл и добавляет кадры в очередь."""
    global x_pos, x_direction

    while True:
        screen.fill((0, 0, 0))

        x_pos += x_direction * 5
        if x_pos + SQUARE_SIZE > WIDTH or x_pos < 0:
            x_direction *= -1

        pygame.draw.rect(screen, (0, 255, 0), (x_pos, HEIGHT // 2 - SQUARE_SIZE // 2, SQUARE_SIZE, SQUARE_SIZE))

        # Преобразование кадра игры в объект Pillow для сохранения в формате картинки
        image_data = pygame.image.tostring(screen, "RGB")
        image = Image.frombytes("RGB", screen.get_size(), image_data)

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        if not frame_queue.full():
            await frame_queue.put(buffer.read())

        await asyncio.sleep(1 / FPS)


async def send_frames(websocket):
    """Обрабатывает WebSocket-соединение и отправляет кадры из очереди."""
    while True:
        frame_data = await frame_queue.get()

        await websocket.send(frame_data)


async def main():
    """Основной цикл приложения."""
    game_task = asyncio.create_task(update_game())  # Обновление игрового цикла
    server = await websockets.serve(send_frames, "localhost", 8080)  # WebSocket-сервер

    await asyncio.gather(game_task, server.wait_closed())


# Запуск сервера
asyncio.run(main())
