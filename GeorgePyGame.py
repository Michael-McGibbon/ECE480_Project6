

# This is George's Test PyGame application :) 
# Icons made by <a href="https://www.flaticon.com/authors/flat-icons" title="Flat Icons">Flat Icons</a> from <a href="https://www.flaticon.com/" title="Flaticon"> www.flaticon.com</a>#

import pygame

# Initiazlie the Game
pygame.init()

# Create the Screen
screen = pygame.display.set_mode((800, 600))

# Title & Icon
pygame.display.set_caption("George's Go at Dance Dance")
icon = pygame.image.load('dance.png')
pygame.display.set_icon(icon)


# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

