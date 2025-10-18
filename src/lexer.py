import json
import os

def classify_char(c):
    if c.isalpha():
        return "letter"
    elif c.isdigit():
        return "digit"
    elif c.isspace():
        return "space"
    else:
        return c

def load_dfa_rules():
    current_dir = os.path.dirname(__file__)
    dfa_path = os.path.join(current_dir, "dfa_rules.json")
    with open(dfa_path, "r") as f:
        return json.load(f)

def tokenize(source_code, dfa):
    state = dfa["start_state"]
    final_states = dfa["final_states"]
    transitions = dfa["transitions"]

    tokens = []
    current_token = ""
    i = 0
    length = len(source_code)

    while i < length:
        c = source_code[i]
        char_type = classify_char(c)
        
        if state == "S_COMMENT_BRACE":
            if c == "}":
                state = "S0"
                i += 1
                continue
            else:
                i += 1
                continue

        elif state == "S_COMMENT_STAR":
            if c == "*":
                state = "S_COMMENT_STAR_END_WAIT"
                i += 1
                continue
            else:
                i += 1
                continue

        elif state == "S_COMMENT_STAR_END_WAIT":
            if c == ")":
                state = "S0"
                i += 1
                continue
            else:
                state = "S_COMMENT_STAR"
                i += 1
                continue

        elif state == "S_IN_STRING":
            current_token += c
            if c == "'":
                if i + 1 < length and source_code[i + 1] == "'":
                    current_token += "'"
                    i += 2
                    continue
                else:
                    state = "S_STRING_END_WAIT"
                    i += 1
                    continue
            else:
                i += 1
                continue

        elif state == "S_STRING_END_WAIT":
            token_type = final_states.get("S_STRING_END_WAIT", "STRING_LITERAL")
            tokens.append((token_type, current_token))
            current_token = ""
            state = dfa["start_state"]
            continue

        if state == "S0" and c == "(" and i + 1 < length and source_code[i + 1] == "*":
            state = "S_COMMENT_STAR"
            i += 2
            continue

        next_state = transitions.get(state, {}).get(char_type) or transitions.get(state, {}).get(c)

        if next_state:
            current_token += c
            state = next_state
            i += 1
        else:
            if state in final_states:
                token_type = final_states[state]
                word = current_token.strip()

                if token_type == "IDENTIFIER":
                    if word.lower() in dfa["keywords"]:
                        token_type = "KEYWORD"
                        word = word.lower()
                    elif word.lower() in dfa["logical_operators"]:
                        token_type = "LOGICAL_OPERATOR"
                        word = word.lower()
                    elif word.lower() in dfa["arithmetic_keywords"]:
                        token_type = "ARITHMETIC_OPERATOR"
                        word = word.lower()
                    else:
                        token_type = "IDENTIFIER"

                tokens.append((token_type, word))

            current_token = ""
            state = dfa["start_state"]

            if c.isspace():
                i += 1

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
