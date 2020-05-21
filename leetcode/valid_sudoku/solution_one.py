import unittest

from typing import List


def is_valid_sudoku(board: List[List[str]]) -> bool:
    n = len(board)
    for i in range(0, n):
        row_left, col_left = i, 0
        row_right, col_right = i, n - 1
        is_valid = check(row_left, col_left, row_right, col_right, board)
        if not is_valid:
            return False

        row_left, col_left = 0, i
        row_right, col_right = n - 1, i
        is_valid = check(row_left, col_left, row_right, col_right, board)
        if not is_valid:
            return False

    for i in range(0, n, 3):
        for j in range(0, n, 3):
            row_left, col_left = i, j
            row_right, col_right = i + 2, j + 2
            is_valid = check(row_left, col_left, row_right, col_right, board)
            if not is_valid:
                return False
    return True


def check(
        row_left: int, col_left: int, row_right: int, col_right:int,
        board: List[List[str]]
) -> bool:
    seen = set()
    for r in range(row_left, row_right + 1):
        for c in range(col_left, col_right + 1):
            if board[r][c] == '.':
                continue
            if board[r][c] in seen:
                return False
            seen.add(board[r][c])
    return True


class TestCase(unittest.TestCase):
    def test(self):
        board = [
            ["5", "3", ".", ".", "7", ".", ".", ".", "."],
            ["6", ".", ".", "1", "9", "5", ".", ".", "."],
            [".", "9", "8", ".", ".", ".", ".", "6", "."],
            ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
            ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
            ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
            [".", "6", ".", ".", ".", ".", "2", "8", "."],
            [".", ".", ".", "4", "1", "9", ".", ".", "5"],
            [".", ".", ".", ".", "8", ".", ".", "7", "9"]
        ]
        self.assertTrue(is_valid_sudoku(board))


if __name__ == '__main__':
    unittest.main()
