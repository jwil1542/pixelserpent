# FinalPixelSerpentGame_fixed.py
import pygame as pg
import sys
import random
import time
import os


pg.init()

FONT_FILE = "CookieCrisp-L36ly.ttf"   # optional; fallback to system font if missing
MUSIC_FILE = "background_music.wav"   # renamed to avoid problems with spaces (optional)
SCREEN_SIZE = (800, 450)

# -------------------------
# Helpers for fonts & music
# -------------------------
def load_font(size):
    """Return a pygame Font object, using the local FONT_FILE if present,
    otherwise fall back to a default system font."""
    if FONT_FILE and os.path.isfile(FONT_FILE):
        try:
            return pg.font.Font(FONT_FILE, size)
        except Exception:
            pass
    # fallback
    return pg.font.SysFont(None, size)

def try_play_music():
    """Try to play background music but don't crash if it fails."""
    if not MUSIC_FILE or not os.path.isfile(MUSIC_FILE):
        print("Music file not found; skipping music.")
        return
    try:
        # initialize mixer more safely
        if not pg.mixer.get_init():
            pg.mixer.init()
        pg.mixer.music.load(MUSIC_FILE)
        pg.mixer.music.play(-1)  # loop forever
    except Exception as e:
        print("Music not loaded:", e)

