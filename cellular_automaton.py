#-*- coding: utf-8 -*-
from __future__ import unicode_literals


class CellularAutomatonBaseClass(object):

    def __init__(self, size_x, size_y, total_size_x, total_size_y, states,
                 states_colors=None, start_x=0, start_y=0):

        self.size_x = size_x
        self.size_y = size_y

        self._start_x = start_x
        self._start_y = start_y

        self.total_size_x = total_size_x
        self.total_size_y = total_size_y

        self.table = None
        self.states = states
        self.states_colors = states_colors

    def check_cell(self, x, y):
        raise NotImplementedError

    def update_cell(self, x, y, state=None):
        raise NotImplementedError

    def update_table(self):
        raise NotImplementedError

    def clean(self):
        self.table = self._gen_matrix(self.total_size_x, self.total_size_y)

    @staticmethod
    def _gen_matrix(x, y, value=0):
        return [[value for _ in range(x)]
                for _ in range(y)]

    @staticmethod
    def _copy_matrix(matrix):
        return [list(i) for i in matrix]


class ConwayLifeOutflow(CellularAutomatonBaseClass):

    DEAD_CELL = 'DeadCell'
    LIVE_CELL = 'LiveCell'

    def __init__(self, num_of_cells_x, num_of_cells_y):
        states = {self.DEAD_CELL: 0, self.LIVE_CELL: 1}
        states_colors = {self.DEAD_CELL: 'white', self.LIVE_CELL: 'blue'}
        super(ConwayLifeOutflow, self).__init__(num_of_cells_x, num_of_cells_y,
                                                num_of_cells_x+2, num_of_cells_y+2, states,
                                                states_colors=states_colors, start_x=1, start_y=1)
        self.table = self._gen_matrix(self.total_size_x, self.total_size_y, self.states[self.DEAD_CELL])

    def update_table(self):
        tmp = self._copy_matrix(self.table)
        for j in range(1, self.size_y+1):
            for i in range(1, self.size_x+1):
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
