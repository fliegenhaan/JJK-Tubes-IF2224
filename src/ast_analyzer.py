import sys
from ast_nodes import *

OBJ_CONSTANT  = 0
OBJ_VARIABLE  = 1
OBJ_TYPE      = 2
OBJ_PROCEDURE = 3
OBJ_FUNCTION  = 4
OBJ_PROGRAM   = 5
OBJ_PARAMETER = 6 

T_NOTYPE  = 0 
T_INTEGER = 1
T_REAL    = 2
T_BOOLEAN = 3
T_CHAR    = 4
T_STRING  = 5 

class TabEntry:
    def __init__(self, name, obj, type_idx, ref, nrm, lev, adr, link):
        self.name = name    # Identifier name
        self.obj = obj      # Constant, Variable, etc.
        self.type = type_idx# Reference to type (Primitive ID or Tab Index)
        self.ref = ref      # Reference to ATAB (if array) or Size (if Record Type)
        self.nrm = nrm      # Normal (1) or Indirect/Param (0)
        self.lev = lev      # Scope Level
        self.adr = adr      # Memory Offset / Address / Value / Size
        self.link = link    # Pointer to previous symbol in same scope

    def __repr__(self):
        obj_map = ["Const", "Var", "Type", "Proc", "Func", "Prog", "Param"]
        obj_str = obj_map[self.obj] if 0 <= self.obj < len(obj_map) else "?"
        return f"| {self.name:<10} | {obj_str:<5} | Typ:{self.type:<3} | Ref:{self.ref:<3} | Nrm:{self.nrm:<1} | Lev:{self.lev:<1} | Adr:{self.adr:<3} | Link:{self.link:<2} |"

class BtabEntry:
    def __init__(self, last, lpar, psze, vsze):
        self.last = last    # Index of last identifier in this block (in tab)
        self.lpar = lpar    # Index of last parameter (in tab)
        self.psze = psze    # Parameter Size
        self.vsze = vsze    # Variable Size (Local variables)

    def __repr__(self):
        return f"| Last:{self.last:<3} | Lpar:{self.lpar:<3} | P.Sz:{self.psze:<3} | V.Sz:{self.vsze:<3} |"

class AtabEntry:
    def __init__(self, inxtyp, eltyp, elref, low, high, elsze, size):
        self.inxtyp = inxtyp # Index type (T_INTEGER etc)
        self.eltyp = eltyp   # Element type (Primitive ID or Tab Index)
        self.elref = elref   # Reference to ATAB if element is array
        self.low = low       # Low bound value
        self.high = high     # High bound value
        self.elsze = elsze   # Element size
        self.size = size     # Total size

    def __repr__(self):
        # ElSz added as requested
        return f"| Inx:{self.inxtyp:<3} | ElTyp:{self.eltyp:<3} | ElRef:{self.elref:<3} | Low:{self.low:<3} | High:{self.high:<3} | ElSz:{self.elsze:<3} | Sz:{self.size:<3} |"

# ==========================================
# SEMANTIC ANALYZER (VISITOR)
# ==========================================

