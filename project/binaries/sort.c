/*  Bubble Sort with reversed array
    Build:  gcc -O2 -static -o sort.elf sort.c            */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define DEFAULT_SIZE 256

static void bubble_sort(int *a, int n)
{
    for (int i = 0; i < n - 1; ++i)
        for (int j = 0; j < n - i - 1; ++j)
            if (a[j] > a[j + 1])
            {
                int tmp = a[j];
                a[j] = a[j + 1];
                a[j + 1] = tmp;
            }
}

int main(int argc, char **argv)
{
    const int N = (argc > 1) ? atoi(argv[1]) : DEFAULT_SIZE;

    int *arr = malloc(N * sizeof(int));
    if (!arr)
    {
        perror("malloc");
        return 1;
    }

    for (int i = 0; i < N; ++i)
        arr[i] = N - i;

    for (int pass = 0; pass < 5; ++pass)
        bubble_sort(arr, N);

    printf("arr[0] = %d (N=%d)\n", arr[0], N);
    free(arr);
    return 0;
}
