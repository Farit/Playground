import unittest

from typing import List


def rotate_ninety_degree_clockwise(matrix: List[List[int]]) -> None:
    n = len(matrix)

    # First reverse up to down along the horizontal axis of symmetry
    i, j = 0, n - 1
    while i < j:
        for c in range(n):
            matrix[i][c], matrix[j][c] = matrix[j][c], matrix[i][c]
        i += 1
        j -= 1

    # Swap the elements along the diagonal axis of symmetry
    for d in range(n):
        for e in range(d+1, n):
            matrix[d][e], matrix[e][d] = matrix[e][d], matrix[d][e]


class TestCase(unittest.TestCase):
    def test(self):
        matrix = [
          [5, 1, 9, 11],
          [2, 4, 8, 10],
          [13, 3, 6, 7],
          [15, 14, 12, 16]
        ]
        rotate_ninety_degree_clockwise(matrix)
        rotated_matrix = [
          [15, 13, 2, 5],
          [14, 3, 4, 1],
          [12, 6, 8, 9],
          [16, 7, 10, 11]
        ]
        self.assertEquals(matrix, rotated_matrix)


if __name__ == '__main__':
    unittest.main()
