# snake_game_cookiecrisp_outline.py
import pygame as pg
import sys
import random
import time

# -------------------------
# Init
# -------------------------
pg.init()

FONT_FILE = "CookieCrisp-L36ly.ttf"   
MUSIC_FILE = "background music.wav"         
SCREEN_SIZE = (800, 450)

# -------------------------
def blit_text_outline(surface, text, size, x, y, inside_color=(255,255,255), outline_color=(0,0,0), center=False):
    """
    font = pg.font.Font(FONT_FILE, size)
    # outline offsets (8-directional; adjust distance for thicker outline)
    offsets = [(-2,0),(2,0),(0,-2),(0,2),(-2,-2),(2,-2),(-2,2),(2,2)]
    for dx, dy in offsets:
        surf = font.render(text, True, outline_color)
        rect = surf.get_rect()
        if center:
            rect.center = (x + dx, y + dy)
            surface.blit(surf, rect)
        else:
            surface.blit(surf, (x + dx, y + dy))
    main_surf = font.render(text, True, inside_color)
    main_rect = main_surf.get_rect()
    if center:
        main_rect.center = (x, y)
        surface.blit(main_surf, main_rect)
    else:
        surface.blit(main_surf, (x, y))

# simple helper to get a font object (if you need a direct Font for measuring)
def get_cookie_font(size):
    return pg.font.Font(FONT_FILE, size)

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

# Try to play music (non-fatal)
def try_play_music():
    try:
        pg.mixer.init(22050, -16, 2, 4096)
        pg.mixer.music.load(MUSIC_FILE)
        pg.mixer.music.play(20, 5.0)
    except Exception as e:
        print("Music not loaded:", e)

# -------------------------
# Collision helpers
# -------------------------
def collide(x1,y1,x2,y2,x3,y3,x4,y4):
    return ((x3+x4) > x1 > x3 and (y3+y4) > y1 > y3) or ((x3+x4) > x2 > x3 and (y3+y4) > y2 > y3)

def collide2(x1,y1,x2,y2,x3,y3,x4,y4,size):
    return ((x3+(11*size)) > x1 > x3-1 and (y3+(11*size)) > y1 > y3-1) or ((x3+(11*size)) > x2 >x3-1 and (y3+(11*size)) > y2 > y3-1)

def collide3(x1,y1,x2,y2,x3,y3,x4,y4,size):
    return ((x3+(10*size)) > x1 > x3 and (y3+(10*size)) > y1 > y3) or ((x3+(10*size)) > x2 >x3 and (y3+(10*size)) > y2 > y3)

# -------------------------
# Snake and Apple
# -------------------------
class Snake:
    def __init__(self,speed, size):
        self.pos = [20,20]
        self.size = size
        self.cell = 10 * size
        self.image = pg.Surface((self.cell,self.cell))
        self.image.fill((0,255,0))
        self.speed = speed
        self.direction = [0,0]
        self.score = 0
        self.segments = []      # list of positions for body segments
        self.old_pos = []       # buffer of previous head positions
        self.max_segments = 0

    def right(self): self.direction = [self.speed,0]
    def left(self):  self.direction = [-self.speed,0]
    def up(self):    self.direction = [0,-self.speed]
    def down(self):  self.direction = [0,self.speed]

    def update(self):
        # record last head position
        self.old_pos.insert(0, [self.pos[0], self.pos[1]])
        # move head
        self.pos[0] += self.direction[0]
        self.pos[1] += self.direction[1]

        # trim old_pos to reasonable size to avoid memory growth
        max_old = max( (self.max_segments+2) * max(1, int((11*self.size) // max(1, int(abs(self.speed))))) , 50)
        if len(self.old_pos) > max_old:
            self.old_pos = self.old_pos[:max_old]

        # rebuild segments from old_pos every update
        self.segments = []
        step = max(1, int((11*self.size)//max(1,int(abs(self.speed)))))
        idx = step
        for i in range(self.max_segments):
            if idx-1 < len(self.old_pos):
                self.segments.append([self.old_pos[idx-1][0], self.old_pos[idx-1][1]])
            else:
                self.segments.append([self.pos[0], self.pos[1]])
            idx += step

    def add_apple(self):
        self.score += 1
        self.max_segments += 1

    def check_collisions(self, x):
        return collide(self.pos[0],self.pos[1],self.pos[0]+self.cell,self.pos[1]+self.cell, x[0],x[1],x[0]+10,x[1]+10)

    def check_apple(self, x):
        return collide2(self.pos[0],self.pos[1],self.pos[0]+self.cell,self.pos[1]+self.cell, x[0],x[1],x[0]+10,x[1]+10, self.size)

    def check_self(self):
        for seg in self.segments:
            if self.pos[0] == seg[0] and self.pos[1] == seg[1]:
                return True
        return False

class Apple:
    def __init__(self,size):
        self.size = size
        self.cell = 10 * size
        self.pos = [random.randrange(10, 780,10), random.randrange(10,430,10)]
        self.image = pg.Surface((self.cell,self.cell))
        self.image.fill((255,0,0))

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
        self.left=self.right=self.up=self.down=False

        color = (0,0,0)
        for x in range(0,800,10):
            t=pg.Surface((10,10)); t.fill(color)
            self.blocks.append([t, [x,0]])
            t2=pg.Surface((10,10)); t2.fill(color)
            self.blocks.append([t2, [x,440]])
        for y in range(0,450,10):
            t=pg.Surface((10,10)); t.fill(color)
            self.blocks.append([t, [0,y]])
            t2=pg.Surface((10,10)); t2.fill(color)
            self.blocks.append([t2, [790,y]])

        self.apple = Apple(size)

        # fonts using CookieCrisp explicitly
        self.font_title = pg.font.Font(FONT_FILE, 80)
        self.font_button = pg.font.Font(FONT_FILE, 24)
        self.font_gameover = pg.font.Font(FONT_FILE, 50)

    def draw_border(self):
        for b in self.blocks:
            self.screen.blit(b[0], b[1])

    def draw_snake(self):
        # draw head
        self.screen.blit(self.snake.image, self.snake.pos)
        # draw body
        for seg in self.snake.segments:
            s = pg.Surface((self.snake.cell,self.snake.cell))
            s.fill((0,200,0))
            self.screen.blit(s, seg)

    def game_over_screen(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit(); sys.exit()
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    return

            self.screen.fill((35,38,117))
            self.draw_border()
            # outlined Game Over (using the blit helper which uses CookieCrisp)
            blit_text_outline(self.screen, "Game Over :(    Score:", 50, 20, 150, inside_color=(255,255,255), outline_color=(0,0,0), center=False)
            blit_text_outline(self.screen, str(self.snake.score), 50, 600, 150, inside_color=(255,255,255), outline_color=(0,0,0), center=False)

            # Restart button
            btn = pg.Rect(153,300,100,50)
            mouse = pg.mouse.get_pos()
            clicked = pg.mouse.get_pressed()[0]
            color = (200,200,200) if btn.collidepoint(mouse) else (255,255,255)
            pg.draw.rect(self.screen, color, btn, border_radius=8)
            blit_text_outline(self.screen, "Restart", 24, btn.centerx, btn.centery, inside_color=(0,0,0), outline_color=(255,255,255), center=True)

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
                        self.reset_dirs(); self.snake.right(); self.right=True
                    if event.key == pg.K_LEFT and not self.right:
                        self.reset_dirs(); self.snake.left(); self.left=True
                    if event.key == pg.K_UP and not self.down:
                        self.reset_dirs(); self.snake.up(); self.up=True
                    if event.key == pg.K_DOWN and not self.up:
                        self.reset_dirs(); self.snake.down(); self.down=True

            self.snake.update()

            # border collisions
            for b in self.blocks:
                if self.snake.check_collisions(b[1]):
                    self.game_over_screen()
                    return

            # self collision
            if self.snake.check_self():
                self.game_over_screen()
                return

            # apple eaten
            if self.snake.check_apple(self.apple.pos):
                self.snake.add_apple()
                # move apple to a new place
                self.apple.pos = [random.randrange(10, 780,10), random.randrange(10,430,10)]

            # draw everything
            self.screen.fill((35,38,117))
            self.draw_border()
            self.screen.blit(self.apple.image, self.apple.pos)
            self.draw_snake()
            # score (small)
            blit_text_outline(self.screen, f"Score: {self.snake.score}", 20, 10, 10, inside_color=(255,255,255), outline_color=(0,0,0), center=False)

            pg.display.update()

    def reset_dirs(self):
        self.left=self.right=self.up=self.down=False

# -------------------------
# Start Menu (safe implementation)
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
        start_game(speed=0.5, size=1)

    def exit_game(self):
        pg.quit(); sys.exit()

    def mainloop(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit(); sys.exit()

            self.screen.fill((35,38,117))
            # title using outline helper (centered)
            blit_text_outline(self.screen, "PIXEL SERPENT", 80, SCREEN_SIZE[0]//2, 150, inside_color=(255,255,255), outline_color=(0,0,0), center=True)

            # draw border decoration
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
                blit_text_outline(self.screen, text, 24, rect.centerx, rect.centery, inside_color=(0,0,0), outline_color=(255,255,255), center=True)
                if rect.collidepoint(mouse) and clicked:
                    pg.time.wait(150)
                    callback()
                    return

            pg.display.update()
            self.clock.tick(30)

# -------------------------
# Top-level helpers
# -------------------------
def start_game(speed=0.5, size=1):
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
