import logging
import sys
from enum import StrEnum
from functools import partial
from itertools import product

import click
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QHBoxLayout,
    QMenuBar,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from pyca.cellular_automaton import CellularAutomatonBaseClass, ConwayLifeOutflow, Sand
from pyca.config import (
    CELL_SIZE,
    DEFAULT_SIMULATION_SPEED,
    MARGIN,
    MAX_SIMULATION_SPEED,
    MIN_SIMULATION_SPEED,
    NUM_OF_CELLS_X,
    NUM_OF_CELLS_Y,
    WINDOW_X_SIZE,
    WINDOW_Y_SIZE,
)

logging.basicConfig(level=logging.INFO)

LOGGER = logging.getLogger(__name__)


class AutomatonType(StrEnum):
    LIFE = "life"
    SAND = "sand"


class CellularAutomatonQt(QWidget):
    def __init__(self, cellular_automaton: CellularAutomatonBaseClass):
        super().__init__()

        self.speed = DEFAULT_SIMULATION_SPEED
        self.cell_size = CELL_SIZE
        self.cellular_automaton = cellular_automaton
        self.num_of_cells_x = self.cellular_automaton.size_x
        self.num_of_cells_y = self.cellular_automaton.size_y

        self.run = False
        self.setWindowTitle("Cellular automaton")
        self.setToolTip("Select cell")
        self.start_btn = QPushButton("Start", self)
        self.start_btn.setToolTip("Start simulation")
        self.clear_btn = QPushButton("Clear", self)
        self.clear_btn.setToolTip("Clear board")
        self.start_btn.clicked.connect(self.toggle)
        self.clear_btn.clicked.connect(self.clean)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.paint_update)
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setMinimum(MIN_SIMULATION_SPEED)
        self.slider.setMaximum(MAX_SIMULATION_SPEED)
        self.slider.setValue(DEFAULT_SIMULATION_SPEED)
        self.slider.setToolTip("Speed of simulation")
        self.slider.valueChanged.connect(self.set_speed_value)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.clear_btn)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        layout.addLayout(btn_layout, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.slider, Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        self.menu_bar = QMenuBar(self)
        self.add_menu_bar()

        self.margin_left = MARGIN
        self.margin_top = MARGIN
        self.resize(WINDOW_X_SIZE, WINDOW_Y_SIZE)
        self.setMinimumSize(WINDOW_X_SIZE, WINDOW_Y_SIZE)

    def resizeEvent(self, event: QtGui.QResizeEvent | None) -> None:
        """Resize grid"""
        width, height = self.width(), self.height()
        new_x_cell_size = (width - MARGIN * 2) // self.num_of_cells_x
        new_y_cell_size = (height - MARGIN * 2) // self.num_of_cells_y
        self.cell_size = min(new_x_cell_size, new_y_cell_size)
        self.margin_left = (width - self.cell_size * self.num_of_cells_x) // 2
        self.margin_top = (height - self.cell_size * self.num_of_cells_y) // 2
        self.repaint()

    def mousePressEvent(self, event: QtGui.QMouseEvent | None) -> None:
        if not event:
            return
        x, y = self._convert_coordinates(event.x(), event.y())
        self._update_cell(x, y)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent | None) -> None:
        if not event:
            return
        x, y = self._convert_coordinates(event.x(), event.y())
        self._update_cell(x, y)

    def paintEvent(self, event: QtGui.QPaintEvent | None) -> None:
        if not event:
            return
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.fillRect(event.rect(), QtGui.QBrush(Qt.GlobalColor.white))
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        cells = product(range(self.num_of_cells_x), range(self.num_of_cells_y))

        for i, j in cells:
            to_paint, color = self.cellular_automaton.check_cell(j, i)
            if to_paint:
                self.paint_cell(i, j, color, painter)

        self._draw_lines(painter)
        painter.end()

    def add_menu_bar(self) -> None:
        if not (exit_menu := self.menu_bar.addMenu("File")):
            raise ValueError("Menu creation has failed")

        conway_action = QAction("Conway Life Game", self)
        cf = partial(
            self.set_automaton, ConwayLifeOutflow(NUM_OF_CELLS_X, NUM_OF_CELLS_Y)
        )
        conway_action.triggered.connect(cf)
        exit_menu.addAction(conway_action)

        sand_action = QAction("Sand", self)
        sf = partial(self.set_automaton, Sand(NUM_OF_CELLS_X, NUM_OF_CELLS_Y))
        sand_action.triggered.connect(sf)
        exit_menu.addAction(sand_action)

        def _on_close() -> None:
            self.close()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(_on_close)
        exit_menu.addAction(exit_action)

    def set_automaton(self, cellular_automaton: CellularAutomatonBaseClass) -> None:
        self.cellular_automaton = cellular_automaton
        self.num_of_cells_x = self.cellular_automaton.size_x
        self.num_of_cells_y = self.cellular_automaton.size_y
        self.repaint()

    def set_speed_value(self) -> None:
        """Set speed value from slider"""
        self.speed = self.slider.value()
        if self.run:
            self.timer.stop()
            self.timer.start(self.speed)

    def stop_simulation(self) -> None:
        self.run = False
        self.start_btn.setToolTip("Start")
        self.start_btn.setText("Start simulation")
        self.timer.stop()

    def toggle(self) -> None:
        """Start/Stop simulation"""
        if self.run:
            self.stop_simulation()
            return
        self.run = True
        self.start_btn.setToolTip("End simulation")
        self.start_btn.setText("End")
        self.timer.start(self.speed)

    def clean(self) -> None:
        self.stop_simulation()
        self.cellular_automaton.clean()
        self.repaint()

    def paint_update(self) -> None:
        self.cellular_automaton.update_table()
        self.repaint()

    def paint_cell(
        self,
        i: int,
        j: int,
        color: str,
        painter: QtGui.QPainter,
    ) -> None:
        i_paint_cord = i * self.cell_size + self.margin_left
        j_paint_cord = j * self.cell_size + self.margin_top
        painter.fillRect(
            i_paint_cord,
            j_paint_cord,
            self.cell_size,
            self.cell_size,
            QtGui.QBrush(QtGui.QColor(color)),
        )

    def _convert_coordinates(self, x: int, y: int) -> tuple[int, int]:
        return (
            (x - self.margin_left) // self.cell_size,
            (y - self.margin_top) // self.cell_size,
        )

    def _update_cell(self, x: int, y: int) -> None:
        if 0 <= x < self.num_of_cells_x and 0 <= y < self.num_of_cells_y:
            self.cellular_automaton.update_cell(x, y)
            self.repaint()

    def _draw_lines(
        self,
        painter: QtGui.QPainter,
        line_width: int = 1,
        line_color: Qt.GlobalColor | QtGui.QColor = Qt.GlobalColor.gray,
        line_style: Qt.PenStyle = Qt.PenStyle.SolidLine,
    ) -> None:
        painter.setPen(QtGui.QPen(QtGui.QBrush(line_color), 1, line_style))

        start_x, start_y = self.margin_left, self.margin_top
        stop_x = self.num_of_cells_x * self.cell_size + start_x
        stop_y = self.num_of_cells_y * self.cell_size + start_y

        for i in range(start_y, stop_y + self.cell_size, self.cell_size):
            painter.drawLine(start_x, i, stop_x, i)

        for i in range(start_x, stop_x + self.cell_size, self.cell_size):
            painter.drawLine(i, start_y, i, stop_y)


@click.command()
@click.argument(
    "automaton_type", type=click.Choice(list(AutomatonType)), default=AutomatonType.LIFE
)
def main(automaton_type: AutomatonType) -> None:
    app = QApplication(sys.argv)

    automaton_cls = {AutomatonType.LIFE: ConwayLifeOutflow, AutomatonType.SAND: Sand}[
        automaton_type
    ]

    automaton = automaton_cls(NUM_OF_CELLS_X, NUM_OF_CELLS_Y)

    automaton_qt = CellularAutomatonQt(automaton)
    automaton_qt.show()
    sys.exit(app.exec_())
