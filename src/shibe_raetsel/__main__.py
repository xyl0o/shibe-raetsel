#!/usr/bin/env python3

# ######################## Imports
import sys
import math
import pyglet  # INSTALL
import pyglet.gl
from pyglet.window import key
from queue import Queue, PriorityQueue  # ,LifoQueue
import random
from shibe_raetsel.search import Search, getNeighborStates


from shibe_raetsel import heuristics as heur


# ######################## Globals

# will be initialized elsewhere
searches = []
curSearch = None
heuristics = []
curHeur = None
keys = {}

# Flags
flag_debug = False
flag_profile = False
flag_hint = False

# Performance Data
heuristic_calls = 0

# ui
font_large = 32
font_small = 11
font_tile = 20

window = pyglet.window.Window(resizable=True, caption='15-Puzzle')
maxdimension = min(window.width, window.height)

try:
    bgimg = pyglet.resource.image('dodge.png')
except Exception:
    print("No dodge found")
    bgimg = None

pyglet.gl.glClearColor(0.1, 0.1, 0.1, 1)


# ######################## Puzzle logic

# Objects of class Puzzle represent a singe game
class Puzzle(object):

    # Initialize with dimension of game
    def __init__(self, dimX, dimY):
        self.dim = (dimX, dimY)

        self.initstate = list(range(self.dim[0] * self.dim[1]))[1:]
        self.initstate.append(0)

        self.twisted = True

        self.reset()

        self.solve('')

        return None

    # Toggle twisted directions
    def twistmoves(self):
        self.twisted = not self.twisted

    # Print the solution
    def debugsolution(self):
        text = "Solution"
        for element in self.solution:
            if self.twisted:
                text = text + ' ' + ['←', '↓', '↑', '→'][int(element)]
            else:
                text = text + ' ' + ['→', '↑', '↓', '←'][int(element)]
        print(text)

    # Run heuristic
    def heuristic(self, _heuristic=curHeur):
        return _heuristic.run(self.state(), self.dim)

    # Update hint
    def calchint(self):
        if not self.solved:
            if self.solution is not '':
                hints = ['→', '↑', '↓', '←']
                if puzzle.twisted:
                    hints.reverse()
                self.hint = hints[int(self.solution[0])]
            else:
                self.hint = None
        else:
            self.hint = None
        return None

    # Set the game to solved state
    def reset(self):
        self.board = self.initcopy()

        self.solved = True
        self.solvable = True
        self.solve('')

    # Provide a solution to the puzzle
    def solve(self, solution):
        if isinstance(solution, tuple):
            self.update(solution[1], _sol=solution[0])
        elif isinstance(solution, str):
            self.solution = solution
        else:
            raise(ValueError("The solution in solve() must be str or tuple"))

        self.calchint()

        return None

    # If there is a solution go one step further
    def step(self):
        if isinstance(self.solution, tuple):
            self.solution = self.solution[0]
            self.step()
        elif isinstance(self.solution, str):
            if len(self.solution) < 1:
                return None  # we are done here

            move = self.solution[0]
            rest = self.solution[1:]
            self.update(
                getNeighborStates(self.board, self.dim)[int(move)],
                _sol=rest)

        if self.solution == '':
            if not self.solved:
                print("the solution was wrong")

    # Return a copy of solved game state
    def initcopy(self):
        return self.initstate[:]

    # Return a copy of actual game state
    def boardcopy(self):
        return self.board[:]

    # Return index of given number in game
    def index(self, element):
        return (
            self.board.index(element) % self.dim[0],
            self.board.index(element) // self.dim[0])

    # Return element at given coords
    def tile(self, x, y):
        return self.board[y * self.dim[0] + x]

    # Set the game state and check for solvability
    def update(self, newfield, _paritycheck=True, _sol=''):
        self.board = newfield[:]
        if _paritycheck:
            self.checkparity()
        self.checksolved()

        self.solve(_sol)

    # Randomize puzzle (with a heuristic bound)
    def random(self, _bound=0, _heuristic=None):
        iter_max = 10000
        if _bound <= 0:
            iter_max = 1

        min_heur = 2147483647
        min_board = None

        for i in range(iter_max):
            board = self.boardcopy()
            self.solvable = False
            while not self.solvable:
                random.shuffle(board)
                self.update(board)

            heur = _heuristic.run(self.state(), self.dim)
            if heur < min_heur:
                min_heur = heur
                min_board = board
                if heur < _bound:
                    break

        self.update(min_board)

    # Is the puzzle solved?
    def checksolved(self):
        self.solved = self.board == self.initcopy()

    # Is the puzzle solvable?
    def checkparity(self):
        inversions = 0
        for num in self.board:
            if num == 0:
                continue
            for other in self.board:
                if other == 0:
                    continue

                numpos = self.board.index(num)
                otherpos = self.board.index(other)
                if (numpos < otherpos) and (other < num):
                    inversions += 1

        if (self.dim[0] % 2) != 0:
            self.solvable = (inversions % 2) == 0
        else:
            if ((self.dim[1] - self.index(0)[1]) % 2) != 0:
                self.solvable = (inversions % 2) == 0
            else:
                self.solvable = (inversions % 2) != 0

        return None

    # Swap the empty tile with neighbor
    def move(self, direction):
        neighbors = list(getNeighborStates(self.board, self.dim))

        if self.twisted:
            direction = [0, 1, 2, 3][::-1][direction]

        new = neighbors[direction]

        if new is None:
            if flag_debug:
                print("This move is not possible (" + str(direction) + ")")
            return None

        if self.solution != '' and str(direction) == self.solution[0]:
            self.update(new, _paritycheck=False, _sol=self.solution[1:])
        else:
            self.update(new, _paritycheck=False)

        return None

    # Run a search on puzzle
    def search(self, searchObject, heuristicObject,
               _debug=False, _profile=False):
        start = self.boardcopy()
        goal = self.initcopy()

        return searchObject.run(
            start=start, goal=goal, dim=self.dim, puzzle=self,
            _heuristic=heuristicObject, _debug=_debug, _profile=_profile)

    # Return a state with no solution
    def state(self):
        return '', self.boardcopy()


# ######################## GUI

@window.event
def on_resize(width, height):
    global maxdimension
    maxdimension = min(width, height)
    if bgimg is not None:
        bgimg.width = maxdimension
        bgimg.height = maxdimension


@window.event
def on_draw():
    global puzzle
    global curHeur

    # ---- Background respond to solved state
    if puzzle.solved:
        pyglet.gl.glClearColor(0.1, 0.3, 0.1, 1)
    else:
        pyglet.gl.glClearColor(0.1, 0.1, 0.1, 1)

    offsetx = (window.width - maxdimension) / 2
    offsety = (window.height - maxdimension) / 2
    window.clear()

    # ---- Use background image
    if bgimg is not None:
        bgimg.blit(offsetx, offsety)
        color = (0, 0, 0, 255)
    else:
        color = (255, 255, 255, 255)

    # ---- Draw puzzle
    for y in range(puzzle.dim[1]):
        for x in range(puzzle.dim[0]):
            tile = str(puzzle.tile(x, y))
            size = font_tile
            if tile == '0':
                size = int(size * 2)
                if flag_hint and puzzle.hint is not None:
                    tile = str(puzzle.hint)
                else:
                    tile = '⋅'

            number = pyglet.text.Label(
                tile, font_size=size, bold=True, color=color,
                x=(offsetx + (x + 1) *
                   (maxdimension / (puzzle.dim[0] + 1))),
                y=(window.height - offsety - (y + 1) *
                   (maxdimension / (puzzle.dim[1] + 1))),
                anchor_x='center', anchor_y='center')
            number.draw()

    # ---- Construct labels
    top = window.height - font_large
    labels = [("Current heuristic function: ", 10, top)]
    for h in heuristics:
        prefix = " "
        if h is curHeur:
            prefix = "*"
        y = top - len(labels) * round(1.5 * font_small)
        text = prefix + " " + str(puzzle.heuristic(h)) + ' ' + h.name
        labels.append((text, 16, y))

    right = window.width - 180
    labels.append(("Hint: " + str(flag_hint), right, top))
    labels.append(("Debug: " + str(flag_debug),
                   right, top - 1.5 * font_small))
    labels.append(("Profile: " + str(flag_profile),
                   right, top - 3 * font_small))
    labels.append(("Solution: " + str(len(puzzle.solution)) + " steps",
                   right, top - 6 * font_small))

    # ---- Draw controls
    x = line = round(1.5 * font_small)
    for char, desc, func in list(keys.values())[::-1]:
        if char is not None:
            labels.append((char + ' - ' + desc, 20, x))
            x += line
    labels.append(("Controls:", 10, x))

    font = 'Monospace'
    for text, posx, posy in labels:
        pyglet.text.Label(
            text, font_name=font, font_size=font_small,
            x=posx, y=posy, anchor_x='left', anchor_y='center').draw()


@window.event
def on_key_press(symbol, modifiers):
    if symbol in keys.keys():
        keys[symbol][2]()


def toggleHeuristic():
    global curHeur, heuristics
    new_index = (heuristics.index(curHeur) + 1) % len(heuristics)
    curHeur = heuristics[new_index]


def toggleDebug():
    global flag_debug
    flag_debug = not flag_debug


def toggleProfile():
    global flag_profile
    flag_profile = not flag_profile


def toggleHint():
    global flag_hint
    flag_hint = not flag_hint


# ######################## Main function

def main():
    global puzzle, searches, curSearch, heuristics, curHeur, keys

    if len(sys.argv) == 1:
        puzzle = Puzzle(4, 4)
    elif len(sys.argv) == 2:
        board = []
        given = sys.argv[1].replace(' ', '').split(',')
        for tile in given:
            tile = int(tile)
            if tile in board or tile < 0 or tile > len(given):
                print("Error reading input!")
                sys.exit(0)
            board.append(tile)
        if 0 not in board:
            print("Error reading input! no zero")
            sys.exit(0)
        y = int(math.sqrt(len(board)))
        while y > 0:
            if len(board) % y != 0:
                y -= 1
            else:
                break
        puzzle = Puzzle(len(board) // y, y)
        puzzle.update(board)
    else:
        print("Unable to parse given data")

    heuristics = [
        heur.misplaced_tiles, heur.toorac, heur.manhattan,
        heur.linear_conflict, heur.linear_conflict_1_1x,
        heur.linear_conflict_1_5x, heur.linear_conflict_2x,
        heur.linear_conflict_3x]
    curHeur = heuristics[0]

    searches = [Search("BFS", Queue),
                Search("A*", PriorityQueue),
                Search("IDA*", None)]
    curSearch = searches[0]

    keys = {
        key.B: ('b', "search BFS",
                lambda: puzzle.solve(
                    puzzle.search(
                        searchObject=searches[0], heuristicObject=curHeur,
                        _debug=flag_debug, _profile=flag_profile))),
        key.A: ('a', "search A*",
                lambda: puzzle.solve(
                    puzzle.search(
                        searchObject=searches[1], heuristicObject=curHeur,
                        _debug=flag_debug, _profile=flag_profile))),
        key.I: ('i', "search IDA*",
                lambda: puzzle.solve(
                    puzzle.search(
                        searchObject=searches[2], heuristicObject=curHeur,
                        _debug=flag_debug, _profile=flag_profile))),
        key.SPACE: ('␣', "step through solution", lambda: puzzle.step()),
        key.ENTER: ('↲', "reset puzzle", lambda: puzzle.reset()),
        key.E: ('e', "change heur", lambda: toggleHeuristic()),
        key.H: ('h', "toggle hint", lambda: toggleHint()),
        key.R: ('r', "random", lambda: puzzle.random(0, curHeur)),
        key.T: ('t', "random (limit)", lambda: puzzle.random(20, curHeur)),
        key.Y: ('y', "switch key directions", lambda: puzzle.twistmoves()),
        key.X: ('x', "toggle debug", lambda: toggleDebug()),
        key.C: ('c', "toggle profile", lambda: toggleProfile()),
        key.P: ('p', "print solution", lambda: puzzle.debugsolution()),
        key.LEFT: (None, "move left", lambda: puzzle.move(3)),
        key.UP: (None, "move up", lambda: puzzle.move(1)),
        key.DOWN: (None, "move down", lambda: puzzle.move(2)),
        key.RIGHT: (None, "move right", lambda: puzzle.move(0))}

    pyglet.app.run()


if __name__ == '__main__':
    main()
