#!/usr/bin/env python3

from __future__ import annotations

from typing import Tuple, Callable


class Heuristic(object):

    # Initialize with name and function
    def __init__(self, name: str, function: Callable) -> None:
        self.name = name
        self.function = function
        return None

    # Calc heuristic cost
    def run(self, state: Tuple[Tuple[int], Tuple[int]],
            dim: Tuple[int]) -> int:
        return self.function(state, dim)


zero = Heuristic("Zero", lambda p, d: 0)


# highly used function!
#
# for a given path, calc the heuristic costs
# heuristic function: Toorac = tiles out of row and column
def hCostToorac(path: Tuple[Tuple[int], Tuple[int]],
                dim: Tuple[int], _oldheur: int = 0) -> int:
    state = path[-1]
    cost = 0
    for row in range(dim[1]):
        for col in range(dim[0]):
            num = state[row * dim[0] + col]
            if num is 0:
                continue
            should_row, should_col = divmod((num - 1), dim[0])
            if row != should_row:
                cost += 1
            if col != should_col:
                cost += 1
    return cost


toorac = Heuristic('Tiles Out Of Row And Column', hCostToorac)


# highly used function!
#
# for a given path, calc the heuristic costs
# heuristic funktion: Mpt = Misplaced Tiles
def hCostMpt(path: Tuple[Tuple[int], Tuple[int]],
             dim: Tuple[int], _oldheur: int = 0) -> int:
    state = path[-1]
    cost = 0
    for i, num in enumerate(state):
        exp = i + 1
        if exp != num and exp != 16:
            cost += 1
    return cost


misplaced_tiles = Heuristic('Misplaced Tiles', hCostMpt)


# highly used function!
#
# for a given path, calc the heuristic costs
# heuristic funktion: Manhattan Distance
def hCostManhattan(path: Tuple[Tuple[int], Tuple[int]],
                   dim: Tuple[int], _oldheur: int = 0) -> int:
    state = path[-1]
    if _oldheur == 0 or len(path[0]) == 0:
        cost = 0
        for row in range(dim[1]):
            for col in range(dim[0]):
                num = state[row * dim[0] + col]
                if num is 0:
                    continue
                should_row, should_col = divmod(num - 1, dim[0])

                if should_row > row:
                    cost += should_row - row
                else:
                    cost += row - should_row

                if should_col > col:
                    cost += should_col - col
                else:
                    cost += col - should_col
        return cost
    lastmove = int(path[0][-1])
    izero = state.index(0)

    swap_was_row, swap_was_col = divmod(izero, dim[0])
    swap_is_row = swap_was_row
    swap_is_col = swap_was_col

    if lastmove == 0:  # left
        iswap = izero + 1
        swap_is_col += 1

    elif lastmove == 1:  # up
        iswap = izero - dim[0]
        swap_is_row -= 1

    elif lastmove == 2:  # down
        iswap = izero + dim[0]
        swap_is_row += 1

    elif lastmove == 3:  # right
        iswap = izero - 1
        swap_is_col -= 1

    swap = state[iswap]

    swap_should_row, swap_should_col = divmod(swap - 1, dim[0])

    swap_was_impact = abs(swap_should_row - swap_was_row) +\
        abs(swap_should_col - swap_was_col)
    swap_is_impact = abs(swap_should_row - swap_is_row) +\
        abs(swap_should_col - swap_is_col)

    cost = _oldheur - swap_was_impact + swap_is_impact
    return cost


manhattan = Heuristic('Manhattan Distance', hCostManhattan)


# highly used function!
#
# for a given path, calc the heuristic costs
# heuristic funktion: LC = Linear Conflicts
def hCostLinearConflict(path: Tuple[Tuple[int], Tuple[int]],
                        dim: Tuple[int], _oldheur: int = 0) -> int:
    state = path[-1]
    cost = 0

    for row in range(dim[1]):
        rowtimesdimzero = row * dim[0]
        for col in range(dim[0]):
            index = rowtimesdimzero + col
            num = state[index]
            if num == 0:
                continue
            should_row, should_col = divmod(num - 1, dim[0])
            if should_col == col:  # col num should
                for i in range(row):
                    pre = state[index - (i + 1) * dim[0]]
                    if pre < num:
                        continue  # pre != 0 is checked implicitly
                    if (pre - 1) % dim[0] != col:
                        continue  # col pre should
                    cost += 2

            if should_row == row:  # row num should
                for x in range(rowtimesdimzero, index):
                    pre = state[x]
                    if pre < num:
                        continue  # pre != 0 is checked implicitly
                    if (pre - 1) // dim[0] != row:
                        continue  # row pre should
                    cost += 2

            if should_row > row:
                cost += should_row - row
            else:
                cost += row - should_row

            if should_col > col:
                cost += should_col - col
            else:
                cost += col - should_col
    return cost


linear_conflict = Heuristic('Linear Conflict', hCostLinearConflict)


# highly used function!
#
# for a given path, calc the heuristic costs
# Just for fun, calc LC times 3
def hCostLC3x(path: Tuple[Tuple[int], Tuple[int]],
              dim: Tuple[int], _oldheur: int = 0) -> int:
    return hCostLinearConflict(path, dim) * 3


linear_conflict_3x = Heuristic('Linear Conflict (x3)', hCostLC3x)


# highly used function!
#
# for a given path, calc the heuristic costs
# Just for fun, calc LC times 2
def hCostLC2x(path: Tuple[Tuple[int], Tuple[int]],
              dim: Tuple[int], _oldheur: int = 0) -> int:
    return hCostLinearConflict(path, dim) * 2


linear_conflict_2x = Heuristic('Linear Conflict (x2)', hCostLC2x)


# highly used function!
#
# for a given path, calc the heuristic costs
# Just for fun, calc LC times 1.5
def hCostLC1_5x(path: Tuple[Tuple[int], Tuple[int]],
                dim: Tuple[int], _oldheur: int = 0) -> int:
    return int(hCostLinearConflict(path, dim) * 1.5)


linear_conflict_1_5x = Heuristic('Linear Conflict (x1.5)', hCostLC1_5x)


# highly used function!
#
# for a given path, calc the heuristic costs
# Just for fun, calc LC times 1.1
def hCostLC1_1x(path: Tuple[Tuple[int], Tuple[int]],
                dim: Tuple[int], _oldheur: int = 0) -> int:
    return int(hCostLinearConflict(path, dim) * 1.1)


linear_conflict_1_1x = Heuristic('Linear Conflict (x1.1)', hCostLC1_1x)
