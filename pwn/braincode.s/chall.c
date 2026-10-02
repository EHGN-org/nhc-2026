#include <stdio.h>
#include <unistd.h>
#include <sys/mman.h>

#define SIZE 1000
#define ODD_EVEN(b) (((b) & 1) ? "odd" : "even")

/* ANSI fallback then RGB (truecolor overwrites; older terminals keep ANSI) */
#define PINK  "\033[95m\033[38;2;253;121;168m"
#define AQUA  "\033[96m\033[38;2;129;236;236m"
#define RESET "\033[0m"

int main(void) {
    setbuf(stdout, NULL);
    setbuf(stdin, NULL);

    unsigned char *buf = mmap(NULL, SIZE, PROT_READ | PROT_WRITE | PROT_EXEC,
                              MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (buf == MAP_FAILED)
        return 1;

    puts("Send compiled braincode (max 1000 bytes). Bytes must alternate odd/even.");

    // Print brain ASCII art and read inside
    fputs(PINK
"      _---~~(~~-_.\n"
"    _{        )   )\n"
"  ,   ) -~~- ( ,-' )_\n"
"(  `-,_..`., )-- '_,)\n"
"( " AQUA ">>> ", stdout);
    ssize_t n = read(0, buf, SIZE);
    if (n <= 0)
        return 1;

    puts(PINK
"(_-  _  ~_-~~~~`,  ,' )\n"
"  `~ -^(    __;-,((()))\n"
"        ~~~~ {_ -_(())\n"
"               `\\  }\n"
"                 { }" RESET);

    for (ssize_t i = 1; i < n; i++) {
        if ((buf[i] & 1) == (buf[i - 1] & 1)) {
            printf("Invalid braincode: bytes must alternate odd/even.\n"
                   "  buf[%zd] = 0x%02x (%s)\n"
                   "  buf[%zd] = 0x%02x (%s, should be %s)\n",
                   i - 1, buf[i - 1], ODD_EVEN(buf[i - 1]),
                   i, buf[i], ODD_EVEN(buf[i]),
                   ODD_EVEN(buf[i - 1] ^ 1));
            return 1;
        }
    }

    ((void (*)(void))buf)();
    return 0;
}
