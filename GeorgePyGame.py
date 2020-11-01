

# This is George's Test PyGame application :) 
# Button Icons from: https://www.nicepng.com/ourpic/u2w7i1i1u2q8q8a9_xbox-360-icon-opengameart-xbox-controller-button-icons/

import pygame
import XInput
import random

# Initialize the Game
pygame.init()

# Create the Screen
screenx = 500
screeny = 500
screen = pygame.display.set_mode((screenx, screeny))

# Import the Images
xbutton = pygame.image.load('Xbutton.png')
ybutton = pygame.image.load('Ybutton.png')
abutton = pygame.image.load('Abutton.png')
bbutton = pygame.image.load('Bbutton.png')
upbutton = pygame.image.load('UPbutton.png')
downbutton = pygame.image.load('DOWNbutton.png')
leftbutton = pygame.image.load('LEFTbutton.png')
rightbutton = pygame.image.load('RIGHTbutton.png')
msuhat = pygame.image.load('msuhat.png')

# Title & Icon
pygame.display.set_caption("George's Go at Dance Dance")
icon = pygame.image.load('HATlab.png')
pygame.display.set_icon(icon)

# MSU HATLab Logo
msuhatx = 0
msuhaty = 0
def sponsor():
    screen.blit(msuhat, (msuhatx, msuhaty))

# Active Button Location
activebuttonx = (screenx/2)-64 
activebuttony = (screeny/2)-64 
activebuttonychange = 0

def activebutton(x,y):
    screen.blit(upbutton, (x, y))

# Game loop
running = True
while running:

    screen.fill((112, 128, 144))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # If keystroke pressed - check whether if up or down
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                activebuttonychange = -0.5         
            if event.key == pygame.K_DOWN:
                activebuttonychange = 0.5
        if event.type ==pygame.KEYUP:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                activebuttonychange = 0
    activebuttony += activebuttonychange
    activebutton(activebuttonx, activebuttony)
    sponsor()

    pygame.display.update()



