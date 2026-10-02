Plaintext: NHCIMAGINEUSINGTHISEVERYTIMEYOUVISITAWEBSITE

Follow tutorial at https://enigma.virtualcolossus.co.uk/VirtualEnigma/

## Encryption

1. Choose day on keypage -> `19`
2. Look up "Walzenlage" on keypage for day, being which rotors in order. Pick up these -> `III V II`
3. Look up "Ringstellung" on keypage for day, being the number to lock the pin per rotor on -> `06 22 05`
4. Look up "Steckerverbindungen" on keypage for day, being the connections to make -> `HL NT EJ OV FR ZK SY DI WU MG`
5. Choose random 3-character string called *wrapper key* -> `DFO`
6. Choose random 3-character string called *wrapper text* -> `ULZ`
7. Set rotors to *wrapper key* (A = 1, Z = 26)
8. Type *wrapper text* into the machine and get output called *real key* -> `XYD`
9. Set rotors to *real key* (A = 1, Z = 26)
10. Type plaintext into the machine and get output called *ciphertext* -> `RPPLDOLBSZREJPVNGSZBATSEWOFVKRBFPKBZXUGJZBNL`
11. Look up "Kenngruppen" on keypage for day and pick a random one of the four 3-character strings called *key identifier* -> `KLY`
12. Choose random 2-character string and append *key identifier*, called *letter identification group* -> `RMKLY`
13. Split the *ciphertext* into chunks of 5 and prepend the *letter identification group*, called *lig+ciphertext* -> `RMKLY RPPLD OLBSZ REJPV NGSZB ATSEW OFVKR BFPKB ZXUGJ ZBNL`
14. Prepend the metadata `1337 = 1TLE = 1TL` (time 13:37, 1 total parts, part 1), the length of *lig+ciphertext* (`58`), and the *wrapper key* & *wrapper text*:

```
1337 = 1TLE = 1TL = 58 = DFO ULZ RMKLY RPPLD OLBSZ REJPV NGSZB ATSEW OFVKR BFPKB ZXUGJ ZBNL
```

15. Send this in morse code

## Decryption (solve)

1. Decode mp3 morse code: https://morsecode.world/international/decoder/audio-decoder-adaptive.html
2. Take `RMKLY` piece and cut off the first 2 random characters to be left with `KLY`. Look this up in the keypage "Kenngruppen" to find it as the 2nd option of day 19
3. Perform steps 2-4 of [Encryption](#encryption) to set up the enigma machine. Either in VirtualEnigma or https://cryptii.com/pipes/enigma-machine/ (make sure to select model "Enigma I" & reflector "UKW B" to match VirtualEnigma)
4. Set the rotor positions to the first 3-character chunk `DFO` (A = 1, Z = 26) -> **4, 6, 15**
5. Input the second 3-character chunk `ULZ` into the machine to get the *real key* -> `XYD`
6. Set rotors to *real key* (A = 1, Z = 26) -> **24, 25, 4**
7. Type *ciphertext* after the first 5-character block into the machine (`RPPLD OLBSZ REJPV NGSZB ATSEW OFVKR BFPKB ZXUGJ ZBNL`) to get plaintext

```
NHCIMAGINEUSINGTHISEVERYTIMEYOUVISITAWEBSITE
```
