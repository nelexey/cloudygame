import pygame
import asyncio
import websockets
from io import BytesIO

# Параметры экрана
WIDTH, HEIGHT = 640, 480


async def receive_frames(uri):
    # Инициализация Pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True

    async with websockets.connect(uri) as websocket:
        while running:
            try:
                # Получаем кадр от сервера
                frame_data = await websocket.recv()

                # Загрузка изображения из полученных данных
                frame = pygame.image.load(BytesIO(frame_data))

                # Отображение кадра на экране
                screen.blit(frame, (0, 0))
                pygame.display.flip()

                # Обработка событий Pygame
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                # Поддержание частоты обновления ~60 FPS
                clock.tick(60)
            except websockets.ConnectionClosed:
                print("Connection closed by server.")
                running = False
            except Exception as e:
                print(f"Error: {e}")
                running = False

    pygame.quit()


# Запуск клиента
asyncio.run(receive_frames("ws://localhost:8765"))
