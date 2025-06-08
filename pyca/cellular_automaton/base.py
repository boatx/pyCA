from abc import ABC, abstractmethod
from typing import Generic, NamedTuple, TypeVar

from pyca.matrix import Matrix

T = TypeVar("T", bound=int)


class CellVisibilityState(NamedTuple):
    visible: bool = False
    color: str = ""


class BaseCellularAutomaton(ABC, Generic[T]):
    STATES_COLORS: dict[T, str]
    table: Matrix[T]

    def __init__(
        self,
        size_x: int,
        size_y: int,
        total_size_x: int,
        total_size_y: int,
        start_x: int = 0,
        start_y: int = 0,
    ):
        self.size_x = size_x
        self.size_y = size_y

        self._start_x = start_x
        self._start_y = start_y

        self.total_size_x = total_size_x
        self.total_size_y = total_size_y

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
