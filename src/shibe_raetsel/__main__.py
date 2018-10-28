#!/usr/bin/env python3

import sys
import math
import pyglet  # INSTALL
import pyglet.gl
from pyglet.window import key

from shibe_raetsel import heuristics as heur
from shibe_raetsel.puzzle import Puzzle
from shibe_raetsel.search import a_star, bfs, ida_star

from functools import partial


# will be initialized elsewhere
searches = []
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
    global puzzle, searches, heuristics, curHeur, keys

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
            sys.exit(1)
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

    searches = [a_star, bfs, ida_star]

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
