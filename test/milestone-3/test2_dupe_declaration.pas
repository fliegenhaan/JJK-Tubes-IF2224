program test0;

konstanta 
    ten = 10; 
    plus = '+';

tipe 
    row = larik [1..ten] dari real;
    complex = rekaman 
        re, im: real 
    selesai;

variabel 
    i, j: integer;
    p: boolean;
    z: complex;
    i: real;               
    matrix: larik [-3..+3] dari row;
    pattern: larik [1..5] dari larik [2..5] dari char;

prosedur dummy(variabel i: integer; variabel z: complex);
variabel 
    u, v: row;
    h1, h2: rekaman 
        c: complex; 
        r: row 
    selesai;

    fungsi null(x, y: real; z: complex): boolean;
    variabel 
        a: larik ['a'..'z'] dari complex;
        u: char;
    mulai
        selama x < y lakukan 
            x := x + 2;
        null := x = y
    selesai;

mulai
    p := null(h1.c.re, h2.c.im, z)
selesai;

mulai
    i := 85; 
    j := 51;
    ulangi
        jika i > j maka 
            i := i - j 
        selain-itu 
            j := j - i
    sampai i = j;
    writeln(i)
selesai.

