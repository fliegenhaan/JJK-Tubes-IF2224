import sys

# Kelas utama

class Token:
    def __init__(self, tipe, nilai):
        self.tipe = tipe
        self.nilai = nilai
    def __repr__(self):
        return f"{self.tipe}({self.nilai})"

class Terminal:
    def __init__(self, tipe, nilai=None):
        self.tipe = tipe
        self.nilai = nilai
    def __repr__(self):
        if self.nilai:
            return f"'{self.nilai}'"
        return self.tipe

class ParseErrorContext:
    def __init__(self):
        self.max_index = -1
        self.expected = None
        self.found = None
        self.rule_name = None

    def report(self, index, expected, found, rule_name):
        if index >= self.max_index:
            self.max_index = index
            self.expected = expected
            self.found = found
            self.rule_name = rule_name

class ParseNode:
    def __init__(self):
        self.name = self.__class__.__name__
        self.children = [] 

    def grammar(self):
        raise NotImplementedError

    def parse(self, tokens, start_idx, error_ctx=None):
        if error_ctx is None:
            error_ctx = ParseErrorContext()

        valid_grammars = self.grammar()

        for rule_sequence in valid_grammars:
            
            curr_idx = start_idx
            temp_children = []
            rule_failed = False

            for element in rule_sequence:
                
                if curr_idx >= len(tokens):
                    if rule_sequence == []: 
                        break
                    error_ctx.report(curr_idx, element, "EOF", self.name)
                    rule_failed = True
                    break

                current_token = tokens[curr_idx]

                if isinstance(element, Terminal):
                    match_type = (element.tipe == current_token.tipe)
                    match_value = (element.nilai is None) or (element.nilai == current_token.nilai)

                    if match_type and match_value:
                        temp_children.append(current_token)
                        curr_idx += 1
                    else:
                        error_ctx.report(curr_idx, element, current_token, self.name)
                        rule_failed = True
                        break

                elif issubclass(element, ParseNode):
                    child_node = element()
                    is_success, next_idx = child_node.parse(tokens, curr_idx, error_ctx)
                    
                    if is_success:
                        temp_children.append(child_node)
                        curr_idx = next_idx
                    else:
                        rule_failed = True
                        break
            
            if not rule_failed:
                self.children = temp_children
                return True, curr_idx

        return False, start_idx

    def __repr__(self):
        return f"<{self.name}>"

    def cetak(self, level=0, prefix=""):
        hasil = ""
        if level == 0:
            hasil += f"{prefix}{self.name}\n"
        
        jumlah_anak = len(self.children)
        for i, child in enumerate(self.children):
            adalah_terakhir = (i == jumlah_anak - 1)
            
            if level == 0:
                prefix_baru = ""
            else:
                prefix_baru = prefix
            
            connector = "└── " if adalah_terakhir else "├── "
            
            if isinstance(child, Token):
                hasil += f"{prefix_baru}{connector}{child}\n"
            elif isinstance(child, ParseNode):
                next_prefix = prefix_baru + ("    " if adalah_terakhir else "│   ")
                hasil += f"{prefix_baru}{connector}{child.name}\n"
                hasil += child.cetak(level + 1, next_prefix)
                
        return hasil

class NumberNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("NUMBER"), Terminal("DOT"), Terminal("NUMBER")],
            
            [Terminal("NUMBER")]
        ]

class FieldAccessTailNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("DOT"), Terminal("IDENTIFIER"), FieldAccessTailNode],
            [Terminal("LBRACKET"), ExpressionNode, Terminal("RBRACKET"), FieldAccessTailNode],
            []
        ]

class FieldAccessNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("IDENTIFIER"), Terminal("DOT"), Terminal("IDENTIFIER"), FieldAccessTailNode],
            [Terminal("IDENTIFIER"), Terminal("LBRACKET"), ExpressionNode, Terminal("RBRACKET"), FieldAccessTailNode]
        ]

