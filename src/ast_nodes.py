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
            elif isinstance(value, list):
                 result += f"\n{prefix}{connector}{key}: [List]"
            elif value is None:
                result += f"\n{prefix}{connector}{key}: None"
            else:
                val_str = f"'{value}'" if isinstance(value, str) else str(value)
                result += f"\n{prefix}{connector}{key}: {val_str}"
                
        return result

class ProgramNode(AST):
    def __init__(self, program_header=None, declaration_part=None, compound_statement=None):
        self.program_header = program_header
        self.declaration_part = declaration_part
        self.compound_statement = compound_statement

class ProgramHeaderNode(AST):
    def __init__(self, identifier=None):
        self.identifier = identifier

class DeclarationPartNode(AST):
    def __init__(self, const_section=None, type_section=None, var_section=None, subprogram_section=None):
        self.const_section = const_section
        self.type_section = type_section
        self.var_section = var_section
        self.subprogram_section = subprogram_section

class ConstSectionNode(AST):
    def __init__(self, const_declaration=None, next_section=None):
        self.const_declaration = const_declaration
        self.next_section = next_section

class TypeSectionNode(AST):
    def __init__(self, type_declaration=None, next_section=None):
        self.type_declaration = type_declaration
        self.next_section = next_section

class VarSectionNode(AST):
    def __init__(self, var_declaration=None, next_section=None):
        self.var_declaration = var_declaration
        self.next_section = next_section

class SubprogramSectionNode(AST):
    def __init__(self, subprogram_declaration=None, next_section=None):
        self.subprogram_declaration = subprogram_declaration
        self.next_section = next_section

class ConstDeclNode(AST):
    def __init__(self, const_item=None, item_tail=None):
        self.const_item = const_item
        self.item_tail = item_tail

class ConstItemNode(AST):
    def __init__(self, identifier, assign_operator=None, value_node=None):
        self.identifier = identifier
        self.assign_operator = assign_operator
        self.value_node = value_node

class ConstTailNode(AST):
    def __init__(self, const_item=None, next_tail=None):
        self.const_item = const_item
        self.next_tail = next_tail

class TypeDeclNode(AST):
    def __init__(self, type_item=None, item_tail=None):
        self.type_item = type_item
        self.item_tail = item_tail

class TypeItemNode(AST):
    def __init__(self, identifier=None, type_definition=None):
        self.identifier = identifier
        self.type_definition = type_definition

class TypeTailNode(AST):
    def __init__(self, type_item=None, next_tail=None):
        self.type_item = type_item
        self.next_tail = next_tail

class RecordTypeNode(AST):
    def __init__(self, field_list=None):
        self.field_list = field_list

class FieldListNode(AST):
    def __init__(self, identifier_list=None, type_definition=None, field_list_tail=None):
        self.identifier_list = identifier_list
        self.type_definition = type_definition
        self.field_list_tail = field_list_tail

class FieldListTailNode(AST):
    def __init__(self):
        pass

class VarDeclNode(AST):
    def __init__(self, var_item=None, item_tail=None):
        self.var_item = var_item
        self.item_tail = item_tail

class VarItemNode(AST):
    def __init__(self, identifier_list=None, type_node=None):
        self.identifier_list = identifier_list
        self.type_node = type_node

class VarTailNode(AST):
    def __init__(self, var_item=None, next_tail=None):
        self.var_item = var_item
        self.next_tail = next_tail

class IdentifierListNode(AST):
    def __init__(self, identifier=None, tail=None):
        self.identifier = identifier
        self.tail = tail

class IdentifierListTailNode(AST):
    def __init__(self, identifier=None, next_tail=None):
        self.identifier = identifier
        self.next_tail = next_tail

class TypeNode(AST):
    def __init__(self, name=None):
        self.name = name

class ArrayTypeNode(AST):
    def __init__(self, range_node=None, type_node=None):
        self.range_node = range_node
        self.type_node = type_node

class RangeNode(AST):
    def __init__(self, expression_1=None, range_operator=None, expression_2=None):
        self.expression_1 = expression_1
        self.range_operator = range_operator
        self.expression_2 = expression_2

class ProcedureNode(AST):
    def __init__(self, identifier=None, formal_parameter_list=None, block=None):
        self.identifier = identifier
        self.formal_parameter_list = formal_parameter_list
        self.block = block

class FunctionNode(AST):
    def __init__(self, identifier=None, formal_parameter_list=None, return_type=None, block=None):
        self.identifier = identifier
        self.formal_parameter_list = formal_parameter_list
        self.return_type = return_type
        self.block = block

class ParameterListNode(AST):
    def __init__(self, arg1=None, arg2=None, arg3=None):
        self.param_group_node = None
        self.expression_node = None
        self.next_tail = None

        if isinstance(arg1, ParamGroupNode):
            self.param_group_node = arg1
            self.next_tail = arg2
        else:
            self.expression_node = arg1
            self.next_tail = arg2

class ParameterGroupNode(AST):
    def __init__(self, modifier=None, identifier_list=None, type_node=None):
        self.modifier = modifier
        self.identifier_list = identifier_list
        self.type_node = type_node

