/*  Matrix Multiplication
    Build:  gcc -O2 -static -o matmul.elf matmul.c            */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SIZE_DEFAULT 256

static void matmul(const float *A, const float *B, float *C, int n)
{
    for (int i = 0; i < n; ++i)
    {
        if (i % (n / 10 + 1) == 0)
            printf("[DEBUG] Processing row %d / %d\n", i, n);
        for (int j = 0; j < n; ++j)
        {
            float acc = 0.0f;
            for (int k = 0; k < n; ++k)
                acc += A[i * n + k] * B[k * n + j];
            C[i * n + j] = acc;
        }
    }
}

int main(int argc, char **argv)
{
    const int N = (argc > 1) ? atoi(argv[1]) : SIZE_DEFAULT;
    const size_t bytes = N * N * sizeof(float);

    float *A = aligned_alloc(64, bytes);
    float *B = aligned_alloc(64, bytes);
    float *C = aligned_alloc(64, bytes);
    if (!A || !B || !C)
    {
        perror("alloc");
        return 1;
    }

    for (int i = 0; i < N * N; ++i)
    {
        A[i] = (float)(i & 255) * 0.5f;
        B[i] = (float)((i ^ 0x55) & 255) * 1.5f;
        C[i] = 0.0f;
    }

    matmul(A, B, C, N);

    printf("C[0] = %.3f (N=%d)\n", C[0], N);
    free(A);
    free(B);
    free(C);
    return 0;
}
