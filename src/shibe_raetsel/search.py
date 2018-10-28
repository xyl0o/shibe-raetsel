from shibe_raetsel import heuristics as heur
from timeit import default_timer as timer
import cProfile
from queue import Queue, PriorityQueue  # ,LifoQueue
import time


# highly used function!
#
# for a element give coords (in state)
def getStatePosition(state, dim, element):
    index = state.index(element)
    return divmod(index, dim[0])


# ######################## Additional functions for search

# highly used function!
#
# for a given state give possible next states
def getNeighborStates(state, dim):
    izero = state.index(0)
    izero_fdiv, izero_mod = divmod(izero, dim[0])

    # left:
    iswap = izero - 1
    if izero_fdiv == iswap // dim[0]:
        left = list(state)
        left[izero] = left[iswap]
        left[iswap] = 0
        left = tuple(left)
    else:
        left = None

    # up:
    iswap = izero + dim[0]
    if iswap < dim[0] * dim[1] and izero_mod == iswap % dim[0]:
        up = list(state)
        up[izero] = up[iswap]
        up[iswap] = 0
        up = tuple(up)
    else:
        up = None

    # down:
    iswap = izero - dim[0]
    if iswap >= 0 and izero_mod == iswap % dim[0]:
        down = list(state)
        down[izero] = down[iswap]
        down[iswap] = 0
        down = tuple(down)
    else:
        down = None

    # right:
    iswap = izero + 1
    if izero_fdiv == iswap // dim[0]:
        right = list(state)
        right[izero] = right[iswap]
        right[iswap] = 0
        right = tuple(right)
    else:
        right = None

    return left, up, down, right


# Do a search without ID
def genericSearch(start_pos, end_state, puzzle, _heurf=lambda p, d: 0,
                  frontierclass=Queue, _debug=False):
    visited = set()
    frontier = frontierclass()

    heuristic_calls = 0
    max_frontier = 0

    item = (_heurf(('', 0, start_pos), puzzle.dim), 1, (' ', start_pos))
    frontier.put(item)

    while not frontier.empty():
        max_frontier = max(frontier.qsize(), max_frontier)

        hcost, plen, path = frontier.get()
        oldhcost = hcost - plen
        plen += 1

        head = path[-1]

        if str(head) in visited:
            continue

        visited.add(str(head))

        if head == end_state:
            return (path[0][1:], start_pos)

        l, u, d, r = getNeighborStates(head, puzzle.dim)

        if l is not None and path[0][-1] != '3' and str(l) not in visited:
            new_path = (path[0] + '0', l)
            frontier.put((
                _heurf(new_path, puzzle.dim, _oldheur=oldhcost) + plen,
                plen, new_path))
            heuristic_calls += 1

        if u is not None and path[0][-1] != '2' and str(u) not in visited:
            new_path = (path[0] + '1', u)
            frontier.put((
                _heurf(new_path, puzzle.dim, _oldheur=oldhcost) + plen,
                plen, new_path))
            heuristic_calls += 1

        if d is not None and path[0][-1] != '1' and str(d) not in visited:
            new_path = (path[0] + '2', d)
            frontier.put((
                _heurf(new_path, puzzle.dim, _oldheur=oldhcost) + plen,
                plen, new_path))
            heuristic_calls += 1

        if r is not None and path[0][-1] != '0' and str(r) not in visited:
            new_path = (path[0] + '3', r)
            frontier.put((
                _heurf(new_path, puzzle.dim, _oldheur=oldhcost) + plen,
                plen, new_path))
            heuristic_calls += 1

        if _debug and len(visited) % 10000 == 0:
            print("----------\n" +
                  "Heur. calls:   " + str(heuristic_calls) + "\n" +
                  "Visited nodes: " + str(len(visited)) + "\n" +
                  "Max. frontier: " + str(max_frontier) + "\n" +
                  "Cur Distance:  " + str(hcost) + " | " +
                  str(hcost - plen + 1) + "h, " + str(plen - 1) + "p")


# Do a search with IDA
def idaSearch(start_pos, end_state, puzzle, heurf,
              frontierclass=Queue, _debug=False):

    # for increasing bound by 2 you need to find the right start bound
    # that is 1 the MD of the blank tile to its final position is odd, 0 else
    y, x = getStatePosition(start_pos, puzzle.dim, 0)
    dist = abs(x - puzzle.dim[0]) + abs(y - puzzle.dim[1])
    bound = (dist % 2)
    if _debug:
        tstart = timer()
        prev_elapsed = 0

    while True:
        path = idaIteration(
            ["x", start_pos], bound, end_state, heurf, puzzle, _debug)

        if path is not None:
            return [path[0][1:], start_pos]

        if _debug:
            tnow = timer()
            elapsed_time = tnow - tstart
            diff = elapsed_time - prev_elapsed
            prev_elapsed = elapsed_time
            print("Iteration " + str(bound) + " done in " + str(elapsed_time) +
                  " (cumulated)" + " add.: " + str(diff))
        bound += 2


