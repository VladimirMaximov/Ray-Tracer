from main import *
import cv2
import glob


# Вычисление косинуса между двумя векторами
def cos(x_1, x_2):
    return np.dot(x_1, x_2) / (np.dot(x_1, x_1) * np.dot(x_2, x_2))


# Вычисление синуса между двумя векторами
def sin(x_1, x_2):
    cr = np.cross(x_1, x_2)
    return np.sqrt(np.dot(cr, cr)) / (np.dot(x_1, x_1) * np.dot(x_2, x_2))


# Функция, возвращающая по заданному параметру t
# точку на окружности, на которой расположена камера
def point_on_circle(t):
    return np.array([0, 3, 4]) + \
           np.array([-3.87 * np.cos(t),
                     0,
                     -3.87 * np.sin(t)]
                    )


# Функция, возвращающая по заданным векторам
# матрицу поворота от первого вектора ко второму
def create_rotation_matrix(vector_1, vector_2):
    r = (np.cross(vector_1, vector_2)) / norm(np.cross(vector_1, vector_2))  # rotational_axis
    cos_fi = cos(vector_1, vector_2)
    sin_fi = sin(vector_1, vector_2)
    v = 1 - cos_fi

    rot_matrix = np.array(
        [[r[0] * r[0] * v + cos_fi, r[0] * r[1] * v - r[2] * sin_fi, r[0] * r[2] * v + r[1] * sin_fi],
         [r[0] * r[1] * v + r[2] * sin_fi, r[1] * r[1] * v + cos_fi, r[1] * r[2] * v - r[0] * sin_fi],
         [r[0] * r[2] * v - r[1] * sin_fi, r[1] * r[2] * v + r[0] * sin_fi, r[2] * r[2] * v + cos_fi]
         ])

    return rot_matrix


# Центром, в который будет направлена камера
# будем считать центр "головы" снеговика
circle_center = np.array([0, 1.2, 4])

# 240 параметров t, находящихся на
# равных интервалах в промежутке между 0 и 2*pi
t240 = np.linspace(0, 2 * np.pi, 240, endpoint=False)
for i in range(240):
    point_on_circle1 = point_on_circle(t240[i])
    v1 = np.array([0, 0, 1])
    v2 = (circle_center - point_on_circle1) / norm(circle_center - point_on_circle1)
    rotation_matrix = create_rotation_matrix(v1, v2)

    # Вызываем функцию paint, тем самым заполняя список
    # arr для дальнейшего преобразования в картинку
    paint(point_on_circle1, rotation_matrix)
    img = Image.fromarray(np.transpose(arr, axes=(1, 0, 2)))
    img.save(f"Pictures/{i}.jpg")

# Создаем видео из кадров
frame_size = (500, 500)
out = cv2.VideoWriter("snowman.mp4", cv2.VideoWriter.fourcc(*"mp4v"), 60, frame_size)
for i in range(0, 240):
    file_name = glob.glob(f"Pictures/{i}.jpg")[0]
    img = cv2.imread(file_name)
    out.write(img)

out.release()
