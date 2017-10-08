import pyDes


def macEnc(key, data):
    """
    Calculates the MAC for `data` using `key`
    :param key: The key used to calculate the MAC
    :param data: The data to process
    :return: The calculated MAC
    """

    k1 = key[0:8]

    k2Start = 8 if len(key) >= 16 else 0
    k2 = key[k2Start:k2Start + 8]

    k3Start = 16 if len(key) >= 24 else 0
    k3 = key[k3Start:k3Start + 8]

    mid1 = desEnc(k1, data)
    mid2 = desDec(k2, mid1[-8:])
    mid3 = desEnc(k3, mid2[:8])

    return mid3


def desEnc(masterKey, data):
    """
    Encrypts `data` using `masterKey` as key and TripleDES with CBC and no padding as algorithm
    :param masterKey: The master encryption key
    :param data: The data to encrypt
    :return: The encrypted data as an array of integers
    """

    key24 = None

    if len(masterKey) == 8:
        key24 = masterKey[0:8] * 3
    elif len(masterKey) == 16:
        key24 = masterKey[0:16] + masterKey[0:8]
    else:
        key24 = masterKey[0:24]

    key24 = ''.join([chr(x) for x in key24])
    data = ''.join([chr(x) for x in data])

    tripleDes = pyDes.triple_des(key24, pyDes.CBC, "\0\0\0\0\0\0\0\0", '', pyDes.PAD_NORMAL)
    return [ord(i) for i in tripleDes.encrypt(data)]


def desDec(masterKey, data):
    """
        Decrypts `data` using `masterKey` as key and TripleDES with CBC and no padding as algorithm
        :param masterKey: The master decryption key
        :param data: The data to decrypt
        :return: The decrypted data as an array of integers
        """

    key24 = None

    if len(masterKey) == 8:
        key24 = masterKey[0:8] * 3
    elif len(masterKey) == 16:
        key24 = masterKey[0:16] + masterKey[0:8]
    else:
        key24 = masterKey[0:24]

    key24 = ''.join([chr(x) for x in key24])
    data = ''.join([chr(x) for x in data])

    tripleDes = pyDes.triple_des(key24, pyDes.CBC, "\0\0\0\0\0\0\0\0", '', pyDes.PAD_NORMAL)
    return [ord(i) for i in tripleDes.decrypt(data)]