class ValueNode(ParseNode):
    def grammar(self):
        return [
            [FieldAccessNode],
            [NumberNode], 
            [Terminal("CHAR_LITERAL")],
            [Terminal("STRING_LITERAL")],
            [Terminal("KEYWORD", "benar")],
            [Terminal("KEYWORD", "salah")],
            [Terminal("IDENTIFIER")]
        ]

class MultiplicativeOperatorNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("ARITHMETIC_OPERATOR", "*")],
            [Terminal("ARITHMETIC_OPERATOR", "/")],
            [Terminal("ARITHMETIC_OPERATOR", "bagi")],
            [Terminal("ARITHMETIC_OPERATOR", "mod")],
            [Terminal("LOGICAL_OPERATOR", "dan")]
        ]

class AdditiveOperatorNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("LOGICAL_OPERATOR", "atau")],
            [Terminal("ARITHMETIC_OPERATOR", "+")],
            [Terminal("ARITHMETIC_OPERATOR", "-")]
        ]

class RelationalOperatorNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("RELATIONAL_OPERATOR", "<>")],
            [Terminal("RELATIONAL_OPERATOR", "<")],
            [Terminal("RELATIONAL_OPERATOR", "<=")],
            [Terminal("RELATIONAL_OPERATOR", ">")],
            [Terminal("RELATIONAL_OPERATOR", ">=")],
            [Terminal("RELATIONAL_OPERATOR", "=")]
        ]

class ParameterListTailNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("COMMA"), ExpressionNode, ParameterListTailNode],
            []
        ]

class ParameterListNode(ParseNode):
    def grammar(self):
        return [
            [ExpressionNode, ParameterListTailNode]
        ]

class CallNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("IDENTIFIER"), Terminal("LPARENTHESIS"), ParameterListNode, Terminal("RPARENTHESIS")],
            [Terminal("IDENTIFIER"), Terminal("LPARENTHESIS"), Terminal("RPARENTHESIS")]
        ]

class FactorNode(ParseNode):
    def grammar(self):
        return [
            [CallNode],
            [ValueNode],
            [Terminal("LPARENTHESIS"), ExpressionNode, Terminal("RPARENTHESIS")],
            [Terminal("LOGICAL_OPERATOR", "tidak"), FactorNode]
        ]

class TermTailNode(ParseNode):
    def grammar(self):
        return [
            [MultiplicativeOperatorNode, FactorNode, TermTailNode],
            []
        ]

class TermNode(ParseNode):
    def grammar(self):
        return [
            [FactorNode, TermTailNode]
        ]

class SimpleExpressionTailNode(ParseNode):
    def grammar(self):
        return [
            [AdditiveOperatorNode, TermNode, SimpleExpressionTailNode],
            []
        ]

class SimpleExpressionNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("ARITHMETIC_OPERATOR", "+"), TermNode, SimpleExpressionTailNode],
            [Terminal("ARITHMETIC_OPERATOR", "-"), TermNode, SimpleExpressionTailNode],
            [TermNode, SimpleExpressionTailNode]
        ]

class ExpressionNode(ParseNode):
    def grammar(self):
        return [
            [SimpleExpressionNode, RelationalOperatorNode, SimpleExpressionNode],
            [SimpleExpressionNode]
        ]

class AssignmentStatementNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("IDENTIFIER"), Terminal("ASSIGN_OPERATOR"), ExpressionNode],
            [FieldAccessNode, Terminal("ASSIGN_OPERATOR"), ExpressionNode]
        ]

class EmptyStatementNode(ParseNode):
    def grammar(self):
        return [ [] ]

class ExpressionStatementNode(ParseNode):
    def grammar(self):
        return [
            [ExpressionNode]
        ]

class IfStatementNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("KEYWORD", "jika"), ExpressionNode, Terminal("KEYWORD", "maka"), StatementNode, Terminal("KEYWORD", "selain-itu"), StatementNode],
            [Terminal("KEYWORD", "jika"), ExpressionNode, Terminal("KEYWORD", "maka"), StatementNode]
        ]

class WhileStatementNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("KEYWORD", "selama"), ExpressionNode, Terminal("KEYWORD", "lakukan"), StatementNode]
        ]

class ForStatementNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("KEYWORD", "untuk"), Terminal("IDENTIFIER"), Terminal("ASSIGN_OPERATOR"), ExpressionNode, Terminal("KEYWORD", "ke"), ExpressionNode, Terminal("KEYWORD", "lakukan"), StatementNode],
            [Terminal("KEYWORD", "untuk"), Terminal("IDENTIFIER"), Terminal("ASSIGN_OPERATOR"), ExpressionNode, Terminal("KEYWORD", "turun-ke"), ExpressionNode, Terminal("KEYWORD", "lakukan"), StatementNode]
        ]

class RepeatStatementNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("KEYWORD", "ulangi"), StatementListNode, Terminal("KEYWORD", "sampai"), ExpressionNode]
        ]

class CaseElementNode(ParseNode):
    def grammar(self):
        return [
            [ExpressionNode, Terminal("COLON"), StatementNode]
        ]

class CaseListTailNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("SEMICOLON"), CaseElementNode, CaseListTailNode],
            [Terminal("SEMICOLON")],
            []
        ]

class CaseListNode(ParseNode):
    def grammar(self):
        return [
            [CaseElementNode, CaseListTailNode]
        ]

class CaseStatementNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("KEYWORD", "kasus"), ExpressionNode, Terminal("KEYWORD", "dari"), CaseListNode, Terminal("KEYWORD", "selesai")]
        ]

class CompoundStatementNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("KEYWORD", "mulai"), StatementListNode, Terminal("KEYWORD", "selesai")]
        ]

class StatementNode(ParseNode):
    def grammar(self):
        return [
            [AssignmentStatementNode],
            [IfStatementNode],
            [WhileStatementNode],
            [ForStatementNode],
            [RepeatStatementNode],
            [CaseStatementNode],
            [CompoundStatementNode],
            [ExpressionStatementNode],
            [EmptyStatementNode]
        ]

class StatementListTailNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("SEMICOLON"), StatementNode, StatementListTailNode],
            []
        ]

class StatementListNode(ParseNode):
    def grammar(self):
        return [
            [StatementNode, StatementListTailNode]
        ]

class RangeNode(ParseNode):
    def grammar(self):
        return [
            [ExpressionNode, Terminal("RANGE_OPERATOR"), ExpressionNode]
        ]

class ArrayTypeNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("KEYWORD", "larik"), Terminal("LBRACKET"), RangeNode, Terminal("RBRACKET"), Terminal("KEYWORD", "dari"), TypeNode]
        ]

class TypeNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("KEYWORD", "integer")],
            [Terminal("KEYWORD", "real")],
            [Terminal("KEYWORD", "boolean")],
            [Terminal("KEYWORD", "char")],
            [ArrayTypeNode],
            [Terminal("IDENTIFIER")]
        ]

class IdentifierListTailNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("COMMA"), Terminal("IDENTIFIER"), IdentifierListTailNode],
            []
        ]

class IdentifierListNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("IDENTIFIER"), IdentifierListTailNode]
        ]

class VarItemTailNode(ParseNode):
    def grammar(self):
        return [
            [VarItemNode, VarItemTailNode],
            []
        ]

class VarItemNode(ParseNode):
    def grammar(self):
        return [
            [IdentifierListNode, Terminal("COLON"), TypeDefinitionNode, Terminal("SEMICOLON")]
        ]

class VarDeclarationNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("KEYWORD", "variabel"), VarItemNode, VarItemTailNode]
        ]

class VarSectionNode(ParseNode):
    def grammar(self):
        return [
            [VarDeclarationNode, VarSectionNode],
            []
        ]

class FieldListTailNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("SEMICOLON"), FieldListNode],
            []
        ]

class FieldListNode(ParseNode):
    def grammar(self):
        return [
            [IdentifierListNode, Terminal("COLON"), TypeDefinitionNode, FieldListTailNode]
        ]

class RecordTypeNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("KEYWORD", "rekaman"), FieldListNode, Terminal("KEYWORD", "selesai")]
        ]

class TypeDefinitionNode(ParseNode):
    def grammar(self):
        return [
            [TypeNode],
            [ArrayTypeNode],
            [RecordTypeNode]
        ]

class TypeItemTailNode(ParseNode):
    def grammar(self):
        return [
            [TypeItemNode, TypeItemTailNode],
            []
        ]

class TypeItemNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("IDENTIFIER"), Terminal("RELATIONAL_OPERATOR", "="), TypeDefinitionNode, Terminal("SEMICOLON")]
        ]

class TypeDeclarationNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("KEYWORD", "tipe"), TypeItemNode, TypeItemTailNode]
        ]

class TypeSectionNode(ParseNode):
    def grammar(self):
        return [
            [TypeDeclarationNode, TypeSectionNode],
            []
        ]

class ConstItemTailNode(ParseNode):
    def grammar(self):
        return [
            [ConstItemNode, ConstItemTailNode],
            []
        ]

class ConstItemNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("IDENTIFIER"), Terminal("RELATIONAL_OPERATOR", "="), ValueNode, Terminal("SEMICOLON")]
        ]

class ConstDeclarationNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("KEYWORD", "konstanta"), ConstItemNode, ConstItemTailNode]
        ]

class ConstSectionNode(ParseNode):
    def grammar(self):
        return [
            [ConstDeclarationNode, ConstSectionNode],
            []
        ]

class ParameterModifierNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("KEYWORD", "variabel")],
            []
        ]

class ParameterGroupTailNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("SEMICOLON"), ParameterGroupNode, ParameterGroupTailNode],
            [Terminal("SEMICOLON")],
            []
        ]

class ParameterGroupNode(ParseNode):
    def grammar(self):
        return [
            [ParameterModifierNode, IdentifierListNode, Terminal("COLON"), TypeNode]
        ]

class FormalParameterListNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("LPARENTHESIS"), ParameterGroupNode, ParameterGroupTailNode, Terminal("RPARENTHESIS")]
        ]

class BlockNode(ParseNode):
    def grammar(self):
        return [
            [DeclarationPartNode, CompoundStatementNode]
        ]

class FunctionDeclarationNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("KEYWORD", "fungsi"), Terminal("IDENTIFIER"), FormalParameterListNode, Terminal("COLON"), TypeNode, Terminal("SEMICOLON"), BlockNode, Terminal("SEMICOLON")],
            [Terminal("KEYWORD", "fungsi"), Terminal("IDENTIFIER"), Terminal("COLON"), TypeNode, Terminal("SEMICOLON"), BlockNode, Terminal("SEMICOLON")]
        ]

class ProcedureDeclarationNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("KEYWORD", "prosedur"), Terminal("IDENTIFIER"), FormalParameterListNode, Terminal("SEMICOLON"), BlockNode, Terminal("SEMICOLON")],
            [Terminal("KEYWORD", "prosedur"), Terminal("IDENTIFIER"), Terminal("SEMICOLON"), BlockNode, Terminal("SEMICOLON")]
        ]

class SubprogramDeclarationNode(ParseNode):
    def grammar(self):
        return [
            [ProcedureDeclarationNode],
            [FunctionDeclarationNode]
        ]

class SubprogramSectionNode(ParseNode):
    def grammar(self):
        return [
            [SubprogramDeclarationNode, SubprogramSectionNode],
            []
        ]

class DeclarationPartNode(ParseNode):
    def grammar(self):
        return [
            [ConstSectionNode, TypeSectionNode, VarSectionNode, SubprogramSectionNode]
        ]

class ProgramHeaderNode(ParseNode):
    def grammar(self):
        return [
            [Terminal("KEYWORD", "program"), Terminal("IDENTIFIER"), Terminal("SEMICOLON")]
        ]

class ProgramNode(ParseNode):
    def grammar(self):
        return [
            [ProgramHeaderNode, DeclarationPartNode, CompoundStatementNode, Terminal("DOT")]
        ]
