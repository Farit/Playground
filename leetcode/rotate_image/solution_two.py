import unittest

from typing import List


def rotate_ninety_degree_clockwise(matrix: List[List[int]]) -> None:
    n = len(matrix)
    r, c = 0, n - 1
    while r < c:
        for i in range(r, c):
            row, col = r, i
            r_row, r_col = col, n - row - 1
            while (r_row, r_col) != (row, col):
                matrix[r_row][r_col], matrix[row][col] = (
                    matrix[row][col], matrix[r_row][r_col]
                )
                r_row, r_col = r_col, n - r_row - 1
        r += 1
        c -= 1


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
