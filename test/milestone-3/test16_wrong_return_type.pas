program test_wrong_return_type;

variabel
    b: boolean;

fungsi isPositive(a: integer): boolean;
mulai
    isPositive := a + 10;  
selesai;



mulai
    b := isPositive(5);
selesai.
