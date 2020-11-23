"""
CloudService.py

Cloud service application which will act as a bridge between the Observer and Actor. May be unnessecary, but unsure.

Author: Jeremy Cowelchuk, (add names here)
"""

#import requests
#from requests import get

#ip = get('https://api.ipify.org').text
#print('IP Address for Server: {}'.format(ip)) 

from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

class TactileFeedback(Protocol):

    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.transport.write(b"Connection Established to Server")

    def dataReceived(self, data):
        decoded_data = data.decode()
        # if still setting up actor and observer
        if self.factory.actor == None:
            if decoded_data == "A":
                print("Connection Established: Actor")
                self.factory.actor = self
        if self.factory.observer == None:
            if decoded_data == "O":
                print("Connection Established: Observer")
                self.factory.observer = self

        # messages recieved are valid and able to be sent
        else:
            # if it's from the actor, send it to the observer
            if decoded_data[0] == "A":
                self.factory.observer.transport.write(data)
            # if it's from the observer, send it to the actor
            elif decoded_data[0] == "O":
                self.factory.actor.transport.write(data)

    def connectionLost(self, reason):
        if self.factory.actor == self:
            print("Connection Lost: Actor")
            self.factory.actor = None
        elif self.factory.observer == self:
            print("Connection Lost: Observer")
            self.factory.observer = None


class TactileFeedbackFactory(Factory):

    # This will be used by the default buildProtocol to create new protocols:
    protocol = TactileFeedback

    def __init__(self):
        self.actor = None
        self.observer = None

    def buildProtocol(self, addr):
        return TactileFeedback(self)



endpoint = TCP4ServerEndpoint(reactor, 25565)
endpoint.listen(TactileFeedbackFactory())
print("server")
reactor.run()