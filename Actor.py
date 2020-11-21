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
#import constants
# twisted imports
from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet.task import LoopingCall


# Constants
DESIRED_FPS = 30.0 # 30 frames per second
ACCEPTED_HATS = [(0,1),(0,-1),(1,0),(-1,0)]

# half of a second
DELAY = 0.56
# one sixth of a second
SHORT_DELAY = 0.1666666

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
DANCINGSPRITEX = (SCREENX/2)-64 
DANCINGSPRITEY = (SCREENY-200)
LEVELX = 0
LEVELY = 64
VIBRATEX = 0
VIBRATEY = (SCREENY/2)-160

CORRECTBUBBLESX = 0
CORRECTBUBBLESY = (SCREENY/2)-64



class Actor():
    def __init__(self, ip):
        self.recievedButton = -1
        self.correct = 0
        self.incorrect = 0
        self.level = 1


        self.BUBBLESINDEX = 0

        #intialize pygame
        pygame.init() # initialize the game and necessary parts
        self.screen = pygame.display.set_mode((SCREENX, SCREENY)) # Set the width and height of the screen (width, height).
        icon = pygame.image.load('ImageFiles/HATlab.png')
        pygame.display.set_icon(icon) # Icon for Game
        pygame.display.set_caption("Actor") #name the program
 
        pygame.joystick.init() # Initialize the joysticks.
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        #initialize pygame font
        self.font = pygame.font.Font('freesansbold.ttf', 20)

        #load all images
        self.import_images()

        # prepare all twisted
        self.point = TCP4ClientEndpoint(reactor, ip, 25565)
        self.connection = ActorTransmit(self)

    def import_images(self):
        """
        I2 = pygame.image.load('ImageFiles/Xbutton.png')
        I3 = pygame.image.load('ImageFiles/Ybutton.png')
        I0 = pygame.image.load('ImageFiles/Abutton.png')
        I1 = pygame.image.load('ImageFiles/Bbutton.png')
        I7 = pygame.image.load('ImageFiles/UPbutton.png')
        I4 = pygame.image.load('ImageFiles/DOWNbutton.png')
        I6 = pygame.image.load('ImageFiles/LEFTbutton.png')
        I5 = pygame.image.load('ImageFiles/RIGHTbutton.png')
        """
        self.background = pygame.image.load('ImageFiles/background.jpg')
        self.msuhat = pygame.image.load('ImageFiles/msuhat.png')
        dance1 = pygame.image.load('ImageFiles/DancingGuy/Dance1.png')
        dance2 = pygame.image.load('ImageFiles/DancingGuy/Dance2.png')
        dance3 = pygame.image.load('ImageFiles/DancingGuy/Dance3.png')
        dance4 = pygame.image.load('ImageFiles/DancingGuy/Dance4.png')
        dance5 = pygame.image.load('ImageFiles/DancingGuy/Dance5.png')
        dance6 = pygame.image.load('ImageFiles/DancingGuy/Dance6.png')

        Correct0 = pygame.image.load('ImageFiles/Bubbles/0Correct.png')
        Correct1 = pygame.image.load('ImageFiles/Bubbles/1Correct.png')
        Correct2 = pygame.image.load('ImageFiles/Bubbles/2Correct.png')
        Correct3 = pygame.image.load('ImageFiles/Bubbles/3Correct.png')
        Correct4 = pygame.image.load('ImageFiles/Bubbles/4Correct.png')
        Correct5 = pygame.image.load('ImageFiles/Bubbles/5Correct.png')

        self.VibrateA = pygame.image.load('ImageFiles/Vibrations/AButton.png')
        self.VibrateB = pygame.image.load('ImageFiles/Vibrations/BButton.png')
        self.VibrateX = pygame.image.load('ImageFiles/Vibrations/XButton.png')
        self.VibrateY = pygame.image.load('ImageFiles/Vibrations/YButton.png')
        self.VibrateDown = pygame.image.load('ImageFiles/Vibrations/DownButton.png')
        self.VibrateLeft = pygame.image.load('ImageFiles/Vibrations/LeftButton.png')
        self.VibrateRight = pygame.image.load('ImageFiles/Vibrations/RightButton.png')
        self.VibrateUp = pygame.image.load('ImageFiles/Vibrations/UpButton.png')
        self.VibrateBlank = pygame.image.load('ImageFiles/Vibrations/BlankPattern.png')

        self.dance = (dance1, dance2, dance3, dance4, dance5, dance6)

        self.bubbles = (Correct0, Correct1, Correct2, Correct3, Correct4, Correct5)

        self.CurrentVibration = self.VibrateBlank
        self.DisplayVibration = self.VibrateBlank

    def display(self):

        #display the background
        self.screen.fill((112, 128, 144))
        self.screen.blit(self.background,(0, 0))

        #display the correct score 
        corrscore = self.font.render("Correct: " + str(self.correct), True, (255,255,255))
        self.screen.blit(corrscore, (CORRECTSCOREX, CORRECTSCOREY))

        #display visual correctness
        self.screen.blit(self.bubbles[self.BUBBLESINDEX], (CORRECTBUBBLESX, CORRECTBUBBLESY))

        #display the incorrect score
        incorrscore = self.font.render("Incorrect: " + str(self.incorrect), True, (255,255,255))
        self.screen.blit(incorrscore, (INCORRECTSCOREX, INCORRECTSCOREY))

        #display hatlab logo
        self.screen.blit(self.msuhat, (0, 0))

        #display the current level
        currlevel = self.font.render("Level: " + str(self.level), True, (255,255,255))
        self.screen.blit(currlevel, (LEVELX, LEVELY))

        #display the vibration pattern
        self.screen.blit(self.DisplayVibration, (VIBRATEX, VIBRATEY))
        
        #display the dancing sprite
        #self.screen.blit(random.choice(self.dance), (DANCINGSPRITEX,DANCINGSPRITEY))
        #time.sleep(.05)


       
    def game_tick(self):
        done = False # Loop until the user clicks the close button.

        events = pygame.event.get()
        for event in events:
            # Process input events
            if event.type == pygame.QUIT: # If user clicked close.
                done = True # Flag that we are done so we exit this loop
            elif event.type == pygame.JOYBUTTONDOWN:
                # handle button presses, not dpad yet
                buttons = self.joystick.get_numbuttons()
                for i in range(buttons):
                    button = self.joystick.get_button(i)
                    if button == 1:

                        #send the button press to the cloud service
                        self.connection.sendButton("A" + str(i))
                        self.VerifyButton(str(i))


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

                        # create a new connection and send it to the Cloud Service
                        self.connection.sendButton("A" + str(hatValue))
                        self.VerifyButton(str(hatValue))

            # elif event.type == pygame.JOYBUTTONUP:
            #button go up :(
    
        
        #redraw()

        self.display()
        pygame.display.update()

        if done == True:
            #quit the game
            pygame.quit()
            reactor.stop()

    def GenerateVibration(self, left_intensity, right_intensity, duration):
        XInput.set_vibration(0, left_intensity, right_intensity)
        time.sleep(duration)
        XInput.set_vibration(0,NO_INTENSITY,NO_INTENSITY)
     
    def VerifyButton(self, button):
        if self.recievedButton == button:
            self.correct += 1
            self.DisplayVibration = self.VibrateBlank
            if self.BUBBLESINDEX <  5:
                self.BUBBLESINDEX += 1
            else:
                self.BUBBLESINDEX = 1
                self.correct = 1
                self.incorrect = 0 
                self.level += 1
        else:
            self.incorrect += 1
            self.BUBBLESINDEX = 0
            self.DisplayVibration = self.CurrentVibration

    def DecodeInput(self, inputSignal):
        self.recievedButton = inputSignal
        if inputSignal == "0":
            # low = A Button
            self.GenerateVibration(NO_INTENSITY,LOW_INTENSITY,DELAY)
        elif inputSignal == "1":
            # low - high  = B button
            self.GenerateVibration(NO_INTENSITY,LOW_INTENSITY,SHORT_DELAY)
            self.GenerateVibration(NO_INTENSITY,NO_INTENSITY,SHORT_DELAY)
            self.GenerateVibration(NO_INTENSITY,HIGH_INTENSITY,SHORT_DELAY)
        elif inputSignal == "2":
            # high - low = X button
            self.GenerateVibration(NO_INTENSITY,HIGH_INTENSITY,SHORT_DELAY)
            self.GenerateVibration(NO_INTENSITY,NO_INTENSITY,SHORT_DELAY)
            self.GenerateVibration(NO_INTENSITY,LOW_INTENSITY,SHORT_DELAY)
        elif inputSignal == "3":
            # high = Y button
            self.GenerateVibration(NO_INTENSITY,HIGH_INTENSITY,DELAY)
        elif inputSignal == "4":
            pass
        elif inputSignal == "5":
            pass
        elif inputSignal == "6":
            pass
        elif inputSignal == "7":
            pass
        elif inputSignal == "8":
            pass
        elif inputSignal == "9":
            pass
        elif inputSignal == "10":
            # low = DOWNbutton
            self.GenerateVibration(LOW_INTENSITY,NO_INTENSITY,2*DELAY)
        elif inputSignal == "11":
            self.CurrentVibration = self.VibrateRight
            # high - high - low = RIGHTbutton
            self.GenerateVibration(LOW_INTENSITY,NO_INTENSITY,SHORT_DELAY)
            self.GenerateVibration(NO_INTENSITY,NO_INTENSITY,SHORT_DELAY)
            self.GenerateVibration(HIGH_INTENSITY,NO_INTENSITY,SHORT_DELAY)
        elif inputSignal == "12":
            self.CurrentVibration = self.VibrateLeft
            # high - low - high = LEFTbutton
            self.GenerateVibration(HIGH_INTENSITY,NO_INTENSITY,SHORT_DELAY)
            self.GenerateVibration(NO_INTENSITY,NO_INTENSITY,SHORT_DELAY)
            self.GenerateVibration(LOW_INTENSITY,NO_INTENSITY,SHORT_DELAY)
        elif inputSignal == "13":
            # high = UPbutton
            self.GenerateVibration(HIGH_INTENSITY,NO_INTENSITY,2*DELAY)

    def Run(self):
        #turn on the game tick at the desired FPS
        tick = LoopingCall(self.game_tick)
        tick.start(1.0 / DESIRED_FPS)

        d = connectProtocol(self.point, self.connection)
        print("actor")
        reactor.run()


