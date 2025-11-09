program ComplexExpressionTest;

variabel
  a, b, c, d: integer;
  x, y: real;
  valid: boolean;

mulai
  a := 10;
  b := 20;
  c := 3;
  d := 5;
  x := (a + b) * c bagi (d - 2) + a mod c;
  y := a * b + c - d bagi 2;
  valid := (a > b) atau ((c < d) dan (x <> y));
  jika (a + b > c * d) dan tidak (x = y) maka
    writeln('Kondisi kompleks terpenuhi')
  selain-itu
    writeln('Kondisi tidak terpenuhi');
selesai.