# Used by IDA to search until a given bound
def idaIteration(path, bound, end_state, heur, puzzle, debug):

    visited = {str(path[-1])}
    visited_dict = {str(path[-1]): 0}
    frontier = [path]

    added_nodes = 0

    start = timer()
    stop = timer()
    while frontier:
        path = frontier.pop()
        moves = path[0]
        node = path[-1]
        if node == end_state:
            if debug:
                print("Visited: " + str(len(visited)))
            return path

        # moves includes start-symbol x, therefore subtract 1
        movelen = len(moves) - 1

        if debug:
            current_added = added_nodes
            print("Visited: " + str(len(visited)))

        l, u, d, r = getNeighborStates(node, puzzle.dim)

        estlen = 0
        string = ""
        if l is not None and moves[-1] != '3':
            estlen = movelen + heur([l], puzzle.dim)
            if estlen <= bound:
                string = str(l)
                if string not in visited or visited_dict[string] > estlen:
                    visited_dict[string] = estlen
                    visited.add(string)
                    frontier.append((moves + '0', l))

        if u is not None and moves[-1] != '2':
            estlen = movelen + heur([u], puzzle.dim)
            if estlen <= bound:
                string = str(u)
                if string not in visited or visited_dict[string] > estlen:
                    visited_dict[string] = estlen
                    visited.add(string)
                    frontier.append((moves + '1', u))

        if d is not None and moves[-1] != '1':
            estlen = movelen + heur([d], puzzle.dim)
            if estlen <= bound:
                string = str(d)
                if string not in visited or visited_dict[string] > estlen:
                    visited_dict[string] = estlen
                    visited.add(string)
                    frontier.append((moves + '2', d))

        if r is not None and moves[-1] != '0':
            estlen = movelen + heur([r], puzzle.dim)
            if estlen <= bound:
                string = str(r)
                if string not in visited or visited_dict[string] > estlen:
                    visited_dict[string] = estlen
                    visited.add(string)
                    frontier.append((moves + '3', r))

        if debug and current_added // 10000 != added_nodes // 10000:
            stop = timer()
            deltaSecs = (stop - start)
            start = timer()
            print("\nCurrent State: ")
            print(node)
            print("\nPath: ")
            print(moves)
            print("\nLength Path: ", movelen)
            print("Bound: ", bound)
            print("Heuristic: ", heur(path, puzzle.dim))
            print("Length+Heuristic: ", estlen)
            print("Added nodes: ", added_nodes)
            print("Closed nodes: ", len(visited))
            print("Stack Length: ", len(frontier))
            print('')
            print("Used Time: {}s".format(deltaSecs))
    return None


class Search(object):

    # Initialize with name and data structure
    def __init__(self, name, frontier=None):
        self.name = name
        self.frontier = frontier

    # Run this search
    def run(self, start, goal, dim, puzzle, _heuristic=heur.zero, _debug=False,
            _profile=False):

        print("\nSearching with " + self.name +
              "\n    Heuristic function: " + _heuristic.name +
              "\n    Debug is " + str(_debug))

        solution = ('', [])

        if _profile:
            solution = self.runProfile(start, goal, dim, _heuristic, _debug)
        else:
            heurf = _heuristic.function
            frontier = self.frontier

            tstart = timer()

            if frontier is None:  # this is an ID search
                solution = idaSearch(
                    start_pos=start, end_state=goal, heurf=heurf,
                    puzzle=puzzle, frontierclass=None, _debug=_debug)
                solution = (solution[0], solution[-1])
            else:                  # this is a normal search
                solution = genericSearch(
                    start_pos=start, end_state=goal, puzzle=puzzle,
                    _heurf=heurf, frontierclass=frontier, _debug=_debug)

            tend = timer()
            elapsed_time = tend - tstart

            print("\n" + self.name + " is complete." +
                  "\n    It took " + str(elapsed_time) + "s." +
                  "\n    Solution has " + str(len(solution[0])) + " steps.")

        return solution

    # Run search with cProfile
    def runProfile(self, start, goal, dim, heuristic, debug):
        heurf = heuristic.function
        frontier = self.frontier
        solution = ('', [])

        ref = [None]  # cProfile: need to pass a mutable object
        if frontier is None:      # this is an ID search
            cProfile.runctx('ref[0] = idaSearch(start, goal, heurf, debug)',
                            globals(), locals())
            solution = (ref[0][0], ref[0][-1])
        else:              # this is a normal search
            cProfile.runctx('ref[0] = genericSearch(start, goal, heurf,' +
                            'frontier, debug)', globals(), locals())
            solution = ref[0]

        print("\n" + self.name + " is complete." +
              "\n    Solution has " + str(len(solution[0])) + " steps.")

        return solution


class BFSSearch(Search):
    def __init__(self):
        super().__init__(name='BFS')

    def run(self, board, dim, goal):
        visited = set()
        frontier = Queue()
        frontier.put((0, (-1, ), tuple(board)))
        goal = tuple(goal)

        while not frontier.empty():
            plen, path, board = frontier.get()

            # next states: 0-l, 1-u, 2-d, 3-r
            for i, x in enumerate(getNeighborStates(board, dim)):
                if x and path[-1] != (3 - i) and x not in visited:
                    frontier.put((plen + 1, path + (i, ), x))
                    visited.add(x)
                    if x == goal:
                        return path + (i, )


class HeuristicSearch(Search):
    def __init__(self, *args, heuristic=None, **kwargs):
        super().__init__(*args, **kwargs)
        if not heuristic:
            raise TypeError(
                "__init__() missing 1 required keyword argument: 'heuristic'")
        self.heuristic = heuristic

    def run(self, *args, **kwargs):
        return super().run(*args, _heuristic=self.heuristic, **kwargs)


class AstarSearch(Search):
    def __init__(self, heuristic):
        super().__init__(
            heuristic=heuristic, name='A*', frontier=PriorityQueue)


class IDAstarSearch(Search):
    def __init__(self, heuristic):
        super().__init__(
            heuristic=heuristic, name='IDA*', frontier=None)