"""Get individual sprites from sprite sheets"""
 
class SpriteSheet(object):
#use to get images from a sprite sheet.
 
    def __init__(self, file_name):
        #Pass the file name of the sprite sheet.
 
        # Load the sprite sheet.
        self.sprite_sheet = pygame.image.load(file_name).convert()
 
 
    def get_image(self, x, y, width, height):
        """ get a single sprite from a spritesheet
            pass x, y coordinates of sprite
            and width and height of the sprite. """
 
        # make new blank image
        image = pygame.Surface([width, height]).convert()
 
        # copy sprite from spritesheet onto smaller image
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
 
        #transparent color (set as black)
        image.set_colorkey(constants.BLACK)
 
        return image


class ActorTransmit(Protocol):

    def __init__(self, actor):
        self.actor = actor

    def connectionMade(self):
        #self.transport.write(b"Actor Connected")
        pass

    def dataReceived(self, data):
        decoded_data = data.decode()
        if decoded_data[1:].isnumeric():
            self.actor.DecodeInput(decoded_data[1:])
        else:
            print(decoded_data)

    def sendButton(self, button):
        self.transport.write(button.encode("utf-8"))


def main():
    #JEREMY: CHANGE "99.28.129.156" INTO "localhost"
    #EVERYONE ELSE: DO THE OPPOSITE OF ABOVE
    ip = "99.28.129.156"
    actor = Actor(ip)
    actor.Run()




main()