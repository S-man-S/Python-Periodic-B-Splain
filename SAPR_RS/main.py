from random import randrange
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtWidgets import QLabel, QSpinBox, QPushButton, QRadioButton, QTableWidget, QTableWidgetItem
from PyQt6.QtGui import QPen, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QPoint
from math import floor


class MainWindow(QMainWindow):
    # Функция инициализации окна, только графика
    def __init__(self, width, height, draw_width):
        self.draw_width, self.draw_height = draw_width, height
        widg_width, widg_height = floor((width - draw_width) / 2), floor(height / 16)

        super().__init__()
        self.setGeometry(0, 0, width, height)

        self.label_draw = QLabel()
        self.setCentralWidget(self.label_draw)
        self.clear_graph()

        self.label_np = QLabel("Количество точек:", self)
        self.label_np.setGeometry(draw_width, 0, widg_width, widg_height)
        self.SB_np = QSpinBox(self)
        self.SB_np.setGeometry(draw_width + widg_width, 0, widg_width, widg_height)
        self.SB_np.setRange(2, 100)  # 49
        self.SB_np.setValue(21)
        self.SB_np.textChanged.connect(self.clear_table)

        self.label_pow = QLabel("Степень сплайна:", self)
        self.label_pow.setGeometry(draw_width, widg_height, widg_width, widg_height)
        self.SB_pow = QSpinBox(self)
        self.SB_pow.setGeometry(draw_width + widg_width, widg_height, widg_width, widg_height)
        self.SB_pow.setRange(0, 5)
        self.SB_pow.setValue(4)
        self.SB_pow.textChanged.connect(self.clear_graph)

        self.label_qual = QLabel("Качество:", self)
        self.label_qual.setGeometry(draw_width, 2 * widg_height, widg_width, widg_height)
        self.SB_qual = QSpinBox(self)
        self.SB_qual.setGeometry(draw_width + widg_width, 2 * widg_height, widg_width, widg_height)
        self.SB_qual.setRange(0, 3)
        self.SB_qual.setValue(2)
        self.SB_qual.textChanged.connect(self.clear_graph)

        self.PB_gen = QPushButton("Генерация точек", self)
        self.PB_gen.setGeometry(draw_width, 3 * widg_height, widg_width, widg_height)
        self.PB_gen.clicked.connect(self.gen_points)

        self.PB_draw = QPushButton("Построение графика", self)
        self.PB_draw.setGeometry(draw_width + widg_width, 3 * widg_height, widg_width, widg_height)
        self.PB_draw.clicked.connect(self.drawing)

        self.RB_rand = QRadioButton("Случайно", self)
        self.RB_rand.setGeometry(draw_width, 4 * widg_height, widg_width, widg_height)
        self.RB_ser = QRadioButton("Последовательно\n(Максимум 49 точек)", self)
        self.RB_ser.setGeometry(draw_width + widg_width, 4 * widg_height, widg_width, widg_height)
        self.RB_ser.setChecked(True)

        self.T = QTableWidget(self)
        self.T.setColumnCount(3)
        for i in range(3):
            self.T.setColumnWidth(i, 86)
        self.T.setGeometry(draw_width, 5 * widg_height, 2 * widg_width, 11 * widg_height)

    # Очистка таблицы точек, только графика
    def clear_table(self):
        self.T.clear()
        self.T.setRowCount(0)
        self.clear_graph()

    # Очистка области рисования, только графика
    def clear_graph(self):
        canvas = QPixmap(1200, 800)
        canvas.fill(Qt.GlobalColor.white)
        self.label_draw.setPixmap(canvas)
        canvas = self.label_draw.pixmap()
        painter = QPainter(canvas)
        pen = QPen()
        pen.setColor(QColor(0, 0, 0))
        pen.setWidth(3)
        painter.setPen(pen)
        point0 = QPoint(floor(self.draw_width / 25), floor(24 * self.draw_height / 25))
        point1 = QPoint(floor(self.draw_width / 5), floor(24 * self.draw_height / 25))
        point2 = QPoint(floor(self.draw_width / 25), floor(4 * self.draw_height / 5))
        point3 = QPoint(floor(self.draw_width / 10), floor(9 * self.draw_height / 10))
        painter.drawLine(point0, point1)
        painter.drawText(point1, "X")
        painter.drawLine(point0, point2)
        painter.drawText(point2, "Y")
        painter.drawLine(point0, point3)
        painter.drawText(point3, "Z")
        painter.end()
        self.label_draw.setPixmap(canvas)

    # Рекурсивное получение интервала параметризации
    def get_part(self, power, region, parameters):  # Передаём степень сплайна, номер интервала и параметры
        # Базис рекурсии
        if region < 0 or region > power:
            return [0] * (power + 1)
        if power == 0:
            return [1]
        rez = [0] * (power + 1)  # Список коэффициентов при t от p до 0
        # Получение коэффициентов параметризации меньшей степени
        prev_left = self.get_part(power - 1, region, parameters[:len(parameters) - 1])
        prev_right = self.get_part(power - 1, region - 1, parameters[1:])
        # Коэффициенты при t и и не t в формуле Кокса де Бура
        t_left = 1 / (parameters[power] - parameters[0])
        left = -1 * parameters[0] / (parameters[power] - parameters[0])
        right = parameters[power + 1] / (parameters[power + 1] - parameters[1])
        t_right = -1 / (parameters[power + 1] - parameters[1])
        # Получаем список коэффициентов по формуле Кокса де Бура
        for i in range(power):
            # Так как умножаем на коэффициент при t прибавляем к большей степени
            rez[i] += prev_left[i] * t_left + prev_right[i] * t_right
            # Так как умножаем на коэффициент без t прибавляем к текущей степени
            rez[i + 1] += prev_left[i] * left + prev_right[i] * right
        return rez

    # Отрисовка сплайна
    def draw_graph(self, points, status=0):
        canvas = self.label_draw.pixmap()
        painter = QPainter(canvas)
        # Прибавляем к координатам x и y координату z умноженную на cos(45) или sin(45) (sqrt(2) / 2)
        for i in range(len(points)):
            koef = round(points[i][2] / pow(2, (1 / 2)))
            points[i][0] += koef
            points[i][1] += koef
        pen = QPen()
        # Установка цвета и толщины линий, отрисовка точек
        if status == 0:
            pen.setColor(QColor(0, 255, 0))
            pen.setWidth(10)
            painter.setPen(pen)
            painter.drawEllipse(points[0][0] - 5, (800 - points[0][1]) - 5, 10, 10)
            painter.drawEllipse(points[len(points) - 1][0] - 5, (800 - points[len(points) - 1][1]) - 5, 10, 10)
            pen.setColor(QColor(255, 0, 0))
            pen.setWidth(6)
            painter.setPen(pen)
            for i in range(1, len(points) - 1):
                painter.drawEllipse(points[i][0] - 3, (800 - points[i][1]) - 3, 6, 6)
            pen.setWidth(3)
            painter.setPen(pen)
        else:
            pen.setColor(QColor(0, 0, 255))
            pen.setWidth(5)
            painter.setPen(pen)
        # Отрисовка графика
        for i in range(len(points) - 1):
            painter.drawLine(points[i][0], (800 - points[i][1]), points[i + 1][0], (800 - points[i + 1][1]))
        painter.end()
        self.label_draw.setPixmap(canvas)

    # Генерация опорных точек
    def gen_points(self):
        if (self.SB_np.value() < 50 or self.RB_rand.isChecked()) and self.SB_np.value() >= self.SB_pow.value() + 1:
            self.T.setRowCount(self.SB_np.value())
            for i in range(self.SB_np.value()):
                if self.RB_ser.isChecked():
                    x_lower = floor(self.draw_width / (self.SB_np.value() + 1) * i)
                    x_upper = floor(self.draw_width / (self.SB_np.value() + 1)) * (i + 1)
                    self.T.setItem(i, 0, QTableWidgetItem(str(randrange(x_lower, x_upper))))
                    self.T.setItem(i, 1, QTableWidgetItem(str(randrange(0, self.draw_height))))
                    self.T.setItem(i, 2, QTableWidgetItem(str(randrange(-100, 100))))
                else:
                    self.T.setItem(i, 0, QTableWidgetItem(str(randrange(100, self.draw_width - 100))))
                    self.T.setItem(i, 1, QTableWidgetItem(str(randrange(100, self.draw_height - 100))))
                    self.T.setItem(i, 2, QTableWidgetItem(str(randrange(-100, 100))))

    # Обработка нажатия на кнопку "Построения графика"
    def drawing(self):
        # Только если в таблице есть точки
        if self.T.rowCount() != 0:
            # Очистка поля графика
            self.clear_graph()
            # Количество точек
            num_points = self.SB_np.value()
            # Степень
            power = self.SB_pow.value()
            # Качество (количество точек для отрисовки одного элементарного сплайна)
            quality = pow(10, self.SB_qual.value())
            # Число существенных интервалов (int - зарезервированное слово, его использовать нельзя)
            imp = num_points - power
            # Интервал параметризации
            parameters = [i for i in range(power + num_points + 1)]
            # Получаем опорные точки из таблицы
            pts = []
            for i in range(self.T.rowCount()):
                pts.append(
                    [int(self.T.item(i, 0).text()), int(self.T.item(i, 1).text()), int(self.T.item(i, 2).text())])
            # Получение точек для отрисовки сплайна в количестве imp * quality, у точек три координаты: x, y, z
            pts2 = [[0] * 3 for _ in range(imp * quality)]
            for t in range(power * quality, num_points * quality):
                # Получение коэффициентов для каждого интервала параметризации
                vector = [[0] * (power + 1) for _ in range(power + 1)]
                for i in range(power + 1):
                    left_cap = i + floor(t / quality) - power
                    right_cap = i + floor(t / quality) + 2
                    vector[i] = self.get_part(power, (power - i), parameters[left_cap: right_cap])
                # Находим текущую опорную точку
                t_cur = (t / quality)
                # Получаем координаты текущей точки сплайна,
                # для чего перемножаем вектор степеней t на матрицу коэффициентов t, на вектор координат опорных точек
                for i in range(power + 1):
                    for j in range(power + 1):
                        degree = (power - j)
                        for k in range(3):
                            point_cur = pts[i + floor(t_cur) - power][k]
                            pts2[t - (power * quality)][k] += vector[i][j] * (t_cur ** degree) * point_cur
                # Округляем полученные координаты для отрисовки
                for i in range(3):
                    pts2[t - (power * quality)][i] = round(pts2[t - (power * quality)][i])
            # Отрисовка сплайна и ломанной по опорным точкам
            window.draw_graph(pts2, 1)
            window.draw_graph(pts)


if __name__ == '__main__':
    # Инициализация, только графика
    window_size_x, window_size_y = 1500, 800
    draw_size_x, draw_size_y = 1200, 800
    app = QApplication([])
    window = MainWindow(window_size_x, window_size_y, draw_size_x)
    window.show()
    app.exec()
