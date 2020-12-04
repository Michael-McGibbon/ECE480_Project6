"""
GameDemo2.py
 
 Python application for running a game and transmitting button presses across a cloud service
    
 Author: Jeremy Cowelchuk, David Geisler, George Legacy, Michael McGibbon (add your names here)

 
# Button Icons from: https://www.nicepng.com/ourpic/u2w7i1i1u2q8q8a9_xbox-360-icon-opengameart-xbox-controller-button-icons/ - In the process of being made ourselves :)
# Background Image: https://depositphotos.com/stock-photos/dancefloor.html?qview=9919783 - Will need to find roalty free :) 
"""

#########################################################
# Imports
#########################################################
# Default imports as well as initalize next imports
import pygame
import time
import random
import XInput
import pandas as pd

# twisted imports
# Twisted is the python library which handles cloud services and netcode
from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet.task import LoopingCall

#random imports
# Random imports for handling seeds and which button gets added
from random import seed
from random import randint

#datetime imports
# Datetime imports for truely random seed generation
from datetime import datetime

#########################################################
# Constants
#########################################################

DESIRED_FPS = 30.0 # 30 frames per second
ACCEPTED_HATS = [(0,1),(0,-1),(1,0),(-1,0)] # HATS are the numpad listed as coordinates

SCREENX = 400 # X size of application
SCREENY = 600 # Y size of application
ACTIVEBUTTONX = (SCREENX/2)-64 # X Location of the button, minus button size
ACTIVEBUTTONY = (SCREENY/2)-64 # Y Location of the button, minus button size
CORRECTSCOREX = (SCREENX - 135) # X Location of the score
CORRECTSCOREY = 10 # Y Location of the score
INCORRECTSCOREX = CORRECTSCOREX # X Location of the incorrect score
INCORRECTSCOREY = (CORRECTSCOREY + 20) # Y Location of the incorrect score
DANCINGSPRITEX = (SCREENX/2)-64 # X Location of the dancer
DANCINGSPRITEY = (SCREENY-200) # Y Location of the dancer
LEVELX = 0 # X Location of Button
LEVELY = 64 # Y Location of Button


