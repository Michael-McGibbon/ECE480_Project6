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
import pandas as pd

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
CORRECTSCOREX = (SCREENX - 135)
CORRECTSCOREY = 10
INCORRECTSCOREX = CORRECTSCOREX
INCORRECTSCOREY = (CORRECTSCOREY + 20)
DANCINGSPRITEX = (SCREENX/2)-64 
DANCINGSPRITEY = (SCREENY-200)
LEVELX = 0
LEVELY = 64



class Observer():
    def __init__(self, ip, maxLevels = 8):
        #intialize variables
        self.correct = 0
        self.incorrect = 0
        self.pressedButton = -1
        self.done = False
        self.timePressed = 0
        self.timeRecieved = 0
        self.buttonList = []
        self.level = 0
        self.maxLevels = maxLevels
        self.correctInARow = 0
        self.enabled = True

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
    
        # Set up font
        self.font = pygame.font.Font('comicsans.ttf', 20)


        #set up pandas dataframe for data collection
        self.df = pd.DataFrame(columns=['Level', 'Intended Button', 'Pressed Button','Correct/Incorrect', 'Time'])

        # set up twisted end point and connection channel
        self.point = TCP4ClientEndpoint(reactor, ip, 25565)
        self.connection = ObserverTransmit(self)
        
        #level up to select a random button
        self.LevelUp()

    def import_images(self):
        I2 = pygame.image.load('ImageFiles/Buttons/Xbutton.png')
        I3 = pygame.image.load('ImageFiles/Buttons/Ybutton.png')
        I0 = pygame.image.load('ImageFiles/Buttons/Abutton.png')
        I1 = pygame.image.load('ImageFiles/Buttons/Bbutton.png')
        I7 = pygame.image.load('ImageFiles/Buttons/UPbutton.png')
        I4 = pygame.image.load('ImageFiles/Buttons/DOWNbutton.png')
        I6 = pygame.image.load('ImageFiles/Buttons/LEFTbutton.png')
        I5 = pygame.image.load('ImageFiles/Buttons/RIGHTbutton.png')

        dance1 = pygame.image.load('ImageFiles/DancingGuy/Dance1.png')
        dance2 = pygame.image.load('ImageFiles/DancingGuy/Dance2.png')
        dance3 = pygame.image.load('ImageFiles/DancingGuy/Dance3.png')
        dance4 = pygame.image.load('ImageFiles/DancingGuy/Dance4.png')
        dance5 = pygame.image.load('ImageFiles/DancingGuy/Dance5.png')
        dance6 = pygame.image.load('ImageFiles/DancingGuy/Dance6.png')

        self.background = pygame.image.load('ImageFiles/background.jpg')
        self.msuhat = pygame.image.load('ImageFiles/msuhat.png')

        self.dance = (dance1, dance2, dance3, dance4, dance5, dance6)
        self.imagelist = [(0,I0), (1,I1), (2,I2), (3,I3), (10,I4), (11,I5), (12,I6), (13,I7)]

    def display(self):

        #display the background
        self.screen.fill((112, 128, 144))
        self.screen.blit(self.background,(0, 0))

        #display hatlab logo
        self.screen.blit(self.msuhat, (0, 0))

        #display the active button
        self.screen.blit(self.activeButtonImage, (ACTIVEBUTTONX, ACTIVEBUTTONY))

        #display the dancing sprite
        #self.screen.blit(random.choice(self.dance), (DANCINGSPRITEX,DANCINGSPRITEY))
        #time.sleep(.05)
        
        #display the correct score 
        corrscore = self.font.render("Correct: " + str(self.correct), True, (255,255,255))
        self.screen.blit(corrscore, (CORRECTSCOREX, CORRECTSCOREY))
        
        #display the incorrect score
        incorrscore = self.font.render("Incorrect: " + str(self.incorrect), True, (255,255,255))
        self.screen.blit(incorrscore, (INCORRECTSCOREX, INCORRECTSCOREY))

        #display the current level
        currlevel = self.font.render("Level: " + str(self.level), True, (255,255,255))
        self.screen.blit(currlevel, (LEVELX, LEVELY))

    def ChangeButton(self):
        newButton = random.choice(self.buttonList)
        self.activeButtonImage = (newButton[1])
        self.activeButton = (newButton[0])

        self.display()
        pygame.display.update()

    def LevelUp(self):
        self.level += 1
        self.incorrect = 0
        self.correct = 0
        self.correctInARow = 0

        #if we're above the max number of levels, stop
        if self.maxLevels < self.level:
            #quit the game
            self.enabled = False
            reactor.stop()
            pygame.quit()
            return

        newButton = random.choice(self.imagelist)
        self.buttonList.append(newButton)
        self.imagelist.remove(newButton)

        #automatically have the first value after a level up be the new button
        self.activeButtonImage = (newButton[1])
        self.activeButton = (newButton[0])

        self.display()
        pygame.display.update()

    def VerifyButton(self, button):
        self.timeRecieved = int(round(time.time() * 1000))
        if self.pressedButton == button:
            self.correct += 1
        else:
            self.incorrect += 1
            self.correctInARow = 0
        self.CollectData(button)
        self.ChangeButton()

    #updates the pandas dataframe when buttons from observer and actor are recorded
    def CollectData(self, button):
        buttonStr = self.ButtonValueConversion(button)
        pressedButtonStr = self.ButtonValueConversion(self.pressedButton)
        timeStamp = self.timeRecieved - self.timePressed
        if self.correct == 0 and self.incorrect == 0:
            self.df = self.df.append({'Level': self.level}, ignore_index=True)
        if self.pressedButton == button:
            self.df = self.df.append({'Intended Button': pressedButtonStr, 'Pressed Button': buttonStr, 'Correct/Incorrect': 'Correct', 'Time': timeStamp}, ignore_index=True)
        else:
            self.df = self.df.append({'Intended Button': pressedButtonStr, 'Pressed Button': buttonStr, 'Correct/Incorrect': 'Incorrect', 'Time': timeStamp}, ignore_index=True)
    
    #Converts the numerical button value to the button name for data collection purposes
    def ButtonValueConversion(self, button):
        if button == 0:
            return 'A'
        elif button == 1:
            return 'B'
        elif button == 2:
            return 'X'
        elif button == 3:
            return 'Y'
        elif button == 10:
            return 'Down Numpad'
        elif button == 11:
            return 'Right Numpad'
        elif button == 12:
            return 'Left Numpad'
        elif button == 13:
            return 'Up Numpad'

    #Updates the pandas dataframe with total buttons pressed and exports it to an excel file
    def ExportData(self):
        #self.df[1, 'Total Buttons Pressed'] = self.correct + self.incorrect
        self.df.to_csv("Data.csv",index=False)

    def game_tick(self):
        if self.enabled == True:
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
                            if i == self.activeButton:
                                self.connection.sendButton("O" + str(i))
                                self.pressedButton = i
                                self.enabled = False

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

                            if hatValue == self.activeButton:
                                #send the hat press to actor.py
                                self.connection.sendButton("O" + str(hatValue))
                                self.pressedButton = hatValue
                                self.enabled = False

                self.timePressed = int(round(time.time() * 1000))
                # elif event.type == pygame.JOYBUTTONUP:
                #button go up :(
    
        
                #redraw()



                if self.done == True:
                    #quit the game
                    reactor.stop()
                    pygame.quit()

                else:
                    self.display()
                    pygame.display.update()

    def Run(self):
        # Set up a looping call every 1/30th of a second to run your game tick
        tick = LoopingCall(self.game_tick)
        tick.start(1.0 / DESIRED_FPS)

        d = connectProtocol(self.point, self.connection)
        print("observer")
        reactor.run()

    def EnableGameLoop(self):
        self.enabled = True

