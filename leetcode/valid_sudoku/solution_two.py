import unittest

from typing import List


def is_valid_sudoku(board: List[List[str]]) -> bool:
    n = len(board)
    seen = set()
    for r in range(0, n):
        for c in range(0, n):
            cell = board[r][c]
            if cell == '.':
                continue
            row = f'{cell} in row {r}'
            col = f'{cell} in col {c}'
            block = f'{cell} in block {r//3}{c//3}'
            if row in seen or col in seen or block in seen:
                return False
            seen.add(row)
            seen.add(col)
            seen.add(block)
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