###
# Observer Class
# This class is the "observer" in the two application system. It will display a "game" to press the correct buttons and the buttons
# are transmitted to the twin application, the Actor. 
###
class Observer():
    ## Initalizes the Observer class
    # will go through and set everything up, making sure that everything is prepared in both the game and the networking side
    # /param ip The IP address the observer application will be connecting to
    # /param maxLevels The total number of levels that the program is able to run. Defaults to 5. Maximizes at 8.
    def __init__(self, ip, maxLevels = 5):
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
        if pygame.joystick.get_count() == 0: #error check to ensure that a joystick is plugged in.
            print("ERROR: No joystick has been plugged in")
            exit(0)
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


    ## import images function
    # loads all images for displaying buttons as well as the "dancer" sprite.
    # all extra images to be loaded should be loaded in here
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
        
        dance_crisscross1 = pygame.image.load('ImageFiles/Dancer-Crisscross/crisscross_1.png')
        dance_crisscross2 = pygame.image.load('ImageFiles/Dancer-Crisscross/crisscross_2.png')
        dance_crisscross3 = pygame.image.load('ImageFiles/Dancer-Crisscross/crisscross_3.png')
        dance_crisscross4 = pygame.image.load('ImageFiles/Dancer-Crisscross/crisscross_4.png')
        dance_crisscross5 = pygame.image.load('ImageFiles/Dancer-Crisscross/crisscross_5.png')
        dance_crisscross6 = pygame.image.load('ImageFiles/Dancer-Crisscross/crisscross_6.png')

        dance_egyptian1 = pygame.image.load('ImageFiles/Dancer-Egyptian/egyptian_1.png')
        dance_egyptian2 = pygame.image.load('ImageFiles/Dancer-Egyptian/egyptian_2.png')
        dance_egyptian3 = pygame.image.load('ImageFiles/Dancer-Egyptian/egyptian_3.png')
        dance_egyptian4 = pygame.image.load('ImageFiles/Dancer-Egyptian/egyptian_4.png')
        dance_egyptian5 = pygame.image.load('ImageFiles/Dancer-Egyptian/egyptian_5.png')
        dance_egyptian6 = pygame.image.load('ImageFiles/Dancer-Egyptian/egyptian_6.png')
        dance_egyptian7 = pygame.image.load('ImageFiles/Dancer-Egyptian/egyptian_7.png')
        dance_egyptian8 = pygame.image.load('ImageFiles/Dancer-Egyptian/egyptian_8.png')
        dance_egyptian9 = pygame.image.load('ImageFiles/Dancer-Egyptian/egyptian_9.png')
        dance_egyptian10 = pygame.image.load('ImageFiles/Dancer-Egyptian/egyptian_10.png')
        dance_egyptian11 = pygame.image.load('ImageFiles/Dancer-Egyptian/egyptian_11.png')
        dance_egyptian12 = pygame.image.load('ImageFiles/Dancer-Egyptian/egyptian_12.png')
        dance_egyptian13 = pygame.image.load('ImageFiles/Dancer-Egyptian/egyptian_13.png')
        dance_egyptian14 = pygame.image.load('ImageFiles/Dancer-Egyptian/egyptian_14.png')
        dance_egyptian15 = pygame.image.load('ImageFiles/Dancer-Egyptian/egyptian_15.png')
        dance_egyptian16 = pygame.image.load('ImageFiles/Dancer-Egyptian/egyptian_16.png')
        dance_egyptian17 = pygame.image.load('ImageFiles/Dancer-Egyptian/egyptian_17.png')
        dance_egyptian18 = pygame.image.load('ImageFiles/Dancer-Egyptian/egyptian_18.png')

        dance_lawnmower1 = pygame.image.load('ImageFiles/Dancer-Lawnmower/lawnmower_1.png')
        dance_lawnmower2 = pygame.image.load('ImageFiles/Dancer-Lawnmower/lawnmower_2.png')
        dance_lawnmower3 = pygame.image.load('ImageFiles/Dancer-Lawnmower/lawnmower_3.png')
        dance_lawnmower4 = pygame.image.load('ImageFiles/Dancer-Lawnmower/lawnmower_4.png')
        dance_lawnmower5 = pygame.image.load('ImageFiles/Dancer-Lawnmower/lawnmower_5.png')
        dance_lawnmower6 = pygame.image.load('ImageFiles/Dancer-Lawnmower/lawnmower_6.png')
        dance_lawnmower7 = pygame.image.load('ImageFiles/Dancer-Lawnmower/lawnmower_7.png')
        dance_lawnmower8 = pygame.image.load('ImageFiles/Dancer-Lawnmower/lawnmower_8.png')
        dance_lawnmower9 = pygame.image.load('ImageFiles/Dancer-Lawnmower/lawnmower_9.png')
        dance_lawnmower10 = pygame.image.load('ImageFiles/Dancer-Lawnmower/lawnmower_10.png')
        dance_lawnmower11 = pygame.image.load('ImageFiles/Dancer-Lawnmower/lawnmower_11.png')
        dance_lawnmower12 = pygame.image.load('ImageFiles/Dancer-Lawnmower/lawnmower_12.png')

        dance_scuba1 = pygame.image.load('ImageFiles/Dancer-Scuba/scuba_1.png')
        dance_scuba2 = pygame.image.load('ImageFiles/Dancer-Scuba/scuba_2.png')
        dance_scuba3 = pygame.image.load('ImageFiles/Dancer-Scuba/scuba_3.png')
        dance_scuba4 = pygame.image.load('ImageFiles/Dancer-Scuba/scuba_4.png')
        dance_scuba5 = pygame.image.load('ImageFiles/Dancer-Scuba/scuba_5.png')
        dance_scuba6 = pygame.image.load('ImageFiles/Dancer-Scuba/scuba_6.png')
        dance_scuba7 = pygame.image.load('ImageFiles/Dancer-Scuba/scuba_7.png')
        dance_scuba8 = pygame.image.load('ImageFiles/Dancer-Scuba/scuba_8.png')
        dance_scuba9 = pygame.image.load('ImageFiles/Dancer-Scuba/scuba_9.png')
        dance_scuba10 = pygame.image.load('ImageFiles/Dancer-Scuba/scuba_10.png')
        dance_scuba11 = pygame.image.load('ImageFiles/Dancer-Scuba/scuba_11.png')
        dance_scuba12 = pygame.image.load('ImageFiles/Dancer-Scuba/scuba_12.png')

        dance_snap1 = pygame.image.load('ImageFiles/Dancer-Snap/snap_1.png')
        dance_snap2 = pygame.image.load('ImageFiles/Dancer-Snap/snap_2.png')
        dance_snap3 = pygame.image.load('ImageFiles/Dancer-Snap/snap_3.png')
        dance_snap4 = pygame.image.load('ImageFiles/Dancer-Snap/snap_4.png')
        dance_snap5 = pygame.image.load('ImageFiles/Dancer-Snap/snap_5.png')
        dance_snap6 = pygame.image.load('ImageFiles/Dancer-Snap/snap_6.png')
        dance_snap7 = pygame.image.load('ImageFiles/Dancer-Snap/snap_7.png')
        dance_snap8 = pygame.image.load('ImageFiles/Dancer-Snap/snap_8.png')
        dance_snap9 = pygame.image.load('ImageFiles/Dancer-Snap/snap_9.png')
        dance_snap10 = pygame.image.load('ImageFiles/Dancer-Snap/snap_10.png')
        dance_snap11 = pygame.image.load('ImageFiles/Dancer-Snap/snap_11.png')
        dance_snap12 = pygame.image.load('ImageFiles/Dancer-Snap/snap_12.png')
       
        dance_split1 = pygame.image.load('ImageFiles/Dancer-Split/split_1.png')
        dance_split2 = pygame.image.load('ImageFiles/Dancer-Split/split_2.png')
        dance_split3 = pygame.image.load('ImageFiles/Dancer-Split/split_3.png')
        dance_split4 = pygame.image.load('ImageFiles/Dancer-Split/split_4.png')
        dance_split5 = pygame.image.load('ImageFiles/Dancer-Split/split_5.png')
        dance_split6 = pygame.image.load('ImageFiles/Dancer-Split/split_6.png')
        dance_split7 = pygame.image.load('ImageFiles/Dancer-Split/split_7.png')
        dance_split8 = pygame.image.load('ImageFiles/Dancer-Split/split_8.png')
        dance_split9 = pygame.image.load('ImageFiles/Dancer-Split/split_9.png')
        dance_split10 = pygame.image.load('ImageFiles/Dancer-Split/split_10.png')
        dance_split11 = pygame.image.load('ImageFiles/Dancer-Split/split_11.png')
        dance_split12 = pygame.image.load('ImageFiles/Dancer-Split/split_12.png')
        dance_split13 = pygame.image.load('ImageFiles/Dancer-Split/split_13.png')
        dance_split14 = pygame.image.load('ImageFiles/Dancer-Split/split_14.png')
        dance_split15 = pygame.image.load('ImageFiles/Dancer-Split/split_15.png')
        dance_split16 = pygame.image.load('ImageFiles/Dancer-Split/split_16.png')
        dance_split17 = pygame.image.load('ImageFiles/Dancer-Split/split_17.png')
        dance_split18 = pygame.image.load('ImageFiles/Dancer-Split/split_18.png')
        dance_split19 = pygame.image.load('ImageFiles/Dancer-Split/split_19.png')
        dance_split20 = pygame.image.load('ImageFiles/Dancer-Split/split_20.png')
        dance_split21 = pygame.image.load('ImageFiles/Dancer-Split/split_21.png')
        dance_split22 = pygame.image.load('ImageFiles/Dancer-Split/split_22.png')
        dance_split23 = pygame.image.load('ImageFiles/Dancer-Split/split_23.png')
        dance_split24 = pygame.image.load('ImageFiles/Dancer-Split/split_24.png')

        dance_sprinkler1 = pygame.image.load('ImageFiles/Dancer-Sprinkler/sprinkler_1.png')
        dance_sprinkler2 = pygame.image.load('ImageFiles/Dancer-Sprinkler/sprinkler_2.png')
        dance_sprinkler3 = pygame.image.load('ImageFiles/Dancer-Sprinkler/sprinkler_3.png')
        dance_sprinkler4 = pygame.image.load('ImageFiles/Dancer-Sprinkler/sprinkler_4.png')
        dance_sprinkler5 = pygame.image.load('ImageFiles/Dancer-Sprinkler/sprinkler_5.png')
        dance_sprinkler6 = pygame.image.load('ImageFiles/Dancer-Sprinkler/sprinkler_6.png')
        dance_sprinkler7 = pygame.image.load('ImageFiles/Dancer-Sprinkler/sprinkler_7.png')
        dance_sprinkler8 = pygame.image.load('ImageFiles/Dancer-Sprinkler/sprinkler_8.png')

        dance_wave1 = pygame.image.load('ImageFiles/Dancer-Wave/wave_1.png')
        dance_wave2 = pygame.image.load('ImageFiles/Dancer-Wave/wave_2.png')
        dance_wave3 = pygame.image.load('ImageFiles/Dancer-Wave/wave_3.png')
        dance_wave4 = pygame.image.load('ImageFiles/Dancer-Wave/wave_4.png')
        dance_wave5 = pygame.image.load('ImageFiles/Dancer-Wave/wave_5.png')
        dance_wave6 = pygame.image.load('ImageFiles/Dancer-Wave/wave_6.png')
        dance_wave7 = pygame.image.load('ImageFiles/Dancer-Wave/wave_7.png')
        dance_wave8 = pygame.image.load('ImageFiles/Dancer-Wave/wave_8.png')
        dance_wave9 = pygame.image.load('ImageFiles/Dancer-Wave/wave_9.png')
        dance_wave10 = pygame.image.load('ImageFiles/Dancer-Wave/wave_10.png')
        

        self.background = pygame.image.load('ImageFiles/background.jpg')
        self.msuhat = pygame.image.load('ImageFiles/msuhat.png')

        self.crisscrossdance = (dance_crisscross1, dance_crisscross2, dance_crisscross3, dance_crisscross4, dance_crisscross5, dance_crisscross6)
        self.egyptiandance = (dance_egyptian1, dance_egyptian2, dance_egyptian3, dance_egyptian4, dance_egyptian5, dance_egyptian6, dance_egyptian7, dance_egyptian8, dance_egyptian9, dance_egyptian10, dance_egyptian11, dance_egyptian12, dance_egyptian13, dance_egyptian14, dance_egyptian15, dance_egyptian16, dance_egyptian17, dance_egyptian18)
        self.lawnmowerdance = (dance_lawnmower1, dance_lawnmower2, dance_lawnmower3, dance_lawnmower4, dance_lawnmower5, dance_lawnmower6, dance_lawnmower7, dance_lawnmower8, dance_lawnmower9, dance_lawnmower10, dance_lawnmower11, dance_lawnmower12)
        self.scubadance = (dance_scuba1, dance_scuba2, dance_scuba3, dance_scuba4, dance_scuba5, dance_scuba6, dance_scuba7, dance_scuba8, dance_scuba9, dance_scuba10, dance_scuba11, dance_scuba12)
        self.snapdance = (dance_snap1, dance_snap2, dance_snap3, dance_snap4, dance_snap5, dance_snap6, dance_snap7, dance_snap8, dance_snap9, dance_snap10, dance_snap11, dance_snap12)
        self.splitdance = (dance_split1, dance_split2, dance_split3, dance_split4, dance_split5, dance_split6, dance_split7, dance_split8, dance_split9, dance_split10, dance_split11, dance_split12, dance_split13, dance_split14, dance_split15, dance_split16, dance_split17, dance_split18, dance_split19, dance_split20, dance_split21, dance_split22, dance_split23, dance_split24)
        self.sprinklerdance = (dance_sprinkler1, dance_sprinkler2, dance_sprinkler3, dance_sprinkler4, dance_sprinkler5, dance_sprinkler6, dance_sprinkler7, dance_sprinkler8)
        self.wavedance = (dance_wave1, dance_wave2, dance_wave3, dance_wave4, dance_wave5, dance_wave6, dance_wave7, dance_wave8, dance_wave9, dance_wave10)
        self.imagelist = [(0,I0), (1,I1), (2,I2), (3,I3), (10,I4), (11,I5), (12,I6), (13,I7)]


    ## displays all images needed for the game
    # blits the pygame game to create the visuals necessary to create the game.
    # all display should be placed in here
    def Display(self):

        # Set up font
        self.font = pygame.font.Font('comicsans.ttf', 20)

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


    ## is the "dance" system for handling the "dancer"
    # allows the dancer do dance
    # all dancing related spritework should be placed in here
    def Dance(self,button):
            if button == 0:
                self.screen.blit(self.crisscrossdance, (DANCINGSPRITEX, DANCINGSPRITEY))
            elif button == 1:
                self.screen.blit(self.egyptiandance, (DANCINGSPRITEX, DANCINGSPRITEY))
            elif button == 2:
                self.screen.blit(self.lawnmowerdance, (DANCINGSPRITEX, DANCINGSPRITEY))
            elif button == 3: 
                self.screen.blit(self.scubadance, (DANCINGSPRITEX, DANCINGSPRITEY))
            elif button == 10:
                self.screen.blit(self.snapdance, (DANCINGSPRITEX, DANCINGSPRITEY))
            elif button == 11:
                self.screen.blit(self.splitdance, (DANCINGSPRITEX, DANCINGSPRITEY))
            elif button == 12:
                self.screen.blit(self.sprinklerdance, (DANCINGSPRITEX, DANCINGSPRITEY))
            elif button == 13:
                self.screen.blit(self.wavedance, (DANCINGSPRITEX, DANCINGSPRITEY))


    ## Changes the buttons to the next desired button
    # This will randomly pick a new button from the list of available buttons, 
    # then set the active displayed buttton and active desired button to the
    # selected button. The display will then be forced to update to ensure the
    # correct button is displayed.
    def ChangeButton(self):
        #select the new button from the list
        newButton = random.choice(self.buttonList)
        self.activeButtonImage = (newButton[1])
        self.activeButton = (newButton[0])

        # force update the display
        self.display()
        pygame.display.update()


    ## Levels up the game to include new buttons
    # This resets the score for a given level and increments the level counter.
    # Additionally this adds a "section" in the excel sheet to seperate this level
    # from the previous levels. After this, it checks if the level exceeds max levels, then
    # levels up if so.  Then, it forces the next button to be the new button and forces the
    # display to update
    def LevelUp(self):
        # Resets scores and increments levels
        self.level += 1
        self.incorrect = 0
        self.correct = 0

        # adds new data collection section
        self.df = self.df.append({'Level': self.level}, ignore_index=True)

        #if we're above the max number of levels, stop
        if self.maxLevels < self.level:
            #quit the game
            self.enabled = False
            reactor.stop()
            pygame.quit()
            return

        # Randomly select the new button from the available buttons, then remove it from that list
        newButton = random.choice(self.imagelist)
        self.buttonList.append(newButton)
        self.imagelist.remove(newButton)

        # Force the next button to the be new button
        self.activeButtonImage = (newButton[1])
        self.activeButton = (newButton[0])

        # Force update the display to ensure new button is displayed immedietely
        self.Display()
        pygame.display.update()


    ## Verfies if the recieved button is the correct button
    # This first checks the time the button has been recieved, then check the
    # veracity of the button. Then it calls collect data and changes the button
    # /param button The inputted button
    def VerifyButton(self, button):
        # check the time between button presses
        self.timeRecieved = int(round(time.time() * 1000))

        # Check the button versus the sent button
        if self.pressedButton == button:
            self.correct += 1
            #self.Dance()
        else:
            self.incorrect += 1

        # Collects data
        self.CollectData(button)

        # Changes the button regardless if correct or not
        self.ChangeButton()


    ## Handles Pandas Data Collection
    # First converts the button into a valid type, then calculates time total of the button press.
    # Then updates the Data Frame with the value of the button and it's veracity.
    # \param button The inputted button
    def CollectData(self, button):
        # Collect the data for adding to the data frame
        buttonStr = self.ButtonValueConversion(button)
        pressedButtonStr = self.ButtonValueConversion(self.pressedButton)
        timeStamp = self.timeRecieved - self.timePressed

        # check button veracity
        if self.pressedButton == button:
            veracity = "Correct"
        else:
            veracity = "Incorrect"

        # Update the data frame
        self.df = self.df.append({'Intended Button': pressedButtonStr, 'Pressed Button': buttonStr, 'Correct/Incorrect': veracity, 'Time': timeStamp}, ignore_index=True)


    ## Converts button integer values into String values representative of their button
    # Checks in inputted integer value and converts it among accepted signals.
    # Additionally checks to ensure that the inputted value is an accepted value
    # \param button The inputted button
    # \return The string value of the button inputted
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
        else: #error check
            print("ERROR: Invalid button press")

        
    ## Exports the Pandas Data Frame to a .csv file
    # Exports the data frame
    def ExportData(self):
        # exports as a .csv
        self.df.to_csv("Data.csv",index=False)


    ## Handles the game tick of the game played.
    # Enabled or disabled depending on the send/recieve cycle of the Actor/Observer pair.
    # Then handles all input for the pygame and processes it.
    def game_tick(self):
        # Check to see if any values should be read
        if self.enabled == True:
            events = pygame.event.get()
            for event in events:

                # Process input events
                if event.type == pygame.QUIT: # If user clicked close.
                    self.done = True # Flag that we are done so we exit this loop

                elif event.type == pygame.JOYBUTTONDOWN: # If input on joystick buttons
                    buttons = self.joystick.get_numbuttons()
                    for i in range(buttons): # Check each button,
                        button = self.joystick.get_button(i) # Get if button is pressed
                        if button == 1: #if button is pressed ( == 1)
                            if i == self.activeButton: # prevent the incorrect button from being sent
                                #send the button with an attached "O" to mark the file of origin
                                self.connection.sendButton("O" + str(i)) 
                                self.pressedButton = i # mark the button as the sent button
                                self.enabled = False  # disable the game tick

                elif event.type == pygame.JOYHATMOTION: # if input on joystick directional pad (HAT)
                    # handle dpad presses
                    hats = self.joystick.get_numhats()
                    for i in range(hats): #check each potential hat pair
                        hat = self.joystick.get_hat(i) #gets the value
                        if (hat in ACCEPTED_HATS): #ensure that only the four cardian directions are considered as input
                            #convert the value of the hat into an integer value for transmission, as opposed to a pair
                            if hat == (0,1):
                                hatValue = 13
                            elif hat == (0,-1):
                                hatValue = 10
                            elif hat == (1,0):
                                hatValue = 11
                            elif hat == (-1,0):
                                hatValue = 12

                            if hatValue == self.activeButton: # make sure the button is the correct button
                                #send the hat press to actor.py with an attached "O" to mark application of origin
                                self.connection.sendButton("O" + str(hatValue))
                                self.pressedButton = hatValue # mark the button as the sent button
                                self.enabled = False #disable game loop

                self.timePressed = int(round(time.time() * 1000)) # Mark the time in milliseconds as the moment the button was pressed
        
                # if the game is marked as "done"
                if self.done == True:
                    #quit the game
                    reactor.stop()
                    pygame.quit()

                else: #update the games visuals
                    self.Display()
                    pygame.display.update()

    
    ## Allow the gameloop to run again
    def EnableGameLoop(self):
        # enable the game tick 
        self.enabled = True

    ## Run the observer application
    # First set up a looping call function to allow the pygame application and twisted reactor to run simultaneously.
    # If this was not done, then one of the two would hog all processor and prevent the other from running.
    def Run(self):
        # Set up a looping call every 1/30th of a second to run your game tick
        # This allows the game to run in addition to the server client
        tick = LoopingCall(self.game_tick)
        tick.start(1.0 / DESIRED_FPS)

        # connect the client to the server.
        d = connectProtocol(self.point, self.connection)
        print("observer")
        reactor.run()


