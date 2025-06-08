from enum import IntEnum
from itertools import product

from pyca.cellular_automaton.base import BaseCellularAutomaton, CellVisibilityState
from pyca.matrix import Matrix


class ConwayLifeState(IntEnum):
    DEAD_CELL = 0
    LIVE_CELL = 1


class ConwayLifeOutflow(BaseCellularAutomaton[ConwayLifeState]):
    STATES_COLORS = {
        ConwayLifeState.DEAD_CELL: "white",
        ConwayLifeState.LIVE_CELL: "blue",
    }
    DYING_CELL_LOW_RANGE = 2
    DYING_CELL_UPPER_RANGE = 3
    NEW_LIVING_CELL_CONDITION = 3

    def __init__(self, num_of_cells_x: int, num_of_cells_y: int):
        super().__init__(
            num_of_cells_x,
            num_of_cells_y,
            num_of_cells_x + 2,
            num_of_cells_y + 2,
            start_x=1,
            start_y=1,
        )

    def init_table(self) -> Matrix:
        """
        Generate random matrix with borders 0 value

        Borders of matrix are not updated, make sure that all borders
        of random matrix have value 0. Otherwise cells adjacent to
        borders will behave randomly (depending on value of invisible
        cell).
        """
        table = Matrix.generate_random_matrix(
            self.total_size_x, self.total_size_y, list(ConwayLifeState)
        )
        for x in range(self.total_size_x):
            table[0][x] = 0
            table[self.total_size_y - 1][x] = 0

        for y in range(1, self.total_size_y - 1):
            table[y][0] = 0
            table[y][self.total_size_x - 1] = 0

        return table

    def get_neighborhood(self, x: int, y: int) -> list[list[ConwayLifeState]]:
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
                    tmp[i][j] = ConwayLifeState.DEAD_CELL
            elif counter == self.NEW_LIVING_CELL_CONDITION:
                tmp[i][j] = ConwayLifeState.LIVE_CELL

        self.table = tmp
        return tmp

    def check_cell(self, x: int, y: int) -> CellVisibilityState:
        x += self._start_x
        y += self._start_y

        if self.table[x][y] == ConwayLifeState.LIVE_CELL:
            return CellVisibilityState(
                visible=True,
                color=self.STATES_COLORS[ConwayLifeState.LIVE_CELL],
            )

        return CellVisibilityState()

    def update_cell(self, x: int, y: int) -> None:
        x += self._start_x
        y += self._start_y

        if self.table[y][x] == ConwayLifeState.LIVE_CELL:
            self.table[y][x] = ConwayLifeState.DEAD_CELL
        else:
            self.table[y][x] = ConwayLifeState.LIVE_CELL
