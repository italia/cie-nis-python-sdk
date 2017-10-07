import sys

from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.util import toHexString
from smartcard.Exceptions import CardRequestTimeoutException

from Utilities import *
from Algorithms import *


class CIEInterface:
    def __init__(self):
        cardtype = AnyCardType()
        cardrequest = CardRequest(timeout=3, cardType=cardtype)

        self.seq = None
        self.kSessEnc = None
        self.kSessMac = None

        print('Waiting for the CIE...')
        try:
            self.cardservice = cardrequest.waitforcard()
        except CardRequestTimeoutException:
            print('Card not found, exiting')
            sys.exit(1)

        self.cardservice.connection.connect()

    def selectIAS(self):
        apdu = [0x00,  # CLA
                0xa4,  # INS = SELECT FILE
                0x04,  # P1 = Select By AID
                0x0c,  # P2 = Return No Data
                0x0d,  # LC = lenght of AID
                0xA0, 0x00, 0x00, 0x00, 0x30, 0x80, 0x00, 0x00, 0x00, 0x09, 0x81, 0x60, 0x01  # AID
                ]
        return self.transmit(apdu)

    def selectCIE(self):
        apdu = [
            0x00,  # CLA
            0xa4,  # INS = SELECT FILE
            0x04,  # P1 = Select By AID
            0x0c,  # P2 = Return No Data
            0x06,  # LC = lenght of AID
            0xA0, 0x00, 0x00, 0x00, 0x00, 0x39  # AID
        ]
        return self.transmit(apdu)

    def readNIS(self):
        self.selectIAS()
        self.selectCIE()

        response, _ = self.transmit(string_to_byte("00B081000C"))
        return response

    def readSOD(self):
        self.selectIAS()
        self.selectCIE()

        response, sw = self.transmit(string_to_byte("00B086000A"))
        return response

    def initialSelect(self):
        apdu = string_to_byte("00A4040C07A0000002471001")
        return self.transmit(apdu)

    def randomNumber(self):
        apdu = string_to_byte("0084000008")
        response, _ = self.transmit(apdu)
        return response

    def mrtdAuth(self, birthStr, expireStr, pnStr):
        self.initialSelect()
        rndMrtd = nfc_response_to_array(self.randomNumber())

        birth = string_to_chars_values(birthStr)
        expire = string_to_chars_values(expireStr)
        pn = string_to_chars_values(pnStr)

        seedPartPn = pn + [checkdigit(pn)]
        seedPartBirth = birth + [checkdigit(birth)]
        seedPartExpire = expire + [checkdigit(expire)]

        seedPartData = seedPartPn + seedPartBirth + seedPartExpire

        bacEnc = get_sha1((get_sha1(seedPartData)[:16]) + [0x00, 0x00, 0x00, 0x01])[:16]
        bacMac = get_sha1((get_sha1(seedPartData)[:16]) + [0x00, 0x00, 0x00, 0x02])[:16]

        rndIs1 = getRandomBytes(8)
        kIs = getRandomBytes(16)

        eIs1 = desEnc(bacEnc, rndIs1 + rndMrtd + kIs)
        eisMac = macEnc(bacMac, getIsoPad(eIs1))

        apduMutuaAutenticazione = [0x00, 0x82, 0x00, 0x00, 0x28] + eIs1 + eisMac + [0x28]

        respMutaAuth, sw = self.transmit(apduMutuaAutenticazione)
        respMutaAuth = nfc_response_to_array(respMutaAuth)

        if sw != '9000':
            raise Exception('Errore durante l\'autenticazione')

        kIsMac = macEnc(bacMac, getIsoPad(respMutaAuth[:32]))
        kIsMac2 = respMutaAuth[-8:]

        if kIsMac != kIsMac2:
            raise Exception('Errore durante l\'autenticazione')

        decResp = desDec(bacEnc, respMutaAuth[:32])
        kMrtd = decResp[-16:]
        kSeed = stringXor(kIs, kMrtd)

        self.kSessMac = get_sha1(kSeed + [0x00, 0x00, 0x00, 0x02])[:16]
        self.kSessEnc = get_sha1(kSeed + [0x00, 0x00, 0x00, 0x01])[:16]

        self.seq = decResp[4:8] + decResp[12:16]

    def transmit(self, apdu):
        response, sw1, sw2 = self.cardservice.connection.transmit(apdu)
        status = '%02x%02x' % (sw1, sw2)

        return toHexString(response), status

def main():
    interface = CIEInterface()
    interface.mrtdAuth('YYMMDD', 'YYMMDD', '*********')
    print(interface.kSessMac, interface.kSessEnc, interface.seq)

if __name__ == "__main__":
    main()
