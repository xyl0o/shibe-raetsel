#!/usr/bin/env python3

import random
from shibe_raetsel.search import getNeighborStates


def index_in_board(element, board, dim):
    idx = board.index(element)
    return idx % dim[0], idx // dim[0]


def board_parity(board, dim):
    inversions = 0
    for num in board:
        if num == 0:
            continue
        for other in board:
            if other == 0:
                continue

            numpos = board.index(num)
            otherpos = board.index(other)
            if (numpos < otherpos) and (other < num):
                inversions += 1

    if (dim[0] % 2) != 0:
        return int(not (inversions % 2) == 0)
    else:
        if ((dim[1] - index_in_board(0, board, dim)[1]) % 2) != 0:
            return int(not (inversions % 2) == 0)
        else:
            return int(not (inversions % 2) != 0)


class NoSolutionError(Exception):
    pass


class Puzzle(object):

    # Initialize with dimension of game
    def __init__(self, dimX, dimY, twisted=True):
        self.dim = (dimX, dimY)
        self._board = None
        self._solution = None
        self.reset()

    # Set the game to solved state
    def reset(self):
        self._board = self.initstate
        self._solution = []

    # Print the solution
    def debugsolution(self, twisted=True):
        arrows = ['→', '↑', '↓', '←']
        if twisted:
            arrows.reverse()
        print('Solution ' + ' '.join(arrows[int(e)] for e in self.solution))

    # Run heuristic
    def heuristic(self, heuristic):
        return heuristic.run(('', self.board), self.dim)

    # Update hint
    def hint(self, twisted=True):
        if self.solved or not self.solution:
            return ' '

        hints = ['→', '↑', '↓', '←']
        if twisted:
            hints.reverse()
        return hints[int(self.solution[0])]

    def step(self):
        if not self.solution:
            raise NoSolutionError()

        self.move(self.solution[0])
        self._solution = self.solution[1:]

    @property
    def initstate(self):
        return list(range(1, self.dim[0] * self.dim[1])) + [0]

    @property
    def board(self):
        return self._board[:]

    @board.setter
    def board(self, other_board):
        if not len(other_board) == len(self.board):
            raise ValueError('Cannot assign board with different size.')
        if not board_parity(other_board, self.dim) == 0:
            raise ValueError('Cannot assign unsolvable board')
        self._board = other_board

    @property
    def solution(self):
        return self._solution[:]

    # Return index of given number in game
    def index(self, element):
        return index_in_board(element, self.board, self.dim)

    # Return element at given coords
    def tile(self, x, y):
        return self.board[y * self.dim[0] + x]

    # Randomize puzzle (with a heuristic bound)
    def random(self, _bound=0, _heuristic=None):
        iter_max = 10000
        if _bound <= 0:
            iter_max = 1

        min_heur = 2147483647
        min_board = None

        for i in range(iter_max):
            random.shuffle(self._board)
            while not self.solvable:
                random.shuffle(self._board)

            heur = _heuristic.run(('', self.board), self.dim)
            if heur < min_heur:
                min_heur = heur
                min_board = self._board
                if heur < _bound:
                    break

        self._board = min_board

    @property
    def solved(self):
        return self.board == self.initstate

    @property
    def solvable(self):
        return board_parity(self.board, self.dim) == 0

    def solve(self, search, debug=False):
        self.solution = search.run(
            init=self.board,
            goal=self.initstate,
            dim=self.dim)

    def move(self, direction, twisted=True):
        if twisted:
            direction = [0, 1, 2, 3][::-1][direction]

        new = list(getNeighborStates(self.board, self.dim))[direction]

        if new:
            self.board = new
            if self.solution and direction == self.solution[0]:
                self._solution = self.solution[1:]
        else:
            raise ValueError(f'Move in direction {direction} not possible')
