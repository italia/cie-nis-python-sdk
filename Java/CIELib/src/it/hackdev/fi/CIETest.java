package it.hackdev.fi;

import java.io.UnsupportedEncodingException;
import java.util.List;

import javax.smartcardio.Card;
import javax.smartcardio.CardChannel;
import javax.smartcardio.CardException;
import javax.smartcardio.CardTerminal;
import javax.smartcardio.CommandAPDU;
import javax.smartcardio.ResponseAPDU;
import javax.smartcardio.TerminalFactory;

public class CIETest {

	
	private static byte[] buildReadDiffleHeffman(CardChannel ch) throws CardException, UnsupportedEncodingException {
		byte[] result = new byte[21];
		
		byte[] SEL = new byte[] { 0x00, // CLA
				(byte) 0xA4, // SELECT
				0x00, // P1 select root
				0x0C, // P2 in binario deve valere 0000 1100 -> No Data in response
				0x00}; // Le lunghezza del AID che invieremo in questo caso 13
		
		ResponseAPDU answSEL = ch.transmit(new CommandAPDU(SEL));
		System.out.println("selectROOT: " + answSEL);
		System.out.println("SW: " + answSEL.getSW()); // questi comandi restituiscono la conversione in decimale hex del												// SW
		System.out.println("NR " + answSEL.getNr());
		System.out.println("DATA " + new String(answSEL.getData(), "UTF-8"));
		
		/*
		 * 0xA0, 0x00, 0x00, 0x00, 0x00, 0x39 // AID per applicazione CIE
		 */
		byte[] SEL2 = new byte[] { 0x00, // CLA
				(byte) 0xA4, // SELECT
				0x02, // P1 in binariio deve valere 0000 0010 -> Select EF under current DF
				0x0C, // P2 in binario deve valere 0000 1100 -> No Data in response
				0x04, // Le lunghezza del EFID che invieremo in questo caso 4
				(byte) 0x0D, 0x00, 0x00, 0x04 }; // EFID

		ResponseAPDU answSEL2 = ch.transmit(new CommandAPDU(SEL2));
		System.out.println("answSEL2: " + answSEL2);
		System.out.println("SW: " + answSEL2.getSW()); // questi comandi restituiscono la conversione in decimale hex
		System.out.println("NR " + answSEL2.getNr());
		System.out.println("DATA " + new String(answSEL2.getData(), "UTF-8"));
		
		
		
		
		
		
		byte[] READ_DH = new byte[] { 0x00, // CLA
				(byte) 0xB0, // READ BINARY
				(byte) 0x1D, // P1 1000 0001 -> Table 28 read by SFID e il 1B DH
				(byte) 0x00, // P2 0000 0000 -> Offset in file over 8bit
				(byte) 0xFF // LE byte to read in questo caso 12. E' nella specifica di
		};
		
		ResponseAPDU answREAD_DH = ch.transmit(new CommandAPDU(READ_DH));
		System.out.println("answREAD_DF: " + answREAD_DH);
		System.out.println("SW: " + answREAD_DH.getSW()); // questi comandi restituiscono la conversione in decimale
		System.out.println("NR " + answREAD_DH.getNr());
		System.out.println("DATA " + new String(answREAD_DH.getData(), "UTF-8"));
	
		
		
		return result;
		
		
	}
	
