#!/usr/bin/env python3
"""Build the spreadsheet CTF.

Sheet1 is the only visible sheet and shows nothing but an input box and a
verdict. Sheets 2-4 are hidden and hold the machinery: MD5 implemented purely
in worksheet formulas, verifying ten salted three-character slices of the flag.

Deliberate anti-tells, so that recognising MD5 is the challenge:
  * nothing is named after what it does, and there are no defined names at
    all: every formula refers to raw cell ranges
  * the salt is stored as XOR-masked byte codes, never as text
  * the flag is split by a permutation that exists only inside the byte
    formulas, with no cell holding a readable fragment
  * digests are compared as four 32-bit words, not as a hex string

Portability notes:
  * rotations use MOD/INT rather than BITLSHIFT, whose intermediates would
    exceed the 2^48 ceiling Excel imposes on the bitwise functions
  * BITAND/BITOR/BITXOR postdate the original xlsx spec, so they must be
    stored as _xlfn.BITAND etc.; XlsxWriter's use_future_functions does this
  * every formula is written with its cached result, so the sheet reads
    correctly even in a viewer that declines to recalculate on load
"""

import argparse
import hashlib
import math

import xlsxwriter

FLAG = "NHC{*3Xc3L*l3Nt_W0Rk_4G3Nt_47}"
SALT = b"s0me_sn34ky_s4lt"
XOR_MASK = 165

NCHUNKS = 10
CHUNK_LEN = 3
FLAG_LEN = NCHUNKS * CHUNK_LEN
PLACEHOLDER = "?" * CHUNK_LEN

MASK = 4294967296
NOT32 = 4294967295
IV = (1732584193, 4023233417, 2562383102, 271733878)

K_TAB = [int(abs(math.sin(i + 1)) * MASK) & NOT32 for i in range(64)]
S_TAB = [7, 12, 17, 22] * 4 + [5, 9, 14, 20] * 4 + [4, 11, 16, 23] * 4 + [6, 10, 15, 21] * 4
G_TAB = (
    [i for i in range(16)]
    + [(5 * i + 1) % 16 for i in range(16, 32)]
    + [(3 * i + 5) % 16 for i in range(32, 48)]
    + [(7 * i) % 16 for i in range(48, 64)]
)

# Sheet2, column H: the input padded out to a fixed width so that MID never
# runs off the end. This is the only cell holding any part of the input, and it
# holds it verbatim, so it gives away nothing about how the input is split.
S2_PAD = 7

# Sheet3 column layout (0-based). The 16 salt bytes never occupy a cell of
# their own: BITXOR is inlined into the first four message words so that
# nothing on the sheet evaluates to a plaintext ASCII code.
C_N, C_LEN = 0, 1
C_BYTE0 = 2
C_NBYTES = 64 - len(SALT)
C_WORD0 = C_BYTE0 + C_NBYTES
C_CALC = C_WORD0 + 16
C_STORE = C_CALC + 4
C_MATCH = C_STORE + 4
C_GATE = C_MATCH + 1
S3_NCOLS = C_GATE + 1

# Sheet4 stride: one IV row followed by 64 round rows
S4_STRIDE = 65


def a1(col):
    s = ""
    col += 1
    while col:
        col, rem = divmod(col - 1, 26)
        s = chr(65 + rem) + s
    return s


def iv_row(n):
    """0-based row of slice n's IV line on Sheet4."""
    return 1 + (n - 1) * S4_STRIDE


def slices_of(flag):
    """Interleaved: slice n takes characters n, n+NCHUNKS, n+2*NCHUNKS."""
    if len(flag) != FLAG_LEN:
        return [PLACEHOLDER] * NCHUNKS
    return ["".join(flag[i + k * NCHUNKS] for k in range(CHUNK_LEN)) for i in range(NCHUNKS)]


def message_for(chunk):
    """The exact byte string the workbook hashes for a slice."""
    return SALT + chunk.encode()


