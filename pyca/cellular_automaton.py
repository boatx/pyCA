from abc import ABC, abstractmethod
from itertools import product
from typing import NamedTuple

from pyca.matrix import Matrix


class CellVisibilityState(NamedTuple):
    visible: bool = False
    color: str = ""


class CellularAutomatonBaseClass(ABC):
    table: Matrix

    def __init__(
        self,
        size_x: int,
        size_y: int,
        total_size_x: int,
        total_size_y: int,
        states: dict[str, int],
        states_colors: dict[str, str],
        start_x: int = 0,
        start_y: int = 0,
    ):
        self.size_x = size_x
        self.size_y = size_y

        self._start_x = start_x
        self._start_y = start_y

        self.total_size_x = total_size_x
        self.total_size_y = total_size_y

        self.states = states
        self.states_colors = states_colors
        self.table = self.init_table()

    @abstractmethod
    def init_table(self) -> Matrix:
        """
        Initialize table
        """

    @abstractmethod
    def check_cell(self, x: int, y: int) -> CellVisibilityState:
        """
        Check value of cell (x,y).
        :param int x: x coordinate of cell
        :param int y: y coordinate of cell
        """

    @abstractmethod
    def update_cell(self, x: int, y: int) -> None:
        """
        Update state of cell x,y.
        :param int x: x coordinate of cell
        :param int y: y coordinate of cell
        :param state: state of cell
        """

    @abstractmethod
    def update_table(self) -> Matrix:
        """
        Update values of cell table
        """

    def clean(self) -> None:
        """
        Clean cell table.
        """
        self.table = Matrix.generate_matrix(self.total_size_x, self.total_size_y)


class ConwayLifeOutflow(CellularAutomatonBaseClass):
    DEAD_CELL = "DeadCell"
    LIVE_CELL = "LiveCell"
    STATES = {DEAD_CELL: 0, LIVE_CELL: 1}
    STATES_COLORS = {DEAD_CELL: "white", LIVE_CELL: "blue"}
    DYING_CELL_LOW_RANGE = 2
    DYING_CELL_UPPER_RANGE = 3
    NEW_LIVING_CELL_CONDITION = 3

    def __init__(self, num_of_cells_x: int, num_of_cells_y: int):
        super().__init__(
            num_of_cells_x,
            num_of_cells_y,
            num_of_cells_x + 2,
            num_of_cells_y + 2,
            self.STATES,
            states_colors=self.STATES_COLORS,
            start_x=1,
            start_y=1,
        )

    def init_table(self) -> Matrix:
        return self._generate_random_matrix_with_empty_borders()

    def _generate_random_matrix_with_empty_borders(self) -> Matrix:
        """
        Generate random matrix with borders 0 value

        Borders of matrix are not updated, make sure that all borders
        of random matrix have value 0. Otherwise cells adjacent to
        borders will behave randomly (depending on value of invisible
        cell).
        """
        table = Matrix.generate_random_matrix(
            self.total_size_x, self.total_size_y, list(self.states.values())
        )
        for x in range(self.total_size_x):
            table[0][x] = 0
            table[self.total_size_y - 1][x] = 0

        for y in range(1, self.total_size_y - 1):
            table[y][0] = 0
            table[y][self.total_size_x - 1] = 0

        return table

    def get_neighborhood(self, x: int, y: int) -> list[list[int]]:
        """
        Return Moore neighborhood of cell x, y.

        :param int x: cell coordinate
        :param int y: cell coordinate
        :rtype: list
        """
        return [row[y - 1 : y + 2] for row in self.table[x - 1 : x + 2]]

    def _count_cells_in_neighborhood(self, x: int, y: int) -> int:
        """
        Count neighbors of cell x,y in Moore Neighborhood.
        :param int x: x coordinate of cell
        :param int y: y coordinate of cell
        """
        counter = 0
        for row in self.get_neighborhood(x, y):
            for item in row:
                if item:
                    counter += 1

        if self.table[x][y]:
            counter -= 1

        return counter

    def update_table(self) -> Matrix:
        tmp = self.table.copy()
        for i, j in product(range(1, self.size_y + 1), range(1, self.size_x + 1)):
            counter = self._count_cells_in_neighborhood(i, j)

            if self.table[i][j]:
                if (
                    counter < self.DYING_CELL_LOW_RANGE
                    or counter > self.DYING_CELL_UPPER_RANGE
                ):
                    tmp[i][j] = self.states[self.DEAD_CELL]
            elif counter == self.NEW_LIVING_CELL_CONDITION:
                tmp[i][j] = self.states[self.LIVE_CELL]

        self.table = tmp
        return tmp

    def check_cell(self, x: int, y: int) -> CellVisibilityState:
        x += self._start_x
        y += self._start_y

        if self.table[x][y] == self.states[self.LIVE_CELL]:
            return CellVisibilityState(
                visible=True, color=self.states_colors[self.LIVE_CELL]
            )

        return CellVisibilityState()

    def update_cell(self, x: int, y: int) -> None:
        x += self._start_x
        y += self._start_y

        if self.table[y][x] == self.states[self.LIVE_CELL]:
            self.table[y][x] = self.states[self.DEAD_CELL]
        else:
            self.table[y][x] = self.states[self.LIVE_CELL]


