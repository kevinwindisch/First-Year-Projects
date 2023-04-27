"""
implementation of the game 'Mines' in N dimensions
utilizes recursion to design algorithms
"""

import typing
import doctest



def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f"{key}:")
            for inner in val:
                print(f"    {inner}")
        else:
            print(f"{key}:", val)


# Helper functions


def get_value(board, coordinates):
    """
    gets value of coordinates in a board
    """
    value = board[coordinates[0]]
    if len(coordinates) > 1:
        value = board[coordinates[0]]
        for coordinate in coordinates[1:]:
            value = value[coordinate]
    return value


def set_value(board, coordinates, value):
    """
    sets value of coordinates in a board
    """
    if len(coordinates) == 1:
        board[coordinates[0]] = value
    else:
        key = board[coordinates[0]]
        for coordinate in coordinates[1:-1]:
            key = key[coordinate]
        key[coordinates[-1]] = value


def get_state(game, coordinates):
    """
    checks if game is over, returns state
    """
    if get_value(game["board"], coordinates) == ".":
        return "defeat"

    bombs = 0
    hidden_tiles = 0
    for coordinate in get_possible_coordinates(game["dimensions"]):
        item = get_value(game["board"], coordinate)
        hidden = get_value(game["hidden"], coordinate)
        if item == ".":
            bombs += 1
        if hidden:
            hidden_tiles += 1
    if bombs == hidden_tiles:
        return "victory"
    return "ongoing"


def get_neighbors(dimensions, coordinates):
    """
    gets all the neighbors of coordinates given a game
    """
    neighbors = set()
    for shift in (-1, 0, 1):
        new_value = coordinates[0] + shift
        if len(coordinates) == 1:
            if 0 <= new_value < dimensions[0]:
                neighbors.add((new_value,))
        else:
            new_neighbors = get_neighbors(dimensions[1:], coordinates[1:])
            for neighbor in new_neighbors:
                new_coordinate = (new_value,) + neighbor
                neighbors.add(new_coordinate)
                for index, value in enumerate(new_coordinate):
                    if not 0 <= value < dimensions[index]:
                        neighbors.discard(new_coordinate)
    return neighbors


def get_every_0_neighbor(game, coordinates):
    """
    gets every neighbor for a clump of 0 tiles
    """
    every_neighbor = {coordinates}
    visited = {coordinates}
    agenda = [coordinates]
    while agenda:
        value = agenda.pop()
        for neighbor in get_neighbors(game["dimensions"], value):
            if neighbor not in visited:
                every_neighbor.add(neighbor)
                visited.add(neighbor)
                if get_value(game["board"], neighbor) == 0:
                    agenda.append(neighbor)

    return every_neighbor


def get_possible_coordinates(dimensions):
    """
    gets all the possible coordinates of a game
    """
    coordinates = set()
    if len(dimensions) == 1:
        for value in range(dimensions[0]):
            coordinates.add((value,))
    else:
        for value in range(dimensions[0]):
            for coordinate in get_possible_coordinates(dimensions[1:]):
                coordinates.add((value,) + coordinate)
    return coordinates


def make_array(dimensions, value):
    """
    makes an array of one value given dimensions
    """
    if len(dimensions) == 1:
        return [value] * dimensions[0]
    else:
        array = []
        for _ in range(dimensions[0]):
            array.append(make_array(dimensions[1:], value))
        return array


# 2-D IMPLEMENTATION


def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'hidden' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    hidden:
        [True, True, True, True]
        [True, True, True, True]
    state: ongoing
    """
    return new_game_nd((num_rows, num_cols), bombs)


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['hidden'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is revealed on the board after digging (i.e. game['hidden'][bomb_location]
    == False), 'victory' when all safe squares (squares that do not contain a
    bomb) and no bombs are revealed, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden': [[True, False, True, True],
    ...                  [True, True, True, True]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    hidden:
        [True, False, False, False]
        [True, True, False, False]
    state: victory

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden': [[True, False, True, True],
    ...                  [True, True, True, True]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    hidden:
        [False, False, True, True]
        [True, True, True, True]
    state: defeat
    """
    return dig_nd(game, (row, col))


def render_2d_locations(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  game['hidden'] indicates which squares should be hidden.  If
    xray is True (the default is False), game['hidden'] is ignored and all
    cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the that are not
                    game['hidden']

    Returns:
       A 2D array (list of lists)

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden':  [[True, False, False, True],
    ...                   [True, True, False, True]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden':  [[True, False, True, False],
    ...                   [True, True, True, False]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    return render_nd(game, xray)


def render_2d_board(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['hidden']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'hidden':  [[False, False, False, True],
    ...                            [True, True, False, True]]})
    '.31_\\n__1_'
    """
    board = ""
    locations = render_2d_locations(game, xray)
    for row_i, row in enumerate(locations):
        new_row = "".join(row)
        if row_i != len(locations) - 1:
            new_row += "\n"
        board += new_row
    return board


# N-D IMPLEMENTATION


def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'hidden' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of tuples, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, True], [True, True], [True, True], [True, True]]
        [[True, True], [True, True], [True, True], [True, True]]
    state: ongoing
    """

    board = make_array(dimensions, 0)

    for bomb in bombs:
        set_value(board, bomb, ".")
        for neighbor in get_neighbors(dimensions, bomb):
            value = get_value(board, neighbor)
            if isinstance(value, int):
                set_value(board, neighbor, value + 1)

    return {
        "dimensions": dimensions,
        "board": board,
        "hidden": make_array(dimensions, True),
        "state": "ongoing",
    }


def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the hidden to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is revealed on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are revealed, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [True, True],
    ...                [True, True]],
    ...               [[True, True], [True, True], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, True], [True, False], [False, False], [False, False]]
        [[True, True], [True, True], [False, False], [False, False]]
    state: ongoing
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [True, True],
    ...                [True, True]],
    ...               [[True, True], [True, True], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, False], [True, False], [True, True], [True, True]]
        [[True, True], [True, True], [True, True], [True, True]]
    state: defeat
    """

    if not get_value(game["hidden"], coordinates):
        return 0

    set_value(game["hidden"], coordinates, False)

    game["state"] = get_state(game, coordinates)

    if get_value(game["board"], coordinates) != 0:
        return 1
    else:
        revealed = 1
        for neighbor in get_every_0_neighbor(game, coordinates):
            if get_value(game["hidden"], neighbor):
                set_value(game["hidden"], neighbor, False)
                revealed += 1

    game["state"] = get_state(game, coordinates)

    return revealed


def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  The game['hidden'] array indicates which squares should be
    hidden.  If xray is True (the default is False), the game['hidden'] array
    is ignored and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['hidden']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [False, False],
    ...                [False, False]],
    ...               [[True, True], [True, True], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """

    def render_row(row, hidden_row, xray=False):
        rendered_row = []
        if isinstance(row[0], (int, str)):
            for value, hidden in zip(row, hidden_row):
                if not xray and hidden:
                    rendered_row.append("_")
                elif value == 0:
                    rendered_row.append(" ")
                else:
                    rendered_row.append(str(value))
        else:
            for next_row, next_hidden_row in zip(row, hidden_row):
                rendered_row.append(render_row(next_row, next_hidden_row, xray))
        return rendered_row

    rendered_board = []
    for row, hidden_row in zip(game["board"], game["hidden"]):
        rendered_board.append(render_row(row, hidden_row, xray))

    return rendered_board


# testing

if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    # doctest.run_docstring_examples(
    #    render_2d_locations,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )
