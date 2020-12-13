"""
Actor.py
Python application for recieving button input from another controller, reading them as vibrations and then sending an interpreted
signal back to the source controller.
Authors: Jeremy Cowelchuk, David Geisler, George Legacy, Michael McGibbon, and Pavan Patel

# Background Image: https://depositphotos.com/stock-photos/dancefloor.html?qview=9919783 - Will need to find roalty free :) 
"""


#########################################################
# Imports
#########################################################
# Default imports
import pygame
import time
import random
import XInput

# Twisted imports for handling client applications
from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet.task import LoopingCall


#########################################################
# CONSTANTS
#########################################################
DESIRED_FPS = 30.0 # 30 frames per second
ACCEPTED_HATS = [(0,1),(0,-1),(1,0),(-1,0)] #acceptable dpad coordinates

#Time Delay Constants
DELAY = 0.50 # half a second
SHORT_DELAY = 0.1666666 # one sixth of a second

#Intensity Constants
HIGH_INTENSITY = 1.0 # full strength
LOW_INTENSITY = 0.125 # one eighth strength
NO_INTENSITY = 0.0 # no strength

# Visual Constants
SCREENX = 400 # screen width
SCREENY = 600 # screen height
CORRECTSCOREX = (SCREENX - 135) # X location of the correct score
CORRECTSCOREY = 10 # Y location of the correct score
INCORRECTSCOREX = CORRECTSCOREX # X location of the incorrect score
INCORRECTSCOREY = (CORRECTSCOREY + 20) # Y location of the incorrect score
DANCINGSPRITEX = (SCREENX/2)-64 # X location of the dancer
DANCINGSPRITEY = (SCREENY-200) # Y location of the dancer
LEVELX = 0 # X location of the level counter
LEVELY = 64 # Y location of the level counter
VIBRATEX = 0 # X location of the vibration hint
VIBRATEY = (SCREENY/2)-160 # Y location of the vibration hint
CORRECTBUBBLESX = 0 # X location of the bubbles
CORRECTBUBBLESY = (SCREENY/2)-64 # Y location of the bubbles


