import sys
from itertools import product
from functools import partial

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (
    QWidget, QApplication, QPushButton, QSlider, QHBoxLayout, QVBoxLayout,
    QMenuBar, QAction
)
from PyQt5 import QtGui

from pyca.cellular_automaton import ConwayLifeOutflow, Sand
from pyca.config import (
    NUM_OF_CELLS_X, NUM_OF_CELLS_Y, CELL_SIZE, MARGIN, WINDOW_Y_SIZE,
    WINDOW_X_SIZE, MIN_SIMULATION_SPEED, MAX_SIMULATION_SPEED,
    DEFAULT_SIMULATION_SPEED
)


class CellularAutomatonQt(QWidget):

    def __init__(self, cellular_automaton):
        super().__init__()

        self.speed = DEFAULT_SIMULATION_SPEED
        self.cell_size = CELL_SIZE
        self.cellular_automaton = cellular_automaton
        self.num_of_cells_x = self.cellular_automaton.size_x
        self.num_of_cells_y = self.cellular_automaton.size_y

        self.run = False
        self.setWindowTitle('Cellular automaton')
        self.setToolTip('Select cell')
        self.start_btn = QPushButton('Start', self)
        self.start_btn.setToolTip('Start simulation')
        self.clear_btn = QPushButton('Clear', self)
        self.clear_btn.setToolTip('Clear board')
        self.start_btn.clicked.connect(self.toggle)
        self.clear_btn.clicked.connect(self.clean)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.paint_update)
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(MIN_SIMULATION_SPEED)
        self.slider.setMaximum(MAX_SIMULATION_SPEED)
        self.slider.setValue(DEFAULT_SIMULATION_SPEED)
        self.slider.setToolTip('Speed of simulation')
        self.slider.valueChanged.connect(self.set_value)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.clear_btn)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignBottom)
        layout.addLayout(btn_layout, Qt.AlignCenter)
        layout.addWidget(self.slider, Qt.AlignCenter)
        self.setLayout(layout)

        self.menu_bar = QMenuBar(self)
        self.add_menu_bar()

        self.margin_left = MARGIN
        self.margin_top = MARGIN
        self.resize(WINDOW_X_SIZE, WINDOW_Y_SIZE)
        self.setMinimumSize(WINDOW_X_SIZE, WINDOW_Y_SIZE)
        self.resizeEvent = self.on_resize

    def add_menu_bar(self):
        exit_menu = self.menu_bar.addMenu('File')

        conway_action = QAction('Conway Life Game', self)
        cf = partial(self.set_automaton,
                     ConwayLifeOutflow(NUM_OF_CELLS_X, NUM_OF_CELLS_Y))
        conway_action.triggered.connect(cf)
        exit_menu.addAction(conway_action)

        sand_action = QAction('Sand', self)
        sf = partial(self.set_automaton, Sand(NUM_OF_CELLS_X, NUM_OF_CELLS_Y))
        sand_action.triggered.connect(sf)
        exit_menu.addAction(sand_action)

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        exit_menu.addAction(exit_action)

    def set_automaton(self, cellular_automaton):
        self.cellular_automaton = cellular_automaton
        self.num_of_cells_x = self.cellular_automaton.size_x
        self.num_of_cells_y = self.cellular_automaton.size_y
        self.repaint()

    def on_resize(self, event):
        """Resize grid"""
        width, height = self.width(), self.height()
        new_x_cell_size = (width - MARGIN*2) // self.num_of_cells_x
        new_y_cell_size = (height - MARGIN*2) // self.num_of_cells_y
        self.cell_size = min(new_x_cell_size, new_y_cell_size)
        self.margin_left = (width - self.cell_size*self.num_of_cells_x) // 2
        self.margin_top = (height - self.cell_size*self.num_of_cells_y) // 2
        self.repaint()

    def set_value(self):
        """Set slider value"""
        self.speed = self.slider.value()
        if self.run:
            self.timer.stop()
            self.timer.start(self.speed)

    def toggle(self):
        """Start simulation"""
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
        self.toggle()
        self.cellular_automaton.clean()
        self.repaint()

    def mousePressEvent(self, event):
        x, y = self._convert_coordinates(event.x(), event.y())
        self._update_cell(x, y)

    def mouseMoveEvent(self, event):
        x, y = self._convert_coordinates(event.x(), event.y())
        self._update_cell(x, y)

    def _convert_coordinates(self, x, y):
        x = (x - self.margin_left) // self.cell_size
        y = (y - self.margin_top) // self.cell_size
        return int(x), int(y)

    def _update_cell(self, x, y):
        if 0 <= x < self.num_of_cells_x and 0 <= y < self.num_of_cells_y:
            self.cellular_automaton.update_cell(x, y)
            self.repaint()

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.fillRect(event.rect(), QtGui.QBrush(Qt.white))
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        cells = product(range(self.num_of_cells_x), range(self.num_of_cells_y))

        for i, j in cells:

            i_paint_cord = i*self.cell_size + self.margin_left

            j_paint_cord = j*self.cell_size + self.margin_top

            to_paint, color = self.cellular_automaton.check_cell(j, i)

            if to_paint:
                painter.fillRect(i_paint_cord, j_paint_cord, self.cell_size,
                                 self.cell_size,
                                 QtGui.QBrush(QtGui.QColor(color)))

        self._draw_lines(painter)
        painter.end()

    def _draw_lines(self, painter, line_width=1, line_color=Qt.gray,
                    line_style=Qt.SolidLine):

        painter.setPen(QtGui.QPen(QtGui.QBrush(line_color), 1, line_style))

        start_x, start_y = self.margin_left, self.margin_top
        stop_x = self.num_of_cells_x*self.cell_size + start_x
        stop_y = self.num_of_cells_y*self.cell_size + start_y

        for i in range(start_y, stop_y + self.cell_size, self.cell_size):
            painter.drawLine(start_x, i, stop_x, i)

        for i in range(start_x, stop_x + self.cell_size, self.cell_size):
            painter.drawLine(i, start_y, i, stop_y)

    def paint_update(self):
        self.cellular_automaton.update_table()
        self.repaint()


def main():
    app = QApplication(sys.argv)

    choose = 'life'

    if len(sys.argv) >= 2:
        choose = sys.argv[1]

    if choose == 'life':
        automat = ConwayLifeOutflow(NUM_OF_CELLS_X, NUM_OF_CELLS_Y)
    elif choose == 'sand':
        automat = Sand(NUM_OF_CELLS_X, NUM_OF_CELLS_Y)
    else:
        print('Invalid automat name: {}'.format(choose))
        sys.exit(1)

    automat_qt = CellularAutomatonQt(automat)
    automat_qt.show()
    sys.exit(app.exec_())
