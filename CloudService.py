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
        self.factory.connections.append(self)
        print("Connection Established: {} Total".format(len(self.factory.connections)))
        self.transport.write(b"Connection Established to Server")

    def dataReceived(self, data):
        decoded_data = data.decode()
        # if it's from the actor, send it to the observer
        if decoded_data[0] == "A":
            self.factory.connections[0].transport.write(data)
        # if it's from the observer, send it to the actor
        elif decoded_data[0] == "O":
            self.factory.connections[1].transport.write(data)

    def connectionLost(self, reason):
        self.factory.connections.remove(self)
        print("Connection Lost: {} Total".format(len(self.factory.connections)))



class TactileFeedbackFactory(Factory):

    # This will be used by the default buildProtocol to create new protocols:
    protocol = TactileFeedback

    def __init__(self):
        self.connections = []

    def buildProtocol(self, addr):
        return TactileFeedback(self)



endpoint = TCP4ServerEndpoint(reactor, 25565)
endpoint.listen(TactileFeedbackFactory())
print("server")
reactor.run()