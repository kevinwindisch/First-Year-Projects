"""
finding the Kevin Bacon number of different actors in a database
utilizes a flood fill searching technique to find connecting paths between actors
"""

import pickle


def transform_data(raw_data):
    """
    input: raw data: list of tuples [(actor1, actor2, film)...]
    which shows which actors acted together in a film

    turns data into a dictionary with each key being a unique actor.
    the value of each key is a list containing two sets.
    the first set is every actor the key actor has acted with.
    the second set is every movie that the actor has been in.
    """
    transformed_data = {}
    for data in raw_data:  # creates uniqe keys for each actor
        if data[0] != data[1]:
            if data[0] not in transformed_data:
                transformed_data[data[0]] = [{data[1]}]
            if data[1] not in transformed_data:
                transformed_data[data[1]] = [{data[0]}]
            transformed_data[data[0]][0].add(
                data[1]
            )  # adds every actor acted with to the first set
            transformed_data[data[1]][0].add(data[0])

    for data in raw_data:
        if len(transformed_data[data[0]]) == 1:
            transformed_data[data[0]].append(
                {data[2]}
            )  # adds every movie the actor has been in to the second set
        if len(transformed_data[data[1]]) == 1:
            transformed_data[data[1]].append({data[2]})
        transformed_data[data[0]][1].add(data[2])
        transformed_data[data[1]][1].add(data[2])

    delete = set()
    for actor1 in transformed_data:
        if (
            len(transformed_data[actor1][0]) == 1
        ):  # deletes any pair of actors that have only acted with each
            # other (causes problems)
            for actor2 in transformed_data[actor1][0]:
                if len(transformed_data[actor2][0]) == 1:
                    delete.add(actor1)
                    delete.add(actor2)
    for actor in delete:
        del transformed_data[actor]

    return transformed_data


def acted_together(transformed_data, actor_id_1, actor_id_2):
    """
    Returns True if actors have acted together and False if they have not
    """

    if actor_id_1 in transformed_data[actor_id_2][0]:
        return True
    if actor_id_2 in transformed_data[actor_id_1][0]:
        return True
    if actor_id_1 == actor_id_2:
        return True
    return False


def actors_with_bacon_number(transformed_data, n):
    """
    Returns a set of all of the actor ids with the given Bacon Number n
    """
    if n == 0:  # Kevin Bacon himself
        return {4724}
    if n > 10**6:  # No such bacon number exists
        return set()
    previous_actors = {4724}
    old_actors = {4724}
    new_actors = set()
    for _ in range(n):  # Iterates n times, finds bacon number in increasing order
        new_actors.clear()
        for actor in previous_actors:
            new_actors = new_actors.union(transformed_data[actor][0])
        new_actors = new_actors.difference(old_actors)
        old_actors = old_actors.union(new_actors)
        previous_actors = new_actors.copy()
    return new_actors


def bacon_path(transformed_data, actor_id):
    """
    finds the shortest path from Kevin Bacon to the actor
    returns list of actors connecting Kevin Bacon to the actor
    """
    target = actor_id
    visited = {4724}
    possible_paths = [[4724]]  # flood fill technique
    new_possible_paths = []
    dummy = 1
    while dummy > 0:
        for path in possible_paths:  # iterates through each possible path
            actor1 = path[-1]
            for actor2 in transformed_data[actor1][
                0
            ]:  # finds neighbors of previous actor
                if actor2 == target:  # target!
                    path.append(actor2)
                    return path
                if actor2 not in visited:  # checks if actor has been visited
                    new_path = path.copy()
                    new_path.append(actor2)
                    new_possible_paths.append(new_path)
                    visited.add(actor2)
                if len(visited) == len(transformed_data):  # checks if no path exists
                    return None
        possible_paths = new_possible_paths.copy()
        new_possible_paths.clear()  # resets possible paths


