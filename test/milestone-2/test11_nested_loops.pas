program NestedLoopsTest;

variabel
  i, j, k: integer;
  total: integer;

mulai
  total := 0;

  untuk i := 1 ke 3 lakukan
    mulai
      untuk j := 1 ke 2 lakukan
        mulai
          k := 0;
          selama k < i lakukan
            mulai
              total := total + 1;
              k := k + 1;
            selesai;
          writeln('i=', i, ' j=', j, ' total=', total);
        selesai;
    selesai;

  writeln('Total akhir: ', total);
selesai.
