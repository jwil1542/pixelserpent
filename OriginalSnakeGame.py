import pygame as pg
import sys, random
import time
import pygame, sys

timeamount = input("How many seconds you want to time?:")
timer = int(timeamount)
while (timer != 0):
    timer -= 1
    print(timer)
    pg.time.wait(1000)

clock = pygame.time.Clock()
clock.tick(10)
pg.mixer.init(22050, -16, 2, 4096)
pg.mixer.music.load("jazz.wav")
pg.mixer.music.play(20, 5.0)

# Load Cute Font
def load_font(size):
    return pg.font.Font("CookieCrisp-L36ly.ttf", size)


def collide(x1, y1, x2, y2, x3, y3, x4, y4):
    if (x3 + x4) > x1 > x3 and (y3 + y4) > y1 > y3 or (x3 + x4) > x2 > x3 and (y3 + y4) > y2 > y3:
        return True
    else:
        return False


def collide2(x1, y1, x2, y2, x3, y3, x4, y4, size):
    if (x3 + (11 * size)) > x1 > x3 - 1 and (y3 + (11 * size)) > y1 > y3 - 1 or (x3 + (11 * size)) > x2 > x3 - 1 and (y3 + (11 * size)) > y2 > y3 - 1:
        return True
    else:
        return False


def collide3(x1, y1, x2, y2, x3, y3, x4, y4, size):
    if (x3 + (10 * size)) > x1 > x3 and (y3 + (10 * size)) > y1 > y3 or (x3 + (10 * size)) > x2 > x3 and (y3 + (10 * size)) > y2 > y3:
        return True
    else:
        return False


class snake():
    def __init__(self, speed, size):
        self.pos = [20, 20]
        self.image = pg.Surface((10 * size, 10 * size))
        self.image.fill((0, 255, 0))
        self.speed = speed
        self.size = size
        self.images = []
        self.old_pos = [[20, 20]]
        self.direction = [0, 0]
        self.score = 0

    def right(self):
        self.direction = [self.speed, 0]

    def left(self):
        self.direction = [-self.speed, 0]

    def up(self):
        self.direction = [0, -self.speed]

    def down(self):
        self.direction = [0, self.speed]

    def update(self):
        if self.old_pos[-1] != self.pos:
            self.old_pos.append([self.pos[0], self.pos[1]])
        self.pos[0] += self.direction[0]
        self.pos[1] += self.direction[1]
        a = 1
        for x in self.images:
            try:
                x[1] = self.old_pos[-a]
            except:
                pass
            a += 1

    def check_collisions(self, x):
        return collide(self.pos[0], self.pos[1], self.pos[0] + 10, self.pos[1] + 10, x[0], x[1], x[0] + 10, x[1] + 10)

    def check_apple(self, x):
        return collide2(self.pos[0], self.pos[1], self.pos[0] + 10, self.pos[1] + 10, x[0], x[1], x[0] + 10, x[1] + 10, self.size)

    def check_collisions2(self, x):
        return collide3(self.pos[0], self.pos[1], self.pos[0] + 10, self.pos[1] + 10, x[0], x[1], x[0] + 10, x[1] + 10, self.size)

    def add_apple(self):
        self.score += 1
        block = pg.Surface((10 * self.size, 10 * self.size))
        block.fill((0, 255, 0))
        self.images.append([block, [10, 10]])


class apple():
    def __init__(self, size):
        self.pos = [random.randrange(10, 780, 10), random.randrange(10, 430, 10)]
        self.image = pg.Surface((10 * size, 10 * size))
        self.image.fill((255, 0, 0))