def actor_to_actor_path(transformed_data, actor_id_1, actor_id_2):
    """
    finds path from one actor to another
    returns list of actors who have acted together
    """
    target = actor_id_2
    visited = {actor_id_1}
    possible_paths = [[actor_id_1]]  # similar flood fill technique
    new_possible_paths = []
    dummy = 1
    while dummy > 0:
        for path in possible_paths:  # iterates through each possible path
            actor1 = path[-1]
            for actor2 in transformed_data[actor1][
                0
            ]:  # finds neighbors of the last actor in list
                if actor1 == target:  # checks if target is itself
                    return path
                if actor2 == target:
                    path.append(actor2)
                    return path
                if actor2 not in visited:  # checks if previous actor has been visited
                    new_path = path.copy()
                    new_path.append(actor2)
                    new_possible_paths.append(new_path)
                    visited.add(actor2)
                if len(visited) == len(transformed_data):  # checks if no path exists
                    return None
        possible_paths = new_possible_paths.copy()  # resets possible paths
        new_possible_paths.clear()


def movie_path(raw_data, actor_id_1, actor_id_2):
    """
    connects actors through the movies they have been in
    returns list of movie names connecting the actors
    """
    with open("resources/movies.pickle", "rb") as function:
        moviesdb = pickle.load(function)
    path = actor_to_actor_path(
        transform_data(raw_data), actor_id_1, actor_id_2
    )  # finds shortest path
    movie_data = transform_data(raw_data)
    movies = []
    for n in range(len(path) - 1):
        actor1, actor2 = (
            path[n],
            path[n + 1],
        )  # gets actors 2 at a time starting from start
        intersection = list(
            movie_data[actor1][1].intersection(movie_data[actor2][1])
        )  # finds movie that both acted in
        movies.append(intersection[0])
    movie_names = []
    for movie in movies:  # turns keys of movies into movie names
        for key, value in moviesdb.items():
            if value == movie:
                movie_names.append(key)
    return movie_names


def actor_path(transformed_data, actor_id_1, goal_test_function):
    """
    connects an actor to a list of other actors (in the form of a function)
    """
    visited = {actor_id_1}
    possible_paths = [[actor_id_1]]  # flood fill
    new_possible_paths = []
    n = 1
    while n > 0:
        for path in possible_paths:  # iterates through each path
            actor1 = path[-1]
            for actor2 in transformed_data[actor1][0]:
                if goal_test_function(actor1):  # tests if actor1 fulfills function
                    return path
                if goal_test_function(actor2):  # tests if actor2 fulfills function
                    path.append(actor2)
                    return path
                if actor2 not in visited:  # checks if actor has been visited
                    new_path = path.copy()
                    new_path.append(actor2)
                    new_possible_paths.append(new_path)
                    visited.add(actor2)
                if len(visited) == len(transformed_data):  # checks if no path exists
                    return None
        possible_paths = new_possible_paths.copy()
        new_possible_paths.clear()


def actors_connecting_films(transformed_data, film1, film2):
    """
    finds shortest path from one movie to another using the actors in the movies
    returns a list actors from the starting movie to the end movie
    """
    possible_paths = set()
    film1_actors = set()
    film2_actors = set()
    for actor in transformed_data:  # iterates through every actor
        if film1 in transformed_data[actor][1]:  # checks if actor in film1
            film1_actors.add(actor)
        if film2 in transformed_data[actor][1]:  # checks if actor in film2
            film2_actors.add(actor)
    for actor in film1_actors:  # iterates through each actor in film1
        path = actor_path(
            transformed_data, actor, lambda x: x in film2_actors
        )  # finds shortest path between actor and film2
        possible_paths.add(tuple(path))
    min_len = 10**10
    for path in possible_paths:  # finds the shortest of the possible path
        if len(path) < min_len:
            min_len = len(path)
    for path in possible_paths:
        if len(path) == min_len:
            return list(path)


if __name__ == "__main__":
    with open("resources/small.pickle", "rb") as f:
        smalldb = pickle.load(f)
    with open("resources/names.pickle", "rb") as f:
        namesdb = pickle.load(f)
    with open("resources/tiny.pickle", "rb") as f:
        tinydb = pickle.load(f)
    with open("resources/movies.pickle", "rb") as f:
        moviesdb = pickle.load(f)
    with open("resources/small_names.pickle", "rb") as f:
        small_namesdb = pickle.load(f)
    with open("resources/large.pickle", "rb") as f:
        largedb = pickle.load(f)
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
