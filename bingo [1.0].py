import pygame
import random
from typing import List, Tuple

# Константы
WINDOW_SIZE = (800, 750)
CELL_SIZE = 90
MARGIN = 20
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
INPUT_BOX_WIDTH = 300
INPUT_BOX_HEIGHT = 40
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 40
FONT_SIZE = 24

class BingoGame:
    def __init__(self):
        pygame.init()
        self.width, self.height = WINDOW_SIZE
        self.screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
        pygame.display.set_caption("Бинго")
        self.clock = pygame.time.Clock()
        self.running = True
        self.available_sizes = [3, 4, 5, 6, 7]
        self.current_size_index = 2  # Начинаем с 5x5
        self.grid_size = self.available_sizes[self.current_size_index]
        self.cell_size = CELL_SIZE
        self.grid_offset = (MARGIN, MARGIN)
        self.input_rect = pygame.Rect(0, 0, INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT)
        self.button_rect = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.size_button_rect = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.input_text = ''
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.title_font = pygame.font.Font(None, 48)
        self.subtitle_font = pygame.font.Font(None, 20)
        self.board = self.generate_board()
        self.marked_cells = set()
        self.message = ""
        self.message_timer = 0
        self.input_active = False
        self.editing_cell = None
        self.selected_cell = None
        self.message_rect = pygame.Rect(0, 0, self.width, 30)
        self.adjust_scale()
        self.font_cache = {}

    def generate_board(self) -> List[List[str]]:
        return [['' for _ in range(self.grid_size)] for _ in range(self.grid_size)]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.width, self.height = event.size
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                self.adjust_scale()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    if self.input_rect.collidepoint(event.pos):
                        self.input_active = True
                    elif self.button_rect.collidepoint(event.pos):
                        self.add_word()
                    elif self.size_button_rect.collidepoint(event.pos):
                        self.change_grid_size()
                    else:
                        self.input_active = False
                        self.toggle_cell(event.pos)
                elif event.button == 3:  # Правая кнопка мыши
                    self.edit_word(event.pos)
            elif event.type == pygame.KEYDOWN:
                if self.input_active:
                    if event.key == pygame.K_RETURN:
                        self.add_word()
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        self.input_text += event.unicode

    def toggle_cell(self, pos):
        x, y = pos
        grid_x = (x - self.grid_offset[0]) // self.cell_size
        grid_y = (y - self.grid_offset[1]) // self.cell_size
        if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
            cell = (grid_x, grid_y)
            if cell in self.marked_cells:
                self.marked_cells.remove(cell)
            else:
                self.marked_cells.add(cell)

    def edit_word(self, pos):
        x, y = pos
        grid_x = (x - self.grid_offset[0]) // self.cell_size
        grid_y = (y - self.grid_offset[1]) // self.cell_size
        if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
            self.input_text = self.board[grid_y][grid_x]
            self.editing_cell = (grid_x, grid_y)
            self.selected_cell = (grid_x, grid_y)
            self.input_active = True

    def add_word(self):
        if self.editing_cell is not None:
            x, y = self.editing_cell
            self.board[y][x] = self.input_text
            self.editing_cell = None
            self.message = f"Слово '{self.input_text}' успешно изменено!"
        else:
            self.message = "Выберите клетку для редактирования!"
        self.message_timer = 120
        self.input_text = ''
        self.selected_cell = None

    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1
        else:
            self.message = ""

    def adjust_scale(self):
        max_cell_size = min((self.width - 2 * MARGIN) // self.grid_size,
                            (self.height - 2 * MARGIN - INPUT_BOX_HEIGHT - 200) // self.grid_size)
        self.cell_size = max_cell_size
        self.grid_offset = (
            (self.width - self.grid_size * self.cell_size) // 2,
            max(120, (self.height - self.grid_size * self.cell_size - INPUT_BOX_HEIGHT - 200) // 2)
        )

        input_y = self.grid_offset[1] + self.grid_size * self.cell_size + 30
        total_width = INPUT_BOX_WIDTH + BUTTON_WIDTH + 20
        start_x = (self.width - total_width) // 2
        self.input_rect.topleft = (start_x, input_y)
        self.button_rect.topleft = (start_x + INPUT_BOX_WIDTH + 20, input_y)

        self.size_button_rect.topleft = ((self.width - BUTTON_WIDTH) // 2, self.grid_offset[1] - 60)

        self.message_rect.topleft = (0, self.button_rect.bottom + 20)
        self.message_rect.width = self.width

    def change_grid_size(self):
        self.current_size_index = (self.current_size_index + 1) % len(self.available_sizes)
        self.grid_size = self.available_sizes[self.current_size_index]
        self.board = self.generate_board()
        self.marked_cells = set()
        self.adjust_scale()

    def wrap_text(self, text, font_size, max_width):
        if font_size not in self.font_cache:
            self.font_cache[font_size] = pygame.font.Font(None, font_size)
        font = self.font_cache[font_size]
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            if test_width <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        return lines

    def draw(self):
        self.screen.fill(WHITE)
        # Отрисовка заголовка
        title_text = self.title_font.render("Bingo", True, BLACK)
        title_rect = title_text.get_rect(center=(self.width // 2, self.grid_offset[1] - 90))
        self.screen.blit(title_text, title_rect)

        # Отрисовка кнопки изменения размера
        pygame.draw.rect(self.screen, GRAY, self.size_button_rect)
        pygame.draw.rect(self.screen, BLACK, self.size_button_rect, 2)
        size_text = self.font.render(f"{self.grid_size}x{self.grid_size}", True, BLACK)
        size_text_rect = size_text.get_rect(center=self.size_button_rect.center)
        self.screen.blit(size_text, size_text_rect)

        # Отрисовка сетки и слов
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x = self.grid_offset[0] + i * self.cell_size
                y = self.grid_offset[1] + j * self.cell_size
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                if self.selected_cell == (i, j):
                    pygame.draw.rect(self.screen, YELLOW, rect)
                else:
                    pygame.draw.rect(self.screen, GRAY, rect)
                pygame.draw.rect(self.screen, BLACK, rect, 2)
                word = self.board[j][i]
                if word:
                    self.draw_word(word, x, y)
                if (i, j) in self.marked_cells:
                    pygame.draw.line(self.screen, RED, (x + 5, y + 5),
                                     (x + self.cell_size - 5, y + self.cell_size - 5), 4)
                    pygame.draw.line(self.screen, RED, (x + self.cell_size - 5, y + 5),
                                     (x + 5, y + self.cell_size - 5), 4)

        # Отрисовка интерфейса
        self.draw_interface()
        pygame.display.flip()

    def draw_word(self, word, x, y):
        font_size = 24
        lines = self.wrap_text(word, font_size, self.cell_size - 10)
        while font_size > 10 and (len(lines) > 3 or max(self.font_cache[font_size].size(line)[0] for line in lines) > self.cell_size - 10):
            font_size -= 1
            lines = self.wrap_text(word, font_size, self.cell_size - 10)
        font = self.font_cache[font_size]
        y_offset = y + (self.cell_size - len(lines) * font.get_linesize()) // 2
        for line in lines:
            text = font.render(line, True, BLACK)
            text_rect = text.get_rect(center=(x + self.cell_size // 2, y_offset + font.get_linesize() // 2))
            self.screen.blit(text, text_rect)
            y_offset += font.get_linesize()

    def draw_interface(self):
        pygame.draw.rect(self.screen, WHITE, self.input_rect)
        pygame.draw.rect(self.screen, BLACK, self.input_rect, 2)
        text_surface = self.font.render(self.input_text, True, BLACK)
        self.screen.blit(text_surface, (self.input_rect.x + 5, self.input_rect.y + 5))

        pygame.draw.rect(self.screen, GRAY, self.button_rect)
        pygame.draw.rect(self.screen, BLACK, self.button_rect, 2)
        button_text = self.font.render("Изменить", True, BLACK)
        button_text_rect = button_text.get_rect(center=self.button_rect.center)
        self.screen.blit(button_text, button_text_rect)

        label_text = self.font.render("Введите слово:", True, BLACK)
        label_rect = label_text.get_rect(bottomleft=(self.input_rect.left, self.input_rect.top - 5))
        self.screen.blit(label_text, label_rect)

        if self.message:
            message_surface = self.font.render(self.message, True, BLACK)
            message_rect = message_surface.get_rect(center=self.message_rect.center)
            pygame.draw.rect(self.screen, WHITE, self.message_rect)
            self.screen.blit(message_surface, message_rect)

        subtitle_text = self.subtitle_font.render("by serezha168", True, BLACK)
        subtitle_rect = subtitle_text.get_rect(center=(self.width // 2, self.height - 20))
        self.screen.blit(subtitle_text, subtitle_rect)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    game = BingoGame()
    game.run()
