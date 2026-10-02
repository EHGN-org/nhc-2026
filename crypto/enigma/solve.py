#!uv run
from enigma.machine import EnigmaMachine
from morse_audio_decoder.morse import MorseCode
from pydub import AudioSegment

# Patch modern python issue
MORSE_MAP = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z', '-----': '0', '.----': '1', '..---': '2', '...--': '3',
    '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8',
    '----.': '9', "-...-": "="
}
MorseCode.morse_to_char = property(lambda self: MORSE_MAP)

# Decode morse
audio = AudioSegment.from_mp3("enigma.mp3")
audio.set_channels(1).export("enigma.wav", format="wav")
morse_code = MorseCode.from_wavfile("enigma.wav")

morse_text = morse_code.decode()
print(morse_text)

# Solve enigma

KEY_PAGE = """\
31\tII IV I\t05 21 19\tTC ZP SI KE NV OY BJ XF GU HA\tFXA KBI PMY SBM
30\tIV I V\t20 25 10\tPH CA KR TN GU FS VL DW YI OE\tWHQ FZX ZVF ZSC
29\tI IV II\t12 08 17\tFY BX WI CL AT EK OS RP NV UM\tGIT GZO BCK KIS
28\tV III I\t06 18 05\tAQ PO KD HX FM YU VT JG CL BW\tPBX EAO NEU OXM
27\tIII I V\t26 01 25\tXM TV BR YH AC GJ ZU WL OP FE\tZLH LPV JNI NMG
26\tV II I\t11 13 24\tIG ZY JH DN UL WQ OT PV RB SM\tSIX RQU WQK XPH
25\tI III V\t09 20 19\tJS MK FB EL DO Gl WA ZC PN RY\tZUI NNM UJR EII
24\tI II III\t15 01 12\tDW YF ZJ TO QM XE NP LV AK HB\tELV KWP FRZ SXC
23\tII III V\t08 07 03\tJN QM PO VF HU AT YL KB ZW ES\tGIZ ESI LWY ZGH
22\tV IV I\t26 13 25\tMY NF RD PT SB EI VG UZ JK OA\tKIU KAX ZMC SYD
21\tII I V\t01 18 02\tGA DU SH KO FV RW BL CN IY QP\tARA WBD XVO XXD
20\tIV III I\t19 07 14\tLU KM AB CG SW TI XF PZ OH DR\tBSI JQN HOK VHA
19\tIII V II\t06 22 05\tHL NT EJ OV FR ZK SY DI WU MG\tAJJ KLY OVP SBR
18\tII I IV\t25 24 21\tBV PK NC HR MA SF JD EO ZI TU\tXJA XJT UCX HPF
17\tV III II\t05 08 02\tPZ EI BW NU VF RK QS MD JH AC\tSPK WFK RSN CPL
16\tII IV V\t20 04 12\tNJ ZU BS EM PR WC OT YD IG KV\tAAK CTR VXJ CMB
15\tIII V IV\t09 24 07\tCK VN UQ JA IX TY PR BS ZM WE\tCZG LZM GSD VHP
14\tI II V\t13 10 16\tPV KI JH RZ SU NW EA TO BL CD\tVAJ SKV MXQ MFD
13\tIII IV I\t09 03 08\tYA TS PC KU OL DE ZB IV QN WR\tCWD HXX IWO CNY
12\tV I II\t07 19 22\tSB JO LR FH YD AM VK NG UI PC\tKDJ GPF CKY SVX
11\tIII II IV\t20 04 24\tAV GH OC DU EF IN RZ QX BP WM\tTUD UQU AKY JOG
10\tIII IV V\t11 23 09\tCO JV NB EK HI ZM UP WD LA YF\tZSU CAV TBF MSQ
9\tV II IV\t09 07 04\tFL ZU SW RN BM HP JK XY OG EI\tOQG ZQF GUC HSH
8\tII V I\t15 21 16\tRO PL JX WU IG SD VA BM HF KT\tRNN LRF MUJ NHA
7\tIV I III\t26 11 05\tLM CE VT ID NY JP XF QH RA GB\tRLU YXI EPO BEA
6\tV III IV\t23 14 22\tOB RZ WD LV KF XI QM CN PH AU\tIBP VVP MIZ WRA
5\tIV II V\t21 03 15\tZW VU QS NE RJ GL DF AX IT HO\tKUC GGH NRK OUK
4\tI V II\t25 17 07\tSU JR KE YP CB MH GV DO XF TA\tYWQ NVH FVI MVK
3\tIII V I\t18 04 26\tRD GW MT OZ NH KX QE UI VB YL\tSCH MNO RNN VKA
2\tI III IV\t06 12 01\tPU TV HQ FG BZ IL CY WM ND SE\tWMK NFO JBC XFJ
1\tV IV II\t05 02 07\tGK DL IY AQ FH WB TX PS OM ZU\tJMU EMM VAD YMK"""

def find_settings(cipher_group):
    for row in KEY_PAGE.split('\n'):
        day, rotors, ring_settings, plugboard_settings, groups = row.split('\t')
        for group in groups.split(' '):
            if group == cipher_group:
                return day, rotors, ring_settings, plugboard_settings
    else:
        raise ValueError(f"Cipher group {cipher_group} not found in key page")


_time, _part, _parts, length, ciphertext = morse_text.split(' = ')

wrapper_key, wrapper_text, cipher_group, *ciphertext = ciphertext.split(" ")
assert int(length) == len(' '.join([cipher_group] + ciphertext)), f"{length} != {len(' '.join(ciphertext))}"
cipher_group = cipher_group[2:]
ciphertext = ''.join(ciphertext)

day, rotors, ring_settings, plugboard_settings = find_settings(cipher_group)
print(f"Found settings for {cipher_group} on {day}")
print(f"{rotors=}")
print(f"{ring_settings=}")
print(f"{plugboard_settings=}")

machine = EnigmaMachine.from_key_sheet(
       rotors=rotors,
       reflector='B',
       ring_settings=ring_settings,
       plugboard_settings=plugboard_settings)

print(f"{wrapper_key=}")
print(f"{wrapper_text=}")
machine.set_display(wrapper_key)
msg_key = machine.process_text(wrapper_text)
print(f"{msg_key=}")

machine.set_display(msg_key)
plaintext = machine.process_text(ciphertext)
print(plaintext)
