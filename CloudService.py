"""
CloudService.py

Cloud service application which will act as a bridge between the Observer and Actor. May be unnessecary, but unsure.

Author: Jeremy Cowelchuk, (add names here)
"""

from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

class QOTD(Protocol):

    def connectionMade(self):
        print("client connect")


class QOTDFactory(Factory):

    # This will be used by the default buildProtocol to create new protocols:
    protocol = QOTD



endpoint = TCP4ServerEndpoint(reactor, 8007)
endpoint.listen(QOTDFactory())
print("server")
reactor.run()