import math
import random
import sys
from uuid import NAMESPACE_X500

import numpy as np
import pygame
from pygame.locals import *

width = 620
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
screen = pygame.display.set_mode((width, width))
margin = 0
obstacleList = [
    (300, 100, 40),
    (180, 380, 80),
    (180, 160, 80),
    (90, 600, 80),
    (420, 300, 80),
    (540, 300, 80),
    (380, 600, 60),
]
# obstacleList = [
#     (0, 0, 0),
# ]


class Tile:
    def __init__(self, x, y, size):
        self.position = (x, y)
        self.size = size
        self.color = (255, 255, 255)
        self.danger = 255
        self.flag = False

    def get_danger(self):
        return self.danger

    def update_danger(self, danger):
        self.danger = danger
        self.color = (255 * self.danger, 255 * self.danger, 255 * self.danger)

    def draw(self):
        pygame.draw.rect(
            screen,
            self.color,
            (self.position[0], self.position[1], self.size, self.size),
        )
        if self.flag:
            pygame.draw.rect(
                screen,
                (255, 255, 0),
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
                self.tile_array[list][tile].update_danger(danger_list[list][tile])

    def get_danger(self, node):
        x = node.position[0]
        y = node.position[1]
        n_x = math.floor(x / self.tile_size)
        n_y = math.floor(y / self.tile_size)
        self.tile_array[n_x][n_y].flag = True
        return self.tile_array[n_x][n_y].danger

    def draw(self):
        for list in range(len(self.tile_array)):
            for tile in range(len(self.tile_array[list])):
                self.tile_array[list][tile].draw()


class line:
    def __init__(self, start_position, end_position, color, b):
        self.start_position = start_position
        self.end_position = end_position
        self.color = color
        self.bold = b
        pygame.draw.line(
            screen, self.color, self.start_position, self.end_position, self.bold
        )


class node:
    def __init__(self, x, y):
        self.position = np.array([x, y])
        self.child_node = []
        self.parent = None
        self.cost = 0  # distance cost from parent node
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
    robot_radius = 20
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
            # print((size + robot_radius) ** 2)
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
            line(node.position, path_tree[node.parent].position, blue, 4)


def goal_check(path_tree, end_node):
    for i, path in enumerate(path_tree):
        if np.linalg.norm(path.position - end_node.position) < 5:
            # print("done")
            return i
    return None


def draw_path_from(path_tree, goal_node):
    if goal_node != None:
        index = goal_node
        while index != 0:
            # print(index)
            # print(path_tree[index].parent)
            line(
                path_tree[index].position,
                path_tree[path_tree[index].parent].position,
                red,
                5,
            )
            index = path_tree[index].parent


def path_update(new_node, path_tree, closest_node_id):
    index = len(path_tree) - 1
    cost_sum_new = 0
    while index != 0:
        cost_sum_new += path_tree[index].cost
        index = path_tree[index].parent

    for i, node in enumerate(path_tree):
        if i != closest_node_id:
            cost, theta = calc_distance_theta(new_node, node)
            index = i
            cost_sum = 0
            while index != 0:
                cost_sum += path_tree[index].cost
                index = path_tree[index].parent

            if (
                check_collision(
                    new_node,
                    theta,
                    cost,
                )
                and cost_sum_new + cost < cost_sum
            ):
                node.cost = cost
                node.parent = len(path_tree) - 1


def calc_distance_theta(from_node, to_node):
    vec = to_node.position - from_node.position
    theta = np.arctan2(vec[1], vec[0])
    return np.linalg.norm(vec), theta


pygame.init()
pygame.display.set_caption("RRT")

grid = Grid(20, -20, 0)
grid.update(np.random.rand(grid.x_n, grid.y_n))
start_node = node(50, 50)
end_node = node(550, 550)
goal_node = None
path_tree = []
path_tree.append(start_node)
distance = 100
step_dis = 0.3  #%
goal_rate = 10  # 0-100
while True:
    # print(len(path_tree))
    screen.fill(black)
    # init
    grid.draw()
    start_node.draw()
    end_node.draw()
    for obstacle in obstacleList:
        pygame.draw.circle(screen, black, (obstacle[0], obstacle[1]), obstacle[2])
    print(grid.get_danger(start_node))
    ########plannning
    # search_node = node(random.randint(0, 600), random.randint(0, 600))
    # search_node.draw()
    # if random.randint(0, 100) <= goal_rate:
    #     search_node = end_node
    # closest_node_id = find_closest(search_node, path_tree)
    # closest_node = path_tree[closest_node_id]
    # distance, theta = calc_distance_theta(closest_node, search_node)
    # dis = distance * step_dis
    # new_node = node(
    #     dis * math.cos(theta) + closest_node.position[0],
    #     dis * math.sin(theta) + closest_node.position[1],
    # )
    # if check_collision(closest_node, theta, dis):
    #     new_node.parent = closest_node_id
    #     new_node.cost, theta = calc_distance_theta(new_node, closest_node)
    #     path_tree.append(new_node)
    #     # RRT-star
    #     path_update(new_node, path_tree, closest_node_id)

    # draw(path_tree)

    # goal_node = goal_check(path_tree, end_node)
    # draw_path_from(path_tree, goal_node)

    pygame.time.wait(0)

    # 画面を更新 --- (*4)
    pygame.display.update()
    # 終了イベントを確認 --- (*5)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
