from abc import ABC, abstractmethod
from itertools import product

from pyca.matrix import Matrix


class CellularAutomatonBaseClass(ABC):
    def __init__(
        self,
        size_x,
        size_y,
        total_size_x,
        total_size_y,
        states,
        states_colors=None,
        start_x=0,
        start_y=0,
    ):

        self.size_x = size_x
        self.size_y = size_y

        self._start_x = start_x
        self._start_y = start_y

        self.total_size_x = total_size_x
        self.total_size_y = total_size_y

        self.table = None
        self.states = states
        self.states_colors = states_colors

    @abstractmethod
    def check_cell(self, x, y):
        """
        Check value of cell (x,y).
        :param int x: x coordinate of cell
        :param int y: y coordinate of cell
        """

    @abstractmethod
    def update_cell(self, x, y, state=None):
        """
        Update state of cell x,y.
        :param int x: x coordinate of cell
        :param int y: y coordinate of cell
        :param state: state of cell
        """

    @abstractmethod
    def update_table(self):
        """
        Update values of cell table
        """

    def clean(self):
        """
        Clean cell table.
        """
        self.table = Matrix.generate_matrix(self.total_size_x, self.total_size_y)


class ConwayLifeOutflow(CellularAutomatonBaseClass):

    DEAD_CELL = "DeadCell"
    LIVE_CELL = "LiveCell"
    STATES = {DEAD_CELL: 0, LIVE_CELL: 1}
    STATES_COLORS = {DEAD_CELL: "white", LIVE_CELL: "blue"}

    def __init__(self, num_of_cells_x, num_of_cells_y):
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

        self.table = Matrix.generate_random_matrix(
            self.total_size_x, self.total_size_y, list(self.states.values())
        )

    def get_neighborhood(self, x, y):
        """
        Return Moore neighborhood of cell x, y.

        :param int x: cell coordinate
        :param int y: cell coordinate
        :rtype: list
        """
        assert self.table
        return [row[y - 1 : y + 2] for row in self.table[x - 1 : x + 2]]

    def _count_cells_in_neighborhood(self, x, y):
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

    def update_table(self):
        tmp = self.table.copy()
        for i, j in product(range(1, self.size_y + 1), range(1, self.size_x + 1)):

            counter = self._count_cells_in_neighborhood(i, j)

            if self.table[i][j]:
                if counter < 2 or counter > 3:
                    tmp[i][j] = 0
            else:
                if counter == 3:
                    tmp[i][j] = 1

        self.table = tmp
        return tmp

    def check_cell(self, x, y):
        x += self._start_x
        y += self._start_y

        if self.table[x][y] == self.states[self.LIVE_CELL]:
            return True, self.states_colors[self.LIVE_CELL]
        else:
            return False, None

    def update_cell(self, x, y, state=None):
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

    def __init__(self, num_of_cells_x, num_of_cells_y, outflow=True):
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
        self.table = Matrix.generate_matrix(self.total_size_x, self.total_size_y, 0)
        self.outflow = outflow
        self._add_borders()

    def _add_borders(self):
        """
        Add 'Solid' border to cell table
        """
        for i in range(self.total_size_x):
            self.table[0][i] = 2
            self.table[-3][i] = 2

        for i in range(self.total_size_y):
            self.table[i][0] = 2
            self.table[i][-3] = 2

    def update_table(self):
        for x, y in product(range(self.size_x, -1, -1), range(self.size_y, -1, -1)):
            if self.table[x][y] == 1:
                out = x in (self.size_y, 0) or y in (self.size_x, 0)

                if self.outflow and out:
                    self.table[x][y] = 0
                else:
                    self._move_sand(x, y)

    def _move_sand(self, x, y):
        if self.table[x + 1][y] == 0:
            self.table[x][y] = 0
            self.table[x + 1][y] = 1
        elif self.table[x + 1][y + 1] == 0 and self.table[x][y + 1] != 2:
            self.table[x][y] = 0
            self.table[x + 1][y + 1] = 1
        elif self.table[x + 1][y - 1] == 0 and self.table[x][y - 1] == 0:
            self.table[x][y] = 0
            self.table[x + 1][y - 1] = 1

    def check_cell(self, x, y):
        if self.table[x][y] == self.states[self.SAND]:
            return True, self.states_colors[self.SAND]
        elif self.table[x][y] == self.states[self.SOLID]:
            return True, self.states_colors[self.SOLID]
        else:
            return False, None

    def update_cell(self, x, y, state=None):
        if self.table[y][x] != self.states[self.SOLID]:
            if self.table[y][x] == self.states[self.SAND]:
                self.table[y][x] = self.states[self.EMPTY]
            else:
                self.table[y][x] = self.states[self.SAND]
