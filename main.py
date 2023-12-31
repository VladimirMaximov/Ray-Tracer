from dataclasses import dataclass
import numpy as np
from numpy.linalg import norm
from PIL import Image

# Константы
C_w = 500
C_w_half = C_w // 2
C_h = 500
C_h_half = C_h // 2
C_w_to_C_h = C_w / C_h
recursion_depth = 3
eps = 0.0001
BACKGROUND_COLOR = np.array([0, 0, 0])

# Камера - точка начала лучей, изначально
# камера направлена в сторону оси Z, ось X
# направлена вправо, ось Y влево.
camera1 = np.array([4, 0, 0])
camera_rot = np.array(
    [[0.7071, 0, -0.7071],
     [0, 1, 0],
     [0.7071, 0, 0.7071]]
)


# Класс сферы, задается центром и радиусом
@dataclass
class Sphere:
    center: np.array
    radius: float
    color: np.array
    shine: int
    reflective: float


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
        # Light(1, 0.2, None, None),
        Light(2, 0.6, np.array([20, 20, -20]), None),
        Light(3, 0.4, None, np.array([1, 4, 4]))
    ],
    objects=[
        # Зеркала
        Object(1, Sphere(np.array([-5, -0.5, 4]), 3.0, np.array([0, 255, 0]), -1, 0.7)),
        Object(1, Sphere(np.array([0, -0.5, 9]), 3.0, np.array([255, 0, 0]), -1, 0.7)),
        # Основные шары
        Object(1, Sphere(np.array([0, -0.5, 4]), 0.8, np.array([255, 255, 255]), 10, 0.0)),
        Object(1, Sphere(np.array([0, 0.5, 4]), 0.6, np.array([255, 255, 255]), 10, 0.0)),
        Object(1, Sphere(np.array([0, 1.2, 4]), 0.4, np.array([255, 255, 255]), 10, 0.0)),
        # Нос
        Object(1, Sphere(np.array([0, 1.2, 3.6]), 0.1, np.array([237, 118, 14]), -1, 0.0)),
        Object(1, Sphere(np.array([0, 1.2, 3.55]), 0.09, np.array([237, 118, 14]), -1, 0.0)),
        Object(1, Sphere(np.array([0, 1.2, 3.5]), 0.08, np.array([237, 118, 14]), -1, 0.0)),
        Object(1, Sphere(np.array([0, 1.2, 3.45]), 0.07, np.array([237, 118, 14]), -1, 0.0)),
        Object(1, Sphere(np.array([0, 1.2, 3.40]), 0.06, np.array([237, 118, 14]), -1, 0.0)),
        Object(1, Sphere(np.array([0, 1.2, 3.35]), 0.05, np.array([237, 118, 14]), -1, 0.0)),
        Object(1, Sphere(np.array([0, 1.2, 3.30]), 0.04, np.array([237, 118, 14]), -1, 0.0)),
        # Глаза
        Object(1, Sphere(np.array([0.15, 1.35, 3.66]), 0.04, np.array([255, 0, 0]), -1, 0.0)),
        Object(1, Sphere(np.array([-0.15, 1.35, 3.66]), 0.04, np.array([255, 0, 0]), -1, 0.0)),
        # Ведро
        Object(1, Sphere(np.array([0, 1.5, 4]), 0.3, np.array([192, 192, 192]), 10, 0.2)),
        Object(1, Sphere(np.array([0, 1.55, 4]), 0.3, np.array([192, 192, 192]), 10, 0.2)),
        Object(1, Sphere(np.array([0, 1.60, 4]), 0.3, np.array([192, 192, 192]), 10, 0.2)),
        # Поверхность
        Object(1, Sphere(np.array([0, -5001, 0]), 5000, np.array([255, 255, 255]), -1, 0))

    ]
)


