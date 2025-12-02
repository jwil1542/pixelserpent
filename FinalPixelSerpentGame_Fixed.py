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
        # size: tile multiplier (1 = 10px)
        self.size = max(1, int(size))
        self.cell = 10 * self.size  # tile size in pixels
        # movement timing
        self.moves_per_second = max(1, float(moves_per_second))
        self.move_interval_ms = int(1000 / self.moves_per_second)
        self.last_move_time = pg.time.get_ticks()

        # starting position (aligned to 10px grid)
        self.head = [20, 20]  # pixel coordinates, always multiples of self.cell
        self.direction = [self.cell, 0]  # start moving right by one tile each move
        self.body = [self.head.copy()]  # list of tile positions (head first)
        self.length = 1

        # visuals
        self.image = pg.Surface((self.cell, self.cell))
        self.image.fill((0, 255, 0))

        self.score = 0

    def right(self):
        # prevent reversing
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
        """Move the snake only when enough time has passed (tile-based)."""
        now = pg.time.get_ticks()
        if now - self.last_move_time < self.move_interval_ms:
            return  # not time to move yet
        self.last_move_time = now

        # compute new head tile
        new_head = [self.head[0] + self.direction[0], self.head[1] + self.direction[1]]
        self.head = new_head
        self.body.insert(0, new_head.copy())  # add new head
        # trim tail to length
        if len(self.body) > self.length:
            self.body.pop()

    def grow(self):
        self.length += 1
        self.score += 1

    def head_rect(self):
        return pg.Rect(self.head[0], self.head[1], self.cell, self.cell)

    def check_self_collision(self):
        # True if head overlaps any body segment after the head (i.e., index > 0)
        return any(self.head == seg for seg in self.body[1:])

