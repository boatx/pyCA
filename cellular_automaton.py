# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import random
from itertools import product


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
        """
        Check value of cell (x,y).
        :param int x: x coordinate of cell
        :param int y: y coordinate of cell
        """
        raise NotImplementedError

    def update_cell(self, x, y, state=None):
        """
        Update state of cell x,y.
        :param int x: x coordinate of cell
        :param int y: y coordinate of cell
        :param state: state of cell
        """
        raise NotImplementedError

    def update_table(self):
        """
        Update values of cell table
        """
        raise NotImplementedError

    def clean(self):
        """
        Clean cell table.
        """
        self.table = self._gen_matrix(self.total_size_x, self.total_size_y)

    def von_neumann_neighborhood(self, x, y, r=1):
        """
        Return Von Neumann neighborhood of cell x, y.

        :param int x: cell coordinate
        :param int y: cell coordinate
        :rtype: list
        """
        raise NotImplementedError

    def moore_neighborhood(self, x, y):
        """
        Return Moore neighborhood of cell x, y.

        :param int x: cell coordinate
        :param int y: cell coordinate
        :rtype: list
        """
        return [row[y-1:y+2] for row in self.table[x-1:x+2]]

    @staticmethod
    def _gen_random_matrix(x_len, y_len, values):
        """
        Generate table of size x_len y_len with random values.

        :param int x_len: length of first dimension of table
        :param int y_len: length of second dimension of table
        :param list values: list of values to set randomly
        """
        random.seed()
        end = len(values) - 1
        return [[values[random.randint(0, end)] for _ in range(x_len)]
                for _ in range(y_len)]

    @staticmethod
    def _gen_matrix(x_len, y_len, value=0):
        """
        Generate table of size x_len x y_len and set values of cells to value.

        :param int x_len: length of first dimension of table
        :param int y_len: length of second dimension of table
        :param values:
        """
        return [[value for _ in range(x_len)]
                for _ in range(y_len)]

    @staticmethod
    def _copy_matrix(matrix):
        """
        Return copy of matrix.
        :param list matrix: matrix to copy
        """
        return [list(i) for i in matrix]


class ConwayLifeOutflow(CellularAutomatonBaseClass):

    DEAD_CELL = 'DeadCell'
    LIVE_CELL = 'LiveCell'

    def __init__(self, num_of_cells_x, num_of_cells_y):
        states = {self.DEAD_CELL: 0, self.LIVE_CELL: 1}
        states_colors = {self.DEAD_CELL: 'white', self.LIVE_CELL: 'blue'}
        super(ConwayLifeOutflow, self).__init__(num_of_cells_x, num_of_cells_y,
                                                num_of_cells_x+2,
                                                num_of_cells_y+2,
                                                states,
                                                states_colors=states_colors,
                                                start_x=1, start_y=1)

        self.table = self._gen_random_matrix(self.total_size_x,
                                             self.total_size_y,
                                             self.states.values())

    def _neumann_neighborhood_counter(self, x, y, r=1):
        raise NotImplementedError

    def _moore_neighborhood_counter(self, x, y):
        """
        Count neighbors of cell x,y in Moore Neighborhood.
        :param int x: x coordinate of cell
        :param int y: y coordinate of cell
        """
        counter = 0
        for row in self.moore_neighborhood(x, y):
            for item in row:
                if item:
                    counter += 1

        if self.table[x][y]:
            counter -= 1

        return counter

    def update_table(self):
        tmp = self._copy_matrix(self.table)
        for i, j in product(xrange(1, self.size_y+1),
                            xrange(1, self.size_x+1)):

            counter = self._moore_neighborhood_counter(i, j)

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

    SAND = 'Sand'
    SOLID = 'Solid'
    EMPTY = 'Empty'

    def __init__(self, num_of_cells_x, num_of_cells_y, outflow=True):
        states = {self.EMPTY: 0, self.SAND: 1, self.SOLID: 2}

        states_colors = {self.EMPTY: 'white',
                         self.SAND: 'blue',
                         self.SOLID: 'black'}

        super(Sand, self).__init__(num_of_cells_x, num_of_cells_y,
                                   num_of_cells_x+2,
                                   num_of_cells_y+2,
                                   states,
                                   states_colors=states_colors,
                                   start_x=1, start_y=1)

        self.table = self._gen_matrix(self.total_size_x,
                                      self.total_size_y,
                                      0)
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
        for x, y in product(xrange(self.size_x, -1, -1),
                            xrange(self.size_y, -1, -1)):
            if self.table[x][y] == 1:
                out = x in (self.size_y, 0) or y in (self.size_x, 0)

                if self.outflow and out:
                    self.table[x][y] = 0
                else:
                    self._move_sand(x, y)

    def _move_sand(self, x, y):
        if self.table[x+1][y] == 0:
            self.table[x][y] = 0
            self.table[x+1][y] = 1
        elif self.table[x+1][y+1] == 0 and self.table[x][x+1] != 2:
            self.table[x][y] = 0
            self.table[x+1][y+1] = 1
        elif self.table[x+1][y-1] == 0 and self.table[x][y-1] == 0:
            self.table[x][y] = 0
            self.table[x+1][y-1] = 1

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


class Langtons_Ant(CellularAutomatonBaseClass):
    BLACK_CELL = 'Black_Cell'
    WHITE_CELL = 'White_Cell'
    ANT = 'Ant'

    def __init__(self, num_of_cells_x, num_of_cells_y):
        states = {self.WHITE_CELL: 0,
                  self.BLACK_CELL: 1,
                  self.ANT: 2}

        states_colors = {self.WHITE_CELL: 'white',
                         self.BLACK_CELL: 'black',
                         self.ANT: 'red'}

        super(Langtons_Ant, self).__init__(num_of_cells_x, num_of_cells_y,
                                  num_of_cells_x,
                                  num_of_cells_y,
                                  states,
                                  states_colors=states_colors,
                                  start_x=0, start_y=0)

        self.table = self._gen_matrix(self.total_size_x,
                                      self.total_size_y,
                                      0)
        self._add_borders()

    def check_cell(self, x, y):
        if self.table[x][y] != self.states[self.WHITE_CELL]:
            return True, self.states_colors[self.table[x][y]]
        else:
            return False, None

    def update_cell(self, x, y):
        if self.table[x][y] != self.states[self.ANT]:
            self.table[x][y] = self.states[self.ANT]
        else:
            self.table[x][y] = self.states[self.WHITE_CELL]

    def update_table(self):
        raise NotImplementedError
