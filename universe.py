#! /usr/bin/env python3
import math
import sys
import pygame
import numpy as np
import random
import os

if getattr(sys,'frozen',False):
    basepath = os.path.dirname(sys.executable)
else:
    basepath = os.path.dirname(os.path.abspath(__file__))

fontpath = os.path.join(basepath,"PressStart2P.ttf")
if not os.path.exists(fontpath):
    print("Error: font file not found. I looked in " + fontpath)
    sys.exit(-1)
musicpath = os.path.join(basepath,'keygen_music.mp3')
if not os.path.exists(musicpath):
    print("Error: music file not found. I looked in " + musicpath)
    sys.exit(-1)
uniWidth = 900
uniHeight = 900
blk = 100
pygame.init()
screen = pygame.display.set_mode((uniWidth,uniHeight), pygame.FULLSCREEN)
clock = pygame.time.Clock()
maxfps=60
font = pygame.font.Font(fontpath,20)
bigfont = pygame.font.Font(fontpath,30)
dt = 0.01
dt_per_frame = 1
c=10
num_dt=0
t=0
pausex=0
done=False
paused=True
godmode=False
light_traveling=False
lights_traveling=False
horizons=True
music = False 
WHITE = (255,255,255)
RED   = (255,  0,  0)
GREEN = (  0,255,  0)
BLUE  = (  0,  0,255)
YELLOW= (255,255,  0)
CYAN  = (  0,255,255)
MAGENTA=(255,  0,255)
BLACK = (  0,  0,  0)
q=1

colors = [WHITE,RED,GREEN,BLUE,YELLOW,CYAN,MAGENTA,BLACK]

H0 = 1E-1
def infla(t):
    return np.exp(H0*t)
def rad(t):
    return (2*H0*t)**0.5 # (should this be / 2 ?)
def radH(t):
    return H0 * a(t)**(-2)

def event_horizon(tc,t,godmode):
    if godmode:
        return c/H0*np.exp(-H0*tc)
    else: return a(t)*c/H0*np.exp(-H0*tc)
def max_causal_horizon(godmode):
    if godmode:
        return c/H
    else: return c/H*a(t)

def recompute_grid(t,center_x,center_y,a1):
    # create a square grid, comoving
    grid = []
    w,h,b = uniWidth,uniHeight,blk
    ws,hs = 0,0
    #rescale grid when no longer visible
    while a1 > w/b:
        a1 /= w/b
    for x in range(ws,w,b):
        for y in range(hs,h,b):
            grid.append(pygame.Rect(a1*(x-center_x)+center_x,a1*(y-center_y)+center_y,a1*b,a1*b))
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

drawing_plot = True
p_shape  = np.array((400,200),dtype=int)
p_loc = np.array((uniWidth-(p_shape[0]+50),50),dtype=int)
xlim = np.array((0,200),dtype=int)
ylim = np.array((0,500),dtype=int)
points = []
dpoints = []
godpoints = []
goddpoints = []
ticksize = 10
axiscolor = CYAN
plotcolor = GREEN
dplotcolor = RED
ylabel = "c.h."
xlabel = "t"
def draw_plot(screen):
    # draw background
    pygame.draw.rect(screen, BLACK,(p_loc[0],p_loc[1],p_shape[0],p_shape[1]))
    # x axis and ticks
    pygame.draw.line(screen, axiscolor,(p_loc[0],p_loc[1]+p_shape[1]),(p_loc[0]+p_shape[0],p_loc[1]+p_shape[1]), 3)
    for x in range(p_loc[0],p_shape[0]+p_loc[0],40):
        pygame.draw.line(screen, axiscolor,(x,p_loc[1]+p_shape[1]),(x,p_loc[1]+p_shape[1]-ticksize))
    # y axis and ticks
    pygame.draw.line(screen, axiscolor,(p_loc[0],p_loc[1]),(p_loc[0],p_loc[1]+p_shape[1]), 3)
    for y in range(p_loc[1],p_shape[1]+p_loc[1],40):
        pygame.draw.line(screen, axiscolor,(p_loc[0],y),(p_loc[0]+ticksize,y))
    # axis labels
    text = font.render(xlabel,True,WHITE,BLACK)
    screen.blit(text, p_loc + p_shape + (-3*ticksize,-3*ticksize))
    text = font.render(ylabel,True,WHITE,BLACK)
    screen.blit(text, p_loc + (3*ticksize,2*ticksize))

    # curve
    p = godpoints  if godmode else points
    d = goddpoints if godmode else dpoints
    if len(p)>1:
        pygame.draw.lines(screen, plotcolor, False, p, 3)
        if ((p[-1][0] > p_loc[0] + p_shape[0]) or (p[-1][1] < p_loc[1])):
            blit_txt_with_outline(screen,(250,850),font,"INFLATION IS OFF THE CHARTS!!",WHITE,BLACK,3)

    if len(d)>1:
        pygame.draw.lines(screen, dplotcolor, False, d, 3)

    return

