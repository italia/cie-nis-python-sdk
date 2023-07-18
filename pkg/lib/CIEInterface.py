import progressbar
import six
import sys

from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.util import toHexString
from smartcard.Exceptions import CardRequestTimeoutException

from .Utilities import *
from .Algorithms import *
from .asn1lib import *

if six.PY3:
    xrange = range

__author__ = "Alekos Filini, Daniela Brozzoni"
__license__ = "BSD-3-Clause"
__version__ = "1.0"
__status__ = "Develop"


class CIEInterface:
    """
    The Python interface to read data from a CIE3

    This class uses pyscard as a low-level interface to the NFC card,
    make sure your reader is compatible with this library.
    """

    def __init__(self):
        """
        Generic constructor
        """

        cardtype = AnyCardType()
        cardrequest = CardRequest(timeout=30, cardType=cardtype)

        self.seq = None
        self.kSessEnc = None
        self.kSessMac = None

        self.index = 0

        # Wait for the card
        print('Waiting for the CIE...')
        try:
            self.cardservice = cardrequest.waitforcard()
        except CardRequestTimeoutException:
            print('Card not found, exiting')
            sys.exit(1)

        # Connect to the card if found
        self.cardservice.connection.connect()
        print('Connected!')

    def selectIAS(self):
        """
        Sends an APDU to select the IAS section of the CIE
        :return: The response send by the CIE
        """

        apdu = [0x00,  # CLA
                0xa4,  # INS = SELECT FILE
                0x04,  # P1 = Select By AID
                0x0c,  # P2 = Return No Data
                0x0d,  # LC = lenght of AID
                0xA0, 0x00, 0x00, 0x00, 0x30, 0x80, 0x00, 0x00, 0x00, 0x09, 0x81, 0x60, 0x01  # AID
                ]
        return self.transmit(apdu)

    def selectCIE(self):
        """
        Sends an APDU to select the CIE section of the card
        :return: The response send by the card
        """

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
        """
        Increment the message sequence values
        :param index: Byte to increment
        """

        if index is None:
            return self.seqIncrement(len(self.seq) - 1)

        if self.seq[index] == 0xFF:
            self.seq[index] = 0
            self.seqIncrement(index - 1)
        else:
            self.seq[index] += 1

    def readNIS(self):
        """
        Reads the NIS value from the card and returns it
        :return: The NIS value in form of array of integers
        """

        self.selectIAS()
        self.selectCIE()

        response, _ = self.transmit(string_to_byte("00B081000C"))
        return nfc_response_to_array(response)

    def initialSelect(self):
        """
        Sends an "initial selection" APDU to the card preparing it for the EAC authentication
        :return: The response sent by the CIE
        """

        apdu = string_to_byte("00A4040C07A0000002471001")
        return self.transmit(apdu)

    def randomNumber(self):
        """
        Sends an APDU to the CIE requesting a random number
        :return: The random number in form of integer array
        """

        apdu = string_to_byte("0084000008")
        response, _ = self.transmit(apdu)
        return nfc_response_to_array(response)

    def mrtdAuth(self, birthStr, expireStr, pnStr):
        """
        Unlocks the card using the data contained in the MRZ
        :param birthStr: Card owner's birth date in 'YYMMDD' format
        :param expireStr: Card expiration date in 'YYMMDD' format
        :param pnStr: Card number
        """

        self.initialSelect()
        rndMrtd = self.randomNumber()

        # Split the strings into array of chars
        birth = string_to_chars_values(birthStr)
        expire = string_to_chars_values(expireStr)
        pn = string_to_chars_values(pnStr)

        # Add the checksum at the end
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

        # Calculates the APDU for the mutual authentication
        apduMutuaAutenticazione = [0x00, 0x82, 0x00, 0x00, 0x28] + eIs1 + eisMac + [0x28]

        # Sends the APDU
        respMutaAuth, sw = self.transmit(apduMutuaAutenticazione)
        respMutaAuth = nfc_response_to_array(respMutaAuth)

        if sw != '9000':
            raise Exception('CIEInterface.mrtdAuth: could not complete the authentication process')

        kIsMac = macEnc(bacMac, getIsoPad(respMutaAuth[:32]))
        kIsMac2 = respMutaAuth[-8:]

        # Make sure the calculated and received MAC are the same
        if kIsMac != kIsMac2:
            raise Exception('CIEInterface.mrtdAuth: could not complete the authentication process')

        decResp = desDec(bacEnc, respMutaAuth[:32])
        kMrtd = decResp[-16:]
        kSeed = stringXor(kIs, kMrtd)

        # Sets the session encryption key and session MAC
        self.kSessMac = get_sha1(kSeed + [0x00, 0x00, 0x00, 0x02])[:16]
        self.kSessEnc = get_sha1(kSeed + [0x00, 0x00, 0x00, 0x01])[:16]

        # Initialize the sequence vector
        self.seq = decResp[4:8] + decResp[12:16]

    def secureMessage(self, keyEnc, keyMac, apdu):
        """
        Sends a secure message containing `apdu` to the CIE using the provided encryption keys
        :param keyEnc: The session encryption key
        :param keyMac: The session MAC
        :param apdu: The APDU to send
        :return: The response coming from the CIE
        """

        self.seqIncrement()
        calcMac = getIsoPad(self.seq + apdu[:4])
        smMac = None
        dataField = None
        doob = None

        if apdu[4] != 0 and len(apdu) > 5:
            enc = desEnc(keyEnc, getIsoPad(apdu[5:5 + apdu[4]]))
            if apdu[1] % 2 == 0:
                doob = asn1Tag([0x01] + enc, 0x87)
            else:
                doob = asn1Tag(enc, 0x85)

            calcMac = calcMac + doob
            dataField = (dataField if dataField is not None else []) + doob

        if len(apdu) == 5 or len(apdu) == apdu[4] + 6:
            doob = [0x97, 0x01, apdu[-1]]
            calcMac = calcMac + doob

            if dataField is None:
                dataField = doob[:]
            else:
                dataField = dataField + doob

        smMac = macEnc(keyMac, getIsoPad(calcMac))
        dataField = dataField + [0x8e, 0x08] + smMac
        finale = apdu[:4] + [len(dataField)] + dataField + [0x00]

        return finale

    def setIndex(self, *args):
        """
        Sets the "pointer" to the response buffer
        :param args: multiple values to add to the current index
        """

        tmpIndex = 0
        for i in range(0, len(args)):
            if args[i] < 0:
                tmpIndex += args[i] & 0xFF
            else:
                tmpIndex += args[i]

        self.index = tmpIndex

    def respSecureMessage(self, keyEnc, keySig, resp, odd=False):
        """
        Parses and decrypts the encrypted response coming from the CIE
        :param keyEnc: The session encryption key
        :param keySig: The key signature
        :param resp: The buffer containing the response as array of bytes
        :param odd:
        :return: The decrypted message
        """

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
                    raise Exception('CIEInterface.respSecureMessage: invalid dataObject length')

                dataObj = resp[self.index:self.index + 4]
                self.setIndex(self.index, 4)
                continue

            if resp[self.index] == 0x8e:
                calcMac = macEnc(keySig, getIsoPad(self.seq + encObj + dataObj))
                self.setIndex(self.index + 1)

                if resp[self.index] != 0x08:
                    raise Exception('CIEInterface.respSecureMessage: MAC length must be 0x08')

                self.setIndex(self.index, 1)
                if calcMac != resp[self.index:self.index + 8]:
                    raise Exception('CIEInterface.respSecureMessage: the calculated MAC does not match the returned one')

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

            raise Exception('CIEInterface.respSecureMessage: unknown ASN.1 tag encountered during the response parsing')

        if encData is not None and not odd:
            return isoRemove(desDec(keyEnc, encData))

        return None

    def parseLength(self, data):
        """
        Extracts the length from a BER-encoded buffer of data
        :param data: the data to process
        :return: the size of the data
        """

        dataLen = len(data)

        if dataLen == 0:
            raise Exception('parseLength: empty buffer')

        tag = data[0]
        readPos = 2

        byteLen = data[1]
        if byteLen > 128:
            lenlen = byteLen - 128
            byteLen = 0
            for i in range(lenlen):
                if readPos == dataLen:
                    raise Exception()

                byteLen = (byteLen << 8) | data[readPos]
                readPos += 1

        return readPos + byteLen

    def readDg(self, numDg, progressBar=False):
        """
        Reads the data group identified by `numDg`
        :param numDg: the data group number to read
        :return: the raw data group buffer
        """

        somma = (numDg + 0x80)
        data = []

        appo = [0x0C, 0xB0, somma, 0x00, 0x06]
        apdu = self.secureMessage(self.kSessEnc, self.kSessMac, appo)

        resp, sw = self.transmit(apdu)
        resp = nfc_response_to_array(resp)

        chunkLen = self.respSecureMessage(self.kSessEnc, self.kSessMac, resp)
        maxLen = self.parseLength(chunkLen)

        bar = None
        if progressBar:
            bar = progressbar.ProgressBar(max_value=maxLen)

        dataLen = len(data)
        while dataLen < maxLen:
            readLen = min(0xe0, maxLen - len(data))
            appo2 = [0x0C, 0xB0] + [(len(data) // 256) & 0x7F, len(data) & 0xFF, readLen]
            apduDg = self.secureMessage(self.kSessEnc, self.kSessMac, appo2)
            respDg2, sw = self.transmit(apduDg)

            chunk = self.respSecureMessage(self.kSessEnc, self.kSessMac, nfc_response_to_array(respDg2))

            data += chunk
            dataLen += len(chunk)

            if progressBar:
                bar.update(dataLen)

        return data

    def extractData(self):
        """
        Extracts the personal data from a CIE after the EAC authentication
        :return: The parsed data
        """

        mainDGData = self.readDg(30)
        mainDG = ASN1(mainDGData)

        verifyChild0 = mainDG.root['children'][0]['verify']([0x30, 0x31, 0x30, 0x37])
        verifyChild1 = mainDG.root['children'][1]['verify']([0x30, 0x34, 0x30, 0x30, 0x30, 0x30])

        if not verifyChild0 or not verifyChild1:
            raise Exception('extractData: Invalid DG 30')

        lambdas = {
            0x61: lambda: self.extractMRZ(),
            0x75: lambda: self.extractPhoto(),
            0x6b: lambda: self.extractAdditionalDetails()
        }

        mapNames = {
            0x61: 'mrz',
            0x75: 'photo',
            0x6b: 'additional_details'
        }

        results = {}

        for byte in mainDG.root['children'][2]['bytes']:
            if byte in lambdas:
                results[mapNames[byte]] = lambdas[byte]()

        return results

    def extractMRZ(self):
        """
        Extracts and parses the MRZ data group
        :return: the parsed data group as a string
        """

        data = self.readDg(1)
        parser = ASN1(data)

        mrzStr = ''.join([chr(x) for x in parser.root['children'][0]['bytes']])
        return mrzStr

    def extractAdditionalDetails(self):
        """
        Extracts and parses the additional details stored on the CIE
        :return: a dictionary containing all the additional informations
        """

        data = self.readDg(11)
        parser = ASN1(data)

        ans = {
            'card_id': ''.join(['%02x' % x for x in parser.root['children'][0]['bytes']]),
            'full_name': ''.join([chr(x) for x in parser.root['children'][1]['bytes']]),
            'vat_code': ''.join([chr(x) for x in parser.root['children'][2]['bytes']]),
            'birth_date': ''.join([chr(x) for x in parser.root['children'][3]['bytes']]),
            'birth_place': ''.join([chr(x) for x in parser.root['children'][4]['bytes']]),
            'address': ''.join([chr(x) for x in parser.root['children'][5]['bytes']]),
        }

        return ans

    def extractPhoto(self):
        """
        Extracts and saves the photo stored on the CIE
        :return: The raw JPEG2000 bytes of the photo
        """

        data = self.readDg(2, progressBar=True)
        parser = ASN1(data)

        JPEG_MAGIC = [0x00, 0x00, 0x00, 0x0C, 0x6A, 0x50, 0x20, 0x20, 0x0D, 0x0A, 0x87, 0x0A, 0x00, 0x00, 0x00, 0x14,
                      0x66, 0x74, 0x79, 0x70, 0x6A, 0x70, 0x32]

        photoBytes = parser.root['children'][0]['children'][1]['children'][1]['bytes']
        jpegStart = [x for x in xrange(len(photoBytes)) if photoBytes[x:x + len(JPEG_MAGIC)] == JPEG_MAGIC][0]

        jpegImg = bytearray(photoBytes[jpegStart:])

        with open("img.jpeg", "wb") as file:
            file.write(jpegImg)
            file.close()

        return jpegImg

    def transmit(self, apdu):
        """
        Sends an APDU to the CIE
        :param apdu: bytes to send
        :return: the response and status words
        """

        response, sw1, sw2 = self.cardservice.connection.transmit(apdu)
        status = '%02x%02x' % (sw1, sw2)

        return toHexString(response), status
