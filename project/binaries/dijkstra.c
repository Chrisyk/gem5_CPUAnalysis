/*  Single-source Dijkstra with a binary heap.
    Build:  gcc -O2 -static -o dijkstra.elf dijkstra.c            */

#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <stdbool.h>

#define INF 1000000000
#define V_DEFAULT 256

typedef struct
{
    int v, dist;
} Node;

typedef struct
{
    Node *a;
    int size, cap;
} MinHeap;

static void heap_init(MinHeap *h, int cap)
{
    h->a = malloc(cap * sizeof(Node));
    h->size = 0;
    h->cap = cap;
}

static void heap_push(MinHeap *h, Node x)
{
    /* grow if full */
    if (h->size == h->cap)
    {
        h->cap = h->cap ? h->cap * 2 : 4;
        h->a = realloc(h->a, h->cap * sizeof(Node));
        if (!h->a)
        {
            perror("realloc");
            exit(EXIT_FAILURE);
        }
    }

    int i = h->size++;
    while (i && x.dist < h->a[(i - 1) / 2].dist)
    {
        h->a[i] = h->a[(i - 1) / 2];
        i = (i - 1) / 2;
    }
    h->a[i] = x;
}

static Node heap_pop(MinHeap *h)
{
    Node min = h->a[0];

    /* remove top */
    if (--h->size == 0) /* heap is now empty → return */
        return min;

    Node last = h->a[h->size]; /* safe: size > 0 */

    /* sift-down */
    int i = 0;
    while (i * 2 + 1 < h->size)
    {
        int nxt = i * 2 + 1;
        if (nxt + 1 < h->size && h->a[nxt + 1].dist < h->a[nxt].dist)
            ++nxt;
        if (last.dist <= h->a[nxt].dist)
            break;
        h->a[i] = h->a[nxt];
        i = nxt;
    }
    h->a[i] = last;
    return min;
}

static void dijkstra(int **g, int src, int n)
{
    int *dist = malloc(n * sizeof(int));
    bool *done = calloc(n, sizeof(bool));
    for (int i = 0; i < n; ++i)
        dist[i] = INF;
    dist[src] = 0;

    MinHeap pq;
    heap_init(&pq, n);
    heap_push(&pq, (Node){src, 0});

    while (pq.size)
    {
        Node cur = heap_pop(&pq);
        int u = cur.v;
        if (done[u])
            continue;
        done[u] = true;

        for (int v = 0; v < n; ++v)
        {
            int w = g[u][v];
            if (w && dist[u] + w < dist[v])
            {
                dist[v] = dist[u] + w;
                heap_push(&pq, (Node){v, dist[v]});
            }
        }
    }

    printf("distance(src→V-1) = %d (V=%d)\n", dist[n - 1], n);
    free(dist);
    free(done);
    free(pq.a);
}

int main(int argc, char **argv)
{
    const int N = (argc > 1) ? atoi(argv[1]) : V_DEFAULT;

    /* build a deterministic dense graph */
    int **G = malloc(N * sizeof(int *));
    for (int i = 0; i < N; ++i)
    {
        G[i] = malloc(N * sizeof(int));
        for (int j = 0; j < N; ++j)
            G[i][j] = (i == j) ? 0 : ((i * 131 + j * 31) % 23 + 1);
    }

    dijkstra(G, 0, N); /* one source only */

    for (int i = 0; i < N; ++i)
        free(G[i]);
    free(G);
    return 0;
}
