"""
Actor.py
Python application for recieving button input from another controller, reading them as vibrations and then sending an interpreted
signal back to the source controller.
Author: Jeremy Cowelchuk, (add your names here)

# Background Image: https://depositphotos.com/stock-photos/dancefloor.html?qview=9919783 - Will need to find roalty free :) 
"""


# imports
import pygame
import time
import random
import XInput

# twisted imports
from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet.task import LoopingCall

# Constants
DESIRED_FPS = 30.0 # 30 frames per second
ACCEPTED_HATS = [(0,1),(0,-1),(1,0),(-1,0)]

DELAY = 0.25

HIGH_INTENSITY = 1.0
LOW_INTENSITY = 0.125
NO_INTENSITY = 0.0

SCREENX = 400
SCREENY = 600
ACTIVEBUTTONX = (SCREENX/2)-64 
ACTIVEBUTTONY = (SCREENY/2)-64 
CORRECTSCOREX = (SCREENX - 137)
CORRECTSCOREY = 10
INCORRECTSCOREX = CORRECTSCOREX
INCORRECTSCOREY = (CORRECTSCOREY + 20)
CORRECT = 0
INCORRECT = 0
DANCINGSPRITEX = (SCREENX/2)-64 
DANCINGSPRITEY = (SCREENY-200)

# Import Images
I2 = pygame.image.load('ImageFiles/Xbutton.png')
I3 = pygame.image.load('ImageFiles/Ybutton.png')
I0 = pygame.image.load('ImageFiles/Abutton.png')
I1 = pygame.image.load('ImageFiles/Bbutton.png')
I7 = pygame.image.load('ImageFiles/UPbutton.png')
I4 = pygame.image.load('ImageFiles/DOWNbutton.png')
I6 = pygame.image.load('ImageFiles/LEFTbutton.png')
I5 = pygame.image.load('ImageFiles/RIGHTbutton.png')
background = pygame.image.load('ImageFiles/background.jpg')
msuhat = pygame.image.load('ImageFiles/msuhat.png')
dance1 = pygame.image.load('ImageFiles/DancingGuy/Dance1.png')
dance2 = pygame.image.load('ImageFiles/DancingGuy/Dance2.png')
dance3 = pygame.image.load('ImageFiles/DancingGuy/Dance3.png')
dance4 = pygame.image.load('ImageFiles/DancingGuy/Dance4.png')
dance5 = pygame.image.load('ImageFiles/DancingGuy/Dance5.png')
dance6 = pygame.image.load('ImageFiles/DancingGuy/Dance6.png')

dance = (dance1, dance2, dance3, dance4, dance5, dance6)

#initialize pygame
pygame.init() # initialize the game and necessary parts
screen = pygame.display.set_mode((SCREENX, SCREENY)) # Set the width and height of the screen (width, height).
icon = pygame.image.load('ImageFiles/HATlab.png')
pygame.display.set_icon(icon) # Icon for Game
pygame.display.set_caption("Actor") #name the program
 
pygame.joystick.init() # Initialize the joysticks.
joystick = pygame.joystick.Joystick(0)
joystick.init()

# MSU HATLab Logo
def sponsor():
    screen.blit(msuhat, (0, 0))

# Dancing Sprite
def dancer(x,y):
    screen.blit(random.choice(dance), (x,y))
    time.sleep(.1)


def GenerateVibration(intensity, duration, delay):
    XInput.set_vibration(0, intensity, intensity)
    time.sleep(duration)
    XInput.set_vibration(0, NO_INTENSITY, NO_INTENSITY)
    time.sleep(delay)

def DecodeInput(inputSignal):
    if inputSignal == "0":
        # low - low - low = Abutton
        GenerateVibration(LOW_INTENSITY, DELAY, DELAY)
        GenerateVibration(LOW_INTENSITY, DELAY, DELAY)
        GenerateVibration(LOW_INTENSITY, DELAY, DELAY)
    elif inputSignal == "1":
        # low - low - high = BbUtton
        GenerateVibration(LOW_INTENSITY, DELAY, DELAY)
        GenerateVibration(LOW_INTENSITY, DELAY, DELAY)
        GenerateVibration(HIGH_INTENSITY, DELAY, DELAY)
    elif inputSignal == "2":
        # low - high - low = Xbutton
        GenerateVibration(LOW_INTENSITY, DELAY, DELAY)
        GenerateVibration(HIGH_INTENSITY, DELAY, DELAY)
        GenerateVibration(LOW_INTENSITY, DELAY, DELAY)
    elif inputSignal == "3":
        # low - high - high = Ybutton
        GenerateVibration(LOW_INTENSITY, DELAY, DELAY)
        GenerateVibration(HIGH_INTENSITY, DELAY, DELAY)
        GenerateVibration(HIGH_INTENSITY, DELAY, DELAY)
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
        # high - high - high = DOWNbutton
        GenerateVibration(HIGH_INTENSITY, DELAY, DELAY)
        GenerateVibration(HIGH_INTENSITY, DELAY, DELAY)
        GenerateVibration(HIGH_INTENSITY, DELAY, DELAY)
    elif inputSignal == "11":
        # high - high - low = RIGHTbutton
        GenerateVibration(HIGH_INTENSITY, DELAY, DELAY)
        GenerateVibration(HIGH_INTENSITY, DELAY, DELAY)
        GenerateVibration(LOW_INTENSITY, DELAY, DELAY)
    elif inputSignal == "12":
        # high - low - high = LEFTbutton
        GenerateVibration(HIGH_INTENSITY, DELAY, DELAY)
        GenerateVibration(LOW_INTENSITY, DELAY, DELAY)
        GenerateVibration(HIGH_INTENSITY, DELAY, DELAY)
    elif inputSignal == "13":
        # high - low - low = UPbutton
        GenerateVibration(HIGH_INTENSITY, DELAY, DELAY)
        GenerateVibration(LOW_INTENSITY, DELAY, DELAY)
        GenerateVibration(LOW_INTENSITY, DELAY, DELAY)


def game_tick():
    done = False # Loop until the user clicks the close button.

    screen.fill((112, 128, 144))
    screen.blit(background,(0, 0))

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

    sponsor()
    dancer(DANCINGSPRITEX, DANCINGSPRITEY)
    pygame.display.update()

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
        #self.transport.write(b"Actor Connected")
        pass

    def dataReceived(self, data):
        decoded_data = data.decode()
        if decoded_data[1:].isnumeric():
            DecodeInput(decoded_data[1:])
        else:
            print(decoded_data)

    def sendButton(self, button):
        self.transport.write(button.encode("utf-8"))


#JEREMY: CHANGE "99.28.129.156" INTO "localhost"
#EVERYONE ELSE: DO THE OPPOSITE OF ABOVE
point = TCP4ClientEndpoint(reactor, "localhost", 25565)
connection = ActorTransmit()
d = connectProtocol(point, connection)
print("actor")
reactor.run()




