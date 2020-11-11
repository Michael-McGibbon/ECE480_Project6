"""
GameDemo2.py
 
 Python application for running a game and transmitting button presses across a cloud service
    
 Author: Jeremy Cowelchuk, David Geisler, George Legacy, Michael McGibbon (add your names here)

 
# Button Icons from: https://www.nicepng.com/ourpic/u2w7i1i1u2q8q8a9_xbox-360-icon-opengameart-xbox-controller-button-icons/ - In the process of being made ourselves :)
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

#random imports
from random import seed
from random import randint

#datetime imports
from datetime import datetime

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
DANCINGSPRITEX = (SCREENX/2)-64 
DANCINGSPRITEY = (SCREENY-200)


class Observer():
    def __init__(self):
        #intialize variables
        self.correct = 0
        self.incorrect = 0
        self.pressedButton = -1
        self.done = False

        #set up random seed based on current time
        a = datetime.now()
        a = int(a.strftime('%S'))

        seed(a)

        #initialize pygame
        pygame.init() # initialize the game and necessary parts
        self.screen = pygame.display.set_mode((SCREENX, SCREENY)) # Set the width and height of the screen (width, height).
        icon = pygame.image.load('ImageFiles/HATlab.png')
        pygame.display.set_icon(icon) # Icon for Game
        pygame.display.set_caption("Observer") #name the program

        pygame.joystick.init() # Initialize the joysticks.
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        #import images
        self.import_images()

        #set current button
        self.activeButton = random.choice(self.imagelist)

        # set up twisted end point and connection channel
            #JEREMY: CHANGE "99.28.129.156" INTO "localhost"
            #EVERYONE ELSE: DO THE OPPOSITE OF ABOVE
        self.point = TCP4ClientEndpoint(reactor, "localhost", 25565)
        self.connection = ObserverTransmit(self)

    def import_images(self):
        I2 = pygame.image.load('ImageFiles/Xbutton.png')
        I3 = pygame.image.load('ImageFiles/Ybutton.png')
        I0 = pygame.image.load('ImageFiles/Abutton.png')
        I1 = pygame.image.load('ImageFiles/Bbutton.png')
        I7 = pygame.image.load('ImageFiles/UPbutton.png')
        I4 = pygame.image.load('ImageFiles/DOWNbutton.png')
        I6 = pygame.image.load('ImageFiles/LEFTbutton.png')
        I5 = pygame.image.load('ImageFiles/RIGHTbutton.png')

        dance1 = pygame.image.load('ImageFiles/DancingGuy/Dance1.png')
        dance2 = pygame.image.load('ImageFiles/DancingGuy/Dance2.png')
        dance3 = pygame.image.load('ImageFiles/DancingGuy/Dance3.png')
        dance4 = pygame.image.load('ImageFiles/DancingGuy/Dance4.png')
        dance5 = pygame.image.load('ImageFiles/DancingGuy/Dance5.png')
        dance6 = pygame.image.load('ImageFiles/DancingGuy/Dance6.png')

        self.background = pygame.image.load('ImageFiles/background.jpg')
        self.msuhat = pygame.image.load('ImageFiles/msuhat.png')

        self.dance = (dance1, dance2, dance3, dance4, dance5, dance6)
        self.imagelist = [I0, I1, I2, I3, I4, I5, I6, I7]

    def display(self):

        # Set up font
        font = pygame.font.Font('freesansbold.ttf', 20)

        #display the background
        self.screen.fill((112, 128, 144))
        self.screen.blit(self.background,(0, 0))

        #display hatlab logo
        self.screen.blit(self.msuhat, (0, 0))

        #display the active button
        self.screen.blit(self.activeButton, (ACTIVEBUTTONX, ACTIVEBUTTONY))

        #display the dancing sprite
        self.screen.blit(random.choice(self.dance), (DANCINGSPRITEX,DANCINGSPRITEY))
        time.sleep(.1)
        
        #display the correct score 
        corrscore = font.render("Correct: " + str(self.correct), True, (255,255,255))
        self.screen.blit(corrscore, (CORRECTSCOREX, CORRECTSCOREY))
        
        #display the incorrect score
        incorrscore = font.render("Incorrect: " + str(self.incorrect), True, (255,255,255))
        self.screen.blit(incorrscore, (INCORRECTSCOREX, INCORRECTSCOREY))

    def VerifyButton(self, button):
        if self.pressed_button == button:
            self.correct += 1
            self.activeButton = random.choice(self.imagelist)
        else:
            self.incorrect += 1

    def DataCollection(self, button):
        df = pd.Dataframe(index-index, column=['Intended Button', 'Pressed Button','Correct/Incorrect', 'Time','Total Buttons Pressed'])
        a = 0
        df(a, 'Intended Button', button)
        df(a, 'Pressed Button', self.pressedButton)
        if self.pressedButton == button:
            df(a,'Correct/Incorrect', 'Correct')
        
            a += 1
        else:
            df(a,'Correct/Incorrect', 'Incorrect')
            a += 1

        if self.done == True:
            df(1, 'Total Buttons Pressed', a)
            df.to_excel("Data.xlsx")

    def game_tick(self):
        events = pygame.event.get()
        for event in events:

            # Process input events
            if event.type == pygame.QUIT: # If user clicked close.
                self.done = True # Flag that we are done so we exit this loop

            elif event.type == pygame.JOYBUTTONDOWN:
                # handle button presses, not dpad yet
                buttons = self.joystick.get_numbuttons()
                for i in range(buttons):
                    button = self.joystick.get_button(i)
                    if button == 1:
                        #send the button press to actor.py
                        self.connection.sendButton("O" + str(i))
                        self.pressedButton = i

            elif event.type == pygame.JOYHATMOTION:
                # handle dpad presses
                hats = self.joystick.get_numhats()
                for i in range(hats):
                    hat = self.joystick.get_hat(i)
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
                        self.connection.sendButton("O" + str(hatValue))
                        self.pressedButton = hatValue

            # elif event.type == pygame.JOYBUTTONUP:
            #button go up :(
    
        
            #redraw()

            self.display()
            pygame.display.update()

            if self.done == True:
                #quit the game
                pygame.quit()
                reactor.stop()

    def Run(self):
        # Set up a looping call every 1/30th of a second to run your game tick
        tick = LoopingCall(self.game_tick)
        tick.start(1.0 / DESIRED_FPS)

        d = connectProtocol(self.point, self.connection)
        print("observer")
        reactor.run()

# Set up anything else twisted here, like listening sockets
class ObserverTransmit(Protocol):

    def __init__(self, observer):
        self.observer = observer

    def connectionMade(self):
       # self.transport.write(b"Observer Connected")
        pass

    def dataReceived(self, data):
        decoded_data = data.decode()
        if decoded_data[1:].isnumeric(): 
            self.observer.VerifyButton(int(decoded_data[1:]))
        else:
            print(decoded_data)
    
    def sendButton(self, button):
        self.transport.write(button.encode("utf-8"))

def main():
    observer = Observer()
    observer.Run()

main()

