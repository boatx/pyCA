# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from cellular_automaton import ConwayLifeOutflow, Sand
from config import NUM_OF_CELLS_X, NUM_OF_CELLS_Y, CELL_SIZE, \
    MARGIN, WINDOW_Y_SIZE, WINDOW_X_SIZE


class CellularAutomatonQt(QWidget):

    def __init__(self, cellular_automaton):
        QWidget.__init__(self)

        self.speed = 1000
        self.cellular_automaton = cellular_automaton
        self.num_of_cells_x = self.cellular_automaton.size_x
        self.num_of_cells_y = self.cellular_automaton.size_y
        self.cell_size = CELL_SIZE

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
        self.margin_left = MARGIN
        self.margin_top = MARGIN
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
        self.start()
        self.cellular_automaton.clean()
        self.repaint()

    def mousePressEvent(self, event):
        x, y = self._convert_coordinates(event.x(), event.y())
        self._update_cell(x, y)

    def mouseMoveEvent(self, event):
        x, y = self._convert_coordinates(event.x(), event.y())
        self._update_cell(x, y)

    def _convert_coordinates(self, x, y):
        x = int((x - self.margin_left)/self.cell_size)
        y = int((y - self.margin_top)/self.cell_size)
        return x, y

    def _update_cell(self, x, y):
        if 0 <= x < self.num_of_cells_x and 0 <= y < self.num_of_cells_y:
            self.cellular_automaton.update_cell(x, y)
            self.repaint()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.fillRect(event.rect(), QBrush(Qt.white))
        painter.setRenderHint(QPainter.Antialiasing)
        for i in range(self.num_of_cells_x):
            a = i*self.cell_size+self.margin_left

            for j in range(self.num_of_cells_y):
                b = j*self.cell_size+self.margin_top

                to_paint, color = self.cellular_automaton.check_cell(j, i)

                if to_paint:
                    painter.fillRect(a, b, self.cell_size, self.cell_size,
                                     QBrush(QColor(color)))

        self._draw_line(painter)
        painter.end()

    def _draw_line(self, painter, line_width=1, line_color=Qt.gray,
                   line_style=Qt.SolidLine):
        # rysowanie siatki
        painter.setPen(QPen(QBrush(Qt.gray), 1, Qt.SolidLine))

        line_start = self.margin_left
        line_stop = self.num_of_cells_x*self.cell_size+line_start
        for i in range(line_start, line_stop+self.cell_size, self.cell_size):
            painter.drawLine(line_start, i, line_stop, i)

        line_start = self.margin_top
        line_stop = self.num_of_cells_y*self.cell_size+line_start
        for i in range(line_start, line_stop+self.cell_size, self.cell_size):
            painter.drawLine(i, line_start, i, line_stop)

    def paint_update(self):
        self.cellular_automaton.update_table()
        self.repaint()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    choose = 'life'

    if len(sys.argv) >= 2:
        choose = sys.argv[1]

    if choose == 'life':
        automat = ConwayLifeOutflow(NUM_OF_CELLS_X, NUM_OF_CELLS_Y)
    elif choose == 'sand':
        automat = Sand(NUM_OF_CELLS_X, NUM_OF_CELLS_Y)
    else:
        print 'Invalid automat name: {}'.format(choose)
        sys.exit(1)

    automat_qt = CellularAutomatonQt(automat)
    automat_qt.show()
    sys.exit(app.exec_())
