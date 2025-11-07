program MultipleSubprogramsTest;

variabel
  hasil, a, b: integer;

prosedur tukar(x, y: integer);
variabel
  temp: integer;
mulai
  temp := x;
  x := y;
  y := temp;
selesai;

fungsi tambah(x, y: integer): integer;
mulai
  tambah := x + y;
selesai;

fungsi kali(x, y: integer): integer;
variabel
  i, akumulasi: integer;
mulai
  akumulasi := 0;
  untuk i := 1 ke y lakukan
    akumulasi := akumulasi + x;
  kali := akumulasi;
selesai;

prosedur cetak_hasil(nilai: integer);
mulai
  writeln('Hasil perhitungan: ', nilai);
selesai;

mulai
  a := 5;
  b := 3;

  hasil := tambah(a, b);
  cetak_hasil(hasil);

  hasil := kali(a, b);
  cetak_hasil(hasil);

  tukar(a, b);
  writeln('a=', a, ' b=', b);
selesai.
