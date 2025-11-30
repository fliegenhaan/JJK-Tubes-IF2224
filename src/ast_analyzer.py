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
        self.current_subprogram = None
        
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


    def _expr_is_char(self, node):
        if isinstance(node, CharNode):
            return True
        if isinstance(node, SimpleExprNode):
            return self._expr_is_char(node.term)
        if isinstance(node, TermNode):
            return self._expr_is_char(node.factor)
        if isinstance(node, UnaryOpNode):
            return (self._expr_is_char(node.term_node) or
                    self._expr_is_char(node.factor_node))
        return False

    def _build_record_block(self, record_node: RecordTypeNode):
        self.level += 1
        new_btab_idx = len(self.btab)
        self.btab.append(BtabEntry(last=0, lpar=0, psze=0, vsze=0))
        self.display[self.level] = new_btab_idx

        rec_size = self.analyze(record_node.field_list)
        self.btab[new_btab_idx].vsze = rec_size

        self.level -= 1
        return new_btab_idx, rec_size


    def _normalize_type(self, type_idx, ref):
        if type_idx > 5 and type_idx < len(self.tab):
            tentry = self.tab[type_idx]
            if tentry.obj == OBJ_TYPE:
                base_type = tentry.type
                base_ref  = tentry.ref

                if base_type in (T_INTEGER, T_REAL, T_BOOLEAN, T_CHAR, T_STRING):
                    return base_type, 0

                if base_type in (5, 6):
                    return base_type, base_ref

        return type_idx, ref

    def _array_element_after_index(self, current_type, current_ref, index_expr):
        current_type, current_ref = self._normalize_type(current_type, current_ref)

        if current_type != 5:
            self.error("Attempting to index a non-array value")

        if current_ref <= 0 or current_ref > len(self.atab):
            self.error("Invalid array type reference for indexing")

        arr_desc = self.atab[current_ref - 1]

        index_type = self.analyze_expression(index_expr)

        if arr_desc.inxtyp == T_INTEGER:
            if index_type != T_INTEGER:
                self.error("Array index must be of type integer")
        elif arr_desc.inxtyp == T_CHAR:
            if index_type != T_CHAR:
                self.error("Array index must be of type char")
        else:
            self.error("Unsupported array index type")

        if arr_desc.inxtyp == T_INTEGER:
            static_index = None
            try:
                static_index = self.evaluate_static_expr(index_expr)
            except Exception:
                static_index = None

            if static_index is not None:
                if static_index < arr_desc.low or static_index > arr_desc.high:
                    self.error(
                        f"Array index {static_index} out of bounds "
                        f"[{arr_desc.low}..{arr_desc.high}]"
                    )

        elem_type = arr_desc.eltyp
        elem_ref  = arr_desc.elref

        return elem_type, elem_ref


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
        if type_idx <= 5 and type_idx != T_NOTYPE:
            return 1

        if 0 < type_idx < len(self.tab):
            entry = self.tab[type_idx]
            if entry.obj == OBJ_TYPE:
                if entry.adr > 0:
                    return entry.adr
                if entry.ref > 0 and entry.ref <= len(self.atab):
                    return self.atab[entry.ref - 1].size

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

        self.level = 1
        new_btab_idx = len(self.btab)
        parent_idx = self.display[0]
        parent_last = self.btab[parent_idx].last

        self.btab.append(BtabEntry(last=parent_last, lpar=0, psze=0, vsze=0))
        self.display[self.level] = new_btab_idx

        self.enter(prog_name, OBJ_PROGRAM, T_NOTYPE, nrm=1)

        self.analyze(node.declaration_part)
        self.analyze(node.compound_statement)

        self.level = 0
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
        
        self.enter(name, OBJ_CONSTANT, type_idx, adr=val, nrm=0)
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
            base_idx = self._resolve_type(node.type_definition)
            self.enter(name, OBJ_TYPE, base_idx, ref=0)
            return T_NOTYPE

        idx = self.enter(name, OBJ_TYPE, T_NOTYPE)
        if isinstance(node.type_definition, ArrayTypeNode):
            atab_idx = self.analyze(node.type_definition)
            arr_size = self.atab[atab_idx - 1].size

            self.tab[idx].type = 5
            self.tab[idx].ref = atab_idx
            self.tab[idx].adr = arr_size

        elif isinstance(node.type_definition, RecordTypeNode):
            block_idx, rec_size = self._build_record_block(node.type_definition)

            self.tab[idx].type = 6
            self.tab[idx].ref = block_idx
            self.tab[idx].adr = rec_size

        return T_NOTYPE


    def visit_RecordTypeNode(self, node):
        block_idx, _ = self._build_record_block(node)
        return block_idx

    def _visit_FieldAccessNode_expr(self, node):
        idx, entry = self.lookup(node.identifier_1)
        if not entry:
            self.error(f"Undeclared variable '{node.identifier_1}'")

        current_type, current_ref = self._normalize_type(entry.type, entry.ref)

        if node.identifier_2 is not None:
            if current_type != 6:
                self.error(f"'{node.identifier_1}' is not a record")
            current_type, current_ref = self._lookup_field_in_record(
                current_ref,
                node.identifier_2
            )

        elif getattr(node, "index_expr", None) is not None:
            current_type, current_ref = self._array_element_after_index(
                current_type,
                current_ref,
                node.index_expr
            )

        tail = node.tail
        while tail and (tail.identifier is not None or getattr(tail, "index_expr", None) is not None):
            if tail.identifier is not None:
                current_type, current_ref = self._normalize_type(current_type, current_ref)
                if current_type != 6:
                    self.error(f"Accessing field '{tail.identifier}' of non-record value")
                current_type, current_ref = self._lookup_field_in_record(
                    current_ref,
                    tail.identifier
                )

            elif tail.index_expr is not None:
                current_type, current_ref = self._array_element_after_index(
                    current_type,
                    current_ref,
                    tail.index_expr
                )

            tail = tail.next_tail

        node.type_index = current_type
        return current_type


    def _lookup_field_in_record(self, block_idx, field_name):
        b = self.btab[block_idx]
        curr = b.last
        limit = b.lpar

        while curr > limit:
            entry = self.tab[curr]
            if entry.name == field_name and entry.obj == OBJ_VARIABLE:
                field_type = entry.type
                field_ref  = entry.ref

                if field_type > 5 and field_type < len(self.tab):
                    type_entry = self.tab[field_type]
                    if type_entry.obj == OBJ_TYPE:
                        if type_entry.type in (T_INTEGER, T_REAL, T_BOOLEAN, T_CHAR, T_STRING):
                            field_type = type_entry.type

                        elif type_entry.type == 5:
                            field_type = 5
                            field_ref  = type_entry.ref

                        elif type_entry.type == 6:
                            field_type = 6
                            field_ref  = type_entry.ref

                return field_type, field_ref

            curr = entry.link

        self.error(f"Unknown field '{field_name}' in record")


        
    def visit_FieldListNode(self, node):
        type_idx = self._resolve_type(node.type_definition)
        size_per_field = self.get_type_size(type_idx)

        field_type = type_idx
        field_ref  = 0
        if type_idx > 5:
            type_entry = self.tab[type_idx]
            field_type = type_entry.type
            field_ref  = type_entry.ref

        identifiers = self._collect_identifiers(node.identifier_list)

        offset_accum = 0
        for field_name in identifiers:
            self.enter(field_name, OBJ_VARIABLE, field_type, ref=field_ref, adr=offset_accum)
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
        low_expr = node.range_node.expression_1
        high_expr = node.range_node.expression_2

        low_raw = self.evaluate_static_expr(low_expr)
        high_raw = self.evaluate_static_expr(high_expr)

        is_char_index = self._expr_is_char(low_expr) or self._expr_is_char(high_expr)

        if is_char_index:
            inxtyp = T_CHAR
            count = high_raw - low_raw + 1
            low = 1
            high = count
        else:
            inxtyp = T_INTEGER
            low = low_raw
            high = high_raw
            count = high - low + 1

        eltyp = T_NOTYPE
        elref = 0
        elsze = 1

        if isinstance(node.type_node, ArrayTypeNode):
            inner_atab_idx = self.analyze(node.type_node)
            elsze = self.atab[inner_atab_idx - 1].size
            eltyp = 5
            elref = inner_atab_idx

        else:
            if isinstance(node.type_node, TypeNode):
                resolved = self._resolve_type(node.type_node)
            else:
                resolved = T_NOTYPE

            if resolved <= 5 and resolved != T_NOTYPE:
                eltyp = resolved
                elsze = 1
                elref = 0
            elif resolved > 5:
                type_entry = self.tab[resolved]
                eltyp = type_entry.type
                elref = type_entry.ref
                elsze = self.get_type_size(resolved)

        total_size = count * elsze

        new_entry = AtabEntry(
            inxtyp=inxtyp,
            eltyp=eltyp,
            elref=elref,
            low=low,
            high=high,
            elsze=elsze,
            size=total_size
        )
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

        v_type = T_NOTYPE
        v_ref = 0
        size_per_var = 1

        if isinstance(node.type_node, RecordTypeNode):
            rec_block_idx, rec_size = self._build_record_block(node.type_node)
            v_type = 6
            v_ref = rec_block_idx
            size_per_var = rec_size

        elif isinstance(node.type_node, ArrayTypeNode):
            atab_idx = self.analyze(node.type_node)
            v_type = 5
            v_ref = atab_idx
            size_per_var = self.atab[atab_idx - 1].size

        else:
            resolved = self._resolve_type(node.type_node)
            if resolved <= 5 and resolved != T_NOTYPE:
                v_type = resolved
                v_ref = 0
                size_per_var = 1
            else:
                type_entry = self.tab[resolved]
                v_type = type_entry.type
                v_ref = type_entry.ref
                size_per_var = self.get_type_size(resolved)

        for name in identifiers:
            current_vsze = self.btab[btab_idx].vsze
            self.enter(name, OBJ_VARIABLE, v_type, ref=v_ref, adr=current_vsze)
            self.btab[btab_idx].vsze += size_per_var

        return T_NOTYPE


    def visit_ProcedureNode(self, node):
        proc_name = node.identifier
        proc_idx = self.enter(proc_name, OBJ_PROCEDURE, T_NOTYPE)
        prev_subprog = self.current_subprogram
        self.current_subprogram = proc_idx
        
        self.level += 1
        new_btab_idx = len(self.btab)
        self.btab.append(BtabEntry(last=self.tab[proc_idx].link, lpar=0, psze=0, vsze=0)) 
        self.display[self.level] = new_btab_idx
        
        if node.formal_parameter_list:
            self.analyze(node.formal_parameter_list)
        
        if self.btab[new_btab_idx].lpar > 0:
            self.btab[new_btab_idx].last = self.btab[new_btab_idx].lpar
        else:
            self.btab[new_btab_idx].last = self.tab[proc_idx].link

        self.analyze(node.block)
        self.level -= 1
        self.current_subprogram = prev_subprog
        return T_NOTYPE

    def visit_FunctionNode(self, node):
        func_name = node.identifier
        ret_type_idx = self._resolve_type(node.return_type)
        func_idx = self.enter(func_name, OBJ_FUNCTION, ret_type_idx)
        prev_subprog = self.current_subprogram
        self.current_subprogram = func_idx
        
        self.level += 1
        new_btab_idx = len(self.btab)
        self.btab.append(BtabEntry(last=self.tab[func_idx].link, lpar=0, psze=0, vsze=0))
        self.display[self.level] = new_btab_idx
        
        if node.formal_parameter_list:
            self.analyze(node.formal_parameter_list)
            
        if self.btab[new_btab_idx].lpar > 0:
            self.btab[new_btab_idx].last = self.btab[new_btab_idx].lpar
        else:
            self.btab[new_btab_idx].last = self.tab[func_idx].link
            
        self.analyze(node.block)
        self.level -= 1
        self.current_subprogram = prev_subprog
        return T_NOTYPE

    def visit_ParameterListNode(self, node):
        self.analyze(node.param_group_node)
        self.analyze(node.next_tail)
        return T_NOTYPE

    def visit_ParameterGroupNode(self, node):
        identifiers = self._collect_identifiers(node.identifier_list)
        type_idx = self._resolve_type(node.type_node)

        is_var_param = (node.modifier.keyword == 'variabel') if node.modifier else False
        nrm = 0

        btab_idx = self.display[self.level]
        param_adr = self.btab[btab_idx].psze

        if self.current_subprogram is None:
            self.error("Internal error: parameter group outside of procedure/function")
        subprog_entry = self.tab[self.current_subprogram]
        if not hasattr(subprog_entry, "param_types"):
            subprog_entry.param_types = []
            subprog_entry.param_is_var = []
        for name in identifiers:
            idx = self.enter(name, OBJ_PARAMETER, type_idx, nrm=nrm, adr=param_adr)
            subprog_entry.param_types.append(type_idx)
            subprog_entry.param_is_var.append(is_var_param)
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
                if entry.obj == OBJ_CONSTANT:
                    self.error(f"Cannot assign to constant '{name}'")
                node.var_node.tab_index = idx
                node.var_node.type_index = entry.type
                lhs_type = entry.type
            else:
                self.error(f"Undeclared variable '{name}'")
                return T_NOTYPE

        elif isinstance(node.field_access_node, FieldAccessNode):
            lhs_type = self._visit_FieldAccessNode_expr(node.field_access_node)

        rhs_type = self.analyze_expression(node.expression)

        if lhs_type != T_NOTYPE and rhs_type != T_NOTYPE:

            if lhs_type == T_REAL and rhs_type == T_INTEGER:
                return lhs_type

            if lhs_type != rhs_type:
                type_names = {
                    1: 'integer',
                    2: 'real',
                    3: 'boolean',
                    4: 'char',
                    5: 'string'
                }

                l_name = type_names.get(
                    lhs_type,
                    self.tab[lhs_type].name if lhs_type > 28 and lhs_type < len(self.tab) else str(lhs_type)
                )
                r_name = type_names.get(
                    rhs_type,
                    self.tab[rhs_type].name if rhs_type > 28 and rhs_type < len(self.tab) else str(rhs_type)
                )

                self.error(f"Type mismatch: cannot assign {r_name} to {l_name}")
                return T_NOTYPE

        return lhs_type


    def _typename(self, tid):
        names = {
            T_INTEGER:"integer",
            T_REAL:"real",
            T_BOOLEAN:"boolean",
            T_CHAR:"char",
            T_STRING:"string",
        }
        if tid in names:
            return names[tid]
        if tid < len(self.tab) and self.tab[tid].obj == OBJ_TYPE:
            return self.tab[tid].name
        return "?"


    def _is_lvalue(self, node):
        if isinstance(node, VarNode):
            return True
        if isinstance(node, FieldAccessNode):
            return True
        if isinstance(node, SimpleExprNode):
            return self._is_lvalue(node.term)
        if isinstance(node, TermNode):
            return self._is_lvalue(node.factor)
        if hasattr(node, "inner") and isinstance(node.inner, AST):
            return self._is_lvalue(node.inner)
        return False

    def visit_CallNode(self, node):
        name = node.identifier
        idx, entry = self.lookup(name)
        if not entry:
            if name not in ['writeln', 'write']:
                self.error(f"Undeclared procedure or function '{name}'")
            return T_NOTYPE
        if entry.obj not in [OBJ_PROCEDURE, OBJ_FUNCTION]:
            self.error(f"'{name}' is not callable")

        node.tab_index = idx
        formal_types = getattr(entry, "param_types", [])
        formal_is_var = getattr(entry, "param_is_var", [])
        actual_types = []
        actual_nodes = []
        if node.parameter_list:
            curr = node.parameter_list
            while curr:
                expr = getattr(curr, "expression_node", None)
                if expr is None:
                    break

                t = self.analyze_expression(expr)
                actual_types.append(t)
                actual_nodes.append(expr)

                curr = curr.next_tail

        if len(actual_types) != len(formal_types):
            self.error(
                f"Wrong number of arguments in call to '{name}': "
                f"expected {len(formal_types)}, got {len(actual_types)}"
            )

        for i, (ftype, atype) in enumerate(zip(formal_types, actual_types)):
            if formal_is_var[i]:
                if not self._is_lvalue(actual_nodes[i]):
                    self.error(
                        f"Parameter {i+1} of '{name}' must be a variable "
                        f"(passed expression)"
                    )
            if ftype == T_REAL and atype == T_INTEGER:
                continue

            if ftype != atype:
                self.error(
                    f"Type mismatch in argument {i+1} of '{name}': "
                    f"expected {self._typename(ftype)}, got {self._typename(atype)}"
                )

        if entry.obj == OBJ_FUNCTION:
            return entry.type

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
        if node is None:
            return T_NOTYPE

        if isinstance(node, (NumberNode, CharNode, StringNode, BooleanNode)):
            if isinstance(node, NumberNode):
                t = T_REAL if '.' in str(node.value) else T_INTEGER
            elif isinstance(node, CharNode):
                t = T_CHAR
            elif isinstance(node, StringNode):
                t = T_STRING
            elif isinstance(node, BooleanNode):
                t = T_BOOLEAN
            node.type_index = t
            return t

        if isinstance(node, FieldAccessNode):
            return self._visit_FieldAccessNode_expr(node)

        if isinstance(node, VarNode):
            idx, entry = self.lookup(node.identifier)
            if entry:
                node.tab_index = idx
                node.type_index = entry.type
                return entry.type
            self.error(f"Undeclared variable '{node.identifier}'")
            return T_NOTYPE

        if isinstance(node, CallNode):
            self.analyze(node)
            idx, entry = self.lookup(node.identifier)
            if entry and entry.obj == OBJ_FUNCTION:
                node.type_index = entry.type
                return entry.type
            self.error(f"Call to non-function '{node.identifier}' in expression")
            return T_NOTYPE

        if isinstance(node, UnaryOpNode):
            op = node.operator.lexeme
            operand_type = self.analyze_expression(node.term_node)

            if op in ['+', '-']:
                if operand_type in (T_INTEGER, T_REAL):
                    node.type_index = operand_type
                    return operand_type
                self.error(f"Unary '{op}' requires numeric operand")
                return T_NOTYPE

            if op == 'not':
                if operand_type == T_BOOLEAN:
                    node.type_index = T_BOOLEAN
                    return T_BOOLEAN
                self.error("Unary 'not' requires boolean operand")
                return T_NOTYPE

            self.error(f"Unknown unary operator '{op}'")
            return T_NOTYPE

        if isinstance(node, BinOpNode):
            op = node.operator.lexeme
            left_type = self.analyze_expression(node.left)
            right_type = self.analyze_expression(node.right)

            if op in ['=', '<>', '<', '>', '<=', '>=']:
                if left_type == right_type:
                    node.type_index = T_BOOLEAN
                    return T_BOOLEAN
                self.error(f"Operands for relational operator '{op}' must have same type")
                return T_NOTYPE

            self.error(f"Unknown operator '{op}' in BinOpNode")
            return T_NOTYPE

        if isinstance(node, SimpleExprNode):
            left_type = self.analyze_expression(node.term)
            tail = node.tail

            while tail:
                if tail.additive_operator is None:
                    tail = tail.next_tail
                    continue

                op = tail.additive_operator.lexeme
                right_type = self.analyze_expression(tail.term)

                if op in ['+', '-']:
                    if left_type in (T_INTEGER, T_REAL) and right_type in (T_INTEGER, T_REAL):
                        left_type = T_REAL if T_REAL in (left_type, right_type) else T_INTEGER
                    else:
                        self.error(f"Incompatible operands for '{op}'")
                        return T_NOTYPE

                elif op in ['or']:
                    if left_type == T_BOOLEAN and right_type == T_BOOLEAN:
                        left_type = T_BOOLEAN
                    else:
                        self.error("Operands for 'or' must be boolean")
                        return T_NOTYPE

                tail = tail.next_tail

            node.type_index = left_type
            return left_type

        if isinstance(node, TermNode):
            left_type = self.analyze_expression(node.factor)
            tail = node.tail

            while tail:
                opnode = tail.multiplicative_operator
                if opnode is None:
                    tail = tail.next_tail
                    continue

                op = opnode.lexeme
                right_type = self.analyze_expression(tail.factor)

                if op == '*':
                    if left_type in (T_INTEGER, T_REAL) and right_type in (T_INTEGER, T_REAL):
                        left_type = T_REAL if T_REAL in (left_type, right_type) else T_INTEGER
                    else:
                        self.error(f"Incompatible operands for '*'")
                        return T_NOTYPE

                elif op == '/':
                    if left_type in (T_INTEGER, T_REAL) and right_type in (T_INTEGER, T_REAL):
                        left_type = T_REAL
                    else:
                        self.error("Operands for '/' must be numeric")
                        return T_NOTYPE

                elif op in ['div', 'mod']:
                    if left_type == T_INTEGER and right_type == T_INTEGER:
                        left_type = T_INTEGER
                    else:
                        self.error(f"Operands for '{op}' must be integers")
                        return T_NOTYPE

                elif op == 'and':
                    if left_type == T_BOOLEAN and right_type == T_BOOLEAN:
                        left_type = T_BOOLEAN
                    else:
                        self.error("Operands for 'and' must be boolean")
                        return T_NOTYPE

                else:
                    self.error(f"Unknown multiplicative operator '{op}'")
                    return T_NOTYPE

                tail = tail.next_tail

            node.type_index = left_type
            return left_type


        return T_NOTYPE

    def visit_WhileNode(self, node):
        cond_type = self.analyze_expression(node.expression)

        if cond_type != T_BOOLEAN:
            self.error("Condition of WHILE must be boolean")

        self.analyze(node.statement)


    def visit_IfNode(self, node):
        cond_type = self.analyze_expression(node.expression)

        if cond_type != T_BOOLEAN:
            self.error("Condition of IF must be boolean")

        self.analyze(node.then_statement)

        if node.else_statement:
            self.analyze(node.else_statement)


    def visit_RepeatNode(self, node):
        self.analyze(node.statement_list)

        cond_type = self.analyze_expression(node.expression)

        if cond_type != T_BOOLEAN:
            self.error("Condition of REPEAT..UNTIL must be boolean")

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
        print(f"{'Idx':<4} | {'Identifier':<12} | {'Link':<4} | {'Obj':<3} | {'Typ':<3} | {'Ref':<3} | {'Nrm':<3} | {'Lev':<3} | {'Adr':<3} |")
        print("-" * 85)

        for i, e in enumerate(self.tab):
            # Skip the 0-padding entries if needed
            if i > 0:
                print(f"{i:<4} | "
                      f"{e.name:<12} | "
                      f"{e.link:<4} | "
                      f"{e.obj:<3} | "
                      f"{e.type:<3} | "
                      f"{e.ref:<3} | "
                      f"{e.nrm:<3} | "
                      f"{e.lev:<3} | "
                      f"{e.adr:<3} |")

        print("\n--- BLOCK TABLE (btab) ---")
        print(f"{'Idx':<4} | {'Last':<4} | {'Lpar':<4} | {'P.Sz':<4} | {'V.Sz':<4} |")
        print("-" * 40)

        for i, b in enumerate(self.btab):
            print(f"{i:<4} | {b.last:<4} | {b.lpar:<4} | {b.psze:<4} | {b.vsze:<4} |")

        print("\n--- ARRAY TABLE (atab) ---")
        print(f"{'Idx':<4} | {'Xtyp':<4} | {'Etyp':<4} | {'Eref':<4} | {'Low':<4} | {'High':<4} | {'ElSz':<4} | {'Size':<4} |")
        print("-" * 70)

        for i, a in enumerate(self.atab):
            print(f"{i+1:<4} | "
                  f"{a.inxtyp:<4} | "
                  f"{a.eltyp:<4} | "
                  f"{a.elref:<4} | "
                  f"{a.low:<4} | "
                  f"{a.high:<4} | "
                  f"{a.elsze:<4} | "
                  f"{a.size:<4} |")

