import json
import os

def load_dfa_rules():
    current_dir = os.path.dirname(__file__)
    dfa_path = os.path.join(current_dir, "dfa_rules.json")
    with open(dfa_path, "r") as f:
        return json.load(f)

def classify_char(c):
    if c.isalpha() or c == '_':
        return "letter"
    elif c.isdigit():
        return "digit"
    elif c.isspace():
        return "space"
    else:
        return c

def step(current_state, c, transitions):
    table = transitions.get(current_state, {})
    # exact character
    if c in table:
        return table[c]
    # character class
    t = classify_char(c)
    if t in table:
        return table[t]
    # wildcard
    for k, v in table.items():
        if k.startswith("any_not_"):
            forbidden = k[len("any_not_"):]
            if c != forbidden:
                return v
    return None

def finalize_identifier(token_type, word, keywords, logical_ops, arith_keywords):
    wl = word.lower()
    if wl in keywords:
        return "KEYWORD"
    if wl in logical_ops:
        return "LOGICAL_OPERATOR"
    if wl in arith_keywords:
        return "ARITHMETIC_OPERATOR"
    return token_type

def in_comment_state(s):
    return s.startswith("S_COMMENT")

def merge_hyphenated_keywords(tokens, keywords):
    # menggabungkan token yang membentuk keyword dengan hyphen
    # mis: identifier(selain) + operator(-) + identifier(itu) = keyword(selain-itu)
    merged = []
    i = 0
    while i < len(tokens):
        # cek apakah ada pola: (identifier|keyword) - (identifier|keyword)
        if (i + 2 < len(tokens) and
            tokens[i][0] in ["IDENTIFIER", "KEYWORD"] and
            tokens[i + 1][0] == "ARITHMETIC_OPERATOR" and tokens[i + 1][1] == "-" and
            tokens[i + 2][0] in ["IDENTIFIER", "KEYWORD"]):

            # gabung jadi satu kata dengan hyphen
            combined = tokens[i][1] + "-" + tokens[i + 2][1]

            # cek apakah gabungan tersebut adalah keyword
            if combined.lower() in keywords:
                merged.append(("KEYWORD", combined))
                i += 3  # skip 3 token
                continue

        # jika bukan pola keyword dengan hyphen, tambahkan token seperti biasa
        merged.append(tokens[i])
        i += 1
    return merged

def tokenize(source_code, dfa):
    start_state = dfa["start_state"]
    final_states = dfa["final_states"]
    transitions = dfa["transitions"]
    keywords = set(dfa.get("keywords", []))
    logical_ops = set(dfa.get("logical_operators", []))
    arith_keywords = set(dfa.get("arithmetic_keywords", []))

    tokens = []
    state = start_state
    current_token = ""
    i = 0
    n = len(source_code)

    # untuk backtracking
    last_final_state = None
    last_final_pos = -1
    last_final_token = ""

    while i < n:
        c = source_code[i]
        if state == start_state and c.isspace():
            i += 1
            continue
        nxt = step(state, c, transitions)
        if nxt:
            if in_comment_state(state) or in_comment_state(nxt):
                state = nxt
                i += 1
                continue
            current_token += c
            state = nxt
            i += 1

            # simpan posisi final state terakhir untuk backtracking
            if state in final_states:
                last_final_state = state
                last_final_pos = i
                last_final_token = current_token

            continue
        if state in final_states:
            lexeme = current_token
            token_type = finalize_identifier(final_states[state] ,lexeme, keywords, logical_ops, arith_keywords)
            tokens.append((token_type, lexeme))
            current_token = ""
            state = start_state
            last_final_state = None
            last_final_pos = -1
            last_final_token = ""
            continue

        # backtracking: jika ada final state sebelumnya, gunakan itu
        if last_final_state is not None:
            lexeme = last_final_token
            token_type = finalize_identifier(final_states[last_final_state], lexeme, keywords, logical_ops, arith_keywords)
            tokens.append((token_type, lexeme))
            current_token = ""
            state = start_state
            i = last_final_pos
            last_final_state = None
            last_final_pos = -1
            last_final_token = ""
            continue

        return (1,None)

    if (current_token):
        # flush last token
        if state in final_states:
            lexeme = current_token
            token_type = finalize_identifier(final_states[state], lexeme, keywords, logical_ops, arith_keywords)
            tokens.append((token_type, lexeme))
        else:
            return (1,None)

    # post-processing: gabungkan token yang membentuk keyword dengan hyphen
    tokens = merge_hyphenated_keywords(tokens, keywords)

    return (0,tokens)

def load_tokens_from_file(file_path):
    # membaca tokens dari file .txt hasil tokenisasi
    # format: TOKEN_TYPE(value)
    tokens = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # parse format TOKEN_TYPE(value)
            if '(' in line and line.endswith(')'):
                token_type = line[:line.index('(')]
                value = line[line.index('(') + 1:-1]
                tokens.append((token_type, value))

    return tokens

def print_tokens(tokens, input_path):
    base_name = os.path.basename(input_path)
    output_name = base_name.replace("test", "result").replace(".pas", ".txt")

    output_dir = os.path.dirname(input_path)
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, output_name)

    with open(output_path, "w") as f:
        for token_type, value in tokens:
            f.write(f"{token_type}({value})\n")

    print(f"Tokens written to {output_path}")
