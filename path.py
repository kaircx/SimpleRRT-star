import math
import random
import sys

import numpy as np
import pygame
from pygame.locals import *

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
screen = pygame.display.set_mode((600, 600))
margin = 0


class Tile:
    def __init__(self, x, y, size):
        self.position = (x, y)
        self.size = size
        self.color = (255, 255, 255)
        self.danger = 255

    def update_danger(self, danger):
        self.danger = danger

    def draw(self):
        self.color = (self.danger, self.danger, self.danger)
        pygame.draw.rect(
            screen,
            self.color,
            (self.position[0], self.position[1], self.size, self.size),
        )


class Grid:
    def __init__(self, size, base_x, base_y):
        self.base = (base_x, base_y)
        self.height = screen.get_height() - 2 * margin
        self.width = screen.get_width() - 2 * margin
        self.tile_size = size
        self.x_n = math.floor(self.width / size)
        self.y_n = math.floor(self.height / size)
        self.tile_array = []
        x = self.base[0]
        y = self.base[1]
        for index_x in range(self.x_n):

            x = self.base[0]
            self.tile_array.append([])
            for i in range(self.y_n):
                x += self.tile_size
                self.tile_array[index_x].append(Tile(x, y, self.tile_size))
            y += self.tile_size

    def update(self, danger_list):
        for list in range(len(self.tile_array)):
            for tile in range(len(self.tile_array[list])):
                self.tile_array[list][tile].update_danger(
                    math.floor(255 * danger_list[list][tile])
                )

    def draw(self):
        for list in range(len(self.tile_array)):
            for tile in range(len(self.tile_array[list])):
                self.tile_array[list][tile].draw()


class robot:
    def __init__(self, x, y, r):
        self.position = (x, y)
        self.r = r
        self.range = 100
        self.distance = 2

    def draw(self):
        pygame.draw.circle(screen, green, self.position, self.r, 3)
        pygame.draw.circle(screen, red, self.position, self.r)

    def move(self):
        distance = random.randint(self.distance / 2, self.distance)
        theta = random.uniform(-math.pi, math.pi)
        self.position = (
            self.position[0] + distance * math.cos(theta),
            self.position[1] + distance * math.sin(theta),
        )


class line:
    def __init__(self, start_position, end_position, color, bold):
        self.start_position = start_position
        self.end_position = end_position
        self.color = color
        self.bold = bold

    def draw(self):
        pygame.draw.line(
            screen, self.color, self.start_position, self.end_position, self.bold
        )


class path:
    def __init__(self):
        self.lines = []

    def add(self):
        pass

    def delete(self):
        pass


class node:
    def __init__(self, x, y):
        self.position = (x, y)
        self.child_node = []
        pygame.draw.circle(screen, green, self.position, 5, 3)

        self.range = 100
        self.distance = 50

    def explore_new_node(self):
        distance = random.randint(self.distance / 2, self.distance)
        theta = random.uniform(-math.pi, math.pi)
        new_position = (
            self.position[0] + distance * math.cos(theta),
            self.position[1] + distance * math.sin(theta),
        )
        return node(new_position[0], new_position[1])


pygame.init()
pygame.display.set_caption("RRT")

grid = Grid(50, 0, 0)
grid.update(np.random.rand(grid.x_n, grid.y_n))
r = robot(400, 300, 10)
grid.draw()
start_node = node(100, 100)
end_node = node(500, 500)
path = []
path.append(start_node.explore_new_node())
while True:
    # screen.fill(black)  # 背景を黒で塗りつぶす

    # r.move()
    # r.draw()
    new_node = path[len(path) - 1].explore_new_node()

    # 画面を更新 --- (*4)
    pygame.display.update()
    # 終了イベントを確認 --- (*5)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
