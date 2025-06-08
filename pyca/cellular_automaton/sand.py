from enum import IntEnum
from itertools import product

from pyca.cellular_automaton.base import BaseCellularAutomaton, CellVisibilityState
from pyca.matrix import Matrix


class SandState(IntEnum):
    EMPTY = 0
    SAND = 1
    SOLID = 2


class Sand(BaseCellularAutomaton[SandState]):
    STATES_COLORS = {
        SandState.EMPTY: "white",
        SandState.SAND: "blue",
        SandState.SOLID: "black",
    }

    def __init__(
        self,
        num_of_cells_x: int,
        num_of_cells_y: int,
        outflow: bool = True,
    ):
        super().__init__(
            num_of_cells_x,
            num_of_cells_y,
            num_of_cells_x + 2,
            num_of_cells_y + 2,
            start_x=1,
            start_y=1,
        )
        self.outflow = outflow

    def init_table(self) -> Matrix:
        """
        Create empty table with 'SOLID' borders
        """
        table = Matrix.generate_matrix(
            self.total_size_x, self.total_size_y, SandState.EMPTY
        )
        for i in range(self.total_size_x):
            table[0][i] = SandState.SOLID
            table[-3][i] = SandState.SOLID

        for i in range(self.total_size_y):
            table[i][0] = SandState.SOLID
            table[i][-3] = SandState.SOLID
        return table

    def update_table(self) -> Matrix:
        for x, y in product(range(self.size_x, -1, -1), range(self.size_y, -1, -1)):
            if self.table[x][y] == SandState.SAND:
                is_out = x in (self.size_y, 0) or y in (self.size_x, 0)

                if self.outflow and is_out:
                    self.table[x][y] = SandState.EMPTY
                else:
                    self._move_sand(x, y)
        return self.table

    def _move_sand(self, x: int, y: int) -> None:
        if self.table[x + 1][y] == SandState.EMPTY:
            self.table[x][y] = SandState.EMPTY
            self.table[x + 1][y] = SandState.SAND
        elif (
            self.table[x + 1][y + 1] == SandState.EMPTY
            and self.table[x][y + 1] != SandState.SOLID
        ):
            self.table[x][y] = SandState.EMPTY
            self.table[x + 1][y + 1] = SandState.SAND
        elif (
            self.table[x + 1][y - 1] == SandState.EMPTY
            and self.table[x][y - 1] == SandState.EMPTY
        ):
            self.table[x][y] = SandState.EMPTY
            self.table[x + 1][y - 1] = SandState.SAND

    def check_cell(self, x: int, y: int) -> CellVisibilityState:
        cell = self.table[x][y]
        if cell == SandState.SAND:
            return CellVisibilityState(
                visible=True, color=self.STATES_COLORS[SandState.SAND]
            )

        if cell == SandState.SOLID:
            return CellVisibilityState(
                visible=True, color=self.STATES_COLORS[SandState.SOLID]
            )

        return CellVisibilityState()

    def update_cell(self, x: int, y: int) -> None:
        cell_value = self.table[y][x]

        if cell_value == SandState.SOLID:
            return

        self.table[y][x] = (
            SandState.EMPTY if cell_value == SandState.SAND else SandState.SAND
        )
