"""
CloudService.py

Cloud service application which will act as a bridge between the Observer and Actor. May be unnessecary, but unsure.

Author: Jeremy Cowelchuk, (add names here)
"""

from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

class TactileFeedback(Protocol):

    def connectionMade(self):
        #empty for now
        return

    def dataReceived(self, data):
        print(data)
        #return super().dataReceived(data)



class TactileFeedbackFactory(Factory):

    # This will be used by the default buildProtocol to create new protocols:
    protocol = TactileFeedback



endpoint = TCP4ServerEndpoint(reactor, 25565)
endpoint.listen(TactileFeedbackFactory())
print("server")
reactor.run()