# -------------------------
# Text outline helper
# -------------------------
def blit_text_outline(surface, text, size, x, y,
                      inside_color=(255,255,255),
                      outline_color=(0,0,0),
                      center=False):
    """
    Draw text with an outline on `surface`.
    """
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
# Snake and Apple (using Rect collisions)
# -------------------------
class Snake:
    def __init__(self, speed, size):
        # Use integers for positions for reliable blitting and collisions
        self.pos = [20, 20]
        self.size = max(1, int(size))
        self.cell = 10 * self.size
        self.image = pg.Surface((self.cell, self.cell))
        self.image.fill((0, 255, 0))
        self.speed = float(speed)
        # direction will be in pixels per update; ensure integer movement
        self.direction = [0, 0]
        self.score = 0
        self.segments = []      # list of positions for body segments
        self.old_pos = []       # buffer of previous head positions
        self.max_segments = 0

    def right(self): self.direction = [int(self.speed), 0]
    def left(self):  self.direction = [-int(self.speed), 0]
    def up(self):    self.direction = [0, -int(self.speed)]
    def down(self):  self.direction = [0, int(self.speed)]

    def update(self):
        # record last head position
        self.old_pos.insert(0, [int(self.pos[0]), int(self.pos[1])])

        # move head
        self.pos[0] += int(self.direction[0])
        self.pos[1] += int(self.direction[1])

        # trim old_pos to reasonable size to avoid memory growth
        step = max(1, int((11 * self.size) // max(1, abs(int(self.speed)))))
        max_old = max((self.max_segments + 2) * max(1, step), 50)
        if len(self.old_pos) > max_old:
            self.old_pos = self.old_pos[:max_old]

        # rebuild segments from old_pos every update
        self.segments = []
        idx = step
        for i in range(self.max_segments):
            if idx - 1 < len(self.old_pos):
                self.segments.append([self.old_pos[idx - 1][0], self.old_pos[idx - 1][1]])
            else:
                self.segments.append([int(self.pos[0]), int(self.pos[1])])
            idx += step

    def add_apple(self):
        self.score += 1
        self.max_segments += 1

    def head_rect(self):
        return pg.Rect(int(self.pos[0]), int(self.pos[1]), self.cell, self.cell)

    def check_collisions_with_rect(self, rect):
        return self.head_rect().colliderect(rect)

    def check_apple(self, apple_pos):
        apple_rect = pg.Rect(int(apple_pos[0]), int(apple_pos[1]), 10 * self.size, 10 * self.size)
        return self.head_rect().colliderect(apple_rect)

    def check_self(self):
        hx, hy = int(self.pos[0]), int(self.pos[1])
        for seg in self.segments:
            if hx == seg[0] and hy == seg[1]:
                return True
        return False

class Apple:
    def __init__(self, size):
        self.size = max(1, int(size))
        self.cell = 10 * self.size
        self.pos = [random.randrange(10, 780, 10), random.randrange(10, 430, 10)]
        self.image = pg.Surface((self.cell, self.cell))
        self.image.fill((255, 0, 0))

    def rect(self):
        return pg.Rect(int(self.pos[0]), int(self.pos[1]), self.cell, self.cell)

# -------------------------
# Game
# -------------------------
class Game:
    def __init__(self, speed, size=1):
        self.screen = pg.display.set_mode(SCREEN_SIZE)
        pg.display.set_caption('Pixel Serpent')
        self.clock = pg.time.Clock()
        self.snake = Snake(speed, size)
        self.size = size
        self.blocks = []
        self.left = self.right = self.up = self.down = False

        color = (0, 0, 0)
        # create border tiles and also keep Rects for collisions
        for x in range(0, 800, 10):
            t = pg.Surface((10, 10)); t.fill(color)
            self.blocks.append((t, (x, 0), pg.Rect(x, 0, 10, 10)))
            t2 = pg.Surface((10, 10)); t2.fill(color)
            self.blocks.append((t2, (x, 440), pg.Rect(x, 440, 10, 10)))
        for y in range(0, 450, 10):
            t = pg.Surface((10, 10)); t.fill(color)
            self.blocks.append((t, (0, y), pg.Rect(0, y, 10, 10)))
            t2 = pg.Surface((10, 10)); t2.fill(color)
            self.blocks.append((t2, (790, y), pg.Rect(790, y, 10, 10)))

        self.apple = Apple(size)

        # fonts using load_font (with fallback)
        self.font_title = load_font(80)
        self.font_button = load_font(24)
        self.font_gameover = load_font(50)

    def draw_border(self):
        for t, pos, _ in self.blocks:
            self.screen.blit(t, pos)

    def draw_snake(self):
        # draw head
        self.screen.blit(self.snake.image, (int(self.snake.pos[0]), int(self.snake.pos[1])))
        # draw body
        for seg in self.snake.segments:
            s = pg.Surface((self.snake.cell, self.snake.cell))
            s.fill((0, 200, 0))
            self.screen.blit(s, (seg[0], seg[1]))

    def game_over_screen(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit(); sys.exit()
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    return

            self.screen.fill((35, 38, 117))
            self.draw_border()

            # Game Over text
            blit_text_outline(self.screen, "Game Over :(    Score:", 50, 20, 150,
                              inside_color=(255, 255, 255), outline_color=(0, 0, 0), center=False)
            blit_text_outline(self.screen, str(self.snake.score), 50, 600, 150,
                              inside_color=(255, 255, 255), outline_color=(0, 0, 0), center=False)

            # Restart button
            btn = pg.Rect(153, 300, 100, 50)
            mouse = pg.mouse.get_pos()
            clicked = pg.mouse.get_pressed()[0]
            color = (200, 200, 200) if btn.collidepoint(mouse) else (255, 255, 255)
            pg.draw.rect(self.screen, color, btn, border_radius=8)
            blit_text_outline(self.screen, "Restart", 24, btn.centerx, btn.centery,
                              inside_color=(0, 0, 0), outline_color=(255, 255, 255), center=True)

            if btn.collidepoint(mouse) and clicked:
                pg.time.wait(150)
                return

            pg.display.update()
            self.clock.tick(30)

    def loop(self):
        while True:
            self.clock.tick(15)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit(); sys.exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_RIGHT and not self.left:
                        self.reset_dirs(); self.snake.right(); self.right = True
                    if event.key == pg.K_LEFT and not self.right:
                        self.reset_dirs(); self.snake.left(); self.left = True
                    if event.key == pg.K_UP and not self.down:
                        self.reset_dirs(); self.snake.up(); self.up = True
                    if event.key == pg.K_DOWN and not self.up:
                        self.reset_dirs(); self.snake.down(); self.down = True

            self.snake.update()

            # border collisions (use block rects)
            for _, _, rect in self.blocks:
                if self.snake.check_collisions_with_rect(rect):
                    self.game_over_screen()
                    return

            # self collision
            if self.snake.check_self():
                self.game_over_screen()
                return

            # apple eaten
            if self.snake.check_apple(self.apple.pos):
                self.snake.add_apple()
                # move apple to a new place (avoid placing under borders)
                self.apple.pos = [random.randrange(10, SCREEN_SIZE[0]-20, 10),
                                  random.randrange(10, SCREEN_SIZE[1]-20, 10)]

            # draw everything
            self.screen.fill((35, 38, 117))
            self.draw_border()
            self.screen.blit(self.apple.image, (int(self.apple.pos[0]), int(self.apple.pos[1])))
            self.draw_snake()
            # score (small)
            blit_text_outline(self.screen, f"Score: {self.snake.score}", 20, 10, 10,
                              inside_color=(255, 255, 255), outline_color=(0, 0, 0), center=False)

            pg.display.update()

    def reset_dirs(self):
        self.left = self.right = self.up = self.down = False

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
            (pg.Rect(150, 300, 100, 50), "Start", self.start_game),
            (pg.Rect(550, 300, 100, 50), "Exit", self.exit_game)
        ]

    def start_game(self):
        start_game(speed=1, size=1)

    def exit_game(self):
        pg.quit(); sys.exit()

    def mainloop(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit(); sys.exit()

            self.screen.fill((35, 38, 117))
            # title using outline helper (centered)
            blit_text_outline(self.screen, "PIXEL SERPENT", 80, SCREEN_SIZE[0] // 2, 150,
                              inside_color=(255, 255, 255), outline_color=(0, 0, 0), center=True)

            # draw border decoration
            color = (0, 0, 0)
            for x in range(0, 800, 10):
                t = pg.Surface((10, 10)); t.fill(color)
                self.screen.blit(t, (x, 0)); self.screen.blit(t, (x, 440))
            for y in range(0, 450, 10):
                t = pg.Surface((10, 10)); t.fill(color)
                self.screen.blit(t, (0, y)); self.screen.blit(t, (790, y))

            # draw buttons and detect clicks
            mouse = pg.mouse.get_pos()
            clicked = pg.mouse.get_pressed()[0]
            for rect, text, callback in self.buttons:
                highlight = (0, 200, 0) if rect.collidepoint(mouse) else (0, 255, 0)
                pg.draw.rect(self.screen, highlight, rect, border_radius=8)
                blit_text_outline(self.screen, text, 24, rect.centerx, rect.centery,
                                  inside_color=(0, 0, 0), outline_color=(255, 255, 255), center=True)
                if rect.collidepoint(mouse) and clicked:
                    pg.time.wait(150)
                    callback()
                    return

            pg.display.update()
            self.clock.tick(30)

# -------------------------
# Top-level helpers
# -------------------------
def start_game(speed=1, size=1):
    g = Game(speed, size)
    g.loop()

def menu():
    m = StartMenu()
    m.mainloop()

# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    countdown()
    try_play_music()
    menu()
