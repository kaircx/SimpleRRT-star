import math
import random
import sys
from operator import truediv
from pickle import NONE
from telnetlib import NOOPT

import numpy as np
import pygame
from pygame.locals import *
from soupsieve import closest

width = 600
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
screen = pygame.display.set_mode((width, width))
margin = 0
obstacleList = [
    (300, 100, 40),
    (180, 360, 80),
    (180, 160, 80),
    (90, 600, 80),
    (420, 300, 80),
    (540, 300, 80),
    (380, 600, 60),
]


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
    def __init__(self, start_position, end_position):
        self.start_position = start_position
        self.end_position = end_position
        self.color = blue
        self.bold = 4
        pygame.draw.line(
            screen, self.color, self.start_position, self.end_position, self.bold
        )


class node:
    def __init__(self, x, y):
        self.position = np.array([x, y])
        self.child_node = []
        self.parent = None
        # pygame.draw.circle(screen, green, self.position, 5, 3)

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

    def draw(self):
        pygame.draw.circle(screen, green, self.position, 5, 3)


def check_collision(closest_node, theta, dis):
    robot_radius = 40
    path_x, path_y = [], []
    resolution = 0.2
    for i in range(math.floor(dis / resolution)):
        path_x.append(i * resolution * math.cos(theta) + closest_node.position[0])
        path_y.append(i * resolution * math.sin(theta) + closest_node.position[1])
    for (ox, oy, size) in obstacleList:
        dx_list = [ox - x for x in path_x]
        dy_list = [oy - y for y in path_y]
        d_list = [dx * dx + dy * dy for (dx, dy) in zip(dx_list, dy_list)]
        d_list.append(50000000)
        if min(d_list) <= (size + robot_radius) ** 2:
            print((size + robot_radius) ** 2)
            return False  # collision
    return True  # safe


def find_closest(target, path_tree):
    dlist = [
        (node.position[0] - target.position[0]) ** 2
        + (node.position[1] - target.position[1]) ** 2
        for node in path_tree
    ]
    minind = dlist.index(min(dlist))
    return minind


def draw(path_tree):
    for node in path_tree:
        if node.parent != None:
            line(node.position, path_tree[node.parent].position)


def goal_check(path_tree, end_node):
    for path in path_tree:
        if np.linalg.norm(path.position - end_node.position) < 5:
            while True:
                print("done")


pygame.init()
pygame.display.set_caption("RRT")

grid = Grid(20, 0, 0)
grid.update(np.random.rand(grid.x_n, grid.y_n))
r = robot(400, 300, 10)
grid.draw()
start_node = node(50, 50)
start_node.draw()
end_node = node(580, 580)
end_node.draw()
for obstacle in obstacleList:
    pygame.draw.circle(screen, black, (obstacle[0], obstacle[1]), obstacle[2])
path_tree = []
path_tree.append(start_node)
distance = 100
step_dis = 0.3  #%
goal_rate = 10  # 0-100
while True:
    search_node = node(random.randint(0, 600), random.randint(0, 600))
    if random.randint(0, 100) <= goal_rate:
        search_node = end_node
    closest_node_id = find_closest(search_node, path_tree)
    closest_node = path_tree[closest_node_id]

    vec = search_node.position - closest_node.position
    dis = step_dis * np.linalg.norm(vec)
    theta = np.arctan2(vec[1], vec[0])
    new_node = node(
        dis * math.cos(theta) + closest_node.position[0],
        dis * math.sin(theta) + closest_node.position[1],
    )
    if check_collision(closest_node, theta, dis):
        new_node.parent = closest_node_id
        path_tree.append(new_node)

    goal_check(path_tree, end_node)

    draw(path_tree)

    pygame.time.wait(0)

    # 画面を更新 --- (*4)
    pygame.display.update()
    # 終了イベントを確認 --- (*5)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