class game():
    def __init__(self, speed, size=1):
        self.screen = pg.display.set_mode((800, 450))
        pg.display.set_caption('Snake Game')
        self.snake = snake(speed, size)
        self.blocks = []
        self.size = size
        self.left = self.right = self.up = self.down = False
        self.hover = False
        self.click0 = False

        color = (0, 0, 0)
        for x in range(0, 800, 10):
            t = pg.Surface((10, 10))
            t.fill(color)
            self.blocks.append([t, [x, 0]])
        for x in range(0, 800, 10):
            t = pg.Surface((10, 10))
            t.fill(color)
            self.blocks.append([t, [x, 440]])
        for x in range(0, 450, 10):
            t = pg.Surface((10, 10))
            t.fill(color)
            self.blocks.append([t, [0, x]])
        for x in range(0, 450, 10):
            t = pg.Surface((10, 10))
            t.fill(color)
            self.blocks.append([t, [790, x]])

        self.apple = apple(size)

    def over(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit()

            for x in self.blocks:
                self.screen.blit(x[0], x[1])

            txts = load_font(50).render('Game Over    Score:', True, (255, 255, 255))
            self.screen.blit(txts, (20, 150))

            txts = load_font(50).render(str(self.snake.score), True, (255, 255, 255))
            self.screen.blit(txts, (600, 150))

            pg.display.update()
            self.make_button((153, 300, 100, 50), 'Restart', [(255, 255, 255), (150, 150, 150)], action=lambda: restart())

            if self.hover:
                click = pg.mouse.get_pressed()
                if click[0] == 1:
                    self.click0 = True
                if self.click0 and click[0] == 0:
                    self.buttonclick()
                    self.click0 = False

    def make_button(self, pos, text, color, action=None, textsize=20):
        mouse = pg.mouse.get_pos()
        oldpos = pos
        rect = pg.Rect(pos)
        pos = rect.topleft
        rect.topleft = 0, 0
        rectangle = pg.Surface(rect.size, pg.SRCALPHA)

        circle = pg.Surface([min(rect.size) * 3] * 2, pg.SRCALPHA)
        pg.draw.ellipse(circle, (0, 0, 0), circle.get_rect(), 0)
        circle = pg.transform.smoothscale(circle, [int(min(rect.size) * 0.5)] * 2)

        radius = rectangle.blit(circle, (0, 0))
        radius.bottomright = rect.bottomright
        rectangle.blit(circle, radius)
        radius.topright = rect.topright
        rectangle.blit(circle, radius)
        radius.bottomleft = rect.bottomleft
        rectangle.blit(circle, radius)

        rectangle.fill((0, 0, 0), rect.inflate(-radius.w, 0))
        rectangle.fill((0, 0, 0), rect.inflate(0, -radius.h))
        pos = oldpos

        if (pos[0] + pos[2]) > mouse[0] > pos[0] and (pos[1] + pos[3]) > mouse[1] > pos[1]:
            self.hover = True
            self.buttonclick = action
            color = pg.Color(*color[1])
            alpha = color.a
            color.a = 0
        else:
            color = pg.Color(*color[0])
            alpha = color.a
            color.a = 0
            self.hover = False

        rectangle.fill(color, special_flags=pg.BLEND_RGBA_MAX)
        rectangle.fill((255, 255, 255, alpha), special_flags=pg.BLEND_RGBA_MIN)
        self.screen.blit(rectangle, pos)

        txts = load_font(textsize).render(text, True, (0, 0, 0))
        txtrect = txts.get_rect()
        txtrect.center = (pos[0] + pos[2] / 2, pos[1] + pos[3] / 2)
        self.screen.blit(txts, txtrect)

    def reset(self):
        self.left = self.right = self.up = self.down = False

    def loop(self):
        self.game_over = False
        while not self.game_over:
            self.screen.fill((35, 38, 117))
            self.snake.update()

            for x in self.blocks:
                if self.snake.check_collisions(x[1]):
                    self.over()
                self.screen.blit(x[0], x[1])

            for a, x in enumerate(self.snake.images):
                if a != 0 and self.snake.check_apple(x[1]):
                    self.over()
                self.screen.blit(x[0], x[1])

            if self.snake.check_apple(self.apple.pos):
                self.snake.add_apple()
                self.apple = apple(self.size)

            self.screen.blit(self.apple.image, self.apple.pos)
            self.screen.blit(self.snake.image, self.snake.pos)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_RIGHT and not self.left:
                        self.reset(); self.snake.right(); self.right = True
                    if event.key == pg.K_LEFT and not self.right:
                        self.reset(); self.snake.left(); self.left = True
                    if event.key == pg.K_UP and not self.down:
                        self.reset(); self.snake.up(); self.up = True
                    if event.key == pg.K_DOWN and not self.up:
                        self.reset(); self.snake.down(); self.down = True

            pg.display.update()


class startmenu():
    def __init__(self):
        self.screen = pg.display.set_mode((800, 450))
        self.b1 = '(150, 300,100,50),"Start", [(0,255,0), (0,150,0)], action = self.start'
        self.b2 = '(550, 300,100,50),"Exit", [(255,0,0), (150,0,0)], action = self.exit'
        self.buttons = [self.b1, self.b2]
        self.blocks = []
        self.size = 1
        self.click0 = self.loads = False

        color = (0, 0, 0)
        for x in range(0, 800, 10):
            t = pg.Surface((10, 10))
            t.fill(color)
            self
