import pygame as pg
import sys
import random
import time
import os

# -------------------------
# Init
# -------------------------
pg.init()

# --- Visual / asset settings ---
FONT_FILE = "CookieCrisp-L36ly.ttf"
MUSIC_FILE = "background music.wav"
SCREEN_SIZE = (800, 450)

# -------------------------
# Helper: load font with fallback
# -------------------------
def load_font(size):
    """Return a pygame Font object. Uses FONT_FILE if present, otherwise SysFont."""
    try:
        if FONT_FILE and os.path.isfile(FONT_FILE):
            return pg.font.Font(FONT_FILE, size)
    except Exception:
        pass
    return pg.font.SysFont(None, size)

# -------------------------
# Helper: play music safely (non-fatal)
# -------------------------
def try_play_music():
    if not MUSIC_FILE or not os.path.isfile(MUSIC_FILE):
        print("Music file not found (skipping).")
        return
    try:
        if not pg.mixer.get_init():
            pg.mixer.init()
        pg.mixer.music.load(MUSIC_FILE)
        pg.mixer.music.play(-1)
    except Exception as e:
        print("Music not loaded:", e)

# -------------------------
# Outline text blit helper
# -------------------------
def blit_text_outline(surface, text, size, x, y,
                      inside_color=(255,255,255),
                      outline_color=(0,0,0),
                      center=False):

    font = load_font(size)

    offsets = [(-2,0),(2,0),(0,-2),(0,2),(-2,-2),(2,-2),(-2,2),(2,2)]
    for dx, dy in offsets:
        surf = font.render(text, True, outline_color)
        rect = surf.get_rect()
        if center:
            rect.center = (x + dx, y + dy)
        else:
            rect.topleft = (x + dx, y + dy)
        surface.blit(surf, rect)

    main_surf = font.render(text, True, inside_color)
    main_rect = main_surf.get_rect()
    if center:
        main_rect.center = (x, y)
    else:
        main_rect.topleft = (x, y)

    surface.blit(main_surf, main_rect)

# -------------------------
# Countdown (console)
# -------------------------
def countdown():
    try:
        timeamount = input("How many seconds you want to time?: ")
        timer = int(timeamount)
    except Exception:
        timer = 0

    while timer > 0:
        timer -= 1
        print(timer)
        pg.time.wait(1000)

