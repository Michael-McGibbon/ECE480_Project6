"""
CloudService.py

Cloud service application which will act as a bridge between the Observer and Actor.

Authors: Jeremy Cowelchuk, David Geisler, George Legacy, Michael McGibbon, and Pavan Patel
"""


#ip = get('https://api.ipify.org').text
#print('IP Address for Server: {}'.format(ip)) 

##############
# IMPORTS
##############
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor


## Tacticle Feedback Class
# This class is the protocol class that functions as cloud service.
# It is the host server that allows Observer.py and Actor.py to connect to one another
class TactileFeedback(Protocol):

    ## Initalize the server
    # Sets up the factory object to connect to the instance of the service.
    def __init__(self, factory):
        # The factory contains more variables, but they are specific to the factory
        self.factory = factory


    ## Runs when a connection is made to the server
    # simply sends a message back to the connected application to let it know its connected
    def connectionMade(self):
        #sends a message. The "self" here refers to whatever connected to the server
        self.transport.write(b"Connection Established to Server")


    ## Runs when data is sent to the server
    # The server acts as a "middle man" between the Actor and the Observer. This function
    # catches all transmissions sent between the two and routes it to where it needs to go.
    # Additionally, this section sets up which applications are the Actor and Observer.
    def dataReceived(self, data):
        decoded_data = data.decode() #check what the data is in a readable format
        # if still setting up actor and observer, we need to make sure that they're correctly added
        if self.factory.actor == None:
            # When the Actor first connects, it sends an "A" to be caught here and mark it as the actor
            if decoded_data == "A":
                print("Connection Established: Actor") #print a message confirming it's been successfully connected
                self.factory.actor = self
        if self.factory.observer == None:
            # When the Observer first connects, it sends an "O" to be caught here and mark it as the observer   
            if decoded_data == "O":
                print("Connection Established: Observer") #print a message confirming it's been successfully connected
                self.factory.observer = self

        # messages recieved are valid and able to be sent
        else:
            # if it's from the actor, send it to the observer
            if decoded_data[0] == "A":
                self.factory.observer.transport.write(data)
            # if it's from the observer, send it to the actor
            elif decoded_data[0] == "O":
                self.factory.actor.transport.write(data)


    ## Runs whenever a connection is lost for whatever reason
    # When a connection is lost, we need to confirm which it is and remove it from its specific
    # role to prevent issues.
    def connectionLost(self, reason):
        if self.factory.actor == self:
            print("Connection Lost: Actor")
            self.factory.actor = None
        elif self.factory.observer == self:
            print("Connection Lost: Observer")
            self.factory.observer = None

## Tacticle Feedback Factory Class
# Creates instances of the Tacticle Feedback class. Contains the "Actor" and "Observer" variables for marking
# This may seem redundant, but Twisted requires a factory with the "buildProtocol" function. This allows 
# server protocols to be created and run effectively.
class TactileFeedbackFactory(Factory):

    # This will be used by the default buildProtocol to create new protocols:
    protocol = TactileFeedback

    ## Initalize the factory
    # Sets up the actor and observer connections to None
    def __init__(self):
        self.actor = None
        self.observer = None

    ## Builds the protocol
    # This will not function without this in the factory.
    def buildProtocol(self, addr):
        # This is neccessary in order to even host a server
        return TactileFeedback(self)


#########
# PORT
#########
# this can be changed if desired, defaults to 25565 due to pre-existing port forwarding on personal machine -Jeremy
port = 25565


# set up the end up on this and have it listen
endpoint = TCP4ServerEndpoint(reactor, port)
endpoint.listen(TactileFeedbackFactory())
print("server")
reactor.run()