	public static void main(String args[]) throws CardException, UnsupportedEncodingException {

		/* Reading terminal list */
		TerminalFactory tf = TerminalFactory.getDefault();
		List<CardTerminal> tl = tf.terminals().list();
		System.out.println("Terminals: " + tl.size());

		if (tl.size() <= 0) {
			System.out.println("No terminal found!");
			return;
		}

		CardTerminal terminal = tl.get(0);
		Card card = terminal.connect("*");
		CardChannel ch = card.getBasicChannel();

		buildReadDiffleHeffman(ch);
		
		/*
		 * Per accedere a file system si deve selezione il DF tramite AID (Application
		 * ID) Il DF AID della CIE e' : 0xA0, 0x00, 0x00, 0x00, 0x30, 0x80, 0x00, 0x00,
		 * 0x00, 0x09, 0x81, 0x60, 0x01
		 * 
		 */
		byte[] SEL = new byte[] { 0x00, // CLA
				(byte) 0xA4, // SELECT
				0x04, // P1 in binariio deve valere 0000 0100 -> Select by AID
				0x0C, // P2 in binario deve valere 0000 1100 -> No Data in response
				0x0D, // Le lunghezza del AID che invieremo in questo caso 13
				(byte) 0xA0, 0x00, 0x00, 0x00, 0x30, (byte) 0x80, 0x00, 0x00, 0x00, 0x09, (byte) 0x81, 0x60, 0x01 }; // AID
		ResponseAPDU answSEL = ch.transmit(new CommandAPDU(SEL));
		System.out.println("answSEL: " + answSEL);
		System.out.println("SW: " + answSEL.getSW()); // questi comandi restituiscono la conversione in decimale hex del
														// SW
		System.out.println("NR " + answSEL.getNr());
		System.out.println("DATA " + new String(answSEL.getData(), "UTF-8"));

		/*
		 * 0xA0, 0x00, 0x00, 0x00, 0x00, 0x39 // AID per applicazione CIE
		 */
		byte[] SEL2 = new byte[] { 0x00, // CLA
				(byte) 0xA4, // SELECT
				0x04, // P1 in binariio deve valere 0000 0100 -> Select by AID
				0x0C, // P2 in binario deve valere 0000 1100 -> No Data in response
				0x06, // Le lunghezza del AID che invieremo in questo caso 6
				(byte) 0xA0, 0x00, 0x00, 0x00, 0x00, 0x39 }; // AID

		ResponseAPDU answSEL2 = ch.transmit(new CommandAPDU(SEL2));
		System.out.println("answSEL2: " + answSEL2);
		System.out.println("SW: " + answSEL2.getSW()); // questi comandi restituiscono la conversione in decimale hex
		System.out.println("NR " + answSEL2.getNr());
		System.out.println("DATA " + new String(answSEL2.getData(), "UTF-8"));
		/*
		 * Dopo avere selezinato l'applicazione della CIE e' possinile accedere al suo
		 * filesystem
		 */

		byte[] READ_NIS = new byte[] { 0x00, // CLA
				(byte) 0xB0, // READ BINARY
				(byte) 0x81, // P1 1000 0001 -> Table 28 read by SFID e il NIS e su SFI = 01
				(byte) 0x00, // P2 0000 0000 -> Offset in file over 8bit
				(byte) 0x0C // LE byte to read in questo caso 12. E' nella specifica di
		};

		ResponseAPDU answREAD_NIS = ch.transmit(new CommandAPDU(READ_NIS));
		System.out.println("answREAD_NIS: " + answREAD_NIS);
		System.out.println("SW: " + answREAD_NIS.getSW()); // questi comandi restituiscono la conversione in decimale
		System.out.println("NR " + answREAD_NIS.getNr());
		System.out.println("DATA " + new String(answREAD_NIS.getData(), "UTF-8"));

		byte[] READ_KPUB = new byte[] { 0x00, // CLA
				(byte) 0xB0, // READ BINARY
				(byte) 0x84, // P1 1000 0100 -> Table 28 read by SFID e il NIS e su SFI = 04
				(byte) 0x00, // P2 0000 0000 -> Offset in file over 8bit
				(byte) 0xFF // LE byte to read in questo caso 233.
		};

		ResponseAPDU answREAD_KPUB = ch.transmit(new CommandAPDU(READ_KPUB));
		System.out.println("answREAD_KPUB: " + answREAD_KPUB);
		System.out.println("SW: " + answREAD_KPUB.getSW()); // questi comandi restituiscono la conversione in decimale
		System.out.println("NR " + answREAD_KPUB.getNr());
		System.out.println("DATA " + new String(answREAD_KPUB.getData(), "UTF-8"));	
		
		/* */
		
		
		byte[] VERIFY = new byte[] { 0x00, // CLA
				(byte) 0x20, // VERIFY
				(byte) 0x00, // P1 0000 0009 -> Fisso
				(byte) 0x81, // P2 1000 0001 -> Local reference data application
				(byte) 0x08, // LC byte lunghezza PIN
				0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38 // PIN
		};

		ResponseAPDU answVERIFY = ch.transmit(new CommandAPDU(VERIFY));
		System.out.println("answVERIFY: " + answVERIFY);
		System.out.println("SW: " + answVERIFY.getSW()); // questi comandi restituiscono la conversione in decimale hex
		System.out.println("NR " + answVERIFY.getNr());
		System.out.println("DATA " + new String(answVERIFY.getData(), "UTF-8"));

		card.disconnect(false);
	}

}
