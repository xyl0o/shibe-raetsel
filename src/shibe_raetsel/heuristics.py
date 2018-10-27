
# highly used function!
#
# for a given path, calc the heuristic costs
# heuristic function: Toorac = tiles out of row and column
def hCostToorac(path, dim, _oldheur=0):
    state = path[-1]
    cost = 0
    for row in range(dim[1]):
        for col in range(dim[0]):
            num = state[row * dim[0] + col]
            if num is 0:
                continue
            should_row, should_col = divmod((num-1), dim[0])
            if row != should_row:
                cost += 1
            if col != should_col:
                cost += 1
    return cost


# highly used function!
#
# for a given path, calc the heuristic costs
# heuristic funktion: Mpt = Misplaced Tiles
def hCostMpt(path, dim, _oldheur=0):
    state = path[-1]
    cost = 0
    for i, num in enumerate(state):
        exp = i + 1
        if exp != num and exp != 16:
            cost += 1
    return cost


# highly used function!
#
# for a given path, calc the heuristic costs
# heuristic funktion: Manhattan Distance
def hCostManhattan(path, dim, _oldheur=0):
    state = path[-1]
    if _oldheur == 0 or len(path[0]) == 0:
        cost = 0
        for row in range(dim[1]):
            for col in range(dim[0]):
                num = state[row * dim[0] + col]
                if num is 0:
                    continue
                should_row, should_col = divmod(num-1, dim[0])

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

    swap_should_row, swap_should_col = divmod(swap-1, dim[0])

    swap_was_impact = abs(swap_should_row - swap_was_row) +\
        abs(swap_should_col - swap_was_col)
    swap_is_impact = abs(swap_should_row - swap_is_row) +\
        abs(swap_should_col - swap_is_col)

    cost = _oldheur - swap_was_impact + swap_is_impact
    return cost


# highly used function!
#
# for a given path, calc the heuristic costs
# heuristic funktion: LC = Linear Conflicts
def hCostLinearConflict(path, dim, _oldheur=0):
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
                    pre = state[index - (i+1) * dim[0]]
                    if pre < num:
                        continue  # pre != 0 is checked implicitly
                    if (pre-1) % dim[0] != col:
                        continue  # col pre should
                    cost += 2

            if should_row == row:  # row num should
                for x in range(rowtimesdimzero, index):
                    pre = state[x]
                    if pre < num:
                        continue  # pre != 0 is checked implicitly
                    if (pre-1) // dim[0] != row:
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


# highly used function!
#
# for a given path, calc the heuristic costs
# Just for fun, calc LC times 3
def hCostLC3x(path, dim, _oldheur=0):
    return hCostLinearConflict(path, dim) * 3


# highly used function!
#
# for a given path, calc the heuristic costs
# Just for fun, calc LC times 2
def hCostLC2x(path, dim, _oldheur=0):
    return hCostLinearConflict(path, dim) * 2


# highly used function!
#
# for a given path, calc the heuristic costs
# Just for fun, calc LC times 1.5
def hCostLC1_5x(path, dim, _oldheur=0):
    return int(hCostLinearConflict(path, dim) * 1.5)


# highly used function!
#
# for a given path, calc the heuristic costs
# Just for fun, calc LC times 1.1
def hCostLC1_1x(path, dim, _oldheur=0):
    return int(hCostLinearConflict(path, dim) * 1.1)
