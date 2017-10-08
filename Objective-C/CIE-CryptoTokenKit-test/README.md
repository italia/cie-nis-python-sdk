# CIE CryptoTokenKit test

This [CIE](https://developers.italia.it/en/cie/) CryptoTokenKit test is a MacOS X implementation of the [cie-middleware](https://github.com/italia/cie-middleware/blob/master/EsempioPCSC/EsempioPCSC.cpp) sample, based on MacOS X frameworks. Specifically Apple adopted [Ludovic Rousseau's PCSC](https://github.com/LudovicRousseau/PCSC) in 10.9 days, and in later revisions renamed it to CryptoTokenKit.

This is based on [CryptoTokenKit-TrivialExample-OpenSC](https://github.com/dirkx/CryptoTokenKit-TrivialExample-OpenSC), but is currently non-functional.

CryptoTokenKit requires the application to be code-signed and to have the `com.apple.security.smartcard` entitlement.

This sample attempts to connect via a smartcard reader to the CIE and read the NIS by sending APDU commands. The first and second command complete successfully, the third command always fails with a 0x6a82 error ("file not found").