###
# Observer Protocol Class
# This class enables a client protocol unique to the Observer application and allows it to handle the correct messages and process
# recieved messages correctly.
###
class ObserverTransmit(Protocol):

    ## Intialize the ObserverTransmit
    # Prepares the observer transmitter to run correct by connecting the observer and marking the protocol as "unconnected"
    # \param observer The Observer object the transmit is a part of
    def __init__(self, observer):
        self.observer = observer
        self.connected = False


    ## Runs when the ObserverTransmit successfully connects to a server
    # Sends an "O" to mark the connection as an observer for server side management, then marks
    # connection as "True"
    def connectionMade(self):
        message = "O"
        self.transport.write(message.encode("utf-8")) # sends the message of an "O" in byte format
        self.connected = True


    ## Runs when data is recieved by this client protocol
    # First decodes the data from a utf-8 format into a string. Then processes
    # the recieved transmission and sends it to the correct location
    def dataReceived(self, data):
        decoded_data = data.decode() 
        #ignore the leading character tag of A, read the digits afterwards
        #if all other digits are numeric in value, it's a basic button press
        if decoded_data[1:].isnumeric(): 
            self.observer.EnableGameLoop()
            self.observer.VerifyButton(int(decoded_data[1:]))
        # if the last digit is an "L", it's a level up tag
        elif decoded_data[-1] == "L":
            self.observer.EnableGameLoop()
            self.observer.LevelUp()
    
    ## Sends a inputted button press 
    # Sends a button to the server for redirection to the Actor application
    def sendButton(self, button):
        # checks if the connection has been established to prevent crashes
        if self.connected:
            self.transport.write(button.encode("utf-8")) #sends the button
        else:
            print("ERROR: No connection to server established")


## Main
# For running the Observer application
# ALL VARIABLES THAT CAN BE CHANGED GO IN HERE
def main():

    #ip = "localhost" # If the cloud service is ran on the same computer as this application, this is the ip
    ip = "99.28.129.156" # The ip address of the computer hosting "CloudService.py"
    maxLevels = 3 # The maximum allowed number of levels. This cannot go further than 8 unless additional signals are added

    #create the observer and run it
    observer = Observer(ip,maxLevels) 
    observer.Run()

    #once the observer is done, export all collected data to a file
    observer.ExportData()

main()

