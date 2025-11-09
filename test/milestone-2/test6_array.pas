program ArrayTest;

variabel
  angka: larik[1..5] dari integer;
  i: integer;

mulai
  untuk i := 1 ke 5 lakukan
    angka := i * 2;
  untuk i := 1 ke 5 lakukan
    writeln(angka);
selesai.