## Actor class
# This class handles the "Actor" application. This applications awaits a signal to be recieved from the Observer.
# When it is recieved, the controller generates a unique vibration pattern dependant on the signal recieved
# It then awaits a button press, and checks its veracity. Regardless, it sends the button back to the Observer
# for data collection.
class Actor():

    ## Initalize the actor class
    # Get everything set up for the game and the server of the actor application.
    # \param ip The IP address of the computer the cloud service is hosted on
    # \param maxLevels The maximum number of levels the game will run for. Needs to match the paired Observer. Cannot go beyond 8.
    def __init__(self, ip, maxLevels):
        self.recievedButton = -1
        self.correct = 0
        self.incorrect = 0
        self.level = 1
        self.enabled = False
        self.seenButtons = []
        self.desiredButton = -1
        self.maxLevels = maxLevels
        self.bubblesIndex = 0

        #intialize pygame
        pygame.init() # initialize the game and necessary parts
        self.screen = pygame.display.set_mode((SCREENX, SCREENY)) # Set the width and height of the screen (width, height).
        icon = pygame.image.load('ImageFiles/HATlab.png')
        pygame.display.set_icon(icon) # Icon for Game
        pygame.display.set_caption("Actor") #name the program
 
        pygame.joystick.init() # Initialize the joysticks.
        if pygame.joystick.get_count() == 0: # check for a crash related to no controller plugged in, safely exit if none found.
            print("ERROR: No joystick has been plugged in")
            exit(0)
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        #initialize pygame font
        self.font = pygame.font.Font("comicsans.ttf", 20)

        #load all images
        self.import_images()

        #display all images
        self.Display()
        pygame.display.update()

        # prepare all twisted
        self.point = TCP4ClientEndpoint(reactor, ip, 25565)
        self.connection = ActorTransmit(self)


    ## Imports all images for the game
    # all imports related to images should go here
    def import_images(self):
        #load up background values
        self.background = pygame.image.load('ImageFiles/background.jpg')
        self.msuhat = pygame.image.load('ImageFiles/msuhat.png')
        
        # load up vibration hints
        self.VibrateA = pygame.image.load('ImageFiles/Vibrations/AButton.png')
        self.VibrateB = pygame.image.load('ImageFiles/Vibrations/BButton.png')
        self.VibrateX = pygame.image.load('ImageFiles/Vibrations/XButton.png')
        self.VibrateY = pygame.image.load('ImageFiles/Vibrations/YButton.png')
        self.VibrateDown = pygame.image.load('ImageFiles/Vibrations/DownButton.png')
        self.VibrateLeft = pygame.image.load('ImageFiles/Vibrations/LeftButton.png')
        self.VibrateRight = pygame.image.load('ImageFiles/Vibrations/RightButton.png')
        self.VibrateUp = pygame.image.load('ImageFiles/Vibrations/UpButton.png')
        self.VibrateBlank = pygame.image.load('ImageFiles/Vibrations/BlankPattern.png')

        # load up correct bubble images
        Correct0 = pygame.image.load('ImageFiles/Bubbles/0Correct.png')
        Correct1 = pygame.image.load('ImageFiles/Bubbles/1Correct.png')
        Correct2 = pygame.image.load('ImageFiles/Bubbles/2Correct.png')
        Correct3 = pygame.image.load('ImageFiles/Bubbles/3Correct.png')
        Correct4 = pygame.image.load('ImageFiles/Bubbles/4Correct.png')
        Correct5 = pygame.image.load('ImageFiles/Bubbles/5Correct.png')
        
        # save them to be used elsewhere
        self.bubbles = (Correct0, Correct1, Correct2, Correct3, Correct4, Correct5)

        self.CurrentVibration = self.VibrateBlank
        self.DisplayVibration = self.VibrateBlank

        #intialize all the dancing
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

        self.crisscrossdance = [dance_crisscross1, dance_crisscross2, dance_crisscross3, dance_crisscross4, dance_crisscross5, dance_crisscross6]
        self.egyptiandance = [dance_egyptian1, dance_egyptian2, dance_egyptian3, dance_egyptian4, dance_egyptian5, dance_egyptian6, dance_egyptian7, dance_egyptian8, dance_egyptian9, dance_egyptian10, dance_egyptian11, dance_egyptian12, dance_egyptian13, dance_egyptian14, dance_egyptian15, dance_egyptian16, dance_egyptian17, dance_egyptian18]
        self.lawnmowerdance = [dance_lawnmower1, dance_lawnmower2, dance_lawnmower3, dance_lawnmower4, dance_lawnmower5, dance_lawnmower6, dance_lawnmower7, dance_lawnmower8, dance_lawnmower9, dance_lawnmower10, dance_lawnmower11, dance_lawnmower12]
        self.scubadance = [dance_scuba1, dance_scuba2, dance_scuba3, dance_scuba4, dance_scuba5, dance_scuba6, dance_scuba7, dance_scuba8, dance_scuba9, dance_scuba10, dance_scuba11, dance_scuba12]
        self.snapdance = [dance_snap1, dance_snap2, dance_snap3, dance_snap4, dance_snap5, dance_snap6, dance_snap7, dance_snap8, dance_snap9, dance_snap10, dance_snap11, dance_snap12]
        self.splitdance = [dance_split1, dance_split2, dance_split3, dance_split4, dance_split5, dance_split6, dance_split7, dance_split8, dance_split9, dance_split10, dance_split11, dance_split12, dance_split13, dance_split14, dance_split15, dance_split16, dance_split17, dance_split18, dance_split19, dance_split20, dance_split21, dance_split22, dance_split23, dance_split24]
        self.sprinklerdance = [dance_sprinkler1, dance_sprinkler2, dance_sprinkler3, dance_sprinkler4, dance_sprinkler5, dance_sprinkler6, dance_sprinkler7, dance_sprinkler8]
        self.wavedance = [dance_wave1, dance_wave2, dance_wave3, dance_wave4, dance_wave5, dance_wave6, dance_wave7, dance_wave8, dance_wave9, dance_wave10]

        self.currentDanceFrame = self.crisscrossdance[0]


    ## Displays all game related images
    # all display functions, with some notable exceptions, should go in here.
    # this is useful for game design
    def Display(self):

        #display the background
        self.screen.fill((112, 128, 144))
        self.screen.blit(self.background,(0, 0))

        #display the dancing sprite
        self.screen.blit(self.currentDanceFrame, (DANCINGSPRITEX, DANCINGSPRITEY))

        #display the correct score 
        corrscore = self.font.render("Correct: " + str(self.correct), True, (255,255,255))
        self.screen.blit(corrscore, (CORRECTSCOREX, CORRECTSCOREY))

        #display visual correctness
        self.screen.blit(self.bubbles[self.bubblesIndex], (CORRECTBUBBLESX, CORRECTBUBBLESY))

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
        

    ## is the "dance" system for handling the "dancer"
    # allows the dancer do dance
    # all dancing related spritework should be placed in here
    def Dance(self,button):
        if button == 0:
            for i in range(0,len(self.crisscrossdance)-1):
                self.currentDanceFrame = self.crisscrossdance[i]
                self.Display()
                pygame.display.update()
                time.sleep(0.1)
        elif button == 1:
            for i in range(0,len(self.egyptiandance)-1):
                self.currentDanceFrame = self.egyptiandance[i]
                self.Display()
                pygame.display.update()
                time.sleep(0.1)
        elif button == 2:
            for i in range(0,len(self.lawnmowerdance)-1):
                self.currentDanceFrame = self.lawnmowerdance[i]
                self.Display()
                pygame.display.update()
                time.sleep(0.1)
        elif button == 3: 
            for i in range(0,len(self.scubadance)-1):
                self.currentDanceFrame = self.scubadance[i]
                self.Display()
                pygame.display.update()
                time.sleep(0.1)
        elif button == 10:
            for i in range(0,len(self.snapdance)-1):
                self.currentDanceFrame = self.snapdance[i]
                self.Display()
                pygame.display.update()
                time.sleep(0.1)
        elif button == 11:
            for i in range(0,len(self.splitdance)-1):
                self.currentDanceFrame = self.splitdance[i]
                self.Display()
                pygame.display.update()
                time.sleep(0.1)
        elif button == 12:
            for i in range(0,len(self.sprinklerdance)-1):
                self.currentDanceFrame = self.sprinklerdance[i]
                self.Display()
                pygame.display.update()
                time.sleep(0.1)
        elif button == 13:
            for i in range(0,len(self.wavedance)-1):
                self.currentDanceFrame = self.wavedance[i]
                self.Display()
                pygame.display.update()
                time.sleep(0.1)
        #display the default frame of the dancer
        self.currentDanceFrame = self.crisscrossdance[0]
        self.Display()
        pygame.display.update()
        time.sleep(0.1)


    ## Run the game tick for playing the game and reading player input
    # Checks for all events in game and processes them accordingly.
    # skips over entire loop if not enabled
    def game_tick(self):
        done = False # Loop until the user clicks the close button.

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT: # If user clicked close.
                    done = True # Flag that we are done so we exit this loop
            if self.enabled:
                # Process input events
                if event.type == pygame.JOYBUTTONDOWN:
                    # handle button presses
                    buttons = self.joystick.get_numbuttons()
                    for i in range(buttons):
                        # check which buttons are pressed
                        button = self.joystick.get_button(i)
                        if button == 1:

                            #send the button press to the cloud service
                            self.connection.sendButton("A" + str(i))
                            self.VerifyButton(str(i)) #check the value of the button to the recieved one

                elif event.type == pygame.JOYHATMOTION:
                    # handle dpad presses
                    hats = self.joystick.get_numhats()
                    for i in range(hats):
                        hat = self.joystick.get_hat(i)
                        if (hat in ACCEPTED_HATS): #check to make sure that its a valid dpad input
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
                            self.VerifyButton(str(hatValue)) #check the value of the dpad press to the recieved one
    
        
        #redraw()

        self.Display()
        pygame.display.update()

        if done == True:
            #quit the game
            pygame.quit()
            reactor.stop()


    ## Level up the game 
    # Reset the scores of the game and send a signal to the observer to level up.
    # If the current level is higher than the maximum number of levels, close the program
    def LevelUp(self):
        # reset scores
        self.bubblesIndex = 0
        self.correct = 0
        self.incorrect = 0 
        self.level += 1
        self.connection.sendLevelUp()

        # if we're at max levels, close it
        if self.maxLevels < self.level:
            #quit the game
            """
            self.enabled = False
            reactor.stop()
            pygame.quit()
            """
    

    ## Generate the vibration patterns
    # Generates a pattern following this pattern "SIGNAL - NO_SIGNAL"
    # \param left_intensity The vibration strength of the left half of the controller
    # \param right_intensity The vibration strength of the right half of the controller
    # \param duration The duration of the vibration strength of the entire controller
    def GenerateVibration(self, left_intensity, right_intensity, duration):
        XInput.set_vibration(0, left_intensity, right_intensity)
        time.sleep(duration)
        XInput.set_vibration(0,NO_INTENSITY,NO_INTENSITY)
     

    ## Verifies the button to the recieved button
    # Increases the bubble total if it is a new button that is correct, and if total bubbles are filled, levels up
    # \param button The button to be verified
    def VerifyButton(self, button):
        self.enabled = False # stop the game tick, prevent further presses
        if self.recievedButton == button: # if the buttons match
            self.correct += 1
            self.DisplayVibration = self.VibrateBlank
            if self.desiredButton == button: # if the button is the newest button (one we want to level up on)
                if self.bubblesIndex <  5: # check to see if bubbles are filled
                    self.bubblesIndex += 1
                else:
                    self.LevelUp() #level up if full
            self.Dance(int(button))       # call the dance animation 
        else: # if buttons dont match
            self.incorrect += 1
            self.DisplayVibration = self.CurrentVibration #display the missed vibration


    ## Decodes the input from a button pressed and turns it into a vibration signal
    # First, compares the signal to a list of "seen" signals. This keeps track of what is the newest button, and thus the one
    # to increment bubbles for the next level. Then turns the signal into a vibration pattern.
    def DecodeInput(self, inputSignal):
        self.enabled = True # allow the actor to press buttons again
        self.recievedButton = inputSignal # save it for comparing later
        if self.recievedButton not in self.seenButtons: 
            #see if its a new button, and if it is, add it to seen and make it the level up button
            self.desiredButton = self.recievedButton
            self.seenButtons.append(self.desiredButton)

        # Generate vibrations based on what button it is. If more are to be added, they need to be added here as well as the Observer
            # it is possible to add non-cardinal Dpad inputs, such as "UPRIGHT", but that needs to be added to ACCEPTEDHATS, as well as
            # given an integer value in Observer.py gametick
        if inputSignal == "0":
            self.CurrentVibration = self.VibrateA
            # low = A Button
            self.GenerateVibration(NO_INTENSITY,LOW_INTENSITY,DELAY)
        elif inputSignal == "1":
            self.CurrentVibration = self.VibrateB
            # low - high  = B button
            self.GenerateVibration(NO_INTENSITY,LOW_INTENSITY,SHORT_DELAY)
            self.GenerateVibration(NO_INTENSITY,NO_INTENSITY,SHORT_DELAY)
            self.GenerateVibration(NO_INTENSITY,HIGH_INTENSITY,SHORT_DELAY)
        elif inputSignal == "2":
            self.CurrentVibration = self.VibrateX
            # high - low = X button
            self.GenerateVibration(NO_INTENSITY,HIGH_INTENSITY,SHORT_DELAY)
            self.GenerateVibration(NO_INTENSITY,NO_INTENSITY,SHORT_DELAY)
            self.GenerateVibration(NO_INTENSITY,LOW_INTENSITY,SHORT_DELAY)
        elif inputSignal == "3":
            self.CurrentVibration = self.VibrateY
            # high = Y button
            self.GenerateVibration(NO_INTENSITY,HIGH_INTENSITY,DELAY)
        elif inputSignal == "4":
            # right bumper
            pass
        elif inputSignal == "5":
            # left bumper
            pass
        elif inputSignal == "6":
            # select
            pass
        elif inputSignal == "7":
            # start
            pass
        elif inputSignal == "8":
            # L3
            pass
        elif inputSignal == "9":
            # R3
            pass
        elif inputSignal == "10":
            self.CurrentVibration = self.VibrateDown
            # low = DOWNbutton
            self.GenerateVibration(LOW_INTENSITY,NO_INTENSITY,2*DELAY)
        elif inputSignal == "11":
            self.CurrentVibration = self.VibrateRight
            # low - high = RIGHTbutton
            self.GenerateVibration(LOW_INTENSITY,NO_INTENSITY,SHORT_DELAY)
            self.GenerateVibration(NO_INTENSITY,NO_INTENSITY,SHORT_DELAY)
            self.GenerateVibration(HIGH_INTENSITY,NO_INTENSITY,SHORT_DELAY)
        elif inputSignal == "12":
            self.CurrentVibration = self.VibrateLeft
            # high - low = LEFTbutton
            self.GenerateVibration(HIGH_INTENSITY,NO_INTENSITY,SHORT_DELAY)
            self.GenerateVibration(NO_INTENSITY,NO_INTENSITY,SHORT_DELAY)
            self.GenerateVibration(LOW_INTENSITY,NO_INTENSITY,SHORT_DELAY)
        elif inputSignal == "13":
            self.CurrentVibration = self.VibrateUp
            # high = UPbutton
            self.GenerateVibration(HIGH_INTENSITY,NO_INTENSITY,2*DELAY)


    ## Run the Actor application
    # sets up the game tick and the client to connect to the cloud and prevents them from taking up too much processor so neither
    # can run
    def Run(self):
        #turn on the game tick at the desired FPS
        tick = LoopingCall(self.game_tick)
        tick.start(1.0 / DESIRED_FPS)

        # set up the client connection and run it
        d = connectProtocol(self.point, self.connection)
        print("actor")
        reactor.run()


