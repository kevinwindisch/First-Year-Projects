
import sys
import typing
import doctest

sys.setrecursionlimit(10_000)

# HELPER FUNCTIONS

def simplify_formula(formula, input):
    """
    intakes a formula and simplifies it based on a given input

    removes any variables that will not affect the final output
    """
    new_formula = []
    for clause in formula:
        satisfied = False
        new_clause = []
        for literal in clause:
            if literal[0] != input[0]:
                new_clause.append(literal)
            else:
                if literal[1] == input[1]:
                    satisfied = True
                    break
        if not satisfied:
            new_formula.append(new_clause)
    return new_formula

def remove_unit_cases(formula, unit_cases):
    """
    takes in a formula and removes unit cases, manipulating the formula

    returns the values of variables that were removed.
    returns None if contradiction
    """
    output = {}
    while unit_cases:
        literal = unit_cases.pop()
        if (literal[0], not literal[1]) in unit_cases:
            return None
        while [literal] in formula:
            formula.remove([literal])
            if [] in formula:
                return None
        output = output | {literal[0]: literal[1]}
    return output

def generate_coords(dimension):
    """
    creates all possible coordinates on a board
    """
    coordinates = []
    for num1 in range(dimension):
        for num2 in range(dimension):
            coordinates.append((num1, num2))
    return coordinates

def create_rule_2(dimension, coord):
    """
    creates rule that at least one number must fill a square
    """
    if dimension == 1:
        return []
    
    rule2 = []

    for num in range(1, dimension):
        rule2.append([(coord + (dimension, ), False), ((coord + (num, ), False))])
    
    return rule2 + create_rule_2(dimension - 1, coord)

def get_row_coords(dimension, row):
    """
    gets all the coordinates in a row
    """
    return [(row, num) for num in range(dimension)]

def get_col_coords(dimension, col):
    """
    gets all the coords in a column
    """
    return [(num, col) for num in range(dimension)]

def get_subgrid_coords(dimension, subgrid):
    """
    gets all the coords in a subgrid
    """
    subgrid_dimension = int(dimension ** 0.5)

    fresh_coords = generate_coords(subgrid_dimension)

    subgrid_coords = []
    for coord in fresh_coords:
        subgrid_coords.append((coord[0] + (subgrid[0] * subgrid_dimension), coord[1] + (subgrid[1] * subgrid_dimension)))

    return subgrid_coords

def create_rule_4(dimension, coords):
    """
    makes sure at least one of each number is in the given coords
    """
    rule4 = []
    for num in range(1, dimension + 1):
        new_rule4 = []
        for coord in coords:
            new_rule4.append((coord + (num, ), True))
        rule4.append(new_rule4)
    
    return rule4

def create_rule_5(num, coords):
    """
    makes sure that one number does not occur more than once in given coords
    """ 
    if len(coords) == 1:
        return []
    
    rule5 = []
    for coord in coords[1:]:
        rule5.append([(coords[0] + (num, ), False), (coord + (num, ), False)])

    return rule5 + create_rule_5(num, coords[1:])

# MAIN FUNCTIONS

def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    if not formula:
        return {}
    
    unit_cases = set()
    output = {}

    for clause in formula:
        if not clause:
            return None
        if len(clause) == 1:
            unit_cases.add(clause[0])


    while unit_cases:
        try:
            output = output | remove_unit_cases(formula, unit_cases)
        except:
            return None
        for literal in output.items():
            formula = simplify_formula(formula, literal)
        for clause in formula:
            if len(clause) == 1:
                unit_cases.add(clause[0])

    try:
        variable = formula[0][0][0]
    except:
        return output

    true_formula = simplify_formula(formula, (variable, True))
    true_case = satisfying_assignment(true_formula)
    if true_case is not None:
        return output | {variable: True} | true_case

    false_formula = simplify_formula(formula, (variable, False))
    false_case = satisfying_assignment(false_formula)
    if false_case is not None:
        return output | {variable: False} | false_case
    
    return None

def sudoku_board_to_sat_formula(sudoku_board):
    """
    Generates a SAT formula that, when solved, represents a solution to the
    given sudoku board.  The result should be a formula of the right form to be
    passed to the satisfying_assignment function above.
    """
    dimension = len(sudoku_board)
    coords = generate_coords(dimension)

    flat_board = []
    for row in sudoku_board:
        for num in row:
            flat_board.append(num)

    rule1 = []
    # at least one number must fill the square
    for coord in coords:
        coord_rule1 = []
        for num in range(1, dimension + 1):
            coord_rule1.append((coord + (num, ), True))
        rule1.append(coord_rule1)

    # no more than one number can fill a square
    rule2 = []
    for coord in coords:
        rule2.extend(create_rule_2(dimension, coord))

    # each number on the board must remain
    rule3 = []
    for coord, num in zip(coords, flat_board):
        if num != 0:
            rule3.append([(coord + (num, ), True)])

    # each row, col, and subgrid must have at least one of each number
    rule4 = []
    # each row, col, and subgrid cannot have more than one of each number
    rule5 = []
    for coord_num in range(dimension):
        row_coords = get_row_coords(dimension, coord_num)
        col_coords = get_col_coords(dimension, coord_num)
        rule4.extend(create_rule_4(dimension, row_coords))
        rule4.extend(create_rule_4(dimension, col_coords))
        for num in range(1, dimension + 1):
            rule5.extend(create_rule_5(num, row_coords))
            rule5.extend(create_rule_5(num, col_coords))

    subgrids = generate_coords(int(dimension ** 0.5))
    for subgrid in subgrids:
        subgrid_coords = get_subgrid_coords(dimension, subgrid)
        rule4.extend(create_rule_4(dimension, subgrid_coords))
        for num in range(1, dimension + 1):
            rule5.extend(create_rule_5(num, subgrid_coords))


    return rule1 + rule2 + rule3 + rule4 + rule5

def assignments_to_sudoku_board(assignments, n):
    """
    Given a variable assignment as given by satisfying_assignment, as well as a
    size n, construct an n-by-n 2-d array (list-of-lists) representing the
    solution given by the provided assignment of variables.

    If the given assignments correspond to an unsolvable board, return None
    instead.
    """
    if assignments is None:
        return None
    
    keys = sorted(assignments.keys())
    grid = []
    new_row = []
    for coordinate in keys:
        if assignments[coordinate]:
            new_row.append(coordinate[2])
            if len(new_row) == n:
                grid.append(new_row)
                new_row = []
    
    return grid

            
if __name__ == "__main__":
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)


cnf = [[('a', True), ('b', True)], [('b', True)], [('a', False), ('b', False)], [('d', True), ('c', True)]]


print(satisfying_assignment(cnf))
