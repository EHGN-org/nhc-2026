# Solve

Open `Agent-Clearance_Terminal.xlsx`.

Check value of C8:

```
=IF(Sheet3!$BX$2=1;"● ACCESS GRANTED";"● ACCESS DENIED")
```

Can't see `Sheet3`, learn about "hidden" sheets in Excel. Right click Sheet1, click *Unhide* and select all 3 hidden sheets (2-4) one by one.

Look at cell BX2 in Sheet3:

```
=IF(AND(LEN(Sheet1!$C$6)=30;SUM($BW$2:$BW$11)=10);1;0)
```

Access granted will be shown if the length of `Sheet1!$C$6` is 30, and the sum of `$BW$2:$BW$11` is 10. We can see `$BW$2:$BW$11` are a bunch of booleans currently 0 so they must all become 1.

`Sheet1!$C$6` is our input, so if it must be 30-long, let's input something recognizable of 30 characters:

```
NHC{ABCDEFGHIJKLMNOPQRSTUVWXY}
```

Looking back at the booleans, they all have this format:

```
=IF(AND(BO2=BS2;BP2=BT2;BQ2=BU2;BR2=BV2);1;0)
```

All these 4 pairs must be equal for the boolean to be `1`.

The cells from BS to BV (right hand side of equals) are hardcoded 32-bit random-looking integers like 4072117587.

Looking at the left hand side, `BO2`, for example, we see:

```
=MOD(1732584193+Sheet4!$J$66;4294967296)
```

4294967296 is recognizably `2**32` and with `MOD` (modulus) this is just a 32-bit mask of an addition between `Sheet4!$J$66` and 1732584193.

