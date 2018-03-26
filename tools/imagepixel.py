#coding: utf-8
import sys, random, math, pygame
from pygame.locals import *
import tkFileDialog
import Tkinter

root = Tkinter.Tk()
# root.withdraw()
filename = tkFileDialog.askopenfilename(initialdir = '.')
print filename

pygame.init()

pygame.display.set_caption(filename)
my_font=pygame.font.SysFont(None,22)
font = pygame.font.Font(None, 18)

#space = pygame.image.load("labelIds.png").convert_alpha()
space = pygame.image.load(filename)
width,height = space.get_size()
print width, height
screen = pygame.display.set_mode((width,height+20))
x = 0
y = 0
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    keys = pygame.key.get_pressed()
    #print keys
    x, y = pygame.mouse.get_pos()
    if x<width and y<height:
        color = screen.get_at((x, y))
        #print x,y
        # print color
        textstr = str(color)
    #print textstr
    if keys[K_ESCAPE]:
        sys.exit()
    if keys[K_o]:
        filename = tkFileDialog.askopenfilename(initialdir = '.')
        print filename
        pygame.display.set_caption(filename)
        space = pygame.image.load(filename)
        width,height = space.get_size()
        print width, height
        screen = pygame.display.set_mode((width,height+20))
        x = 0
        y = 0
    screen.fill([0,0,0])  
    screen.blit(space, (0,20))
    text_screen=my_font.render(textstr, True, (255, 255, 255))
    screen.blit(text_screen, (10,0))
    pygame.display.update()