# Функция, вычисляющая отраженный луч относительно нормали
def reflect_ray_direction(light_ray_direction, normal_to_point):
    return 2 * normal_to_point * np.dot(normal_to_point, light_ray_direction) - light_ray_direction


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
def compute_lighting(point_on_sphere, normal_to_point, camera_to_point, specular):
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
                t_max = 1
            else:
                light_ray_direction = light.direction
                t_max = np.Inf

            # Проверка наличия тени
            shadow_sphere, shadow_t = closest_intersection(
                point_on_sphere,
                light_ray_direction,
                eps,
                t_max
            )

            # Если есть объект, который создает
            # тень, то ничего не прибавляем
            if shadow_sphere is not None:
                continue

            # Диффузный (рассеянный) свет
            l_dot_n = np.dot(light_ray_direction, normal_to_point)

            if l_dot_n > 0:
                # Если угол падения луча света меньше 90 градусов
                # (если больше, значит свет достигает задней части поверхности),
                # то вычисляем коэффициент как интенсивность света
                # умноженное на косинус угла падения луча.
                i += light.intensity * l_dot_n / (norm(normal_to_point) * norm(light_ray_direction))

            # Акцентный (направленный) свет
            if specular != -1:
                # Если объект имеет свойство блеска,
                # то вычисляем направление отражения луча света
                reflection_direction = reflect_ray_direction(light_ray_direction, normal_to_point)

                # Вычисляем косинус между лучом отражения и лучем из камеры в точку
                r_dot_c = np.dot(reflection_direction, camera_to_point)
                if r_dot_c > 0:
                    i += light.intensity * \
                         (r_dot_c / (norm(reflection_direction) * norm(camera_to_point))) ** specular

    return i


# Функция поиска пересечения
# луча с ближайшим объектом
def closest_intersection(start_point, direction, t_min, t_max):
    closest_t = t_max
    closest_obj = None

    for obj in scene.objects:
        t1, t2 = intersect_ray_sphere(start_point, direction, obj.object_on_scene)
        if t_min <= t1 < t_max and t1 < closest_t:
            closest_t = t1
            closest_obj = obj
        if t_min <= t2 < t_max and t2 < closest_t:
            closest_t = t2
            closest_obj = obj

    return closest_obj, closest_t


# Главная функция трассировки
def trace_ray(camera_position, direction, t_min, t_max, rec_depth):
    # Ищем ближайший объект, с которым
    # пересекается луч и расстояние до него
    closest_obj, closest_t = closest_intersection(camera_position, direction, t_min, t_max)

    if closest_obj is None:
        return BACKGROUND_COLOR

    point_on_sphere = camera_position + closest_t * direction
    normal_to_point = point_on_sphere - closest_obj.object_on_scene.center

    # Нормализуем нормаль к точке
    normal_to_point /= norm(normal_to_point)

    # Значение отражения объекта
    reflective = closest_obj.object_on_scene.reflective
    local_color = closest_obj.object_on_scene.color * compute_lighting(
        point_on_sphere,
        normal_to_point,
        -direction,
        closest_obj.object_on_scene.shine
    )

    # Если глубина отражения равна 0 или
    # объект не отражающий, то возвращаем цвет
    if rec_depth <= 0 or reflective <= 0:
        return local_color

    # Рассчитываем цвет отражения
    reflect_ray_d = reflect_ray_direction(-direction, normal_to_point)
    reflected_color = trace_ray(point_on_sphere, reflect_ray_d, eps, np.Inf, rec_depth - 1)

    # Возвращаем цвет с учетом отражения
    return local_color * (1 - reflective) + reflected_color * reflective


def paint(camera, camera_rotation):
    for x in range(-C_w_half, C_w_half):
        for y in range(-C_h_half + 1, C_h_half):
            # ray_direction - направление луча (z = 1,
            # так как экран расположен на расстоянии 1)
            ray_direction = np.dot(camera_rotation, np.array([x / C_h, y / C_h, 1]))

            # трассируем луч для определения цвета пикселя
            color = trace_ray(camera, ray_direction, 1, np.Inf, recursion_depth)

            # Прорисовываем пиксель
            arr[C_w_half + x][C_h_half - y] = f(color)


f = np.vectorize(lambda x1: min(x1, 255))
arr = np.array([[[0, 0, 0] for _ in range(C_w)] for _ in range(C_h)], dtype=np.uint8)

if __name__ == "__main__":
    paint(camera1, camera_rot)
    img = Image.fromarray(np.transpose(arr, axes=(1, 0, 2)))
    img.save("123.jpg")
