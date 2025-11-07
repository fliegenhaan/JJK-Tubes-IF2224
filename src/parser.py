class Token:
    def __init__(self, tipe, nilai):
        self.tipe = tipe
        self.nilai = nilai

    def __repr__(self):
        return f"{self.tipe}({self.nilai})"

class NodePohonParsing:
    def __init__(self, nama, anak=None):
        self.nama = nama
        self.anak = anak if anak is not None else []

    def tambah_anak(self, node):
        self.anak.append(node)

    def cetak(self, level=0, prefix=""):
        hasil = ""
        if level == 0:
            hasil += f"{prefix}{self.nama}\n"
        else:
            hasil += f"{prefix}{self.nama}\n"

        jumlah_anak = len(self.anak)
        for i, anak in enumerate(self.anak):
            adalah_terakhir = (i == jumlah_anak - 1)
            if level == 0:
                prefix_baru = ""
            else:
                prefix_baru = prefix

            if adalah_terakhir:
                hasil += anak.cetak(level + 1, prefix_baru + "└── ")
            else:
                hasil += anak.cetak(level + 1, prefix_baru + "├── ")

        return hasil

class SyntaxError(Exception):
    def __init__(self, pesan):
        self.pesan = pesan
        super().__init__(self.pesan)

class Parser:
    def __init__(self, tokens):
        self.tokens = [Token(t[0], t[1]) for t in tokens]
        self.posisi = 0
        self.token_sekarang = self.tokens[0] if len(self.tokens) > 0 else None

    def ambil_token(self):
        return self.token_sekarang

    def maju(self):
        self.posisi += 1
        if self.posisi < len(self.tokens):
            self.token_sekarang = self.tokens[self.posisi]
        else:
            self.token_sekarang = None

    def cocokkan(self, tipe_token, nilai_token=None):
        if self.token_sekarang is None:
            raise SyntaxError(f"error: token tidak ditemukan, diharapkan {tipe_token}, posisi {self.posisi}")

        if self.token_sekarang.tipe != tipe_token:
            raise SyntaxError(f"error: token tidak sesuai, ditemukan {self.token_sekarang.tipe}({self.token_sekarang.nilai}) di posisi {self.posisi}, diharapkan {tipe_token}")

        if nilai_token is not None and self.token_sekarang.nilai != nilai_token:
            raise SyntaxError(f"error: nilai token tidak sesuai, ditemukan {self.token_sekarang.nilai} di posisi {self.posisi}, diharapkan {nilai_token}")

        node = NodePohonParsing(f"{self.token_sekarang.tipe}({self.token_sekarang.nilai})")
        self.maju()
        return node

    def parse_program(self):
        # program => program-header declaration-part compound-statement DOT
        node = NodePohonParsing("<program>")
        node.tambah_anak(self.parse_program_header())
        node.tambah_anak(self.parse_declaration_part())
        node.tambah_anak(self.parse_compound_statement())
        node.tambah_anak(self.cocokkan("DOT"))

        return node

    def parse_program_header(self):
        # program-header => KEYWORD(program) IDENTIFIER SEMICOLON
        node = NodePohonParsing("<program-header>")
        node.tambah_anak(self.cocokkan("KEYWORD", "program"))
        node.tambah_anak(self.cocokkan("IDENTIFIER"))
        node.tambah_anak(self.cocokkan("SEMICOLON"))

        return node

    def parse_declaration_part(self):
        # declaration-part => (const-declaration)* (type-declaration)* (var-declaration)* (subprogram-declaration)*
        node = NodePohonParsing("<declaration-part>")

        # parse const declarations
        while self.token_sekarang and self.token_sekarang.tipe == "KEYWORD" and self.token_sekarang.nilai == "konstanta":
            node.tambah_anak(self.parse_const_declaration())

        # parse type declarations
        while self.token_sekarang and self.token_sekarang.tipe == "KEYWORD" and self.token_sekarang.nilai == "tipe":
            node.tambah_anak(self.parse_type_declaration())

        # parse var declarations
        while self.token_sekarang and self.token_sekarang.tipe == "KEYWORD" and self.token_sekarang.nilai == "variabel":
            node.tambah_anak(self.parse_var_declaration())

        # parse subprogram declarations
        while self.token_sekarang and self.token_sekarang.tipe == "KEYWORD" and (self.token_sekarang.nilai == "prosedur" or self.token_sekarang.nilai == "fungsi"):
            node.tambah_anak(self.parse_subprogram_declaration())

        return node

    def parse_const_declaration(self):
        # const-declaration => KEYWORD(konstanta) (IDENTIFIER = value SEMICOLON)+
        node = NodePohonParsing("<const-declaration>")
        node.tambah_anak(self.cocokkan("KEYWORD", "konstanta"))

        # minimal satu deklarasi konstanta
        while True:
            node.tambah_anak(self.cocokkan("IDENTIFIER"))
            node.tambah_anak(self.cocokkan("RELATIONAL_OPERATOR", "="))

            # value bisa berupa NUMBER atau CHAR_LITERAL atau STRING_LITERAL atau IDENTIFIER
            if self.token_sekarang.tipe == "NUMBER":
                node.tambah_anak(self.cocokkan("NUMBER"))
            elif self.token_sekarang.tipe == "STRING_LITERAL":
                node.tambah_anak(self.cocokkan("STRING_LITERAL"))
            elif self.token_sekarang.tipe == "IDENTIFIER":
                node.tambah_anak(self.cocokkan("IDENTIFIER"))
            else:
                raise SyntaxError(f"error: nilai konstanta tidak valid")

            node.tambah_anak(self.cocokkan("SEMICOLON"))

            # cek apakah masih ada deklarasi konstanta lagi
            if not (self.token_sekarang and self.token_sekarang.tipe == "IDENTIFIER" and
                    self.posisi + 1 < len(self.tokens) and
                    self.tokens[self.posisi + 1].tipe == "RELATIONAL_OPERATOR" and
                    self.tokens[self.posisi + 1].nilai == "="):
                break

        return node

    def parse_type_declaration(self):
        # type-declaration => KEYWORD(tipe) (IDENTIFIER = type-definition SEMICOLON)+
        node = NodePohonParsing("<type-declaration>")
        node.tambah_anak(self.cocokkan("KEYWORD", "tipe"))

        while True:
            node.tambah_anak(self.cocokkan("IDENTIFIER"))
            node.tambah_anak(self.cocokkan("RELATIONAL_OPERATOR", "="))
            node.tambah_anak(self.parse_type())
            node.tambah_anak(self.cocokkan("SEMICOLON"))

            # cek apakah masih ada deklarasi tipe lagi
            if not (self.token_sekarang and self.token_sekarang.tipe == "IDENTIFIER" and
                    self.posisi + 1 < len(self.tokens) and
                    self.tokens[self.posisi + 1].tipe == "RELATIONAL_OPERATOR" and
                    self.tokens[self.posisi + 1].nilai == "="):
                break

        return node

    def parse_var_declaration(self):
        # var-declaration => KEYWORD(variabel) (identifier-list COLON type SEMICOLON)+
        node = NodePohonParsing("<var-declaration>")
        node.tambah_anak(self.cocokkan("KEYWORD", "variabel"))
        while True:
            node.tambah_anak(self.parse_identifier_list())
            node.tambah_anak(self.cocokkan("COLON"))
            node.tambah_anak(self.parse_type())
            node.tambah_anak(self.cocokkan("SEMICOLON"))

            # cek apakah masih ada deklarasi variabel lagi
            if not (self.token_sekarang and self.token_sekarang.tipe == "IDENTIFIER"):
                break

            # pastikan bukan awal dari compound statement
            if self.token_sekarang.tipe == "KEYWORD" and self.token_sekarang.nilai == "mulai":
                break

            # pastikan bukan awal dari subprogram declaration
            if self.token_sekarang.tipe == "KEYWORD" and (self.token_sekarang.nilai == "prosedur" or self.token_sekarang.nilai == "fungsi"):
                break

        return node

    def parse_identifier_list(self):
        # identifier-list => IDENTIFIER (COMMA IDENTIFIER)*
        node = NodePohonParsing("<identifier-list>")
        node.tambah_anak(self.cocokkan("IDENTIFIER"))
        while self.token_sekarang and self.token_sekarang.tipe == "COMMA":
            node.tambah_anak(self.cocokkan("COMMA"))
            node.tambah_anak(self.cocokkan("IDENTIFIER"))

        return node

    def parse_type(self):
        # type => KEYWORD(integer|real|boolean|char) atau array-type
        node = NodePohonParsing("<type>")
        if self.token_sekarang and self.token_sekarang.tipe == "KEYWORD":
            if self.token_sekarang.nilai in ["integer", "real", "boolean", "char"]:
                node.tambah_anak(self.cocokkan("KEYWORD"))
            elif self.token_sekarang.nilai == "larik":
                node.tambah_anak(self.parse_array_type())
            else:
                raise SyntaxError(f"error: tipe data tidak valid: {self.token_sekarang.nilai}")
        elif self.token_sekarang and self.token_sekarang.tipe == "IDENTIFIER":
            # custom type
            node.tambah_anak(self.cocokkan("IDENTIFIER"))
        else:
            raise SyntaxError(f"error: tipe data tidak valid")

        return node

    def parse_array_type(self):
        # array-type => KEYWORD(larik) LBRACKET range RBRACKET KEYWORD(dari) type
        node = NodePohonParsing("<array-type>")
        node.tambah_anak(self.cocokkan("KEYWORD", "larik"))
        node.tambah_anak(self.cocokkan("LBRACKET"))
        node.tambah_anak(self.parse_range())
        node.tambah_anak(self.cocokkan("RBRACKET"))
        node.tambah_anak(self.cocokkan("KEYWORD", "dari"))
        node.tambah_anak(self.parse_type())

        return node

    def parse_range(self):
        # range => expression RANGE_OPERATOR(..) expression
        node = NodePohonParsing("<range>")
        node.tambah_anak(self.parse_expression())
        node.tambah_anak(self.cocokkan("RANGE_OPERATOR"))
        node.tambah_anak(self.parse_expression())

        return node

    def parse_subprogram_declaration(self):
        # subprogram-declaration => procedure-declaration atau function-declaration
        node = NodePohonParsing("<subprogram-declaration>")
        if self.token_sekarang.nilai == "prosedur":
            node.tambah_anak(self.parse_procedure_declaration())
        elif self.token_sekarang.nilai == "fungsi":
            node.tambah_anak(self.parse_function_declaration())
        else:
            raise SyntaxError(f"error: deklarasi subprogram tidak valid")

        return node

    def parse_procedure_declaration(self):
        # procedure-declaration => KEYWORD(prosedur) IDENTIFIER (formal-parameter-list)? SEMICOLON block SEMICOLON
        node = NodePohonParsing("<procedure-declaration>")
        node.tambah_anak(self.cocokkan("KEYWORD", "prosedur"))
        node.tambah_anak(self.cocokkan("IDENTIFIER"))
        if self.token_sekarang and self.token_sekarang.tipe == "LPARENTHESIS":
            node.tambah_anak(self.parse_formal_parameter_list())

        node.tambah_anak(self.cocokkan("SEMICOLON"))
        node.tambah_anak(self.parse_block())
        node.tambah_anak(self.cocokkan("SEMICOLON"))

        return node

    def parse_function_declaration(self):
        # function-declaration => KEYWORD(fungsi) IDENTIFIER (formal-parameter-list)? COLON type SEMICOLON block SEMICOLON
        node = NodePohonParsing("<function-declaration>")
        node.tambah_anak(self.cocokkan("KEYWORD", "fungsi"))
        node.tambah_anak(self.cocokkan("IDENTIFIER"))
        if self.token_sekarang and self.token_sekarang.tipe == "LPARENTHESIS":
            node.tambah_anak(self.parse_formal_parameter_list())
        node.tambah_anak(self.cocokkan("COLON"))
        node.tambah_anak(self.parse_type())
        node.tambah_anak(self.cocokkan("SEMICOLON"))
        node.tambah_anak(self.parse_block())
        node.tambah_anak(self.cocokkan("SEMICOLON"))

        return node

    def parse_formal_parameter_list(self):
        # formal-parameter-list => LPARENTHESIS parameter-group (SEMICOLON parameter-group)* RPARENTHESIS
        node = NodePohonParsing("<formal-parameter-list>")
        node.tambah_anak(self.cocokkan("LPARENTHESIS"))
        node.tambah_anak(self.parse_parameter_group())

        while self.token_sekarang and self.token_sekarang.tipe == "SEMICOLON":
            # simpan posisi untuk backtrack
            posisi_simpan = self.posisi
            self.maju()

            # cek apakah ada parameter group berikutnya atau sudah closing parenthesis
            if self.token_sekarang and self.token_sekarang.tipe == "RPARENTHESIS":
                # backtrack
                self.posisi = posisi_simpan
                self.token_sekarang = self.tokens[self.posisi]
                break
            else:
                # backtrack lalu parse sebagai bagian dari parameter group
                self.posisi = posisi_simpan
                self.token_sekarang = self.tokens[self.posisi]
                node.tambah_anak(self.cocokkan("SEMICOLON"))
                node.tambah_anak(self.parse_parameter_group())
        node.tambah_anak(self.cocokkan("RPARENTHESIS"))

        return node

    def parse_parameter_group(self):
        # parameter-group => (KEYWORD(variabel))? identifier-list COLON type
        node = NodePohonParsing("<parameter-group>")
        if self.token_sekarang and self.token_sekarang.tipe == "KEYWORD" and self.token_sekarang.nilai == "variabel":
            node.tambah_anak(self.cocokkan("KEYWORD", "variabel"))
        node.tambah_anak(self.parse_identifier_list())
        node.tambah_anak(self.cocokkan("COLON"))
        node.tambah_anak(self.parse_type())

        return node

    def parse_block(self):
        # block => declaration-part compound-statement
        node = NodePohonParsing("<block>")
        node.tambah_anak(self.parse_declaration_part())
        node.tambah_anak(self.parse_compound_statement())

        return node

    def parse_compound_statement(self):
        # compound-statement => KEYWORD(mulai) statement-list KEYWORD(selesai)
        node = NodePohonParsing("<compound-statement>")
        node.tambah_anak(self.cocokkan("KEYWORD", "mulai"))
        node.tambah_anak(self.parse_statement_list())
        node.tambah_anak(self.cocokkan("KEYWORD", "selesai"))

        return node

    def parse_statement_list(self):
        # statement-list => statement (SEMICOLON statement)*
        # trailing semicolon sebelum selesai diizinkan dengan empty statement
        node = NodePohonParsing("<statement-list>")
        node.tambah_anak(self.parse_statement())

        while self.token_sekarang and self.token_sekarang.tipe == "SEMICOLON":
            node.tambah_anak(self.cocokkan("SEMICOLON"))

            # cek apakah ada statement berikutnya atau sudah end
            if self.token_sekarang and (self.token_sekarang.tipe == "KEYWORD" and self.token_sekarang.nilai == "selesai"):
                # tambahkan empty statement untuk trailing semicolon
                node.tambah_anak(NodePohonParsing("<empty-statement>"))
                break
            elif self.token_sekarang:
                # ada statement berikutnya
                node.tambah_anak(self.parse_statement())
            else:
                # end of tokens
                break

        return node

    def parse_statement(self):
        # statement bisa berupa assignment, if, while, for, procedure-call, compound, repeat, atau empty
        if not self.token_sekarang:
            return NodePohonParsing("<empty-statement>")
        if self.token_sekarang.tipe == "KEYWORD":
            if self.token_sekarang.nilai == "jika":
                return self.parse_if_statement()
            elif self.token_sekarang.nilai == "selama":
                return self.parse_while_statement()
            elif self.token_sekarang.nilai == "untuk":
                return self.parse_for_statement()
            elif self.token_sekarang.nilai == "mulai":
                return self.parse_compound_statement()
            elif self.token_sekarang.nilai == "ulangi":
                return self.parse_repeat_statement()
            elif self.token_sekarang.nilai == "kasus":
                return self.parse_case_statement()

        if self.token_sekarang.tipe == "IDENTIFIER":
            # bisa assignment atau procedure call
            # cek token berikutnya
            if self.posisi + 1 < len(self.tokens):
                token_berikut = self.tokens[self.posisi + 1]
                if token_berikut.tipe == "ASSIGN_OPERATOR":
                    return self.parse_assignment_statement()
                elif token_berikut.tipe == "LPARENTHESIS" or token_berikut.tipe == "SEMICOLON" or (token_berikut.tipe == "KEYWORD" and token_berikut.nilai == "selesai"):
                    return self.parse_procedure_call()
            else:
                return self.parse_procedure_call()

        # empty statement
        return NodePohonParsing("<empty-statement>")

    def parse_assignment_statement(self):
        # assignment-statement => IDENTIFIER ASSIGN_OPERATOR expression
        node = NodePohonParsing("<assignment-statement>")

        node.tambah_anak(self.cocokkan("IDENTIFIER"))
        node.tambah_anak(self.cocokkan("ASSIGN_OPERATOR"))
        node.tambah_anak(self.parse_expression())

        return node

    def parse_if_statement(self):
        # if-statement => KEYWORD(jika) expression KEYWORD(maka) statement (KEYWORD(selain-itu) statement)?
        node = NodePohonParsing("<if-statement>")
        node.tambah_anak(self.cocokkan("KEYWORD", "jika"))
        node.tambah_anak(self.parse_expression())
        node.tambah_anak(self.cocokkan("KEYWORD", "maka"))
        node.tambah_anak(self.parse_statement())
        if self.token_sekarang and self.token_sekarang.tipe == "KEYWORD" and self.token_sekarang.nilai == "selain-itu":
            node.tambah_anak(self.cocokkan("KEYWORD", "selain-itu"))
            node.tambah_anak(self.parse_statement())

        return node

    def parse_while_statement(self):
        # while-statement => KEYWORD(selama) expression KEYWORD(lakukan) statement
        node = NodePohonParsing("<while-statement>")
        node.tambah_anak(self.cocokkan("KEYWORD", "selama"))
        node.tambah_anak(self.parse_expression())
        node.tambah_anak(self.cocokkan("KEYWORD", "lakukan"))
        node.tambah_anak(self.parse_statement())

        return node

    def parse_for_statement(self):
        # for-statement => KEYWORD(untuk) IDENTIFIER ASSIGN_OPERATOR expression (KEYWORD(ke)|KEYWORD(turun-ke)) expression KEYWORD(lakukan) statement
        node = NodePohonParsing("<for-statement>")
        node.tambah_anak(self.cocokkan("KEYWORD", "untuk"))
        node.tambah_anak(self.cocokkan("IDENTIFIER"))
        node.tambah_anak(self.cocokkan("ASSIGN_OPERATOR"))
        node.tambah_anak(self.parse_expression())

        if self.token_sekarang and self.token_sekarang.tipe == "KEYWORD":
            if self.token_sekarang.nilai == "ke":
                node.tambah_anak(self.cocokkan("KEYWORD", "ke"))
            elif self.token_sekarang.nilai == "turun-ke":
                node.tambah_anak(self.cocokkan("KEYWORD", "turun-ke"))
            else:
                raise SyntaxError(f"error: diharapkan 'ke' atau 'turun-ke'")
        else:
            raise SyntaxError(f"error: diharapkan 'ke' atau 'turun-ke'")

        node.tambah_anak(self.parse_expression())
        node.tambah_anak(self.cocokkan("KEYWORD", "lakukan"))
        node.tambah_anak(self.parse_statement())

        return node

    def parse_repeat_statement(self):
        # repeat-statement => KEYWORD(ulangi) statement-list KEYWORD(sampai) expression
        node = NodePohonParsing("<repeat-statement>")

        node.tambah_anak(self.cocokkan("KEYWORD", "ulangi"))
        node.tambah_anak(self.parse_statement_list())
        node.tambah_anak(self.cocokkan("KEYWORD", "sampai"))
        node.tambah_anak(self.parse_expression())

        return node

    def parse_case_statement(self):
        # case-statement => KEYWORD(kasus) expression KEYWORD(dari) case-list KEYWORD(selesai)
        node = NodePohonParsing("<case-statement>")
        node.tambah_anak(self.cocokkan("KEYWORD", "kasus"))
        node.tambah_anak(self.parse_expression())
        node.tambah_anak(self.cocokkan("KEYWORD", "dari"))

        # case-list minimal satu
        while True:
            # case-element => constant-list COLON statement
            node.tambah_anak(self.parse_expression())
            node.tambah_anak(self.cocokkan("COLON"))
            node.tambah_anak(self.parse_statement())

            # cek apakah ada semicolon untuk case berikutnya
            if self.token_sekarang and self.token_sekarang.tipe == "SEMICOLON":
                node.tambah_anak(self.cocokkan("SEMICOLON"))

                # setelah semicolon, cek apakah selesai atau ada case lagi
                if self.token_sekarang and self.token_sekarang.tipe == "KEYWORD" and self.token_sekarang.nilai == "selesai":
                    break
                # jika bukan selesai, lanjut loop untuk parse case element berikutnya
            else:
                break

        node.tambah_anak(self.cocokkan("KEYWORD", "selesai"))

        return node

    def parse_procedure_call(self):
        # procedure-call => IDENTIFIER (LPARENTHESIS parameter-list RPARENTHESIS)?
        node = NodePohonParsing("<procedure-call>")
        node.tambah_anak(self.cocokkan("IDENTIFIER"))

        if self.token_sekarang and self.token_sekarang.tipe == "LPARENTHESIS":
            node.tambah_anak(self.cocokkan("LPARENTHESIS"))
            node.tambah_anak(self.parse_parameter_list())
            node.tambah_anak(self.cocokkan("RPARENTHESIS"))

        return node

    def parse_parameter_list(self):
        # parameter-list => expression (COMMA expression)*
        node = NodePohonParsing("<parameter-list>")
        node.tambah_anak(self.parse_expression())
        while self.token_sekarang and self.token_sekarang.tipe == "COMMA":
            node.tambah_anak(self.cocokkan("COMMA"))
            node.tambah_anak(self.parse_expression())

        return node

    def parse_expression(self):
        # expression => simple-expression (relational-operator simple-expression)?
        node = NodePohonParsing("<expression>")
        node.tambah_anak(self.parse_simple_expression())
        if self.token_sekarang and self.token_sekarang.tipe == "RELATIONAL_OPERATOR":
            node.tambah_anak(self.cocokkan("RELATIONAL_OPERATOR"))
            node.tambah_anak(self.parse_simple_expression())

        return node

    def parse_simple_expression(self):
        # simple-expression => (ARITHMETIC_OPERATOR(+|-))? term (additive-operator term)*
        node = NodePohonParsing("<simple-expression>")

        if self.token_sekarang and self.token_sekarang.tipe == "ARITHMETIC_OPERATOR" and self.token_sekarang.nilai in ["+", "-"]:
            node.tambah_anak(self.cocokkan("ARITHMETIC_OPERATOR"))

        node.tambah_anak(self.parse_term())
        while self.token_sekarang and (
            (self.token_sekarang.tipe == "ARITHMETIC_OPERATOR" and self.token_sekarang.nilai in ["+", "-"]) or
            (self.token_sekarang.tipe == "LOGICAL_OPERATOR" and self.token_sekarang.nilai == "atau")
        ):
            if self.token_sekarang.tipe == "ARITHMETIC_OPERATOR":
                node.tambah_anak(self.cocokkan("ARITHMETIC_OPERATOR"))
            else:
                node.tambah_anak(self.cocokkan("LOGICAL_OPERATOR"))
            node.tambah_anak(self.parse_term())
        return node

    def parse_term(self):
        # term => factor (multiplicative-operator factor)*
        node = NodePohonParsing("<term>")
        node.tambah_anak(self.parse_factor())
        while self.token_sekarang and (
            (self.token_sekarang.tipe == "ARITHMETIC_OPERATOR" and self.token_sekarang.nilai in ["*", "/", "bagi", "mod"]) or
            (self.token_sekarang.tipe == "LOGICAL_OPERATOR" and self.token_sekarang.nilai == "dan")
        ):
            if self.token_sekarang.tipe == "ARITHMETIC_OPERATOR":
                node.tambah_anak(self.cocokkan("ARITHMETIC_OPERATOR"))
            else:
                node.tambah_anak(self.cocokkan("LOGICAL_OPERATOR"))

            node.tambah_anak(self.parse_factor())

        return node

    def parse_factor(self):
        # factor => IDENTIFIER | NUMBER | STRING_LITERAL | (LPARENTHESIS expression RPARENTHESIS) | LOGICAL_OPERATOR(tidak) factor | function-call
        node = NodePohonParsing("<factor>")
        if not self.token_sekarang:
            raise SyntaxError(f"error: token tidak ditemukan")
        if self.token_sekarang.tipe == "NUMBER":
            node.tambah_anak(self.cocokkan("NUMBER"))
        elif self.token_sekarang.tipe == "STRING_LITERAL":
            node.tambah_anak(self.cocokkan("STRING_LITERAL"))
        elif self.token_sekarang.tipe == "LPARENTHESIS":
            node.tambah_anak(self.cocokkan("LPARENTHESIS"))
            node.tambah_anak(self.parse_expression())
            node.tambah_anak(self.cocokkan("RPARENTHESIS"))
        elif self.token_sekarang.tipe == "LOGICAL_OPERATOR" and self.token_sekarang.nilai == "tidak":
            node.tambah_anak(self.cocokkan("LOGICAL_OPERATOR"))
            node.tambah_anak(self.parse_factor())
        elif self.token_sekarang.tipe == "IDENTIFIER":
            # bisa identifier biasa atau function call
            if self.posisi + 1 < len(self.tokens) and self.tokens[self.posisi + 1].tipe == "LPARENTHESIS":
                node.tambah_anak(self.parse_function_call())
            else:
                node.tambah_anak(self.cocokkan("IDENTIFIER"))
        else:
            raise SyntaxError(f"error: faktor tidak valid, ditemukan {self.token_sekarang.tipe}({self.token_sekarang.nilai})")

        return node

    def parse_function_call(self):
        # function-call => IDENTIFIER LPARENTHESIS (parameter-list)? RPARENTHESIS
        node = NodePohonParsing("<function-call>")
        node.tambah_anak(self.cocokkan("IDENTIFIER"))
        node.tambah_anak(self.cocokkan("LPARENTHESIS"))

        # parameter list opsional
        if self.token_sekarang and self.token_sekarang.tipe != "RPARENTHESIS":
            node.tambah_anak(self.parse_parameter_list())

        node.tambah_anak(self.cocokkan("RPARENTHESIS"))

        return node

    def parse(self):
        try:
            pohon = self.parse_program()
            if self.token_sekarang is not None:
                raise SyntaxError(f"error: masih ada token yang tersisa setelah parsing selesai")
            return pohon
        except SyntaxError as e:
            raise e