def trace(msg):
    """Mirror the worksheet's MD5 exactly, returning every intermediate."""
    length = len(msg)
    byts = []
    for j in range(64):
        if j < length:
            byts.append(msg[j])
        elif j == length:
            byts.append(128)
        elif j == 56:
            byts.append((length * 8) % 256)
        elif j == 57:
            byts.append((length * 8) // 256)
        else:
            byts.append(0)
    words = [
        byts[4 * k] + byts[4 * k + 1] * 256 + byts[4 * k + 2] * 65536 + byts[4 * k + 3] * 16777216
        for k in range(16)
    ]

    rounds = []
    a, b, c, d = IV
    for i in range(64):
        if i < 16:
            f = (b & c) | ((NOT32 - b) & d)
        elif i < 32:
            f = (d & b) | ((NOT32 - d) & c)
        elif i < 48:
            f = (b ^ c) ^ d
        else:
            f = c ^ (b | (NOT32 - d))
        total = (f + a + K_TAB[i] + words[G_TAB[i]]) % MASK
        s = S_TAB[i]
        rot = (total % 2 ** (32 - s)) * 2**s + total // 2 ** (32 - s)
        a, b, c, d = d, (b + rot) % MASK, b, c
        rounds.append((K_TAB[i], s, G_TAB[i], words[G_TAB[i]], f, total, rot, a, b, c, d))

    digest = tuple((init + x) % MASK for init, x in zip(IV, (a, b, c, d)))
    return byts, words, rounds, digest


def stored_words(flag):
    out = []
    for chunk in slices_of(flag):
        dg = hashlib.md5(message_for(chunk)).digest()
        out.append([int.from_bytes(dg[4 * k : 4 * k + 4], "little") for k in range(4)])
    return out


# --------------------------------------------------------------------------


def build(path, prefill=None):
    entered = prefill or ""
    live = slices_of(entered)
    targets = stored_words(FLAG)
    traces = [trace(message_for(live[n - 1])) for n in range(1, NCHUNKS + 1)]
    matches = [1 if list(traces[n][3]) == targets[n] else 0 for n in range(NCHUNKS)]
    gate = 1 if len(entered) == FLAG_LEN and sum(matches) == NCHUNKS else 0
    verdict = "\u25cf ACCESS GRANTED" if gate else "\u25cf ACCESS DENIED"

    # Every range is spliced straight into the formulas that use it. The
    # workbook defines no names, so the range list gives away nothing on its
    # own and each reference has to be chased through the sheets by hand.
    input_ref = "Sheet1!$C$6"
    k_ref = "Sheet2!$B$2:$B$65"
    s_ref = "Sheet2!$C$2:$C$65"
    g_ref = "Sheet2!$D$2:$D$65"
    pad_ref = f"Sheet2!${a1(S2_PAD)}$2"
    words_ref = f"Sheet3!${a1(C_WORD0)}$2:${a1(C_WORD0 + 15)}${NCHUNKS + 1}"

    wb = xlsxwriter.Workbook(path, {"use_future_functions": True})

    ink, steel = "#16233A", "#1F3864"
    f_title = wb.add_format({"font_size": 20, "bold": True, "font_color": steel})
    f_sub = wb.add_format({"italic": True, "font_color": "#5A6785"})
    f_label = wb.add_format({"bold": True, "font_color": ink})
    f_head = wb.add_format({"bold": True, "font_color": "#FFFFFF", "bg_color": steel, "align": "center"})
    f_mono = wb.add_format({"font_name": "Courier New", "font_size": 9, "font_color": "#44506B"})
    f_mono_b = wb.add_format({"font_name": "Courier New", "font_size": 9, "bold": True, "font_color": ink})
    f_input = wb.add_format(
        {
            "font_name": "Courier New", "font_size": 14, "bold": True, "font_color": "#7A4B00",
            "bg_color": "#FFF6D8", "border": 1, "border_color": "#9AA7C2",
            "align": "center", "valign": "vcenter", "locked": False,
        }
    )
    f_out = wb.add_format(
        {
            "font_size": 14, "bold": True, "font_color": ink, "border": 1,
            "border_color": "#9AA7C2", "align": "center", "valign": "vcenter",
        }
    )
    f_pass = wb.add_format({"bg_color": "#C6EFCE", "font_color": "#006100"})
    f_fail = wb.add_format({"bg_color": "#FFC7CE", "font_color": "#9C0006"})

    # ---- Sheet1: the only thing the player sees ----
    s1 = wb.add_worksheet("Sheet1")
    s1.hide_gridlines(2)
    s1.set_column("A:A", 3)
    s1.set_column("B:B", 20)
    s1.set_column("C:C", 46)
    s1.set_row(1, 28)
    s1.set_row(5, 26)
    s1.set_row(7, 26)

    s1.write("B2", "NORTHERN HEMISPHERE COMMAND", f_title)
    s1.write("B3", "Field terminal \u2014 offline clearance check.", f_sub)
    s1.write("B6", "Flag", f_label)
    s1.write("C6", entered, f_input)
    s1.write("B8", "STATUS", f_label)
    s1.write_formula(
        "C8",
        f'=IF(Sheet3!${a1(C_GATE)}$2=1,"\u25cf ACCESS GRANTED","\u25cf ACCESS DENIED")',
        f_out,
        verdict,
    )
    s1.conditional_format(
        "C8:C8",
        {"type": "formula", "criteria": 'ISNUMBER(SEARCH("GRANTED",$C$8))', "format": f_pass},
    )
    s1.conditional_format(
        "C8:C8",
        {"type": "formula", "criteria": 'NOT(ISNUMBER(SEARCH("GRANTED",$C$8)))', "format": f_fail},
    )
    s1.protect()

    # ---- Sheet2: round constants, plus the masked salt bytes ----
    s2 = wb.add_worksheet("Sheet2")
    s2.set_column("A:A", 9)
    s2.set_column("B:B", 14)
    s2.set_column("C:D", 9)
    s2.set_column("F:F", 9)
    s2.set_column(S2_PAD, S2_PAD, 40)
    for i in range(64):
        for col, v in enumerate((i, K_TAB[i], S_TAB[i], G_TAB[i])):
            s2.write_number(i + 1, col, v, f_mono)
    # The table name must not parse as a cell address: TBL1 and friends are
    # real cells (column TBL is 13584, inside the 16384-column grid) and Excel
    # rejects the file. "Table1" is safe because no column name exceeds 3
    # letters.
    s2.add_table(
        0, 0, 64, 3,
        {
            "name": "Table1",
            "style": "Table Style Medium 5",
            "columns": [{"header": h} for h in ("k1", "k2", "k3", "k4")],
        },
    )
    s2.write(0, 5, "k5", f_head)
    for i, byte in enumerate(SALT):
        s2.write_number(i + 1, 5, byte ^ XOR_MASK, f_mono)

    # Pad the input out to FLAG_LEN so MID never runs off the end and CODE
    # never raises #VALUE! on a short entry.
    s2.write(0, S2_PAD, "k6", f_head)
    s2.write_formula(
        1, S2_PAD,
        f'=LEFT({input_ref}&REPT("?",{FLAG_LEN}),{FLAG_LEN})',
        f_mono, (entered + "?" * FLAG_LEN)[:FLAG_LEN],
    )
    s2.freeze_panes(1, 0)

    # ---- Sheet3: padded block, message words and digest per slice ----
    s3 = wb.add_worksheet("Sheet3")
    s3.set_column(C_N, C_N, 6)
    s3.set_column(C_LEN, C_LEN, 6)
    s3.set_column(C_BYTE0, C_BYTE0 + C_NBYTES - 1, 5)
    s3.set_column(C_WORD0, C_GATE, 12)
    for col in range(S3_NCOLS):
        s3.write(0, col, f"c{col + 1}", f_head)

    for n in range(1, NCHUNKS + 1):
        row = n
        xl = row + 1
        byts, words, rounds, digest = traces[n - 1]

        s3.write_number(row, C_N, n, f_mono)
        chars = f"${a1(C_BYTE0)}{xl}:${a1(C_BYTE0 + CHUNK_LEN - 1)}{xl}"
        s3.write_formula(
            row, C_LEN,
            f"=COUNT(Sheet2!$F$2:$F${len(SALT) + 1})+COUNT({chars})",
            f_mono, len(SALT) + CHUNK_LEN,
        )

        # Bytes after the salt: three characters from the input, then the
        # usual MD5 padding. Column A is the slice index used as the MID
        # origin — it is not part of the preimage.
        length = a1(C_LEN)
        msg_len = len(SALT) + CHUNK_LEN
        for j in range(len(SALT), 64):
            col = C_BYTE0 + j - len(SALT)
            if j < msg_len:
                # Slice n is built from input positions n, n+10, n+20: the
                # characters of a slice sit NCHUNKS apart, not side by side.
                step = (j - len(SALT)) * NCHUNKS
                pos = f"$A{xl}" if step == 0 else f"$A{xl}+{step}"
                s3.write_formula(
                    row, col,
                    f"=CODE(MID({pad_ref},{pos},1))",
                    f_mono, byts[j],
                )
            elif j == msg_len:
                s3.write_number(row, col, 128, f_mono)
            elif j >= 56:
                # Little-endian 64-bit bit-length. Only the low byte is
                # nonzero for a 19-byte message, but all eight are written
                # the same way so the field reads as MD5 padding.
                k = j - 56
                s3.write_formula(
                    row, col,
                    f"=MOD(INT(${length}{xl}*8/256^{k}),256)",
                    f_mono, byts[j],
                )
            else:
                s3.write_number(row, col, 0, f_mono)
        for j in range(16):
            if j < len(SALT) // 4:
                parts = []
                for k, mul in enumerate((1, 256, 65536, 16777216)):
                    term = f"BITXOR(Sheet2!$F${4 * j + k + 2},{XOR_MASK})"
                    parts.append(term if mul == 1 else f"{term}*{mul}")
                formula = "=" + "+".join(parts)
            else:
                b = [a1(C_BYTE0 + 4 * j + k - len(SALT)) for k in range(4)]
                formula = f"={b[0]}{xl}+{b[1]}{xl}*256+{b[2]}{xl}*65536+{b[3]}{xl}*16777216"
            s3.write_formula(row, C_WORD0 + j, formula, f_mono, words[j])

        last = iv_row(n) + 64 + 1
        for j, (init, col) in enumerate(zip(IV, "JKLM")):
            s3.write_formula(
                row, C_CALC + j,
                f"=MOD({init}+Sheet4!${col}${last},{MASK})",
                f_mono, digest[j],
            )
        for j in range(4):
            s3.write_number(row, C_STORE + j, targets[n - 1][j], f_mono)

        pairs = ",".join(f"{a1(C_CALC + k)}{xl}={a1(C_STORE + k)}{xl}" for k in range(4))
        s3.write_formula(row, C_MATCH, f"=IF(AND({pairs}),1,0)", f_mono, matches[n - 1])

    s3.write_formula(
        1, C_GATE,
        (
            f"=IF(AND(LEN({input_ref})={FLAG_LEN},"
            f"SUM(${a1(C_MATCH)}$2:${a1(C_MATCH)}${NCHUNKS + 1})={NCHUNKS}),1,0)"
        ),
        f_mono, gate,
    )
    s3.freeze_panes(1, 0)

    # ---- Sheet4: 64 compression rounds per slice, all rows identical ----
    s4 = wb.add_worksheet("Sheet4")
    for col, width in enumerate([6, 6, 12, 6, 5, 12, 12, 12, 12, 12, 12, 12, 12]):
        s4.set_column(col, col, width)
    for col in range(13):
        s4.write(0, col, f"c{col + 1}", f_head)

    for n in range(1, NCHUNKS + 1):
        top = iv_row(n)
        s4.write_number(top, 0, n, f_mono_b)
        s4.write_number(top, 1, -1, f_mono_b)
        for j, init in enumerate(IV):
            s4.write_number(top, 9 + j, init, f_mono_b)

        for i in range(64):
            row = top + 1 + i
            xl = row + 1
            p = xl - 1
            vals = traces[n - 1][2][i]
            s4.write_number(row, 0, n, f_mono)
            s4.write_number(row, 1, i, f_mono)
            s4.write_formula(row, 2, f"=INDEX({k_ref},$B{xl}+1)", f_mono, vals[0])
            s4.write_formula(row, 3, f"=INDEX({s_ref},$B{xl}+1)", f_mono, vals[1])
            s4.write_formula(row, 4, f"=INDEX({g_ref},$B{xl}+1)", f_mono, vals[2])
            s4.write_formula(row, 5, f"=INDEX({words_ref},$A{xl},$E{xl}+1)", f_mono, vals[3])
            s4.write_formula(
                row, 6,
                (
                    f"=IF($B{xl}<16,BITOR(BITAND($K{p},$L{p}),BITAND({NOT32}-$K{p},$M{p})),"
                    f"IF($B{xl}<32,BITOR(BITAND($M{p},$K{p}),BITAND({NOT32}-$M{p},$L{p})),"
                    f"IF($B{xl}<48,BITXOR(BITXOR($K{p},$L{p}),$M{p}),"
                    f"BITXOR($L{p},BITOR($K{p},{NOT32}-$M{p})))))"
                ),
                f_mono, vals[4],
            )
            s4.write_formula(
                row, 7, f"=MOD($G{xl}+$J{p}+$C{xl}+$F{xl},{MASK})", f_mono, vals[5]
            )
            s4.write_formula(
                row, 8,
                f"=MOD($H{xl},2^(32-$D{xl}))*2^$D{xl}+INT($H{xl}/2^(32-$D{xl}))",
                f_mono, vals[6],
            )
            s4.write_formula(row, 9, f"=$M{p}", f_mono, vals[7])
            s4.write_formula(row, 10, f"=MOD($K{p}+$I{xl},{MASK})", f_mono, vals[8])
            s4.write_formula(row, 11, f"=$K{p}", f_mono, vals[9])
            s4.write_formula(row, 12, f"=$L{p}", f_mono, vals[10])

    s4.freeze_panes(1, 2)

    s2.hide()
    s3.hide()
    s4.hide()
    wb.close()
    return targets


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default="Agent_Clearance_Terminal.xlsx")
    ap.add_argument("--prefill", metavar="TEXT", help="pre-populate the input cell (testing only)")
    args = ap.parse_args()
    build(args.out, args.prefill)
    print(f"wrote {args.out}")
    print(f"salt {SALT!r} masked with {XOR_MASK}")
    for n, chunk in enumerate(slices_of(FLAG), 1):
        print(f"  {n:>2}  {chunk!r}  {hashlib.md5(message_for(chunk)).hexdigest()}")
