import pygame as pg
#import numpy as np
import sys

# Инициализация PyGame
pg.init()

# Константы
C_w = pg.display.get_desktop_sizes()[0][0] - 100
C_w_half = C_w // 2
C_h = pg.display.get_desktop_sizes()[0][1] - 100
C_h_half = C_h // 2
FPS = 30

# Окно игры
screen = pg.display.set_mode((C_w, C_h))
screen.fill((255, 255, 255))

# Список для прямого доступа к пикселям окна
pixel_array = pg.PixelArray(screen)

# Ограничение количества кадров в секунду
clock = pg.time.Clock()

# Название приложения
pg.display.set_caption("Ray Tracer")

# Иконка приложения
pg.display.set_icon(pg.image.load("icon.jpg"))

# Функция, которая по координатам пикселя задает ему цвет
def paintPixel(x_coord: int, y_coord: int, pixel_color: tuple):
    pixel_array[C_w_half + x_coord, C_h_half + y_coord] = pixel_color

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()

    for x in range(-C_w_half, C_w_half):
        for y in range(-C_h_half, C_h_half):
            color = (0, 255, 0)
            paintPixel(x, y, color)

    clock.tick(60)
    pg.display.flip()
