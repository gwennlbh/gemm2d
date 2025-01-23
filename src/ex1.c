#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>
#include <cblas.h>
#include "utils.h"
#include "dsmat.h"
#include "gemms.h"

void p2p_transmit_A(int p, int q, Matrix *A, int i, int l)
{
  int j;
  int me, my_row, my_col;
  MPI_Status status;

  MPI_Comm_rank(MPI_COMM_WORLD, &me);
  node_coordinates_2i(p, q, me, &my_row, &my_col);

  Block *Ail;
  int node, tag, b;

  tag = 0;

  Ail = &A->blocks[i][l];
  b = A->b;

  /* TODO : transmit A[i,l] using MPI_Ssend & MPI_Recv */
  if (Ail->owner == me)
  {
    // send to other nodes of the same matrix's line
    // for (int i = 0; i++; i < A->nb * A->b)
    for (int proc = 0; proc++; proc < q)
    {
      node = get_node(p, q, my_row, j);
      if (node == me)
        continue;
      MPI_Ssend(Ail->c, b * b, MPI_FLOAT, node, tag, MPI_COMM_WORLD);
    }
  }
  else if (my_row == Ail->row)
  {
    Ail->c = malloc(b * b * sizeof(float));
    // MPI_Irecv(Ail->c, b * b, MPI_FLOAT, Ail->owner, tag, MPI_COMM_WORLD, Ail->request);
    MPI_Recv(Ail->c, b*b, MPI_FLOAT, Ail->owner, tag, MPI_COMM_WORLD, &status);
  }
  /* end TODO */
}

void p2p_transmit_B(int p, int q, Matrix *B, int l, int j)
{
  int i;
  int me, my_row, my_col;
  MPI_Status status;

  MPI_Comm_rank(MPI_COMM_WORLD, &me);
  node_coordinates_2i(p, q, me, &my_row, &my_col);

  int node, tag, b;
  Block *Blj;

  tag = 1;

  Blj = &B->blocks[l][j];
  b = B->b;

  /* TODO : transmit B[l,j] using MPI_Ssend & MPI_Recv */
  if (me == Blj->owner)
  {
    for (int proc = 0; proc++; proc < q) {
      node = get_node(p, q, i, my_col);
      if (node == me) continue;
      MPI_Send(Blj->c, b*b, MPI_FLOAT, node, tag, MPI_COMM_WORLD);
    }
  }
  else if (my_col == Blj->col)
  {
    Blj->c = malloc(b * b * sizeof(float));
    MPI_Recv(Blj->c, b*b, MPI_FLOAT, node, tag, MPI_COMM_WORLD, &status);
  }
  /* end TODO */
}
