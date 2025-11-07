program FunctionTest;

variabel
  hasil: integer;

fungsi tambah(a, b: integer): integer;
mulai
  tambah := a + b;
selesai;

mulai
  hasil := tambah(5, 10);
  writeln('Hasil: ', hasil);
selesai.
