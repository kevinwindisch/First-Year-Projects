"""
6.1010 Spring '23 Lab 4: Snekoban Game
"""

import json
import typing

# NO ADDITIONAL IMPORTS!


direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    Turns into dictionary where the keys are the tuples representing the positon
    and the value is what is in that position. Also has extra 'dimension' key
    """
    level = {}
    for row_i, row in enumerate(
        level_description
    ):  # find all the coordinates and create key with object
        for col_i, col in enumerate(row):
            level[(row_i, col_i)] = frozenset(col)
    num_rows = len(level_description)
    num_cols = len(level_description[0])
    level["dimension"] = (num_rows, num_cols)  # add dimension key
    return level


def victory_check(game):
    """
    Given a game representation (of the form returned from new_game), return
    a Boolean: True if the given game satisfies the victory condition, and
    False otherwise.
    """
    num_targets = 0
    for position in game:
        if "target" in game[position]:
            num_targets += 1
            if "computer" not in game[position]:
                return False
    if not num_targets:  # checks if no targets
        return False
    return True


def get_new_position(coordinate, direction):
    """
    Gets new position given coordinate and direction
    """
    row, col = coordinate
    row_1, col_1 = direction_vector[direction]
    return((row + row_1, col + col_1))


def step_game(game, direction):
    """
    Given a game representation (of the form returned from new_game), return a
    new game representation (of that same form), representing the updated game
    after running one step of the game.  The user's input is given by
    direction, which is one of the following: {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    level = game.copy()
    for position in level:
        if "player" in level[position]:
            player = position
    new_player = get_new_position(player, direction)  # find new position given input
    if "wall" in level[new_player]:  # does nothing if wall
        return level
    if "computer" in level[new_player]:  # checks if computer in place
        new_position = get_new_position(new_player, direction)
        if (
            "wall" in level[new_position] or "computer" in level[new_position]
        ):  # does nothing if computer next to wall or computer
            return level
        else:
            level[new_player] = level[new_player] - {"computer"}  # moves computer
            level[new_position] = level[new_position].union({"computer"})
    level[player] = level[player] - {'player'}
    level[new_player] = level[new_player].union({"player"})
    return level


def dump_game(game):
    """
    Given a game representation (of the form returned from new_game), convert
    it back into a level description that would be a suitable input to new_game
    (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    level_description = []
    new_row = []
    num_row, num_col = game[
        "dimension"
    ]  # turns coordinates into rows and cols using dimesion
    for row in range(num_row):
        for col in range(num_col):
            new_row.append(list(game[(row, col)]))
        level_description.append(new_row.copy())
        new_row = []
    return level_description


def make_unhashable(game):
    """
    turns game into an unhashable form to store in a set
    """
    # level = dump_game(game)
    # new_level = []
    # new_row = []
    # for row in level:
    #     for item in row:
    #         new_row.append(tuple(item))  # turns all lists into tuples
    #     new_level.append(tuple(new_row))
    #     new_row = []
    # return tuple(new_level)


def solve_puzzle(game):
    """
    Given a game representation (of the form returned from new game), find a
    solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    if victory_check(game):  # checks if game is initially solved
        return []
    visited = set()
    visited.add(tuple(game.items()))  # create visited set and adds starting level
    possible_paths = [[game]]  # list of possible paths
    while possible_paths:  # continues until possible paths is empty
        path = possible_paths.pop(0)
        for direction in [
            "up",
            "down",
            "left",
            "right",
        ]:  # checks each next move from path
            previous_game = path[0] # finds info of previous game
            new_path = path + [direction]
            next_game = step_game(previous_game, direction)  # creates new situation
            if tuple(next_game.items()) not in visited:  # checks if in visited
                if victory_check(next_game):  # checks if win, returns if true
                    return new_path[1:]
                visited.add(tuple(next_game.items()))  # adds to visited
                new_path[0] = next_game
                possible_paths.append(new_path)
    return None