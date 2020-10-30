

# This is George's Test PyGame application :) 
# Button Icons from: https://www.nicepng.com/ourpic/u2w7i1i1u2q8q8a9_xbox-360-icon-opengameart-xbox-controller-button-icons/

import pygame

# Initiazlie the Game
pygame.init()

# Create the Screen
screen = pygame.display.set_mode((500, 500))

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

#Active Button
activebuttonx = 186   
activebuttony = 186

def player():
    screen.blit(xbutton, (activebuttonx, activebuttony))

# Game loop
running = True
while running:

    screen.fill((112, 128, 144))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player()
    sponsor()

    pygame.display.update()