fast = False
godgrid = recompute_grid(t,uniWidth/2,uniHeight/2,1)
a = lambda t: infla(t)
H = lambda t: H0
e = lambda tc,t,godmode: event_horizon(tc,t,godmode)
inflating = True
pygame.mixer.init()
pygame.mixer.music.load(musicpath)
pygame.mixer.music.play(loops=-1)
music = True
while not done:
    keys = pygame.key.get_pressed()
    fast = keys[pygame.K_RETURN]
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if light_traveling:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos2 = pygame.mouse.get_pos()
                pos2 = (pos2-np.array((uniWidth/2,uniHeight/2)))/(a(t)/q)+np.array((uniWidth/2,uniHeight/2))
                lights_traveling = True
                distance = np.linalg.norm((pos1 - pos2))
                tc = t
                td = t+1000
                r=0
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos1 = pygame.mouse.get_pos()
                pos1 = (pos1 - np.array((uniWidth/2,uniHeight/2)))/(a(t)/q)+np.array((uniWidth/2,uniHeight/2))
                light_traveling = True
                tc = t
                td = t+1000
                r=0
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                done=True
            if event.key == pygame.K_p:
                drawing_plot = not drawing_plot
            if event.key == pygame.K_SPACE:
                paused = not paused
                pauset=0
            if event.key == pygame.K_g:
                godmode = not godmode
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                if not music:
                    pygame.mixer.init()
                    pygame.mixer.music.load(musicpath)
                    pygame.mixer.music.play(loops=-1)
                    music = True
                else:
                    pygame.mixer.music.stop()
                    music = False
            if event.key == pygame.K_h:
                horizons = not horizons
            if event.key == pygame.K_e and inflating:
                # let's end inflation, switch a(t) to a different function
                inflating = False
                tswitch = t
                a = lambda t: infla(tswitch) + rad(t-tswitch)
                H = lambda t: radH(t)
                e = lambda tc,t,godmode: 10000
                horizons = False
            if event.key == pygame.K_r:
                #reset to the beginning
                inflating = True
                light_traveling = False
                lights_traveling = False
                horizons = True
                num_dt = 0
                a = lambda t: infla(t)
                H = lambda t: H0
                e = lambda tc,t,godmode: event_horizon(tc,t,godmode)
                points = []
                godpoints = []
                goddpoints= []
                dpoints = []






    if not paused:
        if fast:
            num_dt+=10
        else:
            num_dt+=1

        t = num_dt*dt
        points.append(   p_loc + (0,+p_shape[1]) + (t/xlim[1]*p_shape[0], -e(t,t,False)/ylim[1]*p_shape[1]))
        godpoints.append(p_loc + (0,+p_shape[1]) + (t/xlim[1]*p_shape[0], -e(t,t,True )/ylim[1]*p_shape[1]))

        if lights_traveling:
            dpoints.append(   p_loc + (0,+p_shape[1]) + (t/xlim[1]*p_shape[0], -distance*a(t)/ylim[1]*p_shape[1]))
            goddpoints.append(p_loc + (0,+p_shape[1]) + (t/xlim[1]*p_shape[0], -distance/ylim[1]*p_shape[1]))

        if light_traveling:
            if (tc <= t <= td):
                v = c + H(t)*r
                if fast:
                    r+= v*10*dt
                else:
                    r += v*dt
            else:
                light_traveling = False

        if (num_dt%dt_per_frame==0):
            screen.fill(BLACK)
            if godmode:
                q = a(t)
                grid = godgrid
            else:
                q = 1
                grid = recompute_grid(t,uniWidth/2,uniHeight/2,a(t))

            for square in grid:
                pygame.draw.rect(screen,WHITE,square,1)

            if light_traveling:
                pos1_tmp = np.array((uniWidth/2,uniHeight/2)) + (pos1-np.array((uniWidth/2,uniHeight/2)))*a(t)/q
                pygame.draw.circle(screen,YELLOW,(int(pos1_tmp[0]),int(pos1_tmp[1])),int(r/q),0 if int(r/q)<5 else 5 )
                if horizons:
                    h = e(tc,t,godmode)
                    pygame.draw.circle(screen,RED,(int(pos1_tmp[0]),int(pos1_tmp[1])),int(h),0 if int(h)<5 else 5 )
                if lights_traveling:
                    pos2_tmp = np.array((uniWidth/2,uniHeight/2)) + (pos2-np.array((uniWidth/2,uniHeight/2)))*a(t)/q
                    pygame.draw.circle(screen,YELLOW,(int(pos2_tmp[0]),int(pos2_tmp[1])),int(r/q),0 if int(r/q)<5 else 5 )
                    distance = np.linalg.norm((pos1 - pos2))
                    if horizons:
                        h = e(tc,t,godmode)
                        pygame.draw.circle(screen,RED,(int(pos2_tmp[0]),int(pos2_tmp[1])),int(h),0 if int(h)<5 else 5 )


            blit_txt_with_outline(screen,(20,20),font,"t = %6.4f"%t,WHITE,BLACK,3)
            blit_txt_with_outline(screen,(20,50),font,"a(t) = %3.2f"% a(t),WHITE,BLACK,3)

            if drawing_plot:
                draw_plot(screen)


            pygame.display.flip()
            clock.tick(maxfps)
    else:

        # show instructions
        screen.fill(BLACK)
        fun_color = random.choice(colors)
        wletters = "...o0o0o TEAM LHS=RHS o0o0o..."
        i=0
        for letter in wletters:
            y = 120+30*np.sin(2*np.pi/(uniWidth/2)*(pausex+i*30))
            x = pausex+i*30
            x %= uniWidth
            i += 1
            text = bigfont.render(letter,True,fun_color)
            screen.blit(text,(x,y))


        text = bigfont.render("INFLATION SIMULATOR 9000",True, fun_color)
        text_rect = text.get_rect(center=(int(uniWidth/2),50))
        screen.blit(text,text_rect)


        text = font.render("SPACE    START/PAUSE",True,WHITE)
        text_rect = text.get_rect(left=int(uniWidth/10)-80,top=int(uniHeight/4)+50)
        screen.blit(text,text_rect)

        text = font.render("ENTER    speed up time 10x",True,WHITE)
        text_rect = text.get_rect(left=int(uniWidth/10)-80,top=int(uniHeight/4)+100)
        screen.blit(text,text_rect)

        text = font.render("CLICK    release light beam",True,WHITE)
        text_rect = text.get_rect(left=int(uniWidth/10)-80,top=int(uniHeight/4)+150)
        screen.blit(text,text_rect)


        text = font.render("p    display a(t) plot",True,WHITE)
        text_rect = text.get_rect(left=int(uniWidth/10),top=int(uniHeight/4)+200)
        screen.blit(text,text_rect)

        text = font.render("h    display event horizon",True,WHITE)
        text_rect = text.get_rect(left=int(uniWidth/10),top=int(uniHeight/4)+250)
        screen.blit(text,text_rect)

        text = font.render("e    end inflation, switch to radiation",True,WHITE)
        text_rect = text.get_rect(left=int(uniWidth/10),top=int(uniHeight/4)+300)
        screen.blit(text,text_rect)

        text = font.render("g    GODMODE, become omniscient",True,WHITE)
        text_rect = text.get_rect(left=int(uniWidth/10),top=int(uniHeight/4)+350)
        screen.blit(text,text_rect)

        text = font.render("r    reset simulation",True,WHITE)
        text_rect = text.get_rect(left=int(uniWidth/10),top=int(uniHeight/4)+400)
        screen.blit(text,text_rect)

        text = font.render("m    THE SOUND OF SILENCE",True,WHITE)
        text_rect = text.get_rect(left=int(uniWidth/10),top=int(uniHeight/4)+450)
        screen.blit(text,text_rect)

        pausex += 2

        pygame.display.flip()
        clock.tick(maxfps)
