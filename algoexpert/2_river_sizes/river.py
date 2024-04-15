
from dataclasses import dataclass


WATER_VALUE = 1


@dataclass(frozen=True)
class Cell:
    x: int
    y: int
    value: int


#    y1 y2
# x1
# x2
Matrix = list[list[Cell]]
CellsSet = set[Cell]


def find_river_size_adj(matrix: Matrix, cell: Cell, river_cells_counted: CellsSet) -> int:

    if cell.value != WATER_VALUE or cell in river_cells_counted:
        return 0

    x = cell.x
    y = cell.y
    size = 1
    river_cells_counted.add(cell)

    # right
    if x < len(matrix[y]) - 1:
        size += find_river_size_adj(matrix, matrix[y][x + 1], river_cells_counted)

    # left:
    if x > 0:
        size += find_river_size_adj(matrix, matrix[y][x - 1], river_cells_counted)

    # up
    if y < len(matrix) - 1:
        size += find_river_size_adj(matrix, matrix[y + 1][x], river_cells_counted)

    # down
    if y > 0:
        size += find_river_size_adj(matrix, matrix[y - 1][x], river_cells_counted)

    return size


def riverSizes(input_matrix: list[list[int]]):

    matrix = [[Cell(x, y, value) for x, value in enumerate(row)] for y, row in enumerate(input_matrix)]

    river_cells_counted: CellsSet = set()
    river_sizes: list[int] = []

    for row in matrix:
        for cell in row:
            size = find_river_size_adj(matrix, cell, river_cells_counted)
            if size > 0:
                river_sizes.append(size)

    return river_sizes
