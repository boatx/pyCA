from __future__ import annotations

import random
from collections import UserList
from typing import List, TypeVar

T = TypeVar("T")


class Matrix(UserList[list[T]]):
    def copy(self) -> Matrix:
        return Matrix([list(i) for i in self.data])

    @classmethod
    def generate_matrix(cls, size_x: int, size_y: int, value: int = 0) -> Matrix:
        """
        Generate table of size size_x size_y and set values to value.

        :param int x_len: length of first dimension of table
        :param int y_len: length of second dimension of table
        :param values:
        """
        return cls([[value for _ in range(size_x)] for _ in range(size_y)])

    @classmethod
    def generate_random_matrix(
        cls, size_x: int, size_y: int, values: List[int]
    ) -> Matrix:
        """
        Generate table of size size_x size_y with random values.

        :param int size_x: length of first dimension of table
        :param int size_y: length of second dimension of table
        :param list values: list of values to set randomly
        """
        return cls(
            [[random.choice(values) for _ in range(size_x)] for _ in range(size_y)],
        )
