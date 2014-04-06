#-*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from config import NUM_OF_CELLS_X, NUM_OF_CELLS_Y, CELL_SIZE, \
    MARGIN, WINDOW_Y_SIZE, WINDOW_X_SIZE


class Cell(QWidget):

    @staticmethod
    def _gen_matrix(x, y):
        return [[0 for _ in range(x)]
                for _ in range(y)]

    @staticmethod
    def _copy_matrix(matrix):
        return [list(i) for i in matrix]

    def __init__(self):
        QWidget.__init__(self)

        self.speed = 1000
        #2 rows invisible
        self.num_of_cells_x = NUM_OF_CELLS_X
        self.total_num_of_cells_x = NUM_OF_CELLS_X+2
        #2 rows invisible
        self.num_of_cells_y = NUM_OF_CELLS_Y
        self.total_num_of_cells_y = NUM_OF_CELLS_Y+2
        self.cell_size = CELL_SIZE
        self.table = self._gen_matrix(self.total_num_of_cells_x,
                                      self.total_num_of_cells_y)
        self.run = False
        self.setWindowTitle('Automat komorkowy')
        self.setToolTip('Zaznacz komorki')
        self.start_btn = QPushButton('Start', self)
        self.start_btn.setToolTip('Start Symulacji')
        self.clear_btn = QPushButton('Wyczysc', self)
        self.clear_btn.setToolTip('Wyczysc plansze')
        self.connect(self.start_btn, SIGNAL("clicked()"), self.start)
        self.connect(self.clear_btn, SIGNAL("clicked()"), self.clean)
        self.timer = QTimer(self)
        self.connect(self.timer, SIGNAL("timeout()"), self.paint_update)
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(5)
        self.slider.setMaximum(1000)
        self.slider.setToolTip('Predkosc symulacji')
        self.slider.setValue(500)
        self.connect(self.slider, SIGNAL('valueChanged(int)'), self.set_value)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.clear_btn)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignBottom)
        layout.addLayout(btn_layout, Qt.AlignCenter)
        layout.addWidget(self.slider, Qt.AlignCenter)
        self.setLayout(layout)

        self.window_x_size = WINDOW_X_SIZE
        self.window_y_size = WINDOW_Y_SIZE
        self.resize(self.window_x_size, self.window_y_size)

    def set_value(self):
        self.speed = self.slider.value()
        if self.run:
            self.timer.stop()
            self.timer.start(self.speed)

    def start(self):
        if not self.run:
            self.run = True
            self.start_btn.setToolTip('Koniec Symulacji')
            self.start_btn.setText('Koniec')
            self.timer.start(self.speed)
        else:
            self.run = False
            self.start_btn.setToolTip('Start')
            self.start_btn.setText('Start Symulacji')
            self.timer.stop()

    def clean(self):
        self.table = self._gen_matrix(self.total_num_of_cells_x,
                                      self.total_num_of_cells_y)
        self.repaint()

    def mousePressEvent(self, event):
        x, y = self._convert_cordinates(event.x(), event.y())
        self._update_cell(x, y)

    def mouseMoveEvent(self, event):
        x, y = self._convert_cordinates(event.x(), event.y())
        self._update_cell(x, y)

    def _convert_cordinates(self, x, y):
        x = (x - MARGIN)/self.cell_size
        y = (y - MARGIN)/self.cell_size
        return x, y

    def _update_cell(self, x, y):
        if 0 <= x < self.num_of_cells_x and 0 <= y < self.num_of_cells_y:
            x += 1
            y += 1
            if self.table[y][x] == 1:
                self.table[y][x] = 0
            else:
                self.table[y][x] = 1
            self.repaint()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.fillRect(event.rect(), QBrush(Qt.white))
        painter.setRenderHint(QPainter.Antialiasing)
        for i in range(1, self.num_of_cells_x+1):
            a = (i-1)*self.cell_size+MARGIN
            for j in range(1, self.num_of_cells_y+1):
                b = (j-1)*self.cell_size+MARGIN
                if self.table[j][i] == 1:
                    painter.fillRect(a, b, self.cell_size, self.cell_size, QBrush(Qt.blue))

        #rysowanie siatki linii
        self._draw_line(painter)
        painter.end()

    def _draw_line(self, painter, line_width=1, line_color=Qt.gray, line_style=Qt.SolidLine):
        #rysowanie siatki linii
        painter.setPen(QPen(QBrush(Qt.gray), 1, Qt.SolidLine))

        line_start = MARGIN
        line_stop = self.num_of_cells_x*self.cell_size+line_start
        for i in range(line_start, line_stop+self.cell_size, self.cell_size):
            painter.drawLine(line_start, i, line_stop, i)

        line_start = MARGIN
        line_stop = self.num_of_cells_y*self.cell_size+line_start
        for i in range(line_start, line_stop+self.cell_size, self.cell_size):
            painter.drawLine(i, line_start, i, line_stop)

    def life_rules(self, tmp):
        for j in range(1, self.num_of_cells_y+1):
            for i in range(1, self.num_of_cells_x+1):
                counter = 0
                if self.table[i+1][j+1] == 1:
                    counter += 1
                if self.table[i-1][j-1] == 1:
                    counter += 1
                if self.table[i][j-1] == 1:
                    counter += 1
                if self.table[i-1][j] == 1:
                    counter += 1
                if self.table[i][j+1] == 1:
                    counter += 1
                if self.table[i+1][j] == 1:
                    counter += 1
                if self.table[i-1][j+1] == 1:
                    counter += 1
                if self.table[i+1][j-1] == 1:
                    counter += 1

                if self.table[i][j] == 1:
                    if counter < 2 or counter > 3:
                        tmp[i][j] = 0
                else:
                    if counter == 3:
                        tmp[i][j] = 1
        return tmp

    def paint_update(self):
        tmp = self._copy_matrix(self.table)

        tmp = self.life_rules(tmp)

        self.table = tmp

        self.repaint()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    life = Cell()
    life.show()
    sys.exit(app.exec_())
