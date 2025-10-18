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
            continue
        if state in final_states:
            lexeme = current_token 
            token_type = finalize_identifier(final_states[state] ,lexeme, keywords, logical_ops, arith_keywords)
            tokens.append((token_type, lexeme))
            current_token = ""
            state = start_state
            continue
        tokens.append(("UNKNOWN", c))
        current_token = ""
        state = start_state
        i += 1

    # flush last token
    if current_token and state in final_states:
        lexeme = current_token
        token_type = finalize_identifier(final_states[state], lexeme, keywords, logical_ops, arith_keywords)
        tokens.append((token_type, lexeme))
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
