import unittest

from typing import List


def is_valid_sudoku(board: List[List[str]]) -> bool:
    n = len(board)
    rows_mask = [0] * n
    cols_mask = [0] * n
    blocks_mask = [0] * n
    for r in range(0, n):
        for c in range(0, n):
            cell = board[r][c]
            if cell == '.':
                continue
            value = 1 << int(cell)
            if rows_mask[r] & value:
                return False
            if cols_mask[c] & value:
                return False
            if blocks_mask[3*(r//3) + c//3] & value:
                return False

            rows_mask[r] |= value
            cols_mask[c] |= value
            blocks_mask[3*(r//3) + c//3] |= value
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