# Set up anything else twisted here, like listening sockets
class ObserverTransmit(Protocol):

    def __init__(self, observer):
        self.observer = observer

    def connectionMade(self):
        #send a message to mark this one as the observer and be saved on the server as such
        message = "O"
        self.transport.write(message.encode("utf-8"))

    def dataReceived(self, data):
        decoded_data = data.decode()
        print(decoded_data[1:-0])
        #ignore the leading character tag of A, read the digits afterwards
        #if all other digits are numeric in value, it's a basic button press
        if decoded_data[1:].isnumeric(): 
            self.observer.EnableGameLoop()
            self.observer.VerifyButton(int(decoded_data[1:]))
        # if the last digit is an "L", it's a level up tag
        elif decoded_data[-1] == "L":
            self.observer.EnableGameLoop()
            self.observer.LevelUp()
            
        else:
            print(decoded_data)
    
    def sendButton(self, button):
        self.transport.write(button.encode("utf-8"))

def main():
    #JEREMY: CHANGE "99.28.129.156" INTO "localhost"
    #EVERYONE ELSE: DO THE OPPOSITE OF ABOVE
    ip = "99.28.129.156"
    maxLevels = 8
    observer = Observer(ip,maxLevels)
    observer.Run()
    observer.ExportData()

main()

