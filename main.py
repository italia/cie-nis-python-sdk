import sys

from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.util import toHexString
from smartcard.Exceptions import CardRequestTimeoutException

from Utilities import *

class CIEInterface:
    def __init__(self):
        cardtype = AnyCardType()
        cardrequest = CardRequest(timeout=3, cardType=cardtype)

        print('Waiting for the CIE...')
        try:
            self.cardservice = cardrequest.waitforcard()
        except CardRequestTimeoutException:
            print('Card not found, exiting')
            sys.exit(1)

        self.cardservice.connection.connect()

    def initialSelect(self):
        apdu = string_to_byte("00A4040C07A0000002471001")
        print(self.transmit(apdu))

    def transmit(self, apdu):
        response, sw1, sw2 = self.cardservice.connection.transmit(apdu)
        status = '%02x%02x' % (sw1, sw2)

        return toHexString(response), status

def main():
    interface = CIEInterface()

if __name__ == "__main__":
    main()