Looking up this constant "1732584193" on Google, we get [some results](https://stackoverflow.com/questions/1727104/question-on-md5-state-variables):

> I am studying MD5 algorithm. I found out that there are four state variables (I am not sure what that means). Those variables are 0x67452301 , 0xEFCDAB89, 0x98BADCFE, and 0x10325476. I converted variables to decimals and came up with 1732584193, 4023233417, 2562383102, and 271733878 resepectively.

These aren't just any numbers, these are MD5 constants! It is likely that this Excel workbook is implementing MD5 via formulas.

We could trace the whole MD5 algorithm but that would be a waste of time. The challenge can't just be `if MD5(flag) == constant` because that would take too long to brute force.

Let's instead look at how our *input* is used and where the MD5 part starts.

Excel has a nice feature for this if we select the C6 cell on Sheet1, then *Forumlas* -> *Trace Dependents*. It draws an arrow to another sheet. If we double-click on the arrow, we can select which exact reference to go to:

1. `[Agent_Clearance_Terminal.xlsx]Sheet2!$H$2`
2. `[Agent_Clearance_Terminal.xlsx]Sheet3!$BX$2`

The 1st brings us to Sheet 2 where the following formula appends 30 `?` as padding to the flag:

```
=LEFT(Sheet1!$C$6&REPT("?",30),30)
```

So with 30 characters filled it, is just another copy of the flag. Let's trace it again:

1. `[Agent_Clearance_Terminal.xlsx]Sheet3!$E$2`
2. `[Agent_Clearance_Terminal.xlsx]Sheet3!$E$3`
3. ...
4. `[Agent_Clearance_Terminal.xlsx]Sheet3!$C$10`
5. `[Agent_Clearance_Terminal.xlsx]Sheet3!$C$11`

Many to choose from, but all close to each other so let's pick the first again. It shows a 3x10 table of our input in ASCII using the `MID()` function to select a character:

```
=CODE(MID(Sheet2!$H$2;$A2;1))
```

| C   | D   | E   |
| --- | --- | --- |
| 78  | 71  | 81  |
| 72  | 72  | 82  |
| 67  | 73  | 83  |
| 123 | 74  | 84  |
| 65  | 75  | 85  |
| 66  | 76  | 86  |
| 67  | 77  | 87  |
| 68  | 78  | 88  |
| 69  | 79  | 89  |
| 70  | 80  | 125 |

Now our recognizable test input pays off. We can clearly see the incrementing `ABC...` as 65, 66, 67, etc. going down and to the right.

Tracing the first character C2 again brings us to BC2:

```
=C2+D2*256+E2*65536+F2*16777216
```

It formats our input characters 78, 71 and 81 together with column `F` (static 128) as a 32-bit integer.

If you read the [MD5 Algorithm](https://en.wikipedia.org/wiki/MD5#Algorithm), you might recognize the 128 as the 1 bit and then all 0's used as **padding**:

> The padding works as follows: first, a single bit, 1, is appended to the end of the message. This is followed by as many zeros as are required to bring the length of the message up to 64 bits fewer than a multiple of 512. The remaining bits are filled up with 64 bits representing the length of the original message, modulo 264

So this might be the plaintext put into MD5. Looking back at the sheet, we see the columns G through AP are all 0's, part of the padding. Then 8 columns with a formula:

```
=MOD(INT($B2*8/256^0);256)
=MOD(INT($B2*8/256^1);256)
...
=MOD(INT($B2*8/256^7);256)
```

With the `MOD` those become bytes. 8 bytes = 64 bits, that must be the length represented in little endian.

Its value is 152, remember, MD5 is bit-based so 152 bits = 19 bytes for the length. But we just saw only 3 of our plaintext input bytes used. Where are the other 16 coming from?

The number 152 is just `$B2*8`. So the number of bytes is in B2, set to 19 indeed. Its formula for each row is:

```
=COUNT(Sheet2!$F$2:$F$17)+COUNT($C2:$E2)
=COUNT(Sheet2!$F$2:$F$17)+COUNT($C3:$E3)
...
=COUNT(Sheet2!$F$2:$F$17)+COUNT($C11:$E11)
```

It counts some cells. The left hand side of the addition doesn't change, and the right hand size points to the 3 input bytes we know about. Looking at the F2-F17 range in Sheet 2 we find some bytes:

| F   |
| --- |
| 214 |
| 149 |
| 200 |
| 192 |
| 250 |
| 214 |
| 203 |
| 150 |
| 145 |
| 206 |
| 220 |
| 250 |
| 214 |
| 145 |
| 201 |
| 209 |

16 to be exact. Could these be the missing plaintext bytes our input chunks are prefixed with in the MD5 operation? Checking their usage, they are not just counted:

1. `[Agent_Clearance_Terminal.xlsx]Sheet3!$AY$2`
2. `[Agent_Clearance_Terminal.xlsx]Sheet3!$AY$3`
3. ...
4. `[Agent_Clearance_Terminal.xlsx]Sheet3!$B$11`

Its first usage is very similar to how our input was also turned into a 32-bit number, just with `BITXOR(...;165)` applied over it:

```
=BITXOR(Sheet2!$F$2;165)+BITXOR(Sheet2!$F$3;165)*256+BITXOR(Sheet2!$F$4;165)*65536+BITXOR(Sheet2!$F$5;165)*16777216
```

If we XOR decrypt the F bytes with 165, we get:

```Python
>>> from pwn import xor
>>> F = bytes([214, 149, 200, 192, 250, 214, 203, 150, 145, 206, 220, 250, 214, 145, 201, 209])
>>> xor(F, 165)
b's0me_sn34ky_s4lt'
```

There we have it, a salt! It is prepended to our chunked input, then MD5 hashed, and compared to some constant.

Now we have a full picture of the algorithm and can start to implement a solver. For each chunk we'll need to find which 3 bytes prefixed with the salt hash to a specific constant value in the sheet. To know which value exactly, we can look at the [MD5 Algorithm](https://en.wikipedia.org/wiki/MD5#Algorithm) again:

> ```C
> var int a0 := 0x67452301   // A
> var int b0 := 0xefcdab89   // B
> var int c0 := 0x98badcfe   // C
> var int d0 := 0x10325476   // D
> 
> for each 512-bit chunk of padded message do
>     // Initialize hash value for this chunk:
>     var int A := a0
>     var int B := b0
>     var int C := c0
>     var int D := d0
>     ...
>     a0 := a0 + A
>     b0 := b0 + B
>     c0 := c0 + C
>     d0 := d0 + D
> end for
> 
> var char digest[16] := a0 append b0 append c0 append d0 // (Output > is in little-endian)
> ```

Our earlier find of 1732584193 is `0x67452301` in hex. That matches `A`, the constant added in the last step to the first 4 bytes of the digest. Consequently the 2nd, 3rd and 4th part of the digest are also done after this last addition.

We can verify we have the correct hash implementation by comparing it with one of our inputs. `NHC{ABCDEFGHIJKLMNOPQRSTUVWXY}` is split into chunks of 3 by skipping 10 characters each time, so the first chunk is `NGQ` (bytes 78, 71 and 81). Then prefix with `s0me_sn34ky_s4lt` and MD5 hash:

```py
>>> from hashlib import md5
>>> digest = md5(b"s0me_sn34ky_s4lt" + b"NGQ").digest()
b'\nPT\x88\x12\xa6|\xbd\xfck\xcc6cz{\xe7'
```

The excel workbook stores the variables `a0`, `b0`, `c0` and `d0` separately as 32-bit integers:

| BO         | BP         | BQ        | BR         |
| ---------- | ---------- | --------- | ---------- |
| 2287226890 | 3179062802 | 919366652 | 3883629155 |

So let's do the same with our digest:

```py
>>> a0, b0, c0, d0 = digest[:4], digest[4:8], digest[8:12], digest[12:16]
>>> [int.from_bytes(b, byteorder="little") for b in [a0, b0, c0, d0]]
[2287226890, 3179062802, 919366652, 3883629155]
```

It matches! Now we just need to brute force until it matches the constant it is compared to:

| BS         | BT         | BU         | BV       |
| ---------- | ---------- | ---------- | -------- |
| 4072117587 | 1120387196 | 2102578019 | 85756587 |

```py
from hashlib import md5
import itertools

for guess in itertools.product(range(256), repeat=3):
    digest = md5(b"s0me_sn34ky_s4lt" + bytes(guess)).digest()
    a0, b0, c0, d0 = digest[:4], digest[4:8], digest[8:12], digest[12:16]
    a0, b0, c0, d0 = [int.from_bytes(b, byteorder="little") for b in [a0, b0, c0, d0]]

    if a0 == 4072117587 and b0 == 1120387196 and c0 == 2102578019 and d0 == 85756587:
        print(guess)  # (78, 42, 95) b'N*_'
        break
```

We found the first chunk: `b'N*_'`!

Now all that's left is repeating this for all BS-BV rows from 2-11. Then lining them up again to form the whole flag:

```py
from hashlib import md5
import itertools

CHUNKS = [
    [4072117587, 1120387196, 2102578019, 85756587],
    [3002749583, 3716679707, 3074522701, 1912839214],
    [1202946202, 3060285146, 3794539838, 3225098655],
    [4005615615, 2391617212, 2576942536, 2140002521],
    [1783887626, 3622230939, 1267188250, 2483512918],
    [3971983597, 866610566, 1921144098, 402180923],
    [3409560921, 3103012121, 2261944769, 3919384297],
    [3377601125, 847392938, 543800179, 879909070],
    [2343965920, 2169933120, 1366115365, 931825985],
    [1416552657, 3925964814, 413409308, 1810266362],
]

flag = [ord("?")] * 30


for chunk_i, chunk in enumerate(CHUNKS):
    for guess in itertools.product(range(256), repeat=3):
        digest = md5(b"s0me_sn34ky_s4lt" + bytes(guess)).digest()
        a0, b0, c0, d0 = digest[:4], digest[4:8], digest[8:12], digest[12:16]
        a0, b0, c0, d0 = [int.from_bytes(b, byteorder="little") for b in [a0, b0, c0, d0]]

        if a0 == chunk[0] and b0 == chunk[1] and c0 == chunk[2] and d0 == chunk[3]:
            print(guess, bytes(guess))
            for i in range(3):
                flag[i * 10 + chunk_i] = guess[i]
            print(bytes(flag))
            break
```

Letting it run for a bit:

```
(78, 42, 95) b'N*_'
b'N?????????*?????????_?????????'
(72, 108, 52) b'Hl4'
b'NH????????*l????????_4????????'
(67, 51, 71) b'C3G'
b'NHC???????*l3???????_4G???????'
...
(76, 107, 125) b'Lk}'
b'NHC{*3Xc3L*l3Nt_W0Rk_4G3Nt_47}'
```

The flag is found! We can also input it into the Excel workbook to verify it returns "ACCESS GRANTED"
