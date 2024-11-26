import pygame
import asyncio

from streaming import stream_frame, serve_stream, event_queue  # Импортируем event_queue из streaming.py

WIDTH, HEIGHT = 800, 600
FPS = 60


async def game_loop():
    pygame.init()
    screen = pygame.Surface((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))

        # Проверка на события кликов от клиента
        while not event_queue.empty():
            click_event = await event_queue.get()
            x, y = click_event.get('x'), click_event.get('y')
            print(f"Got click: ({x}, {y})")

        await stream_frame(screen)
        await asyncio.sleep(1 / FPS)

    pygame.quit()


async def main():
    game_task = asyncio.create_task(game_loop())
    server_task = await serve_stream()
    await asyncio.gather(game_task, server_task.wait_closed())


if __name__ == "__main__":
    asyncio.run(main())
