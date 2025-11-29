from ast_nodes import *
from parser2 import Token

class ASTTransformer:
    def transform(self, node):
        if not node:
            return None
        
        if isinstance(node, Token):
            return self.visit_token(node)
            
        method_name = f"visit_{node.name}"
        
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No visitor method defined for {node.name}")

    def get_token_val(self, token):
        if isinstance(token, Token):
            return token.nilai if token.nilai is not None else token.tipe
        return str(token)

    def visit_token(self, token):
        tipe = token.tipe
        val = token.nilai
        
        if tipe == "NUMBER": return NumberNode(val)
        if tipe == "CHAR_LITERAL": return CharNode(val)
        if tipe == "STRING_LITERAL": return StringNode(val)
        if tipe == "IDENTIFIER": return VarNode(val) 
        if tipe == "KEYWORD": 
             if val in ["benar", "salah"]: return BooleanNode(val)
             return val 
        
        return val if val else tipe 

    def visit_ProgramNode(self, node):
        header = self.transform(node.children[0])
        decls = self.transform(node.children[1])
        compound = self.transform(node.children[2])
        return ProgramNode(header, decls, compound)

    def visit_ProgramHeaderNode(self, node):
        id_val = self.get_token_val(node.children[1])
        return ProgramHeaderNode(id_val)

    def visit_BlockNode(self, node):
        return BlockNode(self.transform(node.children[0]), self.transform(node.children[1]))

    def visit_DeclarationPartNode(self, node):
        return DeclarationPartNode(
            self.transform(node.children[0]),
            self.transform(node.children[1]),
            self.transform(node.children[2]),
            self.transform(node.children[3]) 
        )

    def visit_ConstSectionNode(self, node):
        if not node.children: return ConstSectionNode()
        return ConstSectionNode(self.transform(node.children[0]), self.transform(node.children[1]))

    def visit_ConstDeclarationNode(self, node):
        return ConstDeclNode(self.transform(node.children[1]), self.transform(node.children[2]))

    def visit_ConstItemNode(self, node):
        val_node = self.transform(node.children[2])
        return ConstItemNode("=", val_node) 

    def visit_ConstItemTailNode(self, node):
        if not node.children: return ConstTailNode()
        return ConstTailNode(self.transform(node.children[0]), self.transform(node.children[1]))

    def visit_TypeSectionNode(self, node):
        if not node.children: return TypeSectionNode()
        return TypeSectionNode(self.transform(node.children[0]), self.transform(node.children[1]))

    def visit_TypeDeclarationNode(self, node):
        return TypeDeclNode(self.transform(node.children[1]), self.transform(node.children[2]))

    def visit_TypeItemNode(self, node):
        id_val = self.get_token_val(node.children[0])
        type_def = self.transform(node.children[2])
        return TypeItemNode(id_val, type_def)

    def visit_TypeItemTailNode(self, node):
        if not node.children: return TypeTailNode()
        return TypeTailNode(self.transform(node.children[0]), self.transform(node.children[1]))

    def visit_TypeNode(self, node):
        first_child = node.children[0]
        
        if isinstance(first_child, Token):
            val = self.get_token_val(first_child)
            return TypeNode(val)
        
        return self.transform(first_child)

    def visit_ArrayTypeNode(self, node):
        return ArrayTypeNode(self.transform(node.children[2]), self.transform(node.children[5]))

    def visit_RangeNode(self, node):
        return RangeNode(self.transform(node.children[0]), self.transform(node.children[2]))

    def visit_VarSectionNode(self, node):
        if not node.children: return VarSectionNode()
        return VarSectionNode(self.transform(node.children[0]), self.transform(node.children[1]))

    def visit_VarDeclarationNode(self, node):
        return VarDeclNode(self.transform(node.children[1]), self.transform(node.children[2]))

    def visit_VarItemNode(self, node):
        return VarItemNode(self.transform(node.children[0]), self.transform(node.children[2]))

    def visit_VarItemTailNode(self, node):
        if not node.children: return VarTailNode()
        return VarTailNode(self.transform(node.children[0]), self.transform(node.children[1]))

    def visit_IdentifierListNode(self, node):
        id_val = self.get_token_val(node.children[0])
        return IdentifierListNode(id_val, self.transform(node.children[1]))

    def visit_IdentifierListTailNode(self, node):
        if not node.children: return IdentifierListTailNode()
        id_val = self.get_token_val(node.children[1])
        return IdentifierListTailNode(id_val, self.transform(node.children[2]))

    def visit_SubprogramSectionNode(self, node):
        if not node.children: return SubprogramSectionNode()
        return SubprogramSectionNode(self.transform(node.children[0]), self.transform(node.children[1]))

    def visit_SubprogramDeclarationNode(self, node):
        return self.transform(node.children[0])

    def visit_ProcedureDeclarationNode(self, node):
        id_val = self.get_token_val(node.children[1])
        
        if len(node.children) == 5: 
            block = self.transform(node.children[3])
            return ProcedureNode(id_val, None, block)
        else: 
            params = self.transform(node.children[2])
            block = self.transform(node.children[4])
            return ProcedureNode(id_val, params, block)

    def visit_FunctionDeclarationNode(self, node):
        id_val = self.get_token_val(node.children[1])
        
        if len(node.children) == 7:
            type_node = self.transform(node.children[3])
            block = self.transform(node.children[5])
            return FunctionNode(id_val, None, type_node, block)
        else:
            params = self.transform(node.children[2])
            type_node = self.transform(node.children[4])
            block = self.transform(node.children[6])
            return FunctionNode(id_val, params, type_node, block)

    def visit_FormalParameterListNode(self, node):
        return ParamListNode(self.transform(node.children[1]), self.transform(node.children[2]))

    def visit_ParameterGroupNode(self, node):
        return ParamGroupNode(self.transform(node.children[0]), self.transform(node.children[1]), self.transform(node.children[3]))

    def visit_ParameterModifierNode(self, node):
        if not node.children: return ParamModifierNode()
        kw = self.get_token_val(node.children[0])
        return ParamModifierNode(kw)

    def visit_ParameterGroupTailNode(self, node):
        if not node.children or len(node.children) == 1: 
            return ParamTailNode()
            
        return ParamTailNode(self.transform(node.children[1]), self.transform(node.children[2]))

    def visit_CompoundStatementNode(self, node):
        return CompoundNode(self.transform(node.children[1]))

    def visit_StatementListNode(self, node):
        return StatementListNode(self.transform(node.children[0]), self.transform(node.children[1]))

    def visit_StatementListTailNode(self, node):
        if not node.children: return StatementTailNode()
        return StatementTailNode(self.transform(node.children[1]), self.transform(node.children[2]))

    def visit_StatementNode(self, node):
        return self.transform(node.children[0])

    def visit_EmptyStatementNode(self, node):
        return EmptyNode()

    def visit_AssignmentStatementNode(self, node):
        id_val = self.get_token_val(node.children[0])
        expr = self.transform(node.children[2])
        return AssignNode(VarNode(id_val), expr)

    def visit_IfStatementNode(self, node):
        cond = self.transform(node.children[1])
        then_stmt = self.transform(node.children[3])
        else_stmt = None
        
        if len(node.children) == 6:
            else_stmt = self.transform(node.children[5])
            
        return IfNode(cond, then_stmt, else_stmt)

    def visit_WhileStatementNode(self, node):
        return WhileNode(self.transform(node.children[1]), self.transform(node.children[3]))

    def visit_ForStatementNode(self, node):
        id_val = self.get_token_val(node.children[1])
        start_expr = self.transform(node.children[3])
        direction_kw = self.get_token_val(node.children[4])
        end_expr = self.transform(node.children[5])
        stmt = self.transform(node.children[7])
        
        return ForNode(id_val, start_expr, end_expr, direction_kw, stmt)

    def visit_RepeatStatementNode(self, node):
        return RepeatNode(self.transform(node.children[1]), self.transform(node.children[3]))

    def visit_CaseStatementNode(self, node):
        return CaseNode(self.transform(node.children[1]), self.transform(node.children[3]))

    def visit_CaseListNode(self, node):
        return CaseListNode(self.transform(node.children[0]), self.transform(node.children[1]))

    def visit_CaseListTailNode(self, node):
        if not node.children or len(node.children) == 1: 
            return CaseListTailNode()
        return CaseListTailNode(self.transform(node.children[1]), self.transform(node.children[2]))

    def visit_CaseElementNode(self, node):
        return CaseElementNode(self.transform(node.children[0]), self.transform(node.children[2]))

    def visit_ExpressionStatementNode(self, node):
        return self.transform(node.children[0])

    def visit_CallNode(self, node):
        id_val = self.get_token_val(node.children[0])
        params = None
        if len(node.children) == 4:
            params = self.transform(node.children[2])
            
        return CallNode(id_val, params)

    def visit_ParameterListNode(self, node):
        return ParamListNode(self.transform(node.children[0]), self.transform(node.children[1]))

    def visit_ParameterListTailNode(self, node):
        if not node.children: return ParamTailNode()
        return ParamTailNode(self.transform(node.children[1]), self.transform(node.children[2]))

    def visit_ExpressionNode(self, node):
        if len(node.children) == 1:
            return self.transform(node.children[0])
        else:
            left = self.transform(node.children[0])
            op = self.transform(node.children[1]) 
            right = self.transform(node.children[2])
            return BinOpNode(op, left, right)

    def visit_SimpleExpressionNode(self, node):
        if len(node.children) == 3:
            op_val = self.get_token_val(node.children[0])
            return UnaryOpNode(op_val, self.transform(node.children[1]), self.transform(node.children[2]))
        
        return SimpleExprNode(self.transform(node.children[0]), self.transform(node.children[1]))

    def visit_SimpleExpressionTailNode(self, node):
        if not node.children: return SimpleExprTailNode()
        return SimpleExprTailNode(self.transform(node.children[0]), self.transform(node.children[1]), self.transform(node.children[2]))

    def visit_TermNode(self, node):
        return TermNode(self.transform(node.children[0]), self.transform(node.children[1]))

    def visit_TermTailNode(self, node):
        if not node.children: return TermTailNode()
        return TermTailNode(self.transform(node.children[0]), self.transform(node.children[1]), self.transform(node.children[2]))

    def visit_FactorNode(self, node):
        first = node.children[0]
        
        if isinstance(first, Token):
            val = self.get_token_val(first)
            if val == 'tidak':
                return UnaryOpNode(val, self.transform(node.children[1]))
            elif val == '(':
                return self.transform(node.children[1])
        
        return self.transform(first)

    def visit_ValueNode(self, node):
        return self.transform(node.children[0])

    def visit_RelationalOperatorNode(self, node):
        return OperatorNode(self.get_token_val(node.children[0]))

    def visit_AdditiveOperatorNode(self, node):
        return OperatorNode(self.get_token_val(node.children[0]))

    def visit_MultiplicativeOperatorNode(self, node):
        return OperatorNode(self.get_token_val(node.children[0]))
