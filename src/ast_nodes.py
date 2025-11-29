class AST:
    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def __str__(self):
        return self.cetak()

    def cetak(self, prefix="", is_last=True):
        result = ""

        if prefix == "":
            result += self.__class__.__name__
        
        attrs = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        keys = list(attrs.keys())
        count = len(keys)
        
        for i, key in enumerate(keys):
            value = attrs[key]
            is_last_child = (i == count - 1)
            
            connector = "└── " if is_last_child else "├── "
            
            indent = prefix + ("    " if is_last_child else "│   ")
            
            if isinstance(value, AST):
                result += f"\n{prefix}{connector}{key}: {value.__class__.__name__}"
                result += value.cetak(indent, is_last_child)
            else:
                val_str = f"'{value}'" if isinstance(value, str) else str(value)
                result += f"\n{prefix}{connector}{key}: {val_str}"
                
        return result

class ProgramNode(AST):
    def __init__(self, header, declarations, compound_stmt):
        self.header = header
        self.declarations = declarations
        self.compound_stmt = compound_stmt

class ProgramHeaderNode(AST):
    def __init__(self, name):
        self.name = name

class BlockNode(AST):
    def __init__(self, declarations, compound_stmt):
        self.declarations = declarations
        self.compound_stmt = compound_stmt

class DeclarationPartNode(AST):
    def __init__(self, const_section, type_section, var_section, subprogram_section):
        self.const_section = const_section
        self.type_section = type_section
        self.var_section = var_section
        self.subprogram_section = subprogram_section

class ConstSectionNode(AST):
    def __init__(self, declaration=None, next_section=None):
        self.declaration = declaration
        self.next_section = next_section 

class ConstDeclNode(AST):
    def __init__(self, item, tail):
        self.item = item
        self.tail = tail

class ConstItemNode(AST):
    def __init__(self, assign_op, value):
        self.assign_op = assign_op
        self.value = value

class ConstTailNode(AST):
    def __init__(self, item=None, next_tail=None):
        self.item = item
        self.next_tail = next_tail

class TypeSectionNode(AST):
    def __init__(self, declaration=None, next_section=None):
        self.declaration = declaration
        self.next_section = next_section

class TypeDeclNode(AST):
    def __init__(self, item, tail):
        self.item = item
        self.tail = tail

class TypeItemNode(AST):
    def __init__(self, name, type_def):
        self.name = name
        self.type_def = type_def

class TypeTailNode(AST):
    def __init__(self, item=None, next_tail=None):
        self.item = item
        self.next_tail = next_tail

class TypeNode(AST):
    def __init__(self, name_or_keyword):
        self.name = name_or_keyword

class ArrayTypeNode(AST):
    def __init__(self, range_node, type_node):
        self.range_node = range_node
        self.type_node = type_node

class RangeNode(AST):
    def __init__(self, start_expr, end_expr):
        self.start_expr = start_expr
        self.end_expr = end_expr

class VarSectionNode(AST):
    def __init__(self, declaration=None, next_section=None):
        self.declaration = declaration
        self.next_section = next_section

class VarDeclNode(AST):
    def __init__(self, item, tail):
        self.item = item
        self.tail = tail

class VarItemNode(AST):
    def __init__(self, identifier_list, type_node):
        self.identifier_list = identifier_list
        self.type_node = type_node

class VarTailNode(AST):
    def __init__(self, item=None, next_tail=None):
        self.item = item
        self.next_tail = next_tail

class IdentifierListNode(AST):
    def __init__(self, name, tail):
        self.name = name
        self.tail = tail

class IdentifierListTailNode(AST):
    def __init__(self, name=None, next_tail=None):
        self.name = name
        self.next_tail = next_tail

class SubprogramSectionNode(AST):
    def __init__(self, declaration=None, next_section=None):
        self.declaration = declaration
        self.next_section = next_section

class ProcedureNode(AST):
    def __init__(self, name, params, block):
        self.name = name
        self.params = params 
        self.block = block

class FunctionNode(AST):
    def __init__(self, name, params, return_type, block):
        self.name = name
        self.params = params 
        self.return_type = return_type
        self.block = block

class ParamListNode(AST):
    def __init__(self, group_or_expr, tail):
        self.group_or_expr = group_or_expr 
        self.tail = tail

class ParamGroupNode(AST):
    def __init__(self, modifier, id_list, type_node):
        self.modifier = modifier
        self.id_list = id_list
        self.type_node = type_node

class ParamModifierNode(AST):
    def __init__(self, keyword=None):
        self.keyword = keyword 

class ParamTailNode(AST):
    def __init__(self, group_or_expr=None, next_tail=None):
        self.group_or_expr = group_or_expr
        self.next_tail = next_tail

class CompoundNode(AST):
    def __init__(self, statement_list):
        self.statement_list = statement_list

class StatementListNode(AST):
    def __init__(self, statement, tail):
        self.statement = statement
        self.tail = tail

class StatementTailNode(AST):
    def __init__(self, statement=None, next_tail=None):
        self.statement = statement
        self.next_tail = next_tail

class EmptyNode(AST):
    pass

class AssignNode(AST):
    def __init__(self, var_node, expr):
        self.var_node = var_node
        self.expr = expr

class IfNode(AST):
    def __init__(self, condition, then_stmt, else_stmt=None):
        self.condition = condition
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

class WhileNode(AST):
    def __init__(self, condition, statement):
        self.condition = condition
        self.statement = statement

class ForNode(AST):
    def __init__(self, var_name, start_expr, end_expr, direction, statement):
        self.var_name = var_name
        self.start_expr = start_expr
        self.end_expr = end_expr
        self.direction = direction 
        self.statement = statement

class RepeatNode(AST):
    def __init__(self, statement_list, condition):
        self.statement_list = statement_list
        self.condition = condition

class CaseNode(AST):
    def __init__(self, expression, case_list):
        self.expression = expression
        self.case_list = case_list

class CaseListNode(AST):
    def __init__(self, element, tail):
        self.element = element
        self.tail = tail

class CaseListTailNode(AST):
    def __init__(self, element=None, next_tail=None):
        self.element = element
        self.next_tail = next_tail

class CaseElementNode(AST):
    def __init__(self, expression, statement):
        self.expression = expression
        self.statement = statement

class CallNode(AST):
    def __init__(self, name, params=None):
        self.name = name
        self.params = params

class SimpleExprNode(AST):
    def __init__(self, term, tail):
        self.term = term
        self.tail = tail

class SimpleExprTailNode(AST):
    def __init__(self, op=None, term=None, next_tail=None):
        self.op = op
        self.term = term
        self.next_tail = next_tail

class TermNode(AST):
    def __init__(self, factor, tail):
        self.factor = factor
        self.tail = tail

class TermTailNode(AST):
    def __init__(self, op=None, factor=None, next_tail=None):
        self.op = op
        self.factor = factor
        self.next_tail = next_tail

class BinOpNode(AST):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class UnaryOpNode(AST):
    def __init__(self, op, expr, tail=None):
        self.op = op
        self.expr = expr
        self.tail = tail 

class OperatorNode(AST):
    def __init__(self, op_symbol):
        self.op_symbol = op_symbol

class NumberNode(AST):
    def __init__(self, value):
        self.value = value

class CharNode(AST):
    def __init__(self, value):
        self.value = value

class StringNode(AST):
    def __init__(self, value):
        self.value = value

class BooleanNode(AST):
    def __init__(self, value):
        self.value = value

class VarNode(AST):
    def __init__(self, name):
        self.name = name
