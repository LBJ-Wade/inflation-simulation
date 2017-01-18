import math
import pygame
import numpy as np
from scipy.special import jv

import matplotlib
matplotlib.use("Agg")

import matplotlib.backends.backend_agg as agg


import pylab
from pygame.locals import *

uniWidth = 900
uniHeight = 900

pygame.init()
screen = pygame.display.set_mode((uniWidth,uniHeight))
clock = pygame.time.Clock()
maxfps=60
font = pygame.font.Font(None,30)
dt=0.05
dt_per_frame = 1
c = 100
num_dt=0
t=0
done = False
paused = True
light_traveling = False
WHITE = (255,255,255)
BLACK = (  0,  0,  0)

H = 1E-1
# for now, de Sitter expansion
def a(t):
    return jv(1,H*t)


blk = 100
def recompute_grid(t,center_x,center_y):
    # create a square grid, comoving
    grid = []
    a1 = a(t)
    for x in range(0,uniWidth,blk):
        for y in range(0,uniHeight,blk):
            grid.append(pygame.Rect(a1*(x-center_x)+center_x,a1*(y-center_y)+center_y,a1*blk,a1*blk))
    return grid

def blit_txt_with_outline(screen, loc, font, text, fg_color, bg_color,thk):
        textfg = font.render(text,True, fg_color)
        textbg = font.render(text,True, bg_color)
        screen.blit(textbg,loc+(-thk,-thk))
        screen.blit(textbg,loc+( thk,-thk))
        screen.blit(textbg,loc+(-thk, thk))
        screen.blit(textbg,loc+( thk, thk))
        screen.blit(textfg,loc)
        return

t_range=[]
at_range=[]
while not done:
    screen.fill(BLACK)
    if not paused:
        num_dt+=1
        t = num_dt*dt
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done=True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            paused = not paused
        if event.type == pygame.KEYDOWN and event.key == pygame.K_c and light_traveling == False:
            light_traveling = True
            tc = t
            td = t+1


    if (num_dt%dt_per_frame==0):
        grid = recompute_grid(t,uniWidth/2,uniHeight/2)
        for square in grid:
            pygame.draw.rect(screen,WHITE,square,1)

        if light_traveling:
            if (tc <= t <= td):
                # this radius should be a more complicated function of time
                r = int(c*(t-tc))
                pygame.draw.circle(screen,(255,255,0),(int(uniWidth/2),int(uniHeight/2)),r,0 if r<5 else 5 )
            else:
                light_traveling = False

        blit_txt_with_outline(screen,(20,20),font,"t = %6.4f"%t,WHITE,BLACK,3)
        blit_txt_with_outline(screen,(20,50),font,"a(t) = %3.2f"% a(t),WHITE,BLACK,3)
        fig = pylab.figure(figsize=[4, 2], # Inches
                                   dpi=100,        # 100 dots per inch, so the resulting buffer is 400x400 pixels
                                                      )
        ax = fig.gca()
        ax.set_xlim([0,100])
        ax.set_ylim([0,5])
        t_range.append(t)
        at_range.append(a(t))
        ax.plot(t_range, at_range)
        canvas = agg.FigureCanvasAgg(fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()



        #screen = pygame.display.get_surface()

        size = canvas.get_width_height()

        surf = pygame.image.fromstring(raw_data, size, "RGB")
        screen.blit(surf, (500,0))
        #pygame.display.flip()

        #while True:
        #    pass

        pygame.display.flip() 
        clock.tick(maxfps)
