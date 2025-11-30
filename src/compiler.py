import sys
import io

from lexer import load_dfa_rules, tokenize, print_tokens, load_tokens_from_file
from parser2 import ProgramNode as ParserRoot, Token, ParseErrorContext, Terminal
from ast_transformer import ASTTransformer
from ast_nodes import * 
from ast_analyzer import SemanticAnalyzer

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def _get_readable_value(obj):
    if isinstance(obj, (Token, Terminal)):
        if obj.nilai is not None:
            return str(obj.nilai)
        return str(obj.tipe)
    return str(obj)

def _print_stage_header(title):
    print("\n" + "="*50)
    print(f"Tahap: {title}")
    print("="*50)

def _print_syntax_error(tokens, error_ctx):
    _print_stage_header("SYNTAX ERROR FOUND")
    
    if error_ctx.max_index > -1:
        idx = error_ctx.max_index
        
        start_context = max(0, idx - 4)
        end_context = min(len(tokens), idx + 4)
        
        pre_error_tokens = tokens[start_context:idx]
        error_token = tokens[idx] if idx < len(tokens) else None
        post_error_tokens = tokens[idx+1:end_context]
        
        prefix_str = " ".join([_get_readable_value(t) for t in pre_error_tokens])
        error_str = _get_readable_value(error_token) if error_token else "EOF"
        suffix_str = " ".join([_get_readable_value(t) for t in post_error_tokens])
        
        start_dots = "... " if start_context > 0 else ""
        end_dots = " ..." if end_context < len(tokens) else ""
        
        full_context_line = f"{start_dots}{prefix_str} {error_str} {suffix_str}{end_dots}"
        
        caret_offset = len(start_dots) + len(prefix_str) + 1
        if not prefix_str: caret_offset -= 1

        print(f"Error Location (Index): {idx}")
        print(f"Context: {full_context_line}")
        print(" " * (9 + caret_offset) + "^ ERROR HERE")
        print("-" * 50)
        
        expected_val = _get_readable_value(error_ctx.expected)
        found_val = _get_readable_value(error_ctx.found)
        
        if isinstance(error_ctx.expected, Terminal) and error_ctx.expected.nilai is None:
            expected_val = f"Any {error_ctx.expected.tipe}"

        print(f"Expected : {expected_val}")
        print(f"Found    : {found_val}")
        print(f"Rule     : {error_ctx.rule_name}")
    else:
        print("Unknown Error (Parser did not start).")
    
    sys.exit(1)

def run_syntax_analysis(tokens):
    _print_stage_header("Syntax Analysis (Parse Tree / CST)")
    
    parser = ParserRoot()
    error_ctx = ParseErrorContext()
    
    success, end_idx = parser.parse(tokens, 0, error_ctx)

    if success:
        if end_idx == len(tokens):
            print("Parsing berhasil!")
            print("-" * 30)
            print("Concrete Syntax Tree (CST) Structure:")
            print(parser.cetak())
            return parser
        else:
            print(f"Parsing Incomplete. Berhenti di index {end_idx} dari {len(tokens)} token.")
            print(f"Token selanjutnya yang tidak diharapkan: {_get_readable_value(tokens[end_idx])}")
            sys.exit(1)
    else:
        _print_syntax_error(tokens, error_ctx)
        return None 


def run_ast_generation(parse_tree_root):
    _print_stage_header("AST Generation (Abstract Syntax Tree)")

    try:
        transformer = ASTTransformer()
        ast_root = transformer.transform(parse_tree_root)

        print("AST Structure:")
        print("-" * 30)
        print(ast_root)
        
        return ast_root

    except Exception as e:
        print(f"Error during AST Transformation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_semantic_analysis(ast_root):
    _print_stage_header("Semantic Analysis (Symbol Tables)")
    try:
        analyzer = SemanticAnalyzer()
        
        analyzer.analyze(ast_root)
        
        analyzer.print_tables()
        
    except Exception as e:
        print(f"Error during Semantic Analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    lexer_only = False
    source_file = None

    if len(sys.argv) < 2:
        print("Penggunaan: python compiler.py <input_file> [--lexer-only]")
        print("  <input_file> : file .pas (source code) atau .txt (hasil tokenisasi)")
        print("  --lexer-only : hanya melakukan lexical analysis (hanya untuk .pas)")
        sys.exit(1)

    for arg in sys.argv[1:]:
        if arg == "--lexer-only":
            lexer_only = True
        elif arg.endswith(".pas") or arg.endswith(".txt"):
            source_file = arg

    if not source_file:
        print("Error: file .pas atau .txt tidak ditemukan dalam argumen")
        sys.exit(1)

    if "milestone-1" in source_file:
        lexer_only = True

    raw_tokens = []

    if source_file.endswith(".txt"):
        print("Parse dari File Tokenisasi (.txt)")
        print()
        _print_stage_header("Loading Tokens")
        raw_tokens = load_tokens_from_file(source_file)
        
    else:
        print("Compile dari Source Code (.pas)")
        print()
        dfa = load_dfa_rules()
        with open(source_file, "r", encoding="utf-8") as f:
            source_code = f.read()

        _print_stage_header("Lexical Analysis")
        return_code, raw_tokens = tokenize(source_code, dfa)
        
        if return_code == 1:
            print("Error: token tidak valid ditemukan")
            sys.exit(1)
            
        print_tokens(raw_tokens, source_file)
    
    tokens = [Token(t[0], t[1]) for t in raw_tokens]
    print("-" * 50)
    print(f"Berhasil memproses {len(tokens)} token")

    if lexer_only:
        print("\nMode: Lexical Analysis Only. Program berhenti.")
        return

    parse_tree_root = run_syntax_analysis(tokens)
    
    ast_root = run_ast_generation(parse_tree_root)
    
    if ast_root:
        run_semantic_analysis(ast_root)


if __name__ == "__main__":
    main()
