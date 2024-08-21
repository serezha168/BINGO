import unittest
from bingo import BingoGame

class TestBingoGame(unittest.TestCase):
    def setUp(self):
        self.game = BingoGame()

    def test_generate_board(self):
        board = self.game.generate_board()
        self.assertEqual(len(board), 5)
        self.assertEqual(len(board[0]), 5)

    def test_toggle_cell(self):
        # Симулируем клик в центр первой ячейки
        cell_center_x = self.game.grid_offset[0] + self.game.cell_size // 2
        cell_center_y = self.game.grid_offset[1] + self.game.cell_size // 2
        self.game.toggle_cell((cell_center_x, cell_center_y))
        self.assertIn((0, 0), self.game.marked_cells)
        # Проверяем, что повторный клик убирает отметку
        self.game.toggle_cell((cell_center_x, cell_center_y))
        self.assertNotIn((0, 0), self.game.marked_cells)

    def test_edit_word(self):
        # Симулируем правый клик в центр первой ячейки
        cell_center_x = self.game.grid_offset[0] + self.game.cell_size // 2
        cell_center_y = self.game.grid_offset[1] + self.game.cell_size // 2
        self.game.edit_word((cell_center_x, cell_center_y))
        self.assertEqual(self.game.editing_cell, (0, 0))
        self.assertTrue(self.game.input_active)

    def test_add_word(self):
        self.game.input_text = "Test"
        self.game.editing_cell = (0, 0)
        self.game.add_word()
        self.assertEqual(self.game.board[0][0], "Test")

if __name__ == '__main__':
    unittest.main()
