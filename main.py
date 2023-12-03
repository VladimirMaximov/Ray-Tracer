from dataclasses import dataclass
import pygame as pg
import numpy as np
from numpy.linalg import norm
import sys

# Инициализация PyGame
pg.init()

# Константы
C_w = 500
C_w_half = C_w // 2
C_h = 500
C_h_half = C_h // 2
C_w_to_C_h = C_w / C_h
FPS = 30
BACKGROUND_COLOR = np.array([255, 255, 255])

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
    pixel_array[C_w_half + x_coord, C_h_half - y_coord] = tuple(pixel_color)


# Камера - точка начала лучей
camera = np.array([0, 0, 0])


# Класс сферы, задается центром и радиусом
@dataclass
class Sphere:
    center: np.array
    radius: float
    color: np.array


# Класс света, тип света 1 означает общий свет,
# тип света 2 - точечный свет,
# тип света 3 - направленный свет
@dataclass
class Light:
    type_of_light: int
    intensity: float
    position: np.array
    direction: np.array


# Класс объекта, тип объекта 1 - это сфера
@dataclass
class Object:
    type_of_object: int
    object_on_scene: Sphere

# Класс сцена, основной объект,
# который будет прорисовываться на экране
@dataclass
class Scene:
    lights: list[Light]
    objects: list[Object]

# Сцена с объектами
scene = Scene(
    lights=[
        Light(1, 0.2, None, None),
        Light(2, 0.6, np.array([2, 1, 0]), None),
        Light(3, 0.2, None, np.array([1, 4, 4]))
    ],
    objects=[
        Object(1, Sphere(np.array([0, -1, 3]), 1, np.array([255, 0, 0]))),
        Object(1, Sphere(np.array([2, 0, 4]), 1, np.array([0, 0, 255]))),
        Object(1, Sphere(np.array([-2, 0, 4]), 1, np.array([0, 255, 0])))
    ]
)

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

# Функция вычисления освещенности точки
def compute_lighting(point_on_sphere, normal_to_point):
    # Коэффициент яркости
    i = 0.

    # Перебираем все источники освещения
    for light in scene.lights:
        # Если источник освещения - общий свет, то
        # просто прибавляем к коэффициенту значение общего света
        if light.type_of_light == 1:
            i += light.intensity
        else:
            # Иначе вычисляем направление луча света
            if light.type_of_light == 2:
                light_ray_direction = light.position - point_on_sphere
            else:
                light_ray_direction = light.direction

            l_dot_n = np.dot(light_ray_direction, normal_to_point)

            if l_dot_n > 0:
                # Если угол падения луча света меньше 90 градусов
                # (если больше, значит свет достигает задней части поверхности),
                # то вычисляем коэффициент как интенсивность света
                # умноженное на косинус угла падения луча.
                i += light.intensity*l_dot_n/(norm(normal_to_point) * norm(light_ray_direction))

    return i

# Главная функция трассировки
def trace_ray(camera_position, direction, t_min, t_max):
    closest_t = t_max
    closest_obj = None

    for obj in scene.objects:
        t1, t2 = intersect_ray_sphere(camera_position, direction, obj.object_on_scene)
        if t_min <= t1 < t_max and t1 < closest_t:
            closest_t = t1
            closest_obj = obj
        if t_min <= t2 < t_max and t2 < closest_t:
            closest_t = t2
            closest_obj = obj

    if closest_obj is None:
        return BACKGROUND_COLOR

    point_on_sphere = camera_position + closest_t * direction
    normal_to_point = point_on_sphere - closest_obj.object_on_scene.center
    normal_to_point = normal_to_point / norm(normal_to_point)
    return closest_obj.object_on_scene.color * compute_lighting(point_on_sphere, normal_to_point)



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
