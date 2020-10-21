"""
 Observer.py
 
 Python application for running a game and transmitting button presses across a cloud service

 Author: Jeremy Cowelchuk, (add your names here)
"""

# adding this in, will be added to correct location when needed.

# Imports
import pygame
import XInput
import time

# Constants

# initialize the game and necessary parts
pygame.init()

# Set the width and height of the screen (width, height).
screen = pygame.display.set_mode((500, 500))

pygame.display.set_caption("Observer")

# Loop until the user clicks the close button.
done = False

# Initialize the joysticks.
pygame.joystick.init()

joystick = pygame.joystick.Joystick(0)
joystick.init()



# -------- Main Program Loop -----------
while not done:
    #
    # EVENT PROCESSING STEP
    #
    # Possible joystick actions: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
    # JOYBUTTONUP, JOYHATMOTION
    for event in pygame.event.get(): # User did something.
        if event.type == pygame.QUIT: # If user clicked close.
            done = True # Flag that we are done so we exit this loop
        elif event.type == pygame.JOYBUTTONDOWN:

            # handle button presses, not dpad yet
            buttons = joystick.get_numbuttons()
            for i in range(buttons):
                button = joystick.get_button(i)
                if button == 1:
                    print(i)
                    #send the button press to actor.py
                    """
                    USE TWISTED HERE TO SEND TO ACTOR.PY
                    """

        elif event.type == pygame.JOYHATMOTION:
            # handle dpad presses
            hats = joystick.get_numhats()
            for i in range(hats):
                hat = joystick.get_hat(i)
                if (hat != (0,0)):
                    
                    #print it for now
                    print(hat)

                    #send the hat press to actor.py
                    """
                    USE TWISTED HERE TO SEND TO ACTOR.PY
                    """

                

                       
       # elif event.type == pygame.JOYBUTTONUP:
            #button go up :(


  
# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()

#check