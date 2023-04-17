import sys
import pygame
import random

# Constants
BLOCK_SIZE = 30
COLS, ROWS = 10, 20
SCREEN_WIDTH, SCREEN_HEIGHT = BLOCK_SIZE * COLS, BLOCK_SIZE * ROWS
pygame.font.init()
FONT = pygame.font.Font(pygame.font.get_default_font(), 20)
FPS = 30

# Tetromino shapes
SHAPES = [
    [['.....',
      '.....',
      '.OOO.',
      '..O..',
      '.....'],
     ['.....',
      '..O..',
      '..OO.',
      '...O.',
      '.....']],
    [['.....',
      '.....',
      '.OOO.',
      '.O...',
      '.....'],
     ['.....',
      '..OO.',
      '...O.',
      '...O.',
      '.....']],
    [['.....',
      '.....',
      '.OOO.',
      '...O.',
      '.....'],
     ['.....',
      '...O.',
      '...O.',
      '..OO.',
      '.....']],
    [['.....',
      '.....',
      '..OO.',
      '..OO.',
      '.....']],
    [['.....',
      '.....',
      '..OO.',
      '.OO..',
      '.....'],
     ['.....',
      '...O.',
      '..OO.',
      '..O..',
      '.....']],
    [['.....',
      '.....',
      '.OO..',
      '..OO.',
      '.....'],
     ['.....',
      '..O..',
      '.OO..',
      '...O.',
      '.....']],
    [['.....',
      '.....',
      '...O.',
      '.OOO.',
      '.....'],
     ['.....',
      '..O..',
      '..OO.',
      '..O..',
      '.....'],
     ['.....',
      '.....',
      '.OOO.',
      '.O...',
      '.....'],
     ['.....',
      '...O.',
      '...O.',
      '..OO.',
      '.....']]
]

COLORS = [
    (0, 0, 0),
    (255, 85, 85),
    (100, 200, 115),
    (120, 108, 245),
    (255, 140, 50),
    (50, 120, 52),
    (146, 202, 73),
    (150, 161, 218)
]

# Tetromino class
class Tetromino(pygame.sprite.Sprite):
    def __init__(self, x, y, shape):
        super().__init__()
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPES.index(shape) + 1
        self.rotation = 0

# Initialize the game
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH + 200, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')

clock = pygame.time.Clock()
game_over = False

def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for _ in range(COLS)] for _ in range(ROWS)]

    for y in range(ROWS):
        for x in range(COLS):
            if (x, y) in locked_positions:
                color_idx = locked_positions[(x, y)]
                grid[y][x] = COLORS[color_idx]

    return grid

def convert_shape_to_positions(tetromino):
    positions = []
    shape_format = tetromino.shape[tetromino.rotation % len(tetromino.shape)]

    for i, line in enumerate(shape_format):
        row = list(line)
        for j, col in enumerate(row):
            if col == 'O':
                positions.append((tetromino.x + j, tetromino.y + i))

    return positions

def is_valid_space(tetromino, grid):
    accepted_positions = [[(j, i) for j in range(COLS) if grid[i][j] == (0, 0, 0)] for i in range(ROWS)]
    accepted_positions = [pos for sublist in accepted_positions for pos in sublist]

    formatted_positions = convert_shape_to_positions(tetromino)

    for pos in formatted_positions:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True

def move_tetromino(tetromino, x, y, grid):
    tetromino.x += x
    tetromino.y += y

    if not is_valid_space(tetromino, grid):
        tetromino.x -= x
        tetromino.y -= y
        return False

    return True

def rotate_tetromino(tetromino, grid):
    tetromino.rotation += 1
    if not is_valid_space(tetromino, grid):
        tetromino.rotation -= 1
        return False

    return True

def check_collision_bottom_or_locked(tetromino, grid, locked_positions):
    current_positions = convert_shape_to_positions(tetromino)
    
    for pos in current_positions:
        if pos[1] + 1 >= ROWS or (pos[0], pos[1] + 1) in locked_positions:
            return True
    return False

