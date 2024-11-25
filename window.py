import pygame
import asyncio
import websockets
from io import BytesIO


FPS = 60

async def receive_frames(uri):
    pygame.init()
    screen = None  # Экран будет инициализирован при получении первого кадра
    clock = pygame.time.Clock()
    running = True

    async with websockets.connect(uri) as websocket:
        while running:
            try:
                frame_data = await websocket.recv()
                frame = pygame.image.load(BytesIO(frame_data))

                if screen is None:
                    frame_width, frame_height = frame.get_size()
                    screen = pygame.display.set_mode((frame_width, frame_height))

                screen.blit(frame, (0, 0))
                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                clock.tick(FPS)
            except websockets.ConnectionClosed:
                print("Соединение закрыто сервером.")
                running = False
            except Exception as e:
                print(f"Ошибка: {e}")
                running = False

    pygame.quit()

asyncio.run(receive_frames("ws://localhost:8765"))
