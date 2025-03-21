import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

BLOCK_SIZE = 20
SPEED = 20
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (200,0,0)
BLUE1 = (0,0,255)
BLUE2 = (0,100,255)

# initialise modules
pygame.init()
font = pygame.font.Font('Roboto-Medium.ttf', 25)

# reset option
# reward for agent
# play needs to take an action and returns direction
# is_ocllisi



class SnakeGameAI:
    def __init__(self, w=640,h=480):
        self.w=w
        self.h=h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('little snake game')
        self.clock =  pygame.time.Clock()
        self.reset()
     

    def reset(self):
        # init game state
        self.direction = Direction.RIGHT

        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        self.score = 0
        self.food = None
        self.frame_iteration = 0
        self._place_food()

    def _place_food(self):
        # random block position (we use division to ensure its a specific block)
        x = random.randint(0, (self.w-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE

        self.food = Point(x,y)
        # ensure food not in snake, if so just try a new random position
        if self.food in self.snake:
            self._place_food()


    def play_step(self, action):

        self.frame_iteration += 1

        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_LEFT:
            #         self.direction = Direction.LEFT
            #     elif event.key == pygame.K_RIGHT:
            #         self.direction = Direction.RIGHT
            #     elif event.key == pygame.K_UP:
            #         self.direction = Direction.UP
            #     elif event.key == pygame.K_DOWN:
            #         self.direction = Direction.DOWN 
        
        # 2. Move snake
        self._move(action) # update head
        self.snake.insert(0, self.head)
        
        # 3. Check if game over
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            # if there is a collision, or the snake takes ages to do anything
            game_over=True
            reward = -10
            return game_over, self.score, self.score

        # 4. place new food or just move snake
        if self.head == self.food:
            self.score += 1
            reward += 10
            self._place_food()
        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)

        # 6. return if game over and score
        
        return game_over, reward, self.score
    
    def _update_ui(self):
        self.display.fill(BLACK)
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, BLOCK_SIZE-8, BLOCK_SIZE-8))
        pygame.draw.circle(self.display, RED, (self.food.x+BLOCK_SIZE/2, self.food.y+BLOCK_SIZE/2), BLOCK_SIZE/2)

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0,0])
        pygame.display.flip()

    def _move(self, action):
        # [straight, right, left]
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        # interpret action based on array setup
        if np.array_equal(action, [1,0,0]):
            new_dir = clock_wise[idx] # no change
        elif np.array_equal(action, [0,1,0]):
            next_idx = (idx + 1)%4 # turn clockwise / right
            new_dir = clock_wise[next_idx]
        else:
            next_idx = (idx - 1)%4 # turn anti-clockwise / left
            new_dir = clock_wise[next_idx]

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x += -BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y += -BLOCK_SIZE
        self.head = Point(x,y)

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head

        # hits boundary
        if (pt.x > self.w - BLOCK_SIZE) or (pt.x < 0) or (pt.y > self.h - BLOCK_SIZE) or (pt.y < 0):
            print("boundary collision")
            return True
        if pt in self.snake[1:]:
            print("self collision")
            return True
        return False



if __name__ == '__main__':
    game = SnakeGameAI()

    # main game loop
    while True:
        action = [1,0,0]
        game_over, reward, score = game.play_step(action)


        if game_over == True:
            break
            # if game over we break

    print('Final Score', score)
    
    # finish game properly
    pygame.quit()
    