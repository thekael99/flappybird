import time
import os
import pygame
import neat
import random

pygame.init()

BIRDIMGS = [pygame.image.load(os.path.join("imgs", "bird1.png")),
            pygame.image.load(os.path.join("imgs", "bird2.png")),
            pygame.image.load(os.path.join("imgs", "bird3.png"))]
PIPEIMG = pygame.image.load(os.path.join("imgs", "pipe.png"))
BGIMG = pygame.image.load(os.path.join("imgs", "bg.png"))
BASEIMG = pygame.image.load(os.path.join("imgs", "base.png"))

STATFONT = pygame.font.SysFont("comics", 25)

class Bird:
    IMGS = BIRDIMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -6
        self.tick_count = 0
        
    def move(self):
        self.tick_count += 1
        d = self.vel * self.tick_count +  1.1*self.tick_count ** 2
        if d >= 2:
            d = 2
        if d < 0:
            d -= 2.2

        self.y += d

        if d < 0 or self.y < self.height + 40:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION                
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
                
    def drawn(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < 2 * self.ANIMATION_TIME:
            self.img = self.IMGS[1]
        elif self.img_count < 3 * self.ANIMATION_TIME:
            self.img = self.IMGS[2]
        elif self.img_count < 4 * self.ANIMATION_TIME:
            self.img = self.IMGS[1]    
        elif self.img_count < 4 * self.ANIMATION_TIME + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = 2 * self.ANIMATION_TIME
        
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)
        
    def getMask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 80
    VEL = 4
    DISTANCE_BETWEEN = 220

    def __init__(self, x):
        self.x = x
        self.height = 0
        
        self.top = 0
        self.bot = 0
        self.PIPE_TOP = pygame.transform.flip(PIPEIMG, False, True)
        self.PIPE_BOT = PIPEIMG

        self.passed = False
        self.set_height()
    
    def set_height(self):
        self.height = random.randrange(25, 250)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bot = self.height + Pipe.GAP
    
    def move(self):
        self.x -= Pipe.VEL
        if self.x < -100:
            self.set_height()
            self.x += 2 * Pipe.DISTANCE_BETWEEN
            self.passed = False

    def drawn(self, win):
        win.blit(self.PIPE_BOT, (self.x, self.bot))
        win.blit(self.PIPE_TOP, (self.x, self.top))
    
    def getTopMask(self):
        return pygame.mask.from_surface(self.PIPE_TOP)
    
    def getBotMask(self):
        return pygame.mask.from_surface(self.PIPE_BOT)

    def collide(self, bird):
        birdMark = bird.getMask()
        topMark = self.getTopMask()
        botMark = self.getBotMask()
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bot_offset = (self.x - bird.x, self.bot - round(bird.y))
        
        bot_point = birdMark.overlap(botMark, bot_offset)
        top_point = birdMark.overlap(topMark, top_offset)

        if top_point or bot_point:
            return True
        return False        

class Base:
    VEL = 4
    WIDTH = BASEIMG.get_width()
    IMG = BASEIMG
    BASE_APEAR = 400

    def __init__(self):
        self.y = Base.BASE_APEAR
        self.x = 0
        
    def move(self):
        self.x -= Base.VEL

        if self.x + Base.WIDTH < 0:
            self.x += Base.WIDTH

    def drawn(self, win):
        win.blit(self.IMG, (self.x, self.y))
        win.blit(self.IMG, (self.x + Base.WIDTH, self.y))               


class FlappyBird:    
    def __init__(self, numBirds):
        self.numBirds = numBirds
        self.highest = 0

    def drawWindow(self, win):
        win.blit(BGIMG, (0, 0))
        for bird in self.birds:
            bird.drawn(win)
        for pipe in self.pipes:
            pipe.drawn(win)
        self.base.drawn(win)
        textScore = STATFONT.render("Scores: " + str(self.scores), 1, (255, 255, 255))
        win.blit(textScore, (5, 25))
        textHighest = STATFONT.render("Highest: " + str(self.highest), 1, (255, 255, 255))
        win.blit(textHighest, (5, 5))
        # textAlives = STATFONT.render("Alives: " + str(self.alives), 1, (255, 255, 255))
        # win.blit(textAlives, (5,30))
        pygame.display.update()

    def play(self):
        playAgain = True
        while playAgain:
            playAgain = False
            self.scores = 0
            self.alives = self.numBirds
            self.birds = [Bird(40, 180) for x in range(self.numBirds)]
            self.pipes = [Pipe(260), Pipe(260 + Pipe.DISTANCE_BETWEEN)]
            self.base = Base()

            win = pygame.display.set_mode(BGIMG.get_rect().size)
            clock = pygame.time.Clock()
            
            run = True
            while run:
                clock.tick(30)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        pygame.quit()
                        quit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            if self.birds:
                                for bird in self.birds:
                                    bird.jump()
                            else:
                                run = False
                                playAgain = True

                self.base.move()

                for pipe in self.pipes:
                    for bird in self.birds:
                        if pipe.collide(bird) or bird.y > 376 or bird.y < 24:
                            self.birds.remove(bird)
                            self.alives -= 1
                        
                        bird.move()
                    if not pipe.passed and pipe.x < 50 and self.birds:
                        pipe.passed = True
                        self.scores += 1
                        
                    pipe.move()
                if self.birds:
                    self.drawWindow(win)
                else:
                    STATFONT = pygame.font.SysFont("comics", 40)
                    textGameOver = STATFONT.render("GAME OVER!!!", 1, (255, 0, 0))
                    win.blit(textGameOver, (45, 150))
                    if self.scores > self.highest:
                        self.highest = self.scores
                        textGameOver = STATFONT.render(str(self.highest), 1, (255, 0, 0))
                        win.blit(textGameOver, (70, 150))
                    pygame.display.update()
                
    
FlappyBird(1).play()