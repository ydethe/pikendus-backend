// gcc -g -std=gnu99 `python3-config --includes` -Wall -c calcul.c -I. -o calcul.c.o -fPIC
#include <math.h>
#include "item.h"

int c_func(int i, item *subptr)
{
    subptr->i2 = 3.14159;

    return 0;
}
