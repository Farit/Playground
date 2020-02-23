import unittest
import doctest

from itertools import combinations


def subsets(iterable):
    """
    Returns all subsets without an empty subset.
    >>> subsets_generator = subsets(['a', 'b'])
    >>> next(subsets_generator)
    ('a',)
    >>> next(subsets_generator)
    ('b',)
    >>> next(subsets_generator)
    ('a', 'b')
    >>> res = next(subsets_generator, None)
    >>> res is None
    True
    """
    length = len([i for i in iter(iterable)])
    for l in range(1, length + 1):
        subsets_of_size_l = combinations(iter(iterable), l)
        for subset in subsets_of_size_l:
            yield subset


class TestCase(unittest.TestCase):

    def test_subsets(self):
        tests = [
            ([], []),
            (['a'], [
                ('a',)
            ]),
            (['a', 'b'], [
                ('a',), ('b', ), ('a', 'b')
            ]),
            (['a', 'b', 'c'], [
                ('a',), ('b',), ('c',), ('a', 'b'), ('a', 'c'), ('b', 'c'),
                ('a', 'b', 'c')
            ])
        ]
        for data, data_subsets in tests:
            with self.subTest(data):
                generated_subsets = [s for s in subsets(data)]
                self.assertSequenceEqual(generated_subsets, data_subsets)


if __name__ == '__main__':
    unittest.main(exit=False)
    doctest.testmod()
