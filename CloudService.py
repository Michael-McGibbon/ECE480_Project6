"""
CloudService.py

Cloud service application which will act as a bridge between the Observer and Actor. May be unnessecary, but unsure.

Author: Jeremy Cowelchuk, (add names here)
"""

#imports
from twisted.internet import protocol, reactor, endpoints

class Echo(protocol.Protocol):
    def dataReceived(self, data):
        self.transport.write(data)

class EchoFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Echo()

endpoints.serverFromString(reactor, "tcp:1234").listen(EchoFactory())
reactor.run()