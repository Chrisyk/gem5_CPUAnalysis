#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define DEFAULT_N 200

int main(int argc, char **argv)
{
    const long N = (argc > 1) ? atol(argv[1]) : DEFAULT_N;
    long i, sum = 0;

    srand(0);

    for (i = 0; i < N; i++)
    {
        if (rand() & 1)
            sum++;
    }

    printf("sum = %ld (N = %ld)\n", sum, N);
    return 0;
}
