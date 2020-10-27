"""
Actor.py
Python application for recieving button input from another controller, reading them as vibrations and then sending an interpreted
signal back to the source controller.
Author: Jeremy Cowelchuk, (add your names here)
"""

# Imports
import pygame
import time

# Constants
#HIGHPULSE
#LOWPULSE
#LONGPULSE
#SHORTPULSE


# initialize the game and necessary parts
pygame.init()

# Set the width and height of the screen (width, height).
screen = pygame.display.set_mode((500, 500))

pygame.display.set_caption("Actor")

# Loop until the user clicks the close button.
done = False

# Initialize the joysticks.
pygame.joystick.init()

joystick = pygame.joystick.Joystick(0)
joystick.init()

"""
INITIALIZE VARIABLES
"""

inputSignal = -1 

"""
FUNCTIONS BELOW
"""

# The following function reads an integer and generates a coorelating vibration signal
def GenerateVibration(input):
    if inputSignal == 0:
        print("RECIEVED: 0")
    elif inputSignal == 1:
        print("RECIEVED: 1")
    elif inputSignal == 2:
        print("RECIEVED: 2")
    elif inputSignal == 3:
        print("RECIEVED: 3")
    elif inputSignal == 4:
        print("RECIEVED: 4")
    elif inputSignal == 5:
        print("RECIEVED: 5")
    elif inputSignal == 6:
        print("RECIEVED: 6")
    elif inputSignal == 7:
        print("RECIEVED: 7")
    elif inputSignal == 8:
        print("RECIEVED: 8")
    elif inputSignal == 9:
        print("RECIEVED: 9")
    elif inputSignal == 10:
        print("RECIEVED: 10")
    elif inputSignal == 11:
        print("RECIEVED: 11")
    elif inputSignal == 12:
        print("RECIEVED: 12")
    elif inputSignal == 13:
        print("RECIEVED: 13")



# -------- Main Program Loop -----------
while not done:
    #
    # EVENT PROCESSING STEP
    #
    # Possible joystick actions: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
    # JOYBUTTONUP, JOYHATMOTION
    for event in pygame.event.get(): # User did something.

        #See if we got anything from the Observer
        """
        GET VALUE FROM TWISTED HERE
        """

       #default the inputSignal so that it can be ignored when it is not a valid value
        if inputSignal != -1:
            #Generate the vibration signal if the input is a valid input, then reset it so it doesn't softlock itself
            GenerateVibration(inputSignal)
            inputSignal = -1

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
                    if hat == (0,1):
                        hatValue = 13
                    elif hat == (0,-1):
                        hatValue = 10
                    elif hat == (1,0):
                        hatValue = 11
                    elif hat == (-1,0):
                        hatValue = 12

                    #print it for now
                    print(hatValue)

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