## Actor transmit class for handling client server connections
# This is unique to the Actor class and necessary to allow the actor to handle its specific functions
class ActorTransmit(Protocol):

    ## Initalize the actor transmit class
    # Sets up the actor transmit varibles, namely which actor its connected to as well as if its connected
    # \param actor The actor it is connected to
    def __init__(self, actor):
        self.actor = actor
        self.connected = False


    ## Automatically runs when a connection is made to a server
    # Sends an "A" for marking the file of origin as an Actor to be slotted correct, then enables the connection
    def connectionMade(self):
        self.transport.write(b"A")
        self.connected = True


    ## Automatically runs when data is recieved from the server
    # decodes the data and forwards it. Prints it if invalid
    def dataReceived(self, data):
        decoded_data = data.decode() # decode the data from utf-8
        if decoded_data[1:].isnumeric():
            self.actor.DecodeInput(decoded_data[1:]) #remove the leading "A" and send the value to the decode input for signal generation
        else:
            print(decoded_data)


    ## Sends the button to the server
    # Checks if there's a connection to prevent crashes
    def sendButton(self, button):
        if self.connected: #makes sure connected
            self.transport.write(button.encode("utf-8"))
        else:
            print("ERROR: No connection to server established")

    ## Sends a level up tag to the server
    # This doesn't actually send just an "L", it attaches it to a button press. So the signal won't be "L", it'll be "A12L", which can
    # be read by the Observer to level up.
    def sendLevelUp(self):
        message = "L"
        self.transport.write(message.encode("utf-8"))


## Main 
# ALL VARIABLES TO CHANGE ARE LOCATED HERE
def main():

    ip = "localhost" #if the cloud service is running on the same machine, this is the ip that will allow it to connect
    #ip = "99.28.129.156"  # The ip address of the computer hosting the cloud service
    maxLevels = 3 # The total number of levels to be played. Cannot exceed 8.

    # Create the actor and run it
    actor = Actor(ip, 5)
    actor.Run()


main()