# Button Icons from: https://www.nicepng.com/ourpic/u2w7i1i1u2q8q8a9_xbox-360-icon-opengameart-xbox-controller-button-icons/ - In the process of being made ourselves :)
# Background Image: https://depositphotos.com/stock-photos/dancefloor.html?qview=9919783 - Will need to find roalty free :) 

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


# Import the Images
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
imagelist = [I0, I1, I2, I3, I4, I5, I6, I7]
active = random.choice(imagelist)

#initialize pygame
pygame.init() # initialize the game and necessary parts
screen = pygame.display.set_mode((SCREENX, SCREENY)) # Set the width and height of the screen (width, height).
icon = pygame.image.load('ImageFiles/HATlab.png')
pygame.display.set_icon(icon) # Icon for Game
pygame.display.set_caption("Observer") #name the program
pygame.joystick.init() # Initialize the joysticks.
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Create Random List
from datetime import datetime
a = datetime.now()
a = int(a.strftime('%S'))
from random import seed
from random import randint
seed(a)
for _ in range(5):
    value = randint(0,10)
    b = "R" + str(value)
    print(b)

# MSU HATLab Logo
def sponsor():
    screen.blit(msuhat, (0, 0))

# Active Button
def buttonimage(x,y):
    screen.blit(active, (x, y))

# Dancing Sprite
def dancer(x,y):
    screen.blit(random.choice(dance), (x,y))
    time.sleep(.25)

# Button Verification 
def VerifyButton(button):
    global CORRECT
    global INCORRECT 
    if pressed_button == button:
        CORRECT += 1
    else:
        INCORRECT += 1

# Scoring Data
font = pygame.font.Font('freesansbold.ttf', 20)

def scorecorrect(x,y):
    corrscore = font.render("Correct: " + str(CORRECT), True, (255,255,255))
    screen.blit(corrscore, (x, y))

def scoreincorrect(x,y):
    incorrscore = font.render("Incorrect: " + str(INCORRECT), True, (255,255,255))
    screen.blit(incorrscore, (x, y))

def game_tick():
    done = False # Loop until the user clicks the close button.
    global pressed_button
    events = pygame.event.get()

    screen.fill((112, 128, 144))
    screen.blit(background,(0, 0))

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
                    #send the button press to actor.py
                    connection.sendButton("O" + str(i))
                    pressed_button = i

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

                    #send the hat press to actor.py
                    connection.sendButton("O" + str(hatValue))
                    pressed_button = hatValue

        # elif event.type == pygame.JOYBUTTONUP:
        #button go up :(
    
        
    #redraw()

    buttonimage(ACTIVEBUTTONX, ACTIVEBUTTONY)
    sponsor()
    scorecorrect(CORRECTSCOREX, CORRECTSCOREY)
    scoreincorrect(INCORRECTSCOREX, INCORRECTSCOREY)
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
class ObserverTransmit(Protocol):

    def connectionMade(self):
       # self.transport.write(b"Observer Connected")
        pass

    def dataReceived(self, data):
        decoded_data = data.decode()
        if decoded_data[1:].isnumeric(): 
            VerifyButton(int(decoded_data[1:]))
        else:
            print(decoded_data)
    
    def sendButton(self, button):
        self.transport.write(button.encode("utf-8"))

#JEREMY: CHANGE "99.28.129.156" INTO "localhost"
#EVERYONE ELSE: DO THE OPPOSITE OF ABOVE
point = TCP4ClientEndpoint(reactor, "localhost", 25565)
connection = ObserverTransmit()
d = connectProtocol(point, connection)
print("observer")
reactor.run()