class Sand(CellularAutomatonBaseClass):
    SAND = "Sand"
    SOLID = "Solid"
    EMPTY = "Empty"
    STATES = {EMPTY: 0, SAND: 1, SOLID: 2}
    STATES_COLORS = {EMPTY: "white", SAND: "blue", SOLID: "black"}

    def __init__(self, num_of_cells_x: int, num_of_cells_y: int, outflow: bool = True):
        super().__init__(
            num_of_cells_x,
            num_of_cells_y,
            num_of_cells_x + 2,
            num_of_cells_y + 2,
            self.STATES,
            states_colors=self.STATES_COLORS,
            start_x=1,
            start_y=1,
        )
        self.outflow = outflow
        self._add_borders()

    def init_table(self) -> Matrix:
        return Matrix.generate_matrix(self.total_size_x, self.total_size_y, 0)

    def _add_borders(self) -> None:
        """
        Add 'Solid' border to cell table
        """
        for i in range(self.total_size_x):
            self.table[0][i] = 2
            self.table[-3][i] = 2

        for i in range(self.total_size_y):
            self.table[i][0] = 2
            self.table[i][-3] = 2

    def update_table(self) -> Matrix:
        for x, y in product(range(self.size_x, -1, -1), range(self.size_y, -1, -1)):
            if self.table[x][y] == 1:
                out = x in (self.size_y, 0) or y in (self.size_x, 0)

                if self.outflow and out:
                    self.table[x][y] = 0
                else:
                    self._move_sand(x, y)
        return self.table

    def _move_sand(self, x: int, y: int) -> None:
        if self.table[x + 1][y] == 0:
            self.table[x][y] = 0
            self.table[x + 1][y] = 1
        elif self.table[x + 1][y + 1] == 0 and self.table[x][y + 1] != 2:  # noqa: PLR2004
            self.table[x][y] = 0
            self.table[x + 1][y + 1] = 1
        elif self.table[x + 1][y - 1] == 0 and self.table[x][y - 1] == 0:
            self.table[x][y] = 0
            self.table[x + 1][y - 1] = 1

    def check_cell(self, x: int, y: int) -> CellVisibilityState:
        cell = self.table[x][y]
        if cell == self.states[self.SAND]:
            return CellVisibilityState(
                visible=True, color=self.states_colors[self.SAND]
            )

        if cell == self.states[self.SOLID]:
            return CellVisibilityState(
                visible=True, color=self.states_colors[self.SOLID]
            )

        return CellVisibilityState()

    def update_cell(self, x: int, y: int):
        if self.table[y][x] != self.states[self.SOLID]:
            if self.table[y][x] == self.states[self.SAND]:
                self.table[y][x] = self.states[self.EMPTY]
            else:
                self.table[y][x] = self.states[self.SAND]
