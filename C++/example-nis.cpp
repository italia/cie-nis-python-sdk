#include <vector>
#include <fstream>
#include <iostream>
#include <string>
#include <cstring>
#include <thread>
#include <winscard.h>

#include "requests.h"

#define _TCHAR char

int main(int argc, _TCHAR* argv[])
{
	for (int x = 0; x < 6; ++x) {
		// stibilisco la connessione al sottosistema di gestione delle smart card
		SCARDCONTEXT Context;
		SCardEstablishContext(SCARD_SCOPE_SYSTEM, NULL, NULL, &Context);

		// ottiengo la lista dei lettori installati
		char *ReaderList;
		DWORD ReaderListLen = SCARD_AUTOALLOCATE;
		SCardListReaders(Context, NULL, (char *) &ReaderList, &ReaderListLen);
		
		// inserisco i lettori in un vettore
		char* Reader = ReaderList;
		std::vector<char*> Readers;
		while (Reader[0]) {
			Readers.push_back(Reader);
			Reader += strlen(Reader) + 1;
		}

		// richiedo all'utente quale lettore utilizzare
		for (int i = 0; i < Readers.size(); i++) {
			std::cout << (i + 1) << ") " << Readers[i] << "\n";
		}
		std::cout << "Selezionare il lettore su cui è appoggiata la CIE\n";

		int ReaderNum = -1;
		std::cin >> ReaderNum;
		if (ReaderNum < 1 || ReaderNum>Readers.size()) {
			std::cout << "Lettore inesistente\n";
			return 0;
		}
		// apre la connessione al lettore selezionato, specificando l'accesso esclusivo e il protocollo T=1
		SCARDHANDLE Card;
		DWORD Protocol;
		LONG result = SCardConnect(Context, Readers[ReaderNum - 1], SCARD_SHARE_EXCLUSIVE, SCARD_PROTOCOL_T1, &Card, &Protocol);

		if (result != SCARD_S_SUCCESS) {
			std::cout << "Connessione al lettore fallita\n";
			return 0;
		}
		std::vector<BYTE> response(Requests::RESPONSE_SIZE);
		DWORD response_len {Requests::RESPONSE_SIZE};
		// prepara la prima APDU: Seleziona il DF dell'applicazione IAS
		std::vector<BYTE> selectIAS {0x00, // CLA
			0xa4, // INS = SELECT FILE
			0x04, // P1 = Select By AID
			0x0c, // P2 = Return No Data
			0x0d, // LC = length of AID
			0xA0, 0x00, 0x00, 0x00, 0x30, 0x80, 0x00, 0x00,
			0x00, 0x09, 0x81, 0x60, 0x01 // AID
		};
		// invia la prima APDU
		if (!Requests::send_apdu(Card, selectIAS, response)) {
			std::cerr << "Errore nella selezione del DF_IAS\n";
			return EXIT_FAILURE;
		} 
		// prepara la seconda APDU: Seleziona il DF degli oggetti CIE
		std::vector<BYTE> selectCIE {0x00, // CLA
			0xa4, // INS = SELECT FILE
			0x04, // P1 = Select By AID
			0x0c, // P2 = Return No Data
			0x06, // LC = length of AID
			0xA0, 0x00, 0x00, 0x00, 0x00, 0x39 // AID
		};
		// invia la seconda APDU
		if (!Requests::send_apdu(Card, selectCIE, response)) {
			std::cerr << "Errore nella selezione del DF_CIE\n";
			return EXIT_FAILURE;
		} 
		// prepara la terza APDU: Lettura del file dell'ID_Servizi selezionato contestualmente tramite Short Identifier (SFI = 1)
		if (!Requests::read_nis(Card, response)) {
			std::cerr << "Errore nella lettura dell'Id_Servizi\n";
			return EXIT_FAILURE;
		} 
		std::ofstream out_file {"certificate.txt"};
		out_file << response.data() << "\n";
		std::cout << "Certificato scritto su file" << '\n';
		std::cout << "NIS: " << std::string {(char *)response.data()} << std::endl;
		SCardFreeMemory(Context, ReaderList);
		SCardDisconnect(Card, SCARD_RESET_CARD);
		free(ReaderList);
		std::this_thread::sleep_for(std::chrono::milliseconds {5000});
	}
	return 0;
}
