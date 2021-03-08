# Python CIE3 SDK   [![Build Status](https://travis-ci.org/italia/cie-nis-python-sdk.svg?branch=master)](https://travis-ci.org/italia/cie-nis-python-sdk) [![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)

Libreria leggera e portabile in Python per l'estrazione delle informazioni contenute nella CIE 3.0, con e senza autenticazione EAC.


## Installazione

Per iniziare installa tutte le dipendenze tramite il gestore di pacchetti `pip`, con il comando:

```
pip install -r requirements.txt
```

## Esempio

Il file `main.py` contiene un brevissimo esempio che mostra l'estrazione dei dati dalla CIE tramite autenticazione EAC.

## Struttura

L'intera libreria è strutturata attorno alla classe `CIEInterface` che espone molti metodi utili per inviare comandi alla CIE.

Al momento della creazione di un'istanza di `CIEInterface`, il costruttore tenterà di aprire una connessione con un lettore NFC compatibile e si metterà in attesa di rilevare una carta. Il massimo tempo di attesa è attualmente di 3 secondi.

Una volta rilevata la carta il costruttore termina l'esecuzione.

I metodi a disposizione dell'utilizzatore sono i seguenti:

* `CIEInterface.readNIS()`: Legge la sezione `EF.ID_Servizi` della carta, ovvero l'id univoco della carta.
* `CIEInterface.randomNumber()`: Invia un APDU alla carta chiedendo al microprocessore di generare un numero casuale.
* `CIEInterface.mrtdAuth(birthStr, expireStr, pnStr)`: esegue l'autenticazione tramite i dati contenuti nell'MRZ, per poter accedere alle informazioni aggiuntive presenti sulla carta. I parametri sono stringhe, nel caso delle date in formato `YYMMDD`, mentre `pnStr` è semplicemente il numero della CIE.
* `CIEInterface.extractData()`: estrae i dati aggiuntivi disponibili dopo l'unlock della carta. A secodna delle informazioni disponibili vengono estratti:
	* `mrz`: Stringa identica all'`MRZ` stampato sulla carta
	* `additional_details`: Informazioni aggiuntive sul cittadino, come ad esempio l'indirizzo di residenza
	* `photo`: `bytearray` contenete l'immagine in formato JPEG2000. Per comodità l'immagine viene anche salvata su disco nel file `img.jpeg`.

## Supporto

La libreria è stata testata con successo su Python `2.7.14` su sistema `macOS 10.15.3`, ma vista la semplicità è molto probabile che funzioni nativamente anche su altre versioni.
