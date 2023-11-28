from dataclasses import dataclass
import pygame as pg
import numpy as np
import sys

# Инициализация PyGame
pg.init()

# Константы
C_w = pg.display.get_desktop_sizes()[0][0] - 100
C_w_half = C_w // 2
C_h = pg.display.get_desktop_sizes()[0][1] - 100
C_h_half = C_h // 2
C_w_to_C_h = C_w / C_h
FPS = 30
BACKGROUND_COLOR = (255, 255, 255)

# Окно игры
screen = pg.display.set_mode((C_w, C_h))
screen.fill(BACKGROUND_COLOR)

# Список для прямого доступа к пикселям окна
pixel_array = pg.PixelArray(screen)

# Ограничение количества кадров в секунду
clock = pg.time.Clock()

# Название приложения
pg.display.set_caption("Ray Tracer")

# Иконка приложения
pg.display.set_icon(pg.image.load("icon.jpg"))


# Функция, которая по координатам пикселя задает ему цвет
def paintPixel(x_coord: int, y_coord: int, pixel_color):
    pixel_array[C_w_half + x_coord, C_h_half - y_coord] = pixel_color


# Камера - точка начала лучей
camera = np.array([0, 0, 0])


# Класс сферы, задается центром и радиусом
@dataclass
class Sphere:
    center: np.array
    radius: float
    color: tuple


# Сцена с объектами
scene = [
    Sphere(np.array([0, -1, 3]), 1, (255, 0, 0)),
    Sphere(np.array([2, 0, 4]), 1, (0, 0, 255)),
    Sphere(np.array([-2, 0, 4]), 1, (0, 255, 0))
]


# Поиск пересечения луча со сферой
def intersect_ray_sphere(camera_position, direction, sphere):
    C = sphere.center
    r = sphere.radius
    OC = camera_position - C

    k1 = np.dot(direction, direction)
    k2 = 2 * np.dot(OC, direction)
    k3 = np.dot(OC, OC) - r * r

    discriminant = k2 * k2 - 4 * k1 * k3
    if discriminant < 0:
        return np.Inf, np.Inf

    t1 = (-k2 + np.sqrt(discriminant)) / (2 * k1)
    t2 = (-k2 - np.sqrt(discriminant)) / (2 * k1)

    return t1, t2


# Главная функция трассировки
def trace_ray(camera_position, direction, t_min, t_max):
    closest_t = t_max
    closest_obj = None

    for obj in scene:
        t1, t2 = intersect_ray_sphere(camera_position, direction, obj)
        if t_min <= t1 < t_max and t1 < closest_t:
            closest_t = t1
            closest_obj = obj
        if t_min <= t2 < t_max and t2 < closest_t:
            closest_t = t2
            closest_obj = obj

    if closest_obj is None:
        return BACKGROUND_COLOR

    return closest_obj.color


while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()

    for x in range(-C_w_half, C_w_half):
        for y in range(-C_h_half + 1, C_h_half):
            # ray_direction - направление луча (z = 1, так как экран расположен на расстоянии 1)
            ray_direction = np.array([x/C_h, y/C_h, 1])

            # трассируем луч для определения цвета пикселя
            color = trace_ray(camera, ray_direction, 1, np.Inf)

            # Прорисовываем пиксель
            paintPixel(x, y, color)

    clock.tick(FPS)
    pg.display.flip()