class SemanticAnalyzer:
    def __init__(self):
        self.tab = []
        self.btab = []
        self.atab = []
        

        self.display = [0] * 20 
        self.level = 0
        
        self.init_keywords()

    def init_keywords(self):

        keywords = [
            'and', 'array', 'begin', 'case', 'const', 'div', 'do', 'downto', 
            'else', 'end', 'for', 'function', 'if', 'mod', 'not', 'of', 'or', 
            'packed', 'procedure', 'program', 'record', 'repeat', 'string', 
            'then', 'to', 'type', 'until', 'var', 'while'
        ]
        
        for kw in keywords:
            obj_type = OBJ_TYPE if kw == 'string' else OBJ_CONSTANT
            self.tab.append(TabEntry(kw, obj_type, T_NOTYPE, 0, 0, 0, 0, 0))


        self.btab.append(BtabEntry(last=28, lpar=0, psze=0, vsze=0))
        self.display[0] = 0

    def error(self, msg):
        raise Exception(f"Semantic Error: {msg}")

    def enter(self, name, obj, type_idx, ref=0, nrm=1, adr=0):
        current_btab_idx = self.display[self.level]
        curr_idx = self.btab[current_btab_idx].last
        limit = self.btab[current_btab_idx].lpar
        
        while curr_idx > limit: 
            entry = self.tab[curr_idx]
            if entry.name == name and entry.lev == self.level:
                self.error(f"Duplicate declaration of '{name}' in scope level {self.level}")
            curr_idx = entry.link
        
        if self.level > 0:
            curr_idx = self.btab[current_btab_idx].lpar
            while curr_idx > 0 and self.tab[curr_idx].obj == OBJ_PARAMETER:
                entry = self.tab[curr_idx]
                if entry.name == name and entry.lev == self.level:
                    self.error(f"Duplicate declaration of '{name}' (conflicts with parameter)")
                curr_idx = entry.link
        
        if self.level == 0:
            existing_idx, _ = self.lookup(name)
            if existing_idx > 0 and existing_idx <= 28: 
                self.error(f"Cannot redeclare reserved word '{name}'")

        link = self.btab[current_btab_idx].last
        
        new_entry = TabEntry(name, obj, type_idx, ref, nrm, self.level, adr, link)
        
        idx = len(self.tab)
        self.tab.append(new_entry)
        
        self.btab[current_btab_idx].last = idx
        return idx

    def lookup(self, name):
        curr_lev = self.level
        while curr_lev >= 0:
            btab_idx = self.display[curr_lev]
            curr_idx = self.btab[btab_idx].last
            while curr_idx > 0:
                entry = self.tab[curr_idx]
                if entry.name == name:
                    return curr_idx, entry
                curr_idx = entry.link
            curr_lev -= 1
        return 0, None

    def get_type_size(self, type_idx):
        if type_idx <= 5:
            return 1
        else:
            if type_idx < len(self.tab):
                entry = self.tab[type_idx]
                if entry.ref > 0 and entry.ref <= len(self.atab) and entry.obj == OBJ_TYPE: 
                     return self.atab[entry.ref - 1].size
                elif entry.obj == OBJ_TYPE and entry.adr > 0:
                     return entry.adr
            return 1

    def analyze(self, node):
        if node is None: return T_NOTYPE
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        res = T_NOTYPE
        if hasattr(node, '__dict__'):
            for key, value in node.__dict__.items():
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, AST): 
                            val = self.analyze(item)
                            if val != T_NOTYPE: res = val
                elif isinstance(value, AST):
                    val = self.analyze(value)
                    if val != T_NOTYPE: res = val
        return res

    def _resolve_type(self, type_node):
        if isinstance(type_node, TypeNode):
            type_name = str(type_node.name)
            
            if type_name == 'integer': return T_INTEGER
            if type_name == 'real': return T_REAL
            if type_name == 'boolean': return T_BOOLEAN
            if type_name == 'char': return T_CHAR
            if type_name == 'string': return T_STRING
            
            idx, entry = self.lookup(type_name)
            if entry and entry.obj == OBJ_TYPE: 
                return idx 
            
            self.error(f"Undefined type '{type_name}'")
        return T_NOTYPE

    def evaluate_static_expr(self, node):
        if isinstance(node, (SimpleExprNode, TermNode)):
            if hasattr(node, 'term') and node.term: return self.evaluate_static_expr(node.term)
            if hasattr(node, 'factor') and node.factor: return self.evaluate_static_expr(node.factor)
            
        if isinstance(node, NumberNode):
            return int(float(node.value))
        
        if isinstance(node, UnaryOpNode):
            val = self.evaluate_static_expr(node.term_node or node.factor_node)
            if node.operator and node.operator.lexeme == '-':
                return -val
            return val

        if isinstance(node, VarNode):
            _, entry = self.lookup(node.identifier)
            if entry and entry.obj == OBJ_CONSTANT:
                return entry.adr 
            self.error(f"Array bound '{node.identifier}' must be a constant")
            
        if isinstance(node, (CharNode, StringNode)):
            val_str = str(node.value).replace("'", "")
            return ord(val_str[0]) if val_str else 0

        return 0

    def visit_ProgramNode(self, node):
        prog_name = node.program_header.identifier
        self.enter(prog_name, OBJ_PROGRAM, T_NOTYPE)
        
        self.analyze(node.declaration_part)
        self.analyze(node.compound_statement)
        return T_NOTYPE

    def visit_BlockNode(self, node):
        self.analyze(node.declaration_part)
        self.analyze(node.compound_statement)
        return T_NOTYPE

    def visit_ConstSectionNode(self, node):
        self.analyze(node.const_declaration)
        self.analyze(node.next_section)
        return T_NOTYPE

    def visit_ConstDeclNode(self, node):
        self.analyze(node.const_item)
        self.analyze(node.item_tail)
        return T_NOTYPE

    def visit_ConstTailNode(self, node):
        if node.const_item: self.analyze(node.const_item)
        if node.next_tail: self.analyze(node.next_tail)
        return T_NOTYPE

    def visit_ConstItemNode(self, node):
        name = node.identifier
        val_node = node.value_node
        type_idx = T_INTEGER
        val = 0
        
        if hasattr(val_node, 'value'):
             s_val = str(val_node.value)
             if '.' in s_val: 
                 type_idx = T_REAL
                 val = 0 
             elif s_val.startswith("'"): 
                 type_idx = T_CHAR
                 clean_val = s_val.replace("'", "")
                 val = ord(clean_val[0]) if clean_val else 0
             else:
                 try: val = int(s_val)
                 except: pass
        
        self.enter(name, OBJ_CONSTANT, type_idx, adr=val) 
        return T_NOTYPE

    def visit_TypeSectionNode(self, node):
        self.analyze(node.type_declaration)
        self.analyze(node.next_section)
        return T_NOTYPE

    def visit_TypeDeclNode(self, node):
        self.analyze(node.type_item)
        self.analyze(node.item_tail)
        return T_NOTYPE

    def visit_TypeTailNode(self, node):
        if node.type_item: self.analyze(node.type_item)
        if node.next_tail: self.analyze(node.next_tail)
        return T_NOTYPE

    def visit_TypeItemNode(self, node):
        name = node.identifier
        
        if isinstance(node.type_definition, TypeNode):
            type_idx = self._resolve_type(node.type_definition)
            self.enter(name, OBJ_TYPE, type_idx, ref=0)
        else:
            idx = self.enter(name, OBJ_TYPE, T_NOTYPE)
            self.tab[idx].type = idx 

            res = self.analyze(node.type_definition)

            if isinstance(node.type_definition, ArrayTypeNode):
                self.tab[idx].ref = res
            elif isinstance(node.type_definition, RecordTypeNode):
                self.tab[idx].adr = res

        return T_NOTYPE

    def visit_RecordTypeNode(self, node):
        return self.analyze(node.field_list)
        
    def visit_FieldListNode(self, node):
        type_idx = self._resolve_type(node.type_definition)
        
        size_per_field = self.get_type_size(type_idx)
        
        identifiers = self._collect_identifiers(node.identifier_list)
        
        offset_accum = 0
        for field_name in identifiers:
            self.enter(field_name, OBJ_VARIABLE, type_idx, adr=offset_accum) 
            offset_accum += size_per_field
            
        tail_size = 0
        if node.field_list_tail:
            tail_size = self.analyze(node.field_list_tail)
            
        return (len(identifiers) * size_per_field) + tail_size
        
    def visit_FieldListTailNode(self, node):
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                if isinstance(child, AST):
                    return self.analyze(child)
        return 0
        
    def visit_ArrayTypeNode(self, node):

        low = self.evaluate_static_expr(node.range_node.expression_1)
        high = self.evaluate_static_expr(node.range_node.expression_2)
        
        el_type_idx = T_NOTYPE
        el_ref = 0
        el_size = 1
        
        if isinstance(node.type_node, ArrayTypeNode):
            el_ref = self.analyze(node.type_node)
            if el_ref > 0: el_size = self.atab[el_ref - 1].size
            el_type_idx = T_NOTYPE 
        else:
            el_type_idx = self._resolve_type(node.type_node)
            el_size = self.get_type_size(el_type_idx)
            
            if el_type_idx > 5:
                entry = self.tab[el_type_idx]
                if entry.ref > 0: el_ref = entry.ref

        count = (high - low + 1)
        total_size = count * el_size
        
        new_entry = AtabEntry(inxtyp=T_INTEGER, eltyp=el_type_idx, elref=el_ref, 
                              low=low, high=high, elsze=el_size, size=total_size)
        
        self.atab.append(new_entry)
        return len(self.atab)


    def visit_VarDeclNode(self, node):
        self.analyze(node.var_item)
        if node.item_tail: self.analyze(node.item_tail)
        return T_NOTYPE

    def visit_VarTailNode(self, node):
        if node.var_item: self.analyze(node.var_item)
        if node.next_tail: self.analyze(node.next_tail)
        return T_NOTYPE

    def visit_VarItemNode(self, node):
        identifiers = self._collect_identifiers(node.identifier_list)
        btab_idx = self.display[self.level]
        
        # Strategy:
        # 1. If Anonymous Record: We must enter Identifiers FIRST, then fields (fields appear after vars in tab).
        #    But we need size for addressing.
        #    Solution: Enter vars with 0 size -> Analyze Record -> Update vars with size.
        # 2. If Array/Named: Standard flow.

        is_anon_rec = isinstance(node.type_node, RecordTypeNode)
        
        type_idx = T_NOTYPE
        ref_idx = 0
        size_per_var = 1
        var_indices = []

        # Step 1: Resolve Type (or prepare for Anon Record)
        if is_anon_rec:
            # We defer analysis. type_idx is Structure (0).
            pass
        elif isinstance(node.type_node, ArrayTypeNode):
            # Anonymous Array: Create ATAB entry
            ref_idx = self.analyze(node.type_node)
            if ref_idx > 0:
                 size_per_var = self.atab[ref_idx - 1].size
        else:
            # Named Type
            type_idx = self._resolve_type(node.type_node)
            size_per_var = self.get_type_size(type_idx)
            
            # Check if Named Type refers to ATAB
            if type_idx > 28:
                entry = self.tab[type_idx]
                if entry.ref > 0:
                    ref_idx = entry.ref

        # Step 2: Register Variables
        for name in identifiers:
            current_vsze = self.btab[btab_idx].vsze
            idx = self.enter(name, OBJ_VARIABLE, type_idx, ref=ref_idx, adr=current_vsze)
            var_indices.append(idx)
            
            # For anon record, we increment vsze LATER after size calc
            if not is_anon_rec:
                self.btab[btab_idx].vsze += size_per_var

        # Step 3: Handle Anonymous Record (Identifiers already in table)
        if is_anon_rec:
            # Analyze record definition -> Registers fields (c, r) -> Returns size
            rec_size = self.analyze(node.type_node)
            
            # Update registered variables with correct size/addressing logic
            current_base_adr = self.tab[var_indices[0]].adr # Address of first var
            
            for i, idx in enumerate(var_indices):
                entry = self.tab[idx]
                entry.adr = int(current_base_adr + (i * rec_size))
                # Update ref to hold size if needed, or 0
            
            # Update block total size
            total_added_size = len(var_indices) * rec_size
            self.btab[btab_idx].vsze += total_added_size

        return T_NOTYPE


    def visit_ProcedureNode(self, node):
        proc_name = node.identifier
        proc_idx = self.enter(proc_name, OBJ_PROCEDURE, T_NOTYPE)
        
        self.level += 1
        new_btab_idx = len(self.btab)
        self.btab.append(BtabEntry(last=self.tab[proc_idx].link, lpar=0, psze=0, vsze=0)) 
        self.display[self.level] = new_btab_idx
        
        if node.formal_parameter_list: self.analyze(node.formal_parameter_list)
        
        if self.btab[new_btab_idx].lpar > 0:
            self.btab[new_btab_idx].last = self.btab[new_btab_idx].lpar
        else:
            self.btab[new_btab_idx].last = self.tab[proc_idx].link

        self.analyze(node.block)
        self.level -= 1
        return T_NOTYPE

    def visit_FunctionNode(self, node):
        func_name = node.identifier
        ret_type_idx = self._resolve_type(node.return_type)
        func_idx = self.enter(func_name, OBJ_FUNCTION, ret_type_idx)
        
        self.level += 1
        new_btab_idx = len(self.btab)
        self.btab.append(BtabEntry(last=self.tab[func_idx].link, lpar=0, psze=0, vsze=0))
        self.display[self.level] = new_btab_idx
        
        if node.formal_parameter_list: self.analyze(node.formal_parameter_list)
            
        if self.btab[new_btab_idx].lpar > 0:
            self.btab[new_btab_idx].last = self.btab[new_btab_idx].lpar
        else:
            self.btab[new_btab_idx].last = self.tab[func_idx].link
            
        self.analyze(node.block)
        self.level -= 1
        return T_NOTYPE

    def visit_ParameterListNode(self, node):
        self.analyze(node.param_group_node)
        self.analyze(node.next_tail)
        return T_NOTYPE

    def visit_ParameterGroupNode(self, node):
        identifiers = self._collect_identifiers(node.identifier_list)
        type_idx = self._resolve_type(node.type_node)
        is_var_param = (node.modifier.keyword == 'variabel') if node.modifier else False
        nrm = 0 if is_var_param else 1
        
        btab_idx = self.display[self.level]
        param_adr = self.btab[btab_idx].psze 
        
        for name in identifiers:
            idx = self.enter(name, OBJ_PARAMETER, type_idx, nrm=nrm, adr=param_adr)
            self.btab[btab_idx].lpar = idx 
            self.btab[btab_idx].psze += 1 
            param_adr += 1
        return T_NOTYPE
        
    def visit_ParameterTailNode(self, node):
        if node.param_group_node: self.analyze(node.param_group_node)
        if node.next_tail: self.analyze(node.next_tail)
        return T_NOTYPE

    def visit_AssignNode(self, node):
        lhs_type = T_NOTYPE
        if isinstance(node.var_node, VarNode):
            name = node.var_node.identifier
            idx, entry = self.lookup(name)
            if entry:
                node.var_node.tab_index = idx
                node.var_node.type_index = entry.type
                lhs_type = entry.type
            else:
                self.error(f"Undeclared variable '{name}'")
        
        rhs_type = self.analyze_expression(node.expression)
        
        if lhs_type != rhs_type and lhs_type != T_NOTYPE and rhs_type != T_NOTYPE:
            if not (lhs_type == T_REAL and rhs_type == T_INTEGER):
                l_name = self.tab[lhs_type].name if lhs_type > 28 else str(lhs_type)
                r_name = self.tab[rhs_type].name if rhs_type > 28 else str(rhs_type)
                type_names = {1:'integer', 2:'real', 3:'boolean', 4:'char', 5:'string'}
                l_name = type_names.get(lhs_type, l_name)
                r_name = type_names.get(rhs_type, r_name)

                print(f"WARNING: Type mismatch. Target ({l_name}) := Value ({r_name})")
        return T_NOTYPE

    def visit_CallNode(self, node):
        name = node.identifier
        idx, entry = self.lookup(name)
        if not entry:
            if name not in ['writeln', 'write']: 
                self.error(f"Undeclared procedure or function '{name}'")
        else:
            if entry.obj not in [OBJ_PROCEDURE, OBJ_FUNCTION]:
                self.error(f"'{name}' is not callable")
            node.tab_index = idx
        if node.parameter_list: self.analyze(node.parameter_list)
        return T_NOTYPE

    def visit_StatementListNode(self, node):
        self.analyze(node.statement)
        if node.tail: self.analyze(node.tail)
        return T_NOTYPE

    def visit_StatementListTailNode(self, node):
        if node.statement: self.analyze(node.statement)
        if node.next_tail: self.analyze(node.next_tail)
        return T_NOTYPE

    def analyze_expression(self, node):
        if node is None: return T_NOTYPE

        if isinstance(node, (NumberNode, CharNode, StringNode, BooleanNode)):
            if isinstance(node, NumberNode):
                t = T_REAL if '.' in str(node.value) else T_INTEGER
            elif isinstance(node, CharNode): t = T_CHAR
            elif isinstance(node, StringNode): t = T_STRING
            elif isinstance(node, BooleanNode): t = T_BOOLEAN
            else: t = T_NOTYPE
            node.type_index = t
            return t

        if isinstance(node, VarNode):
            idx, entry = self.lookup(node.identifier)
            if entry:
                node.tab_index = idx
                node.type_index = entry.type
                return entry.type
            self.error(f"Undeclared variable '{node.identifier}' used in expression")
            return T_NOTYPE

        if isinstance(node, CallNode):
            self.analyze(node)
            idx, entry = self.lookup(node.identifier)
            if entry and entry.obj == OBJ_FUNCTION: return entry.type
            return T_NOTYPE

        if isinstance(node, BinOpNode):
            left_type = self.analyze_expression(node.left)
            right_type = self.analyze_expression(node.right)
            t = T_NOTYPE
            if left_type == T_REAL or right_type == T_REAL: t = T_REAL
            elif left_type == T_INTEGER and right_type == T_INTEGER: t = T_INTEGER
            elif left_type == T_BOOLEAN and right_type == T_BOOLEAN: t = T_BOOLEAN
            node.type_index = t
            return t
            
        if isinstance(node, UnaryOpNode):
            t = self.analyze_expression(node.term_node) or self.analyze_expression(node.factor_node)
            node.type_index = t
            return t
        
        t = T_NOTYPE
        if hasattr(node, '__dict__'):
            for key, value in node.__dict__.items():
                if isinstance(value, AST) and not isinstance(value, OperatorNode):
                    res_type = self.analyze_expression(value)
                    if res_type != T_NOTYPE: t = res_type
        return t

    def _collect_identifiers(self, id_list_node):
        ids = []
        curr = id_list_node
        while curr:
            if hasattr(curr, 'identifier') and curr.identifier: ids.append(curr.identifier)
            if hasattr(curr, 'tail'): curr = curr.tail
            elif hasattr(curr, 'next_tail'): curr = curr.next_tail
            else: curr = None
        return ids

    def print_tables(self):
        print("\n--- SYMBOL TABLE (tab) ---")
        print(f"{'Idx':<4} | {'Name':<10} | {'Obj':<5} | {'Typ':<3} | {'Ref':<3} | {'Nrm':<3} | {'Lev':<3} | {'Adr':<3} | {'Link':<4} |") 
        print("-" * 75)
        for i, entry in enumerate(self.tab):
            if i > 28 or entry.lev >= 0: print(f"{i:<4} {entry}")

        print("\n--- BLOCK TABLE (btab) ---")
        print(f"{'Idx':<4} | {'Last':<4} | {'Lpar':<4} | {'P.Sz':<4} | {'V.Sz':<4} |")
        print("-" * 30)
        for i, entry in enumerate(self.btab):
            print(f"{i:<4} {entry}")

        if self.atab:
            print("\n--- ARRAY TABLE (atab) ---")
            print(f"{'Idx':<4} | {'Inx':<4} | {'ElTyp':<5} | {'ElRef':<5} | {'Low':<4} | {'High':<4} | {'ElSz':<4} | {'Sz':<4} |")
            print("-" * 70)
            for i, entry in enumerate(self.atab):
                print(f"{i+1:<4} {entry}")
