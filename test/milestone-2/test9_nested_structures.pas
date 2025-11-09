program NestedTest;

variabel
  x, y, z: integer;
  hasil: integer;

mulai
  x := 5;
  y := 10;

  jika x > 0 maka
    mulai
      jika y > x maka
        mulai
          z := x + y;
          jika z > 10 maka
            hasil := 1
          selain-itu
            hasil := 0;
        selesai
      selain-itu
        hasil := -1;
    selesai
  selain-itu
    hasil := -2;
  writeln('Hasil: ', hasil);
selesai.