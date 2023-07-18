#!/usr/bin/env python
# coding=utf-8
import random

from pkg.lib.CIEInterface import CIEInterface
import cv2

__author__ = "Alekos Filini, Daniela Brozzoni"
__license__ = "BSD-3-Clause"
__version__ = "1.0"
__status__ = "Develop"

def hide_sensitive_data(string, chance=0.50):
    return ''.join([s if random.random() > chance else '*' for s in list(string)])


def main():
    print ('\n                ██████╗██╗███████╗██████╗ \n' \
          '               ██╔════╝██║██╔════╝╚════██╗\n' \
          '               ██║     ██║█████╗   █████╔╝\n' \
          '               ██║     ██║██╔══╝   ╚═══██╗\n' \
          '               ╚██████╗██║███████╗██████╔╝\n' \
          '                ╚═════╝╚═╝╚══════╝╚═════╝ \n')

    interface = CIEInterface()
    nis = interface.readNIS()
    print(nis)
    interface.mrtdAuth('YYMMDD', 'YYMMDD', '*********')
    data = interface.extractAdditionalDetails()
    mrz = interface.extractMRZ()
    interface.extractPhoto()
    image = cv2.imread('img.jpeg')
    cv2.imwrite('img.png', image)

    print ('\nNome e cognome: {}\n' \
          'Codice fiscale: {}\n' \
          'Residenza: {}\n' \
          'Luogo di nascita: {}\n' \
          'Data di nascita: {}\n\n' \
          'MRZ: {}' \
        .format(data['full_name'].replace('<<', ' '),
                hide_sensitive_data(data['vat_code']),
                hide_sensitive_data(data['address'].replace('<', ' ')),
                data['birth_place'].replace('<', ' '),
                data['birth_date'],

                hide_sensitive_data(mrz)))

    print('Immagine salvata in: img.png')


if __name__ == "__main__":
    main()