def clear_lines(grid, locked_positions):
    full_lines_indices = []
    for i, row in enumerate(grid):
        if all(cell != (0, 0, 0) for cell in row):
            full_lines_indices.append(i)

    if full_lines_indices:
        for line_index in full_lines_indices:
            for key in sorted(list(locked_positions.keys()), key=lambda x: x[1], reverse=True):
                if key[1] < line_index:
                    locked_positions[(key[0], key[1] + 1)] = locked_positions.pop(key)

    return len(full_lines_indices)

def is_game_over(locked_positions):
    for pos in locked_positions:
        if pos[1] < 1:
            return True
    return False

def draw_gridlines(surface, grid):
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(surface, (128, 128, 128), rect, 1)

def draw_upcoming_tetromino(surface, tetromino):
    x, y = BLOCK_SIZE * COLS + 50, 100
    text = FONT.render("Next:", 1, (255, 255, 255))
    surface.blit(text, (x, y - 30))
    shape_format = tetromino.shape[tetromino.rotation % len(tetromino.shape)]

    for i, line in enumerate(shape_format):
        row = list(line)
        for j, col in enumerate(row):
            if col == 'O':
                pygame.draw.rect(surface, tetromino.color, (x + j * BLOCK_SIZE, y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(surface, (128, 128, 128), (x + j * BLOCK_SIZE, y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def draw_score(surface, score):
    x, y = BLOCK_SIZE * COLS + 50, 250
    text = FONT.render("Score:", 1, (255, 255, 255))
    surface.blit(text, (x, y - 30))
    text = FONT.render(str(score), 1, (255, 255, 255))
    surface.blit(text, (x, y))

def draw_grid(surface, grid):
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            pygame.draw.rect(surface, cell, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

def draw_tetromino(surface, tetromino):
    shape_format = tetromino.shape[tetromino.rotation % len(tetromino.shape)]

    for i, line in enumerate(shape_format):
        row = list(line)
        for j, col in enumerate(row):
            if col == 'O':
                pygame.draw.rect(surface, COLORS[SHAPES.index(tetromino.shape) + 1], (tetromino.x + j * BLOCK_SIZE, tetromino.y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(surface, (128, 128, 128), (tetromino.x + j * BLOCK_SIZE, tetromino.y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def main():
    game_over = False
    locked_positions = {}
    change_piece = False
    score = 0

    current_tetromino = Tetromino(5, 0, random.choice(SHAPES))
    next_tetromino = Tetromino(5, 0, random.choice(SHAPES))

    while not game_over:
        grid = create_grid(locked_positions)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move_tetromino(current_tetromino, -1, 0, grid)
                if event.key == pygame.K_RIGHT:
                    move_tetromino(current_tetromino, 1, 0, grid)
                if event.key == pygame.K_DOWN:
                    move_tetromino(current_tetromino, 0, 1, grid)
                if event.key == pygame.K_UP:
                    rotate_tetromino(current_tetromino, grid)

        if check_collision_bottom_or_locked(current_tetromino, grid, locked_positions):
            for pos in convert_shape_to_positions(current_tetromino):
                locked_positions[pos] = SHAPES.index(current_tetromino.shape)
            current_tetromino = next_tetromino
            next_tetromino = Tetromino(5, 0, random.choice(SHAPES))

            cleared_lines = clear_lines(grid, locked_positions)
            score += cleared_lines * 100

            if is_game_over(locked_positions):
                game_over = True
                print("Game Over! Your score:", score)

        screen.fill((0, 0, 0))

        draw_grid(screen, grid)
        draw_tetromino(screen, current_tetromino)
        draw_gridlines(screen, grid)
        draw_upcoming_tetromino(screen, next_tetromino)
        draw_score(screen, score)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
