#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>

#define STEAM  "\033[90m\033[38;2;186;176;164m"
#define CUP    "\033[33m\033[38;2;232;208;170m"
#define COFFEE "\033[31m\033[38;2;62;32;18m"
#define AQUA   "\033[96m\033[38;2;129;236;236m"
#define RESET  "\033[0m"

struct order {
    char name[32];
    unsigned int price;
    char brew[64];
};

int main(void) {
    setbuf(stdout, NULL);
    setbuf(stdin, NULL);

    struct order order = {0};
    order.price = 5;
    strcpy(order.brew, "echo Thanks!");

    fputs(
STEAM
"      )  (\n"
"     (   ) )\n"
"      ) ( (\n"
CUP
"    _______)_\n"
" .-'---------|\n"
"( " COFFEE "C" CUP "|" COFFEE "/\\/\\/\\/\\/" CUP "|\n"
" '-." COFFEE "/\\/\\/\\/\\/" CUP "|\n"
"   '_________'\n"
"    '-------'\n"
"\n"
"  ~ 0xCAFE ~\n"
RESET, stdout);

    fputs(AQUA "Name: " RESET, stdout);
    if (read(0, order.name, 40) <= 0)
        return 1;

    printf("Hello, %s\n", order.name);
    if (order.price != 0xCAFE) {
        printf("That'll be $%d.\n", order.price);
        return 0;
    }

    puts("On the house!");
    puts("Brewing...");
    system(order.brew);
    return 0;
}
