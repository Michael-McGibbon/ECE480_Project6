"""
 Observer.py
 
 Python application for running a game and transmitting button presses across a cloud service
    
 Author: Jeremy Cowelchuk, David Geisler, George Legacy (add your names here)
"""

# imports
import pygame
import time

# twisted imports
from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet.task import LoopingCall

# Constants
DESIRED_FPS = 30.0 # 30 frames per second
ACCEPTED_HATS = [(0,1),(0,-1),(1,0),(-1,0)]

#initialize pygame
pygame.init() # initialize the game and necessary parts
screen = pygame.display.set_mode((500, 500)) # Set the width and height of the screen (width, height).
pygame.display.set_caption("Observer") #name the program

pygame.joystick.init() # Initialize the joysticks.
joystick = pygame.joystick.Joystick(0)
joystick.init()

def game_tick():
    done = False # Loop until the user clicks the close button.
    events = pygame.event.get()
    for event in events:
        # Process input events
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
                if (hat in ACCEPTED_HATS):
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
    
        
    #redraw()

    if done == True:
        #quit the game
        pygame.quit()
        reactor.stop()


# Set up a looping call every 1/30th of a second to run your game tick
tick = LoopingCall(game_tick)
tick.start(1.0 / DESIRED_FPS)

# Set up anything else twisted here, like listening sockets
class Greeter(Protocol):

    def connectionMade(self):
        print("connected to server")


#JEREMY: CHANGE "99.28.129.156" INTO "localhost"
#EVERYONE ELSE: DO THE OPPOSITE OF ABOVE
point = TCP4ClientEndpoint(reactor, "99.28.129.156", 25565)
d = connectProtocol(point, Greeter())
print("client")
reactor.run()

