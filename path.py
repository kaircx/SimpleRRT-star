from cgi import print_environ_usage
import sys, random
import pygame
from pygame.locals import *
import math
import numpy as np

white = (255,255,255)
black = (0,0,0)
red = (255,0,0)
green = (0,255,0)
screen = pygame.display.set_mode((600, 600))
margin=20

class Tile:
    def __init__(self,x,y,size):
        self.position=(x,y)
        self.size=size
        self.color=(255,255,255)
        self.danger=255
    
    def update_danger(self,danger):
        self.danger=danger

    def draw(self):
        self.color=(self.danger,self.danger,self.danger)
        pygame.draw.rect(screen, self.color,(self.position[0],self.position[1], self.size,self.size))

class Grid:
    def __init__(self,size,base_x,base_y):
        self.base=(base_x,base_y)
        self.height=screen.get_height()-2*margin
        self.width=screen.get_width()-2*margin
        self.tile_size=size
        self.x_n=math.floor(self.width/size)
        self.y_n=math.floor(self.height/size)
        self.tile_array=[]
        x=self.base[0]
        y=self.base[1]
        for index_x in range(self.x_n):
            
            x = self.base[0]
            self.tile_array.append([])
            for index_y in range(self.y_n):
                x += self.tile_size
                self.tile_array[index_x].append(Tile(x ,y,self.tile_size))
            y +=self.tile_size

    def update(self,danger_list):
        for list in range(len(self.tile_array)):
            for tile in range(len(self.tile_array[list])):
                self.tile_array[list][tile].update_danger(math.floor(255*danger_list[list][tile]))

    def draw(self):
        for list in range(len(self.tile_array)):
            for tile in range(len(self.tile_array[list])): 
                self.tile_array[list][tile].draw()


class robot:
    def __init__(self,x,y,r):
        self.position=(x,y)
        self.r=r
        self.range=100
        self.distance=2

    def draw(self):
        pygame.draw.circle(screen,green,self.position,self.r,3)
        pygame.draw.circle(screen,red,self.position,self.r)
    
    def move(self):
        distance=random.randint(self.distance/2,self.distance)
        theta = random.uniform(-math.pi,math.pi)
        self.position=(self.position[0]+distance*math.cos(theta),self.position[1]+distance*math.sin(theta))

pygame.init()
grid=Grid(50,0,0)
grid.update(np.random.rand(grid.x_n, grid.y_n))
r=robot(400,300,10)


while True:
    screen.fill(black) # 背景を黒で塗りつぶす

    
    grid.draw()
    r.move()
    r.draw()
    


    # 画面を更新 --- (*4)
    pygame.display.update()
    # 終了イベントを確認 --- (*5)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()