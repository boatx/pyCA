# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys

from PyQt4.QtCore import SIGNAL, QTimer, Qt
from PyQt4 import QtGui

from cellular_automaton import ConwayLifeOutflow, Sand
from config import NUM_OF_CELLS_X, NUM_OF_CELLS_Y, CELL_SIZE, \
    MARGIN, WINDOW_Y_SIZE, WINDOW_X_SIZE, MIN_SIMULATION_SPEED, \
    MAX_SIMULATION_SPEED, DEFAULT_SIMULATION_SPEED


class CellularAutomatonQt(QtGui.QWidget):

    def __init__(self, cellular_automaton):
        QtGui.QWidget.__init__(self)

        self.speed = 1000
        self.cellular_automaton = cellular_automaton
        self.num_of_cells_x = self.cellular_automaton.size_x
        self.num_of_cells_y = self.cellular_automaton.size_y
        self.cell_size = CELL_SIZE

        self.run = False
        self.setWindowTitle('Cellular automaton')
        self.setToolTip('Select cell')
        self.start_btn = QtGui.QPushButton('Start', self)
        self.start_btn.setToolTip('Start simulation')
        self.clear_btn = QtGui.QPushButton('Clear', self)
        self.clear_btn.setToolTip('Clear board')
        self.connect(self.start_btn, SIGNAL("clicked()"), self.start)
        self.connect(self.clear_btn, SIGNAL("clicked()"), self.clean)
        self.timer = QTimer(self)
        self.connect(self.timer, SIGNAL("timeout()"), self.paint_update)
        self.slider = QtGui.QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(MIN_SIMULATION_SPEED)
        self.slider.setMaximum(MAX_SIMULATION_SPEED)
        self.slider.setValue(DEFAULT_SIMULATION_SPEED)
        self.slider.setToolTip('Speed of simulation')
        self.connect(self.slider, SIGNAL('valueChanged(int)'),
                     self.set_value)
        btn_layout = QtGui.QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.clear_btn)
        layout = QtGui.QVBoxLayout()
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
            self.start_btn.setToolTip('End simulation')
            self.start_btn.setText('End')
            self.timer.start(self.speed)
        else:
            self.run = False
            self.start_btn.setToolTip('Start')
            self.start_btn.setText('Start simulation')
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
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.fillRect(event.rect(), QtGui.QBrush(Qt.white))
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        for i in range(self.num_of_cells_x):
            a = i*self.cell_size+self.margin_left

            for j in range(self.num_of_cells_y):
                b = j*self.cell_size+self.margin_top

                to_paint, color = self.cellular_automaton.check_cell(j, i)

                if to_paint:
                    painter.fillRect(a, b, self.cell_size, self.cell_size,
                                     QtGui.QBrush(QtGui.QColor(color)))

        self._draw_line(painter)
        painter.end()

    def _draw_line(self, painter, line_width=1, line_color=Qt.gray,
                   line_style=Qt.SolidLine):
        # rysowanie siatki
        painter.setPen(QtGui.QPen(QtGui.QBrush(line_color), 1, line_style))

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
    app = QtGui.QApplication(sys.argv)

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
