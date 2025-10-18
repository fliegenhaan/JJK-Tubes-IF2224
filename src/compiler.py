import sys
import os
from lexer import load_dfa_rules, tokenize, print_tokens

def main():
    if len(sys.argv) != 2:
        print("Usage: python compiler.py <program.pas>")
        sys.exit(1)

    source_file = sys.argv[1]
    dfa = load_dfa_rules()

    with open(source_file, "r") as f:
        source_code = f.read()

    return_code, tokens = tokenize(source_code, dfa)

    if (return_code == 1):
        print("Error: invalid token found")
        sys.exit(1)

    print_tokens(tokens, source_file) 

if __name__ == "__main__":
    main()

