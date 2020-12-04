"""
Actor.py
Python application for recieving button input from another controller, reading them as vibrations and then sending an interpreted
signal back to the source controller.
Author: Jeremy Cowelchuk, (add your names here)

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


    ## Displays all game related images
    # all display functions, with some notable exceptions, should go in here.
    # this is useful for game design
    def Display(self):

        #display the background
        self.screen.fill((112, 128, 144))
        self.screen.blit(self.background,(0, 0))

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

    #ip = "localhost" #if the cloud service is running on the same machine, this is the ip that will allow it to connect
    ip = "99.28.129.156"  # The ip address of the computer hosting the cloud service
    maxLevels = 3 # The total number of levels to be played. Cannot exceed 8.

    # Create the actor and run it
    actor = Actor(ip, 5)
    actor.Run()


main()