class Apple:
    def __init__(self, size):
        self.size = max(1, int(size))
        self.cell = 10 * self.size
        self.image = pg.Surface((self.cell, self.cell))
        self.image.fill((255, 0, 0))
        self.pos = self.random_pos()

    def random_pos(self):
        # choose grid-aligned pos within play area avoiding the border (10px border)
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

        # snake and apple
        self.snake = Snake(moves_per_second, size)
        self.apple = Apple(size)
        self.size = size

        # border tiles cache: store surfaces and rects for drawing + collision
        self.border_tiles = []
        border_color = (0, 0, 0)
        # top and bottom rows
        for x in range(0, SCREEN_SIZE[0], 10):
            surf = pg.Surface((10, 10)); surf.fill(border_color)
            self.border_tiles.append((surf, (x, 0), pg.Rect(x, 0, 10, 10)))
            surf2 = pg.Surface((10, 10)); surf2.fill(border_color)
            self.border_tiles.append((surf2, (x, SCREEN_SIZE[1] - 10), pg.Rect(x, SCREEN_SIZE[1] - 10, 10, 10)))
        # left and right columns
        for y in range(0, SCREEN_SIZE[1], 10):
            surf = pg.Surface((10, 10)); surf.fill(border_color)
            self.border_tiles.append((surf, (0, y), pg.Rect(0, y, 10, 10)))
            surf2 = pg.Surface((10, 10)); surf2.fill(border_color)
            self.border_tiles.append((surf2, (SCREEN_SIZE[0] - 10, y), pg.Rect(SCREEN_SIZE[0] - 10, y, 10, 10)))

        # input state to prevent immediate reverse while key held
        self.input_lock = False

        # fonts (use load_font to keep your style if available)
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
                s.fill((0, 255, 0))  # head
            else:
                s.fill((0, 200, 0))  # body
            self.screen.blit(s, (seg[0], seg[1]))

    def game_over_screen(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit(); sys.exit()
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    return
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    # clicking anywhere restarts (or use restart button)
                    return

            self.screen.fill((35, 38, 117))
            self.draw_border()
            blit_text_outline(self.screen, "Game Over :(    Score:", 50, 20, 150,
                              inside_color=(255,255,255), outline_color=(0,0,0), center=False)
            blit_text_outline(self.screen, str(self.snake.score), 50, 600, 150,
                              inside_color=(255,255,255), outline_color=(0,0,0), center=False)

            # Restart button
            btn = pg.Rect(153, 300, 100, 50)
            mouse = pg.mouse.get_pos()
            clicked = pg.mouse.get_pressed()[0]
            color = (200, 200, 200) if btn.collidepoint(mouse) else (255, 255, 255)
            pg.draw.rect(self.screen, color, btn, border_radius=8)
            blit_text_outline(self.screen, "Restart", 24, btn.centerx, btn.centery,
                              inside_color=(0,0,0), outline_color=(255,255,255), center=True)
            if btn.collidepoint(mouse) and clicked:
                pg.time.wait(150)
                return

            pg.display.update()
            self.clock.tick(30)

    def loop(self):
        while True:
            # keep a stable framerate; movement is regulated internally by Snake.move_interval_ms
            self.clock.tick(60)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit(); sys.exit()
                elif event.type == pg.KEYDOWN:
                    # Use input_lock to avoid double-processing keys between moves
                    if event.key == pg.K_RIGHT:
                        self.snake.right()
                    elif event.key == pg.K_LEFT:
                        self.snake.left()
                    elif event.key == pg.K_UP:
                        self.snake.up()
                    elif event.key == pg.K_DOWN:
                        self.snake.down()

            # update snake (only updates position when timer says so)
            prev_head = self.snake.head.copy()
            self.snake.update()
            # after update, if head didn't move (not time yet), we skip collision checks
            if self.snake.head == prev_head:
                # still draw, but no collision checks yet
                self.screen.fill((35, 38, 117))
                self.draw_border()
                self.screen.blit(self.apple.image, (self.apple.pos[0], self.apple.pos[1]))
                self.draw_snake()
                blit_text_outline(self.screen, f"Score: {self.snake.score}", 20, 10, 10,
                                  inside_color=(255,255,255), outline_color=(0,0,0), center=False)
                pg.display.update()
                continue

            # Border collision: if head touches any border rect -> game over
            head_rect = self.snake.head_rect()
            collided_border = any(head_rect.colliderect(rect) for _, _, rect in self.border_tiles)
            if collided_border:
                self.game_over_screen()
                return

            # Self collision
            if self.snake.check_self_collision():
                self.game_over_screen()
                return

            # Apple eaten (exact tile match)
            if self.snake.head == self.apple.pos:
                self.snake.grow()
                # move apple to a new location not on the snake's body and not on border
                new_pos = self.apple.random_pos()
                # ensure not colliding with snake body
                attempts = 0
                while new_pos in self.snake.body and attempts < 200:
                    new_pos = self.apple.random_pos()
                    attempts += 1
                self.apple.pos = new_pos

            # draw everything
            self.screen.fill((35, 38, 117))
            self.draw_border()
            self.screen.blit(self.apple.image, (self.apple.pos[0], self.apple.pos[1]))
            self.draw_snake()
            blit_text_outline(self.screen, f"Score: {self.snake.score}", 20, 10, 10,
                              inside_color=(255,255,255), outline_color=(0,0,0), center=False)
            pg.display.update()

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
        # (rect, text, callback)
        self.buttons = [
            (pg.Rect(150,300,100,50), "Start", self.start_game),
            (pg.Rect(550,300,100,50), "Exit", self.exit_game)
        ]

    def start_game(self):
        # speed here is moves-per-second; use 6 for a comfortable default
        start_game(moves_per_second=6, size=1)

    def exit_game(self):
        pg.quit(); sys.exit()

    def mainloop(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit(); sys.exit()

            self.screen.fill((35,38,117))
            blit_text_outline(self.screen, "PIXEL SERPENT", 80, SCREEN_SIZE[0]//2, 150,
                              inside_color=(255,255,255), outline_color=(0,0,0), center=True)

            # border decoration
            color = (0,0,0)
            for x in range(0,800,10):
                t = pg.Surface((10,10)); t.fill(color)
                self.screen.blit(t,(x,0)); self.screen.blit(t,(x,440))
            for y in range(0,450,10):
                t = pg.Surface((10,10)); t.fill(color)
                self.screen.blit(t,(0,y)); self.screen.blit(t,(790,y))

            # draw buttons and detect clicks
            mouse = pg.mouse.get_pos()
            clicked = pg.mouse.get_pressed()[0]
            for rect, text, callback in self.buttons:
                highlight = (0,200,0) if rect.collidepoint(mouse) else (0,255,0)
                pg.draw.rect(self.screen, highlight, rect, border_radius=8)
                blit_text_outline(self.screen, text, 24, rect.centerx, rect.centery,
                                  inside_color=(0,0,0), outline_color=(255,255,255), center=True)
                if rect.collidepoint(mouse) and clicked:
                    pg.time.wait(150)
                    callback()
                    return

            pg.display.update()
            self.clock.tick(30)

# -------------------------
# Top-level helpers
# -------------------------
def start_game(moves_per_second=6, size=1):
    g = Game(moves_per_second=moves_per_second, size=size)
    g.loop()

def menu():
    m = StartMenu()
    m.mainloop()

# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    # optional: ask for a countdown (keeps your original behavior)
    try:
        countdown()
    except Exception:
        pass

    # try music in background (non-fatal)
    try_play_music()

    # open menu
    menu()
