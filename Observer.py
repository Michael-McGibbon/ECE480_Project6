"""
 Observer.py
 
 Python application for running a game and transmitting button presses across a cloud service
    
 Author: Jeremy Cowelchuk, David Geisler, George Legacy (add your names here)
"""

"""
# adding this in, will be added to correct location when needed.

# Imports
import pygame
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
                    
                    #USE TWISTED HERE TO SEND TO ACTOR.PY
                   

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
                    #USE TWISTED HERE TO SEND TO ACTOR.PY


                

                       
       # elif event.type == pygame.JOYBUTTONUP:
            #button go up :(


  
# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()

#check
#check2 David
#check3 Michael
#check4 Jeremy
#check5 George
"""

from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol

class Greeter(Protocol):

    def connectionMade(self):
        print("connected to server")


point = TCP4ClientEndpoint(reactor, "99.28.129.156", 25565)
d = connectProtocol(point, Greeter())
print("client")
reactor.run()