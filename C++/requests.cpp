#include <iostream>
#include <sstream>
#include <vector>
#include <winscard.h>
#include <ios>
#include "requests.h"

bool Requests::send_apdu(const SCARDHANDLE &card,
		const std::vector<BYTE> &apdu, std::vector<BYTE> &response)
{
	DWORD resp_len {RESPONSE_SIZE};
	SCardTransmit(card, SCARD_PCI_T1, apdu.data(), apdu.size(),
			NULL, response.data(), &resp_len);
	// verifica che la Status Word sia 9000 (OK)
	std::cout << "Il byte di verifica della risposta della carta e': 0x";
	std::cout << std::hex
		<< (unsigned int) (unsigned char) response[resp_len -2]
		<< std::endl;
	if (response[resp_len - 2] != 0x90 || response[resp_len - 1] != 0x00) {
		std::cerr << "Errore nella lettura della risposta\n";
		return false;
	}
	return true;
}

bool Requests::select_df_ias(const SCARDHANDLE &card, std::vector<BYTE> &response)
{
	std::vector<BYTE> selectIAS {0x00, // CLA
		0xa4, // INS = SELECT FILE
		0x04, // P1 = Select By AID
		0x0c, // P2 = Return No Data
		0x0d, // LC = length of AID
		0xA0, 0x00, 0x00, 0x00, 0x30, 0x80, 0x00, 0x00,
		0x00, 0x09, 0x81, 0x60, 0x01 // AID
	};
	// invia l'APDU
	if (!Requests::send_apdu(card, selectIAS, response)) {
		std::cerr << "Errore nella selezione del DF_IAS\n";
		return false;
	} 
	return true;
}

bool Requests::select_cie_df(const SCARDHANDLE &card, std::vector<BYTE> &response)
{
	std::vector<BYTE> selectCIE {0x00, // CLA
		0xa4, // INS = SELECT FILE
		0x04, // P1 = Select By AID
		0x0c, // P2 = Return No Data
		0x06, // LC = length of AID
		0xA0, 0x00, 0x00, 0x00, 0x00, 0x39 // AID
	};
	// invia la seconda APDU
	if (!Requests::send_apdu(card, selectCIE, response)) {
		std::cerr << "Errore nella selezione del DF_CIE\n";
		return false;
	} 
	return true;
}
bool Requests::read_nis(const SCARDHANDLE &card, std::vector<BYTE> &response)
{
	std::vector<BYTE> readNIS = {0x00, // CLA
		0xb0, // INS = READ BINARY
		0x81, // P1 = Read by SFI & SFI = 1 //to read public key
		0x00, // P2 = Offset = 0
		0x0c  // LE = length of NIS
	};
	// invia l'APDU
	if (!Requests::send_apdu(card, readNIS, response)) {
		std::cerr << "Errore nella lettura dell'Id_Servizi\n";
		return false;
	} 
	return true;
}

bool Requests::create_apdu(std::vector<BYTE> &apdu)
{
	std::string apdu_string {};
	std::cout << "Inserisci i valori dell'APDU: ";
	std::cout.flush();
	std::cin >> apdu_string;
	//std::getline(std::cin, apdu_string);
	std::istringstream sstream {apdu_string};

	for (std::string tmp {}; std::getline(sstream, tmp, '-' );)
		apdu.push_back((BYTE) std::stoi(tmp));
	std::cout << apdu_string << '\n';
	std::cout << "Invio dell'APDU personalizzata..." << '\n';
	return 1;
}

bool Requests::start_interactive_session(const SCARDHANDLE &card)
{
	std::vector<BYTE> apdu {};
	std::vector<BYTE> response {};
	bool is_good_response {true};
	while (is_good_response) {
		Requests::create_apdu(apdu);
		is_good_response = Requests::send_apdu(card, apdu, response);
		std::cout << std::endl;
		if (!is_good_response) {
			std::cerr << "Errore nella lettura dell'APDU personalizzata\n";
			return false;
		} 
		std::cout << "output message:" << std::string {(char *)response.data()} << std::endl;
	}
	return true;
}