class ParameterModifierNode(AST):
    def __init__(self, keyword=None):
        self.keyword = keyword

class ParameterTailNode(AST):
    def __init__(self, arg1=None, arg2=None, arg3=None):
        self.param_group_node = None
        self.expression_node = None
        self.next_tail = None

        if arg1 is None and arg2 is None and arg3 is None:
            pass 
        elif isinstance(arg1, ParamGroupNode):
            self.param_group_node = arg1
            self.next_tail = arg2
        else:
            self.expression_node = arg1
            self.next_tail = arg2
            
        if arg3 is not None:
            self.next_tail = arg3

ParamListNode = ParameterListNode
ParamGroupNode = ParameterGroupNode
ParamModifierNode = ParameterModifierNode
ParamTailNode = ParameterTailNode

class CompoundNode(AST):
    def __init__(self, statement_list=None):
        self.statement_list = statement_list

class StatementListNode(AST):
    def __init__(self, statement=None, tail=None):
        self.statement = statement
        self.tail = tail

class StatementTailNode(AST):
    def __init__(self, statement=None, next_tail=None):
        self.statement = statement
        self.next_tail = next_tail

class BlockNode(AST):
    def __init__(self, declaration_part=None, compound_statement=None):
        self.declaration_part = declaration_part
        self.compound_statement = compound_statement

class AssignNode(AST):
    def __init__(self, var_node=None, field_access_node=None, expression=None):
        self.var_node = var_node
        self.field_access_node = field_access_node
        self.expression = expression

class IfNode(AST):
    def __init__(self, expression=None, then_statement=None, else_statement=None):
        self.expression = expression
        self.then_statement = then_statement
        self.else_statement = else_statement

class WhileNode(AST):
    def __init__(self, expression=None, statement=None):
        self.expression = expression
        self.statement = statement

class ForNode(AST):
    def __init__(self, identifier=None, expression_1=None, expression_2=None, direction_keyword=None, statement=None):
        self.identifier = identifier
        self.expression_1 = expression_1
        self.expression_2 = expression_2
        self.direction_keyword = direction_keyword
        self.statement = statement

class RepeatNode(AST):
    def __init__(self, statement_list=None, expression=None):
        self.statement_list = statement_list
        self.expression = expression

class CaseNode(AST):
    def __init__(self, expression=None, case_list=None):
        self.expression = expression
        self.case_list = case_list

class CaseListNode(AST):
    def __init__(self, case_element=None, tail=None):
        self.case_element = case_element
        self.tail = tail

class CaseListTailNode(AST):
    def __init__(self, case_element=None, next_tail=None):
        self.case_element = case_element
        self.next_tail = next_tail

class CaseElementNode(AST):
    def __init__(self, expression=None, statement=None):
        self.expression = expression
        self.statement = statement

class EmptyNode(AST):
    def __init__(self):
        pass

class CallNode(AST):
    def __init__(self, identifier=None, parameter_list=None):
        self.identifier = identifier
        self.parameter_list = parameter_list

class BinOpNode(AST):
    def __init__(self, operator=None, left=None, right=None):
        self.operator = operator
        self.left = left
        self.right = right

class SimpleExprNode(AST):
    def __init__(self, term=None, tail=None):
        self.term = term
        self.tail = tail

class SimpleExprTailNode(AST):
    def __init__(self, additive_operator=None, term=None, next_tail=None):
        self.additive_operator = additive_operator
        self.term = term
        self.next_tail = next_tail

class TermNode(AST):
    def __init__(self, factor=None, tail=None):
        self.factor = factor
        self.tail = tail

class TermTailNode(AST):
    def __init__(self, multiplicative_operator=None, factor=None, next_tail=None):
        self.multiplicative_operator = multiplicative_operator
        self.factor = factor
        self.next_tail = next_tail

class UnaryOpNode(AST):
    def __init__(self, operator=None, term_node=None, factor_node=None, tail=None):
        self.operator = operator
        self.term_node = term_node
        self.factor_node = factor_node
        self.tail = tail

class OperatorNode(AST):
    def __init__(self, lexeme=None):
        self.lexeme = lexeme

class NumberNode(AST):
    def __init__(self, val1=None, dot=None, val2=None):
        if dot == '.' and val2 is not None:
            self.value = f"{val1}.{val2}"
        else:
            self.value = val1

class CharNode(AST):
    def __init__(self, value=None):
        self.value = value

class StringNode(AST):
    def __init__(self, value=None):
        self.value = value

class BooleanNode(AST):
    def __init__(self, value=None):
        self.value = value

class VarNode(AST):
    def __init__(self, identifier=None):
        self.identifier = identifier

class FieldAccessNode(AST):
    def __init__(self, identifier_1=None, identifier_2=None, index_expr=None, tail=None):
        self.identifier_1 = identifier_1
        self.identifier_2 = identifier_2
        self.index_expr = index_expr
        self.tail = tail

class FieldAccessTailNode(AST):
    def __init__(self, identifier=None, index_expr=None, next_tail=None):
        self.identifier = identifier
        self.index_expr = index_expr
        self.next_tail = next_tail
