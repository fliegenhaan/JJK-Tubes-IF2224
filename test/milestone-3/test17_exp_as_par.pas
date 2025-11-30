program test_var_parameter;

variabel
    a: integer;

prosedur inc(variabel x: integer);
mulai
    x := x + 1;
selesai;


mulai
    inc(a + 1);  
selesai.

