import pygame as pg
import sys
import random

pg.init()


# ---------------------------------
# Settings
# ---------------------------------
SCREEN_SIZE = (800, 450)
GRID_SIZE = 20
GRID_WIDTH = SCREEN_SIZE[0] // GRID_SIZE
GRID_HEIGHT = SCREEN_SIZE[1] // GRID_SIZE

FONT_FILE = "CookieCrisp-L36ly.ttf"


# ---------------------------------
# Font Loader
# ---------------------------------
def load_font(size):
    return pg.font.Font(FONT_FILE, size)


# ---------------------------------
# Snake Class
# ---------------------------------
class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = "RIGHT"
        self.length = 1

    def move(self):
        x, y = self.positions[0]

        if self.direction == "UP":
            y -= 1
        elif self.direction == "DOWN":
            y += 1
        elif self.direction == "LEFT":
            x -= 1
        elif self.direction == "RIGHT":
            x += 1

        new_head = (x, y)
        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.positions.pop()

    def grow_if_needed(self):
        pass  # handled in Game.update()

    def draw(self, surface):
        for pos in self.positions:
            rect = pg.Rect(pos[0] * GRID_SIZE, pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pg.draw.rect(surface, (0, 255, 0), rect)


# ---------------------------------
# Apple Class
# ---------------------------------
class Apple:
    def __init__(self):
        self.position = (random.randint(0, GRID_WIDTH - 1),
                         random.randint(0, GRID_HEIGHT - 1))

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1),
                         random.randint(0, GRID_HEIGHT - 1))

    def draw(self, surface):
        rect = pg.Rect(self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pg.draw.rect(surface, (255, 0, 0), rect)


# ---------------------------------
# Game Class
# ---------------------------------
class Game:
    def __init__(self):
        self.snake = Snake()
        self.apple = Apple()
        self.score = 0

    def update(self):
        self.snake.move()
        self.snake.grow_if_needed()

        head = self.snake.positions[0]
        if head == self.apple.position:
            self.snake.length += 1
            self.score += 1
            self.apple.randomize_position()

    def draw(self, surface):
        self.snake.draw(surface)
        self.apple.draw(surface)

        score_font = load_font(24)
        score_surf = score_font.render(f"Score: {self.score}", True, (255, 255, 255))
        surface.blit(score_surf, (10, 10))

    def change_direction(self, new_dir):
        opposite = {
            "UP": "DOWN",
            "DOWN": "UP",
            "LEFT": "RIGHT",
            "RIGHT": "LEFT"
        }
        if opposite[self.snake.direction] != new_dir:
            self.snake.direction = new_dir

    def check_collision(self):
        head_x, head_y = self.snake.positions[0]

        if head_x < 0 or head_x >= GRID_WIDTH or head_y < 0 or head_y >= GRID_HEIGHT:
            return True

        if self.snake.positions[0] in self.snake.positions[1:]:
            return True

        return False


# ---------------------------------
# Gameplay Loop
# ---------------------------------
def start_game(screen, clock):
    game = Game()

    while True:
        dt = clock.tick(10)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        keys = pg.key.get_pressed()
        if keys[pg.K_UP]:
            game.change_direction("UP")
        elif keys[pg.K_DOWN]:
            game.change_direction("DOWN")
        elif keys[pg.K_LEFT]:
            game.change_direction("LEFT")
        elif keys[pg.K_RIGHT]:
            game.change_direction("RIGHT")

        game.update()

        if game.check_collision():
            return game.score

        screen.fill((0, 0, 0))
        game.draw(screen)
        pg.display.flip()


# ---------------------------------
# Menu Screen
# ---------------------------------
def menu(screen, clock):
    while True:
        screen.fill((20, 20, 20))

        title_font = load_font(50)
        btn_font = load_font(32)

        title_surf = title_font.render("PIXEL SERPENT", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SCREEN_SIZE[0] // 2, 100))
        screen.blit(title_surf, title_rect)

        play_surf = btn_font.render("PLAY", True, (255, 255, 255))
        play_rect = play_surf.get_rect(center=(SCREEN_SIZE[0] // 2, 230))
        screen.blit(play_surf, play_rect)

        quit_surf = btn_font.render("QUIT", True, (255, 255, 255))
        quit_rect = quit_surf.get_rect(center=(SCREEN_SIZE[0] // 2, 300))
        screen.blit(quit_surf, quit_rect)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(event.pos):
                    score = start_game(screen, clock)
                    game_over(screen, clock, score)

                elif quit_rect.collidepoint(event.pos):
                    pg.quit()
                    sys.exit()

        pg.display.flip()
        clock.tick(60)


# ---------------------------------
# Game Over Screen
# ---------------------------------

def game_over(screen, clock, score):
    while True:
        screen.fill((0, 0, 0))

        title_font = load_font(50)
        small_font = load_font(28)

        over = title_font.render("GAME OVER", True, (255, 60, 60))
        over_rect = over.get_rect(center=(SCREEN_SIZE[0] // 2, 120))
        screen.blit(over, over_rect)

        score_text = small_font.render(f"Score: {score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(SCREEN_SIZE[0] // 2, 200))
        screen.blit(score_text, score_rect)

        prompt = small_font.render("Click to return to menu", True, (180, 180, 180))
        prompt_rect = prompt.get_rect(center=(SCREEN_SIZE[0] // 2, 280))
        screen.blit(prompt, prompt_rect)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                return  # ← FIXED indentation

        pg.display.flip()
        clock.tick(60)


# ---------------------------------
# Run the Game
# ---------------------------------
if __name__ == "__main__":
    pg.init()
    screen = pg.display.set_mode(SCREEN_SIZE)
    pg.display.set_caption("Pixel Serpent")
    clock = pg.time.Clock()
    menu(screen, clock)
