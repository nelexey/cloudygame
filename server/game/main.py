import pygame
import asyncio
import websockets
from io import BytesIO
from PIL import Image

# Параметры экрана и квадрата
WIDTH, HEIGHT = 640, 480
SQUARE_SIZE = 50
FPS = 60

# Инициализация Pygame
pygame.init()
screen = pygame.Surface((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Позиция и направление квадрата
x_pos = 0
x_direction = 1  # 1 для вправо, -1 для влево

# Очередь для передачи кадров клиентам
frame_queue = asyncio.Queue(maxsize=1)


async def update_game():
    """Обновляет игровой цикл и добавляет кадры в очередь."""
    global x_pos, x_direction

    while True:
        # Заполнение фона чёрным
        screen.fill((0, 0, 0))

        # Двигаем квадрат
        x_pos += x_direction * 5
        if x_pos + SQUARE_SIZE > WIDTH or x_pos < 0:
            x_direction *= -1  # Меняем направление

        # Отрисовка зелёного квадрата
        pygame.draw.rect(screen, (0, 255, 0), (x_pos, HEIGHT // 2 - SQUARE_SIZE // 2, SQUARE_SIZE, SQUARE_SIZE))

        # Преобразуем поверхность Pygame в данные Pillow
        image_data = pygame.image.tostring(screen, "RGB")
        image = Image.frombytes("RGB", screen.get_size(), image_data)

        # Сохраняем в буфер как PNG
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        # Обновляем кадр в очереди
        if not frame_queue.full():
            await frame_queue.put(buffer.read())

        # Задержка для 60 FPS
        await asyncio.sleep(1 / FPS)


async def handle_client(websocket):
    """Отправляет кадры клиенту по WebSocket."""
    try:
        while True:
            frame = await frame_queue.get()  # Получаем текущий кадр из очереди
            await websocket.send(frame)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")


async def websocket_server():
    """Запускает WebSocket-сервер."""
    async with websockets.serve(handle_client, "localhost", 8765):
        await asyncio.Future()  # Бесконечное ожидание


async def main():
    """Основной цикл приложения."""
    await asyncio.gather(
        update_game(),       # Обновление игрового цикла
        websocket_server()   # Обработка WebSocket-соединений
    )


# Запуск
asyncio.run(main())
