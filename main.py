#!/usr/bin/env python
# coding=utf-8
import random

from pkg.lib.CIEInterface import CIEInterface

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
    interface.mrtdAuth('YYMMDD', 'YYMMDD', '*********')
    data = interface.extractData()

    print ('Nome e cognome: {}\n' \
          'Codice fiscale: {}\n' \
          'Residenza: {}\n' \
          'Luogo di nascita: {}\n' \
          'Data di nascita: {}\n\n' \
          'MRZ: {}' \
        .format(data['additional_details']['full_name'].replace('<<', ' '),
                hide_sensitive_data(data['additional_details']['vat_code']),
                hide_sensitive_data(data['additional_details']['address'].replace('<', ' ')),
                data['additional_details']['birth_place'].replace('<', ' '),
                data['additional_details']['birth_date'],

                hide_sensitive_data(data['mrz'])))

    print('Immagine salvata in: img.jpeg')


if __name__ == "__main__":
    main()
