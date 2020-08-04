import pygame
import neat
import time
import os
import random #for height of tubes
pygame.font.init()

GEN = 0
DRAW_LINES = True

#Creating the window
WIN_WIDTH = 500
WIN_HEIGHT = 800
#Loading in assets
BIRD_IMG = [pygame.transform.scale2x(pygame.image.load(os.path.join("Assets", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("Assets", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("Assets", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("Assets", "pipe.png"))) 
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("Assets", "base.png"))) 
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("Assets", "bg.png")))
#Font
STAT_FONT = pygame.font.SysFont("comicsans", 50)
#Bird class
class Bird:
    IMGS = BIRD_IMG 
    MAX_ROTATION = 25 #tilt amount when going up and down
    ROT_VELOCITY = 17 #How fast we roate by each frame
    ANIMATION_TIME = 5 #for switching the images in animation

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0  # degrees to tilt
        self.tick_count = 0
        self.bird_velocity = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        
        self.bird_velocity = -10.5
        self.tick_count = 0
        self.height = self.y
        self.img = self.IMGS[0]

    def move(self):
        self.tick_count += 1 #coutning number of moves since last jump
        
        d = self.bird_velocity*self.tick_count+ 1.5*self.tick_count**2

        if d >= 16: #Setting a terminal velocity
            d = 16
        if d < 0:
            d -=5
        self.y += d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -=self.ROT_VELOCITY
    
    def draw(self, win):
        self.img_count += 1
        #Creating flapping animation based off of img count
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4+1:
            self.img = self.IMGS[0]
            self.img_count = 0

        #Creating 'nose dive' when falling
        if self.tilt <=-75:
            self.img=self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2
        

        
        #Image rotation
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    #for collisions
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


#Pipe class
class Pipe:
    GAP = 200
    PIPE_VELOCITY = 10

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False #check if bird passed the pipe
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.PIPE_VELOCITY

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x -bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True
        
        return False

class Base:
    BASE_VELOCITY= 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1=0
        self.x2=self.WIDTH
    
    def move(self):
        self.x1 -=self.BASE_VELOCITY
        self.x2 -= self.BASE_VELOCITY

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
    
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, birds, pipes, base, score, gen, population, pipe_index):
    win.blit(BG_IMG, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    
    text = STAT_FONT.render("Gen: " + str(gen), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH -10 -  text.get_width(), 10))

    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (10 , 10))

    base.draw(win)

    text = STAT_FONT.render("Population: " + str(population), 1, (0,0,0))
    win.blit(text, (10 , 730))
    for bird in birds:
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_index].x + pipes[pipe_index].PIPE_TOP.get_width()/2, pipes[pipe_index].height), 5)
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_index].x + pipes[pipe_index].PIPE_BOTTOM.get_width()/2, pipes[pipe_index].bottom), 5)
            except:
                pass    
        bird.draw(win)
    pygame.display.update()

def main(genomes, config):
    global GEN
    GEN +=1
    nets = []
    genome = []
    birds = []

    for _,g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(150, 350))
        g.fitness = 0
        genome.append(g)

    base = Base(730)
    pipes = [Pipe(500)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False               
                pygame.quit()
                quit()
            """    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    birds[0].jump()"""
        #Checking which pipe to look at
        pipe_index = 0
        if len(birds)>0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_index = 1
        else:
            run = False
            break
        
        #Bird movements
        for x, bird in enumerate(birds):
            bird.move()
            genome[x].fitness += 0.1

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_index].height), abs(bird.y - pipes[pipe_index].bottom)))

            if output[0] > 0.5:
                bird.jump()
                #pass
                
        
        add_pipe = False
        rem = []
        for pipe in pipes:
            for x,bird in enumerate(birds):
                if pipe.collide(bird):
                    genome[x].fitness -= 1
                    nets.pop(x)
                    genome.pop(x)
                    birds.pop(x)


                if  not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
                
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                        rem.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            for g in genome:
                g.fitness += 5
            pipes.append(Pipe(500))
        
        for p in rem:
            pipes.remove(p)
    
        #Floor collision & ceiling collision
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                nets.pop(x)
                genome.pop(x)
                birds.pop(x)

        base.move()
        draw_window(win, birds, pipes, base,score, GEN, len(genome), pipe_index)



def run(config_path):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
