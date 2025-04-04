import torch
import random
import numpy as np
from collections import deque
from game import SnakeGameAI, Direction, Point
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.005
BOUND_SIZE = 20

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness control
        self.gamma = 0.9 # discount rate (must be smaller than 1)
        self.memory = deque(maxlen = MAX_MEMORY) # automaticlaly removes element from left if we exceed memory
        self.model = Linear_QNet(15,256,3)

        # self.model.load_state_dict(torch.load("model/best_sofar.pth"))
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)


    def get_state(self, game):
        head = game.snake[0]

        # some points near head
        point_l = Point(head.x - BOUND_SIZE, head.y)
        point_r = Point(head.x + BOUND_SIZE, head.y)
        point_u = Point(head.x , head.y - BOUND_SIZE)
        point_d = Point(head.x , head.y + BOUND_SIZE)

        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            # Danger straight
            (dir_r and game.is_collision(point_r)) or 
            (dir_l and game.is_collision(point_l)) or
            (dir_u and game.is_collision(point_u)) or
            (dir_d and game.is_collision(point_d)),

            # Danger Right
            (dir_u and game.is_collision(point_r)) or 
            (dir_d and game.is_collision(point_l)) or
            (dir_l and game.is_collision(point_u)) or
            (dir_r and game.is_collision(point_d)),

            # Danger left
            (dir_d and game.is_collision(point_r)) or 
            (dir_u and game.is_collision(point_l)) or
            (dir_r and game.is_collision(point_u)) or
            (dir_l and game.is_collision(point_d)),

            # Direction
            dir_l, 
            dir_r,
            dir_u,
            dir_d,

            game.food.x < game.head.x,  # food left
            game.food.x > game.head.x,  # food right
            game.food.y < game.head.y,  # food up
            game.food.y > game.head.y,  # food down

            game.snake[-1].x < game.head.x, # tail left
            game.snake[-1].x > game.head.x, # tail right
            game.snake[-1].y < game.head.y, # tail up
            game.snake[-1].y > game.head.y # tail down
        ]

        return np.array(state, dtype=int)

        
    def remember(self, state, action, reward, next_state,game_over):
        self.memory.append((state, action, reward, next_state,game_over)) # will popleft if MAX_MEMORY is reached


    # trains on game?
    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory # take all of memory

        states,actions,rewards,next_sates,game_overs = zip(*mini_sample) # gives us the other dimension, handy!
        self.trainer.train_step(states,actions,rewards,next_sates,game_overs)
    
    # trains on one step
    def train_short_memory(self, state, action, reward, next_state,game_over):
        self.trainer.train_step(state, action, reward, next_state,game_over)

    def get_action(self, state):
        # to begin we do random moves 
        # this is a tradeoff between exploration and exploitation
        # the more games, the less we make random moves
        self.epsilon = max([2,100 - self.n_games])
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0,2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        return final_move

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()
    while True:
        # get old state
        state_old = agent.get_state(game)

        # get move based on current state
        final_move = agent.get_action(state_old)

        # perform move and get new state
        game_over, reward, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # train short memory of the agent (for one step)
        agent.train_short_memory(state_old, final_move, reward, state_new ,game_over)

        # remember
        agent.remember(state_old, final_move, reward, state_new, game_over)

        if game_over:
            # train long memory, plot result
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()