# -------------------------
# Start Menu
# -------------------------
class StartMenu:
    def __init__(self):
        self.screen = pg.display.set_mode(SCREEN_SIZE)
        pg.display.set_caption("Pixel Serpent - Menu")
        self.clock = pg.time.Clock()
        self.buttons = []
        self.create_buttons()

    def create_buttons(self):
        self.buttons = [
            (pg.Rect(150,300,100,50), "Start", self.start_game),
            (pg.Rect(550,300,100,50), "Exit", self.exit_game)
        ]

    def start_game(self):
        start_game(moves_per_second=6, size=1)

    def exit_game(self):
        pg.quit(); sys.exit()

    def mainloop(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit(); sys.exit()

            self.screen.fill((35,38,117))

            blit_text_outline(
                self.screen, "PIXEL SERPENT", 80,
                SCREEN_SIZE[0]//2, 150,
                inside_color=(255,255,255),
                outline_color=(0,0,0),
                center=True
            )

            # Border
            color = (0,0,0)
            for x in range(0,800,10):
                t = pg.Surface((10,10)); t.fill(color)
                self.screen.blit(t,(x,0)); self.screen.blit(t,(x,440))
            for y in range(0,450,10):
                t = pg.Surface((10,10)); t.fill(color)
                self.screen.blit(t,(0,y)); self.screen.blit(t,(790,y))

            mouse = pg.mouse.get_pos()
            clicked = pg.mouse.get_pressed()[0]

            for rect, text, callback in self.buttons:
                highlight = (0,200,0) if rect.collidepoint(mouse) else (0,255,0)
                pg.draw.rect(self.screen, highlight, rect, border_radius=8)

                blit_text_outline(
                    self.screen, text, 24,
                    rect.centerx, rect.centery,
                    inside_color=(0,0,0),
                    outline_color=(255,255,255),
                    center=True
                )

                if rect.collidepoint(mouse) and clicked:
                    pg.time.wait(150)
                    callback()
                    return

            pg.display.update()
            self.clock.tick(30)
# -------------------------
# Snake and Apple (tile-based movement)
# -------------------------
class Snake:
    def __init__(self, moves_per_second, size):
        self.size = max(1, int(size))
        self.cell = 10 * self.size

        self.moves_per_second = max(1, float(moves_per_second))
        self.move_interval_ms = int(1000 / self.moves_per_second)
        self.last_move_time = pg.time.get_ticks()

        self.head = [20, 20]
        self.direction = [self.cell, 0]
        self.body = [self.head.copy()]
        self.length = 1

        self.image = pg.Surface((self.cell, self.cell))
        self.image.fill((0, 255, 0))

        self.score = 0

    def right(self):
        if self.direction != [-self.cell, 0]:
            self.direction = [self.cell, 0]

    def left(self):
        if self.direction != [self.cell, 0]:
            self.direction = [-self.cell, 0]

    def up(self):
        if self.direction != [0, self.cell]:
            self.direction = [0, -self.cell]

    def down(self):
        if self.direction != [0, -self.cell]:
            self.direction = [0, self.cell]

    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_move_time < self.move_interval_ms:
            return
        self.last_move_time = now

        new_head = [self.head[0] + self.direction[0],
                    self.head[1] + self.direction[1]]

        self.head = new_head
        self.body.insert(0, new_head.copy())

        if len(self.body) > self.length:
            self.body.pop()

    def grow(self):
        self.length += 1
        self.score += 1

    def head_rect(self):
        return pg.Rect(self.head[0], self.head[1], self.cell, self.cell)

    def check_self_collision(self):
        return any(self.head == seg for seg in self.body[1:])

class Apple:
    def __init__(self, size):
        self.size = max(1, int(size))
        self.cell = 10 * self.size
        self.image = pg.Surface((self.cell, self.cell))
        self.image.fill((255, 0, 0))
        self.pos = self.random_pos()

    def random_pos(self):
        x = random.randrange(10, SCREEN_SIZE[0] - 20, 10)
        y = random.randrange(10, SCREEN_SIZE[1] - 20, 10)
        return [x, y]

    def rect(self):
        return pg.Rect(self.pos[0], self.pos[1], self.cell, self.cell)

# -------------------------
# Game class
# -------------------------
class Game:
    def __init__(self, moves_per_second=6, size=1):
        self.screen = pg.display.set_mode(SCREEN_SIZE)
        pg.display.set_caption('Pixel Serpent')
        self.clock = pg.time.Clock()

        self.snake = Snake(moves_per_second, size)
        self.apple = Apple(size)
        self.size = size

        self.border_tiles = []
        border_color = (0, 0, 0)

        for x in range(0, SCREEN_SIZE[0], 10):
            surf = pg.Surface((10, 10)); surf.fill(border_color)
            self.border_tiles.append((surf, (x, 0), pg.Rect(x, 0, 10, 10)))
            surf2 = pg.Surface((10, 10)); surf2.fill(border_color)
            self.border_tiles.append((surf2, (x, SCREEN_SIZE[1] - 10),
                                      pg.Rect(x, SCREEN_SIZE[1] - 10, 10, 10)))

        for y in range(0, SCREEN_SIZE[1], 10):
            surf = pg.Surface((10, 10)); surf.fill(border_color)
            self.border_tiles.append((surf, (0, y), pg.Rect(0, y, 10, 10)))
            surf2 = pg.Surface((10, 10)); surf2.fill(border_color)
            self.border_tiles.append((surf2, (SCREEN_SIZE[0] - 10, y),
                                      pg.Rect(SCREEN_SIZE[0] - 10, y, 10, 10)))

        self.input_lock = False

        self.font_title = load_font(80)
        self.font_button = load_font(24)
        self.font_small = load_font(20)
        self.font_gameover = load_font(50)

    def draw_border(self):
        for surf, pos, _ in self.border_tiles:
            self.screen.blit(surf, pos)

    def draw_snake(self):
        for i, seg in enumerate(self.snake.body):
            s = pg.Surface((self.snake.cell, self.snake.cell))
            if i == 0:
                s.fill((0, 255, 0))
            else:
                s.fill((0, 200, 0))
            self.screen.blit(s, (seg[0], seg[1]))

    def game_over_screen(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit(); sys.exit()
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    return
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    return

            self.screen.fill((35, 38, 117))
            self.draw_border()

            blit_text_outline(
                self.screen,
                "Game Over :(   Score:",
                50, 20, 150,
                inside_color=(255,255,255),
                outline_color=(0,0,0)
            )

            blit_text_outline(
                self.screen,
                str(self.snake.score),
                50, 600, 150,
                inside_color=(255,255,255),
                outline_color=(0,0,0)
            )

            btn = pg.Rect(153, 300, 100, 50)
            mouse = pg.mouse.get_pos()
            clicked = pg.mouse.get_pressed()[0]

            color = (200, 200, 200) if btn.collidepoint(mouse) else (255, 255, 255)
            pg.draw.rect(self.screen, color, btn, border_radius=8)

            blit_text_outline(
                self.screen, "Restart", 24,
                btn.centerx, btn.centery,
                inside_color=(0,0,0),
                outline_color=(255,255,255),
                center=True
            )

            if btn.collidepoint(mouse) and clicked:
                pg.time.wait(150)
                return

            pg.display.update()
            self.clock.tick(30)
# ---------------------------------
# Gameplay Loop
# ---------------------------------
def start_game(screen, clock):
    game = Game()
    running = True

    while running:
        dt = clock.tick(10) / 1000  # Limit FPS

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

        # Check for game over
        if game.check_collision():
            return game.score  # return score to menu

        # Draw everything
        screen.fill((0, 0, 0))
        game.draw(screen)
        pg.display.flip()


# ---------------------------------
# Menu Screen
# ---------------------------------
def menu(screen, clock):
    while True:
        screen.fill((15, 15, 15))

        title_font = load_font(50)
        play_font = load_font(32)

        # Title
        title_surf = title_font.render("SNAKE GAME", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SCREEN_SIZE[0] // 2, 100))
        screen.blit(title_surf, title_rect)

        # Play Button
        play_surf = play_font.render("PLAY", True, (255, 255, 255))
        play_rect = play_surf.get_rect(center=(SCREEN_SIZE[0] // 2, 250))
        screen.blit(play_surf, play_rect)

        # Quit Button
        quit_surf = play_font.render("QUIT", True, (255, 255, 255))
        quit_rect = quit_surf.get_rect(center=(SCREEN_SIZE[0] // 2, 320))
        screen.blit(quit_surf, quit_rect)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(event.pos):
                    score = start_game(screen, clock)
                    game_over(screen, clock, score)

                if quit_rect.collidepoint(event.pos):
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

        # Game Over
        over = title_font.render("GAME OVER", True, (255, 50, 50))
        over_rect = over.get_rect(center=(SCREEN_SIZE[0] // 2, 120))
        screen.blit(over, over_rect)

        # Score
        score_text = small_font.render(f"Score: {score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(SCREEN_SIZE[0] // 2, 200))
        screen.blit(score_text, score_rect)

        # Prompt
        prompt = small_font.render("Click to return to menu", True, (200, 200, 200))
        prompt_rect = prompt.get_rect(center=(SCREEN_SIZE[0] // 2, 280))
        screen.blit(prompt, prompt_rect)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                return  # back to menu

        pg.display.flip()
        clock.tick(60)

# ---------------------------------
# Run Game
# ---------------------------------
if __name__ == "__main__":
    screen = pg.display.set_mode(SCREEN_SIZE)
    pg.display.set_caption("Snake Game")
    clock = pg.time.Clock()
    menu(screen, clock)
