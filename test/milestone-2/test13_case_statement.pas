program CaseStatementTest;

variabel
  pilihan: integer;
  hasil: integer;

mulai
  pilihan := 2;
  hasil := 0;

  kasus pilihan dari
    1: hasil := 10;
    2: hasil := 20;
    3: mulai
         hasil := 30;
         writeln('Pilihan tiga dipilih');
       selesai;
    4: hasil := 40;
    5: hasil := 50;
  selesai;
  writeln('Hasil: ', hasil);
selesai.