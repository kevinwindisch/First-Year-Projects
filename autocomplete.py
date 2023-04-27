


import doctest
from text_tokenize import tokenize_sentences


class PrefixTree:
    """
    stores keys organized by their prefixes
    """

    def __init__(self):
        self.value = None
        self.children = {}

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the prefix tree,
        or reassign the associated value if it is already present.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError
        if key == "":
            self.value = value
        else:
            try:
                self.children[key[0]][key[1:]] = value
            except KeyError:
                self.children[key[0]] = PrefixTree()
                self.children[key[0]][key[1:]] = value

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError
        if key == "":
            if self.value is None:
                raise KeyError
            else:
                return self.value
        else:
            try:
                return self.children[key[0]][key[1:]]
            except KeyError as exc:
                raise KeyError from exc

    def __delitem__(self, key):
        """
        Delete the given key from the prefix tree if it exists.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError
        if len(key) == 1:
            if self.children[key].value is not None:
                self.children[key].value = None
            else:
                raise KeyError
        else:
            try:
                del self.children[key[0]][key[1:]]
            except KeyError as exc:
                raise KeyError from exc

    def __contains__(self, key):
        """
        Is key a key in the prefix tree?  Return True or False.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError
        if key == "":
            if self.value is None:
                return False
            else:
                return True
        else:
            try:
                return key[1:] in self.children[key[0]]
            except KeyError:
                return False

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this prefix tree
        and its children.  Must be a generator!
        """
        for child in self.children:
            if self.children[child].value is not None:
                yield (child, self.children[child].value)

            for key, value in self.children[child]:
                yield (child + key, value)


def word_frequencies(text):
    """
    Given a piece of text as a single string, create a prefix tree whose keys
    are the words in the text, and whose values are the number of times the
    associated word appears in the text.
    """
    sentences = tokenize_sentences(text)
    words = {}
    for sentence in sentences:
        sentence_words = sentence.split()
        for word in sentence_words:
            if word not in words:
                words[word] = 1
            else:
                words[word] += 1

    tree = PrefixTree()
    for word in words:
        tree[word] = words[word]

    return tree


def autocomplete(tree, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is not a string.
    """
    if not isinstance(prefix, str):
        raise TypeError

    if not prefix:
        keys = list(tree)
    else:
        new_tree = tree.children[prefix[0]]
        for letter in prefix[1:]:
            try:
                new_tree = new_tree.children[letter]
            except KeyError:
                return []
        keys = list(new_tree)
        if new_tree.value is not None:
            keys.append(("", new_tree.value))

    output = {prefix + key[0] for key in keys}

    if max_count is not None:
        while max_count < len(output):
            lowest = min([key[1] for key in keys])
            new_keys = []
            for key in keys:
                if key[1] > lowest:
                    new_keys.append(key)
                else:
                    if max_count < len(output):
                        output.remove(prefix + key[0])
                    else:
                        break
            keys = new_keys

    return output


def valid_edit_gen(tree, prefix):
    """
    yields most frequent valid edit
    """
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    edits = set()
    for char in alphabet:
        edits = edits | {
            prefix[:index] + char + prefix[index:] for index in range(len(prefix) + 1)
        }
        edits = edits | {
            prefix[:index] + char + prefix[index + 1 :] for index in range(len(prefix))
        }
    edits = edits | {
        prefix[:index] + prefix[index + 1 :] for index in range(len(prefix))
    }
    edits = edits | {
        prefix[:index] + prefix[index + 1] + prefix[index] + prefix[index + 2 :]
        for index in range(len(prefix) - 1)
    }

    valid_edits = {(edit, tree[edit]) for edit in edits if edit in tree}
    while valid_edits:
        highest = max([value[1] for value in valid_edits])
        new_valids = set()
        for edit in valid_edits:
            if edit[1] == highest:
                yield edit[0]
            else:
                new_valids.add(edit)
        valid_edits = new_valids


def autocorrect(tree, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    output = autocomplete(tree, prefix, max_count)

    if max_count is not None:
        if max_count == len(output):
            return output
        else:
            for edit in valid_edit_gen(tree, prefix):
                output.add(edit)
                if max_count == len(output):
                    break
            return output
    else:
        for edit in valid_edit_gen(tree, prefix):
            output.add(edit)
        return output


def word_filter(tree, pattern):
    """
    Return list of (word, freq) for all words in the given prefix tree that
    match pattern.  pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    if not isinstance(pattern, str):
        raise TypeError

    if pattern == "":
        if tree.value is not None:
            return [("", tree.value)]
        else:
            return []
    if pattern[0] == "?":
        values = []
        for child in tree.children:
            values += [
                (child + value[0], value[1])
                for value in word_filter(tree.children[child], pattern[1:])
                if value is not None
            ]
        return values
    elif pattern[0] == "*":
        if 1 < len(pattern):
            if pattern[1] == "*":
                return word_filter(tree, pattern[1:])
        values = set()
        values = values | {
            (value[0], value[1])
            for value in word_filter(tree, pattern[1:])
            if value is not None
        }
        for child in tree.children:
            values = values | {
                (child + value[0], value[1])
                for value in word_filter(tree.children[child], pattern)
                if value is not None
            }
        return list(values)
    else:
        for child in tree.children:
            if child == pattern[0]:
                return [
                    (child + value[0], value[1])
                    for value in word_filter(tree.children[child], pattern[1:])
                    if value is not None
                ]
    return []


# you can include test cases of your own in the block below.
if __name__ == "__main__":
    doctest.testmod()

    with open("pride.txt", encoding="utf-8") as f:
        book = f.read()

    w = word_frequencies(book)
    print(list(autocorrect(w, 'hear')))

    
