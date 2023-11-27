import pygame as pg
import numpy as np
import sys

# Инициализация PyGame
pg.init()

# Константы
WIDTH = pg.display.get_desktop_sizes()[0][0] - 100
HEIGHT = pg.display.get_desktop_sizes()[0][1] - 100
FPS = 30

# Окно игры
screen = pg.display.set_mode((WIDTH, HEIGHT))
screen.fill((255, 255, 255))

# Название приложения
pg.display.set_caption("Ray Tracer")

# Иконка приложения
pg.display.set_icon(pg.image.load("icon.jpg"))

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()

    pg.display.flip()
