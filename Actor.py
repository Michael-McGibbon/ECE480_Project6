"""
Actor.py
Python application for recieving button input from another controller, reading them as vibrations and then sending an interpreted
signal back to the source controller.
Author: Jeremy Cowelchuk, (add your names here)
"""

# imports
import pygame
import time
import XInput

# twisted imports
from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet.task import LoopingCall

# Constants
DESIRED_FPS = 30.0 # 30 frames per second
ACCEPTED_HATS = [(0,1),(0,-1),(1,0),(-1,0)]

SHORT_DELAY = 0.17
LONG_DELAY = 0.33

HIGH_INTENSITY = 1.0
LOW_INTENSITY = 0.125
NO_INTENSITY = 0.0

#initialize pygame
pygame.init() # initialize the game and necessary parts
screen = pygame.display.set_mode((500, 500)) # Set the width and height of the screen (width, height).
pygame.display.set_caption("Actor") #name the program

pygame.joystick.init() # Initialize the joysticks.
joystick = pygame.joystick.Joystick(0)
joystick.init()


def GenerateVibration(intensity, duration, delay):
    XInput.set_vibration(0, intensity, intensity)
    time.sleep(duration)
    XInput.set_vibration(0, NO_INTENSITY, NO_INTENSITY)
    time.sleep(delay)

def DecodeInput(inputSignal):
    if inputSignal == "0":
        # low - low - low
        GenerateVibration(LOW_INTENSITY, SHORT_DELAY, SHORT_DELAY)
        GenerateVibration(LOW_INTENSITY, SHORT_DELAY, SHORT_DELAY)
        GenerateVibration(LOW_INTENSITY, SHORT_DELAY, SHORT_DELAY)
    elif inputSignal == "1":
        # low - low - high
        GenerateVibration(LOW_INTENSITY, SHORT_DELAY, SHORT_DELAY)
        GenerateVibration(LOW_INTENSITY, SHORT_DELAY, SHORT_DELAY)
        GenerateVibration(HIGH_INTENSITY, SHORT_DELAY, SHORT_DELAY)
    elif inputSignal == "2":
        # low - high - low
        GenerateVibration(LOW_INTENSITY, SHORT_DELAY, SHORT_DELAY)
        GenerateVibration(HIGH_INTENSITY, SHORT_DELAY, SHORT_DELAY)
        GenerateVibration(LOW_INTENSITY, SHORT_DELAY, SHORT_DELAY)
    elif inputSignal == "3":
        # low - high - high
        GenerateVibration(LOW_INTENSITY, SHORT_DELAY, SHORT_DELAY)
        GenerateVibration(HIGH_INTENSITY, SHORT_DELAY, SHORT_DELAY)
        GenerateVibration(HIGH_INTENSITY, SHORT_DELAY, SHORT_DELAY)
    elif inputSignal == "4":
        print("RECIEVED: 4")
    elif inputSignal == "5":
        print("RECIEVED: 5")
    elif inputSignal == "6":
        print("RECIEVED: 6")
    elif inputSignal == "7":
        print("RECIEVED: 7")
    elif inputSignal == "8":
        print("RECIEVED: 8")
    elif inputSignal == "9":
        print("RECIEVED: 9")
    elif inputSignal == "10":
        # high - high - high
        GenerateVibration(HIGH_INTENSITY, SHORT_DELAY, SHORT_DELAY)
        GenerateVibration(HIGH_INTENSITY, SHORT_DELAY, SHORT_DELAY)
        GenerateVibration(HIGH_INTENSITY, SHORT_DELAY, SHORT_DELAY)
    elif inputSignal == "11":
        # high - high - low
        GenerateVibration(HIGH_INTENSITY, SHORT_DELAY, SHORT_DELAY)
        GenerateVibration(HIGH_INTENSITY, SHORT_DELAY, SHORT_DELAY)
        GenerateVibration(LOW_INTENSITY, SHORT_DELAY, SHORT_DELAY)
    elif inputSignal == "12":
        # high - low - high
        GenerateVibration(HIGH_INTENSITY, SHORT_DELAY, SHORT_DELAY)
        GenerateVibration(LOW_INTENSITY, SHORT_DELAY, SHORT_DELAY)
        GenerateVibration(HIGH_INTENSITY, SHORT_DELAY, SHORT_DELAY)
    elif inputSignal == "13":
        # high - low - low
        GenerateVibration(HIGH_INTENSITY, SHORT_DELAY, SHORT_DELAY)
        GenerateVibration(LOW_INTENSITY, SHORT_DELAY, SHORT_DELAY)
        GenerateVibration(LOW_INTENSITY, SHORT_DELAY, SHORT_DELAY)


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

                    #send the button press to the cloud service
                    connection.sendButton("A" + str(i))

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

                    # create a new connection and send it to the Cloud Service
                    connection.sendButton("A" + str(hatValue))

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
class ActorTransmit(Protocol):

    def connectionMade(self):
        print("Connetion to server established")

    def dataReceived(self, data):
        decoded_data = data.decode()
        button = decoded_data[1:]
        DecodeInput(button)

    def sendButton(self, button):
        self.transport.write(button.encode("utf-8"))


#JEREMY: CHANGE "99.28.129.156" INTO "localhost"
#EVERYONE ELSE: DO THE OPPOSITE OF ABOVE
point = TCP4ClientEndpoint(reactor, "99.28.129.156", 25565)
connection = ActorTransmit()
d = connectProtocol(point, connection)
print("actor")
reactor.run()




