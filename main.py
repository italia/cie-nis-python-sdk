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

        self.index = 0

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

    def seqIncrement(self, index=None):
        if index is None:
            return self.seqIncrement(len(self.seq) - 1)

        if self.seq[index] == 0xFF:
            self.seq[index] = 0
            self.seqIncrement(index - 1)
        else:
            self.seq[index] += 1

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

    def secureMessage(self, keyEnc, keyMac, apdu):
        self.seqIncrement()
        calcMac = getIsoPad(self.seq + apdu[:4])
        dataField = None

        if apdu[4] != 0 and len(apdu) > 5:
            enc = desEnc(keyEnc, getIsoPad(apdu[5:5 + apdu[4]]))
            if apdu[1] % 2 == 0:
                doob = asn1Tag([0x01] + enc, 0x87)
            else:
                doob = asn1Tag(enc, 0x85)

            calcMac = calcMac + doob
            dataField = dataField if dataField is not None else [] + doob

        if len(apdu) == 5 or len(apdu) == apdu[4] + 6:
            doob = [0x97, 0x01, apdu[-1]]
            calcMac = calcMac + doob

            if dataField is None:
                dataField = doob
            else:
                dataField = dataField + doob

        smMac = macEnc(keyMac, getIsoPad(calcMac))
        dataField = dataField + [0x8e, 0x08] + smMac
        finale = apdu[:4] + [len(dataField)] + dataField + [0x00]

        return finale

    def setIndex(self, *args):
        tmpIndex = 0
        for i in range(0, len(args)):
            if args[i] < 0:
                tmpIndex += args[i] & 0xFF
            else:
                tmpIndex += args[i]

        self.index = tmpIndex

    def respSecureMessage(self, keyEnc, keySig, resp, odd=False):
        self.seqIncrement()

        self.setIndex(0)
        encData = None
        encObj = None
        dataObj = None

        lenResp = len(resp)

        firstPass = True
        while firstPass or self.index < lenResp:
            firstPass = False

            if resp[self.index] == 0x99:
                if resp[self.index + 1] != 0x02:
                    raise Exception('Errore verifica SecureMessage - DataObject length')

                dataObj = resp[self.index:self.index + 4]
                self.setIndex(self.index, 4)
                continue

            if resp[self.index] == 0x8e:
                calcMac = macEnc(keySig, getIsoPad(self.seq + encObj + dataObj))
                self.setIndex(self.index + 1)

                if resp[self.index] != 0x08:
                    raise Exception('Errore verifica del SecureMessage - wrong MAC length')

                self.setIndex(self.index, 1)
                if calcMac != resp[self.index:self.index + 8]:
                    raise Exception('Errore verifica del SecureMessage - MAC mismatch')

                self.setIndex(self.index, 8)
                continue

            if resp[self.index] == 0x87:
                if unsignedToBytes(resp[self.index + 1]) > unsignedToBytes(0x80):
                    lgn = 0
                    llen = unsignedToBytes(resp[self.index + 1]) - 0x80
                    if llen == 1:
                        lgn = unsignedToBytes(resp[self.index + 2])
                    elif llen == 2:
                        lgn = (resp[self.index + 2] << 8) | resp[self.index + 3]

                    encObj = resp[self.index:self.index + llen + lgn + 2]
                    encData = resp[self.index + llen + 3:self.index + llen + 2 + lgn]
                    self.setIndex(self.index, llen, lgn, 2)
                else:
                    encObj = resp[self.index:self.index + resp[self.index + 1] + 2]
                    encData = resp[self.index + 3:self.index + 2 + resp[self.index + 1]]
                    self.setIndex(self.index, resp[self.index + 1], 2)
                continue

            if resp[self.index] == 0x85:
                if resp[self.index + 1] > 0x80:
                    lgn = 0
                    llen = resp[self.index + 1] - 0x80
                    if llen == 1:
                        lgn = resp[self.index + 2]
                    elif llen == 2:
                        lgn = (resp[self.index + 2] << 8) | resp[self.index + 3]

                    encObj = resp[self.index:self.index + llen + lgn + 2]
                    encData = resp[self.index + llen + 2, self.index + llen + 2 + lgn]
                    self.setIndex(self.index, llen, lgn, 2)
                else:
                    encObj = resp[self.index:self.index + resp[self.index + 1] + 2]
                    encData = resp[self.index + 2:self.index + 2 + resp[self.index + 1]]
                    self.setIndex(self.index, resp[self.index + 1], 2)
                continue

            raise Exception('Tag non previsto nella risposta in SecureMessage')

        if encData is not None and not odd:
            return isoRemove(desDec(keyEnc, encData))

        return None

    def readDg(self, numDg):
        somma = (numDg + 0x80)

        appo = [0x0C, 0xB0, somma, 0x00, 0x06]
        apdu = self.secureMessage(self.kSessEnc, self.kSessMac, appo)

        resp, sw = self.transmit(apdu)
        return nfc_response_to_array(resp), sw

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
