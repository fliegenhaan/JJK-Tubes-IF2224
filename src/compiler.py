import sys
import os
from lexer import load_dfa_rules, tokenize, print_tokens, load_tokens_from_file
from parser import Parser, SyntaxError

# set encoding untuk output unicode di windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    # cek argumen
    lexer_only = False
    source_file = None

    if len(sys.argv) < 2:
        print("Penggunaan: python compiler.py <input_file> [--lexer-only]")
        print("  <input_file> : file .pas (source code) atau .txt (hasil tokenisasi)")
        print("  --lexer-only : hanya melakukan lexical analysis (hanya untuk .pas)")
        sys.exit(1)

    # parse argumen
    for arg in sys.argv[1:]:
        if arg == "--lexer-only":
            lexer_only = True
        elif arg.endswith(".pas") or arg.endswith(".txt"):
            source_file = arg

    if not source_file:
        print("Error: file .pas atau .txt tidak ditemukan dalam argumen")
        sys.exit(1)

    # deteksi otomatis milestone-1
    if "milestone-1" in source_file:
        lexer_only = True

    # cek tipe file input
    is_txt_input = source_file.endswith(".txt")

    if is_txt_input:
        # mode 1: input dari file .txt (hasil tokenisasi)
        print("Parse dari File Tokenisasi (.txt)")
        print()
        print("Tahap: Loading Tokens")
        tokens = load_tokens_from_file(source_file)
        print(f"Berhasil membaca {len(tokens)} token dari {source_file}")
        print()

        # langsung ke syntax analysis
        print("Tahap: Syntax Analysis")
        try:
            parser = Parser(tokens)
            pohon_parsing = parser.parse()
            print("Parsing berhasil!")
            print()
            print("Parse Tree")
            print(pohon_parsing.cetak())

        except SyntaxError as e:
            print(f"Syntax Error: {e.pesan}")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)

    else:
        # mode 2: input dari file .pas (source code)
        print("Compile dari Source Code (.pas)")
        print()

        dfa = load_dfa_rules()
        with open(source_file, "r", encoding="utf-8") as f:
            source_code = f.read()

        # tahap lexical analysis
        print("Tahap: Lexical Analysis")
        return_code, tokens = tokenize(source_code, dfa)
        if return_code == 1:
            print("Error: token tidak valid ditemukan")
            sys.exit(1)
        print(f"Berhasil menghasilkan {len(tokens)} token")

        # simpan hasil tokenisasi ke file .txt
        print_tokens(tokens, source_file)
        print()

        # jika mode lexer-only, berhenti di sini
        if lexer_only:
            print("Mode: Lexical Analysis Only")
            return

        # tahap syntax analysis
        print("Tahap: Syntax Analysis")
        try:
            parser = Parser(tokens)
            pohon_parsing = parser.parse()
            print("Parsing berhasil!")
            print()
            print("Parse Tree")
            print(pohon_parsing.cetak())

        except SyntaxError as e:
            print(f"Syntax Error: {e.pesan}")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    main()