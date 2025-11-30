from ast_nodes import *
from parser2 import Token

class ASTTransformer:
    def transform(self, node):
        if node is None:
            return None
        
        if isinstance(node, Token):
            return self.visit_token(node)
        
        method_name = f"visit_{node.name}"
        
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        if not node.children:
            return None
        if len(node.children) == 1:
            return self.transform(node.children[0])
        return [self.transform(child) for child in node.children]

    def get_token_val(self, token):
        if isinstance(token, Token):
            return token.nilai if token.nilai is not None else token.tipe
        if isinstance(token, VarNode):
            return token.identifier
        return str(token)

    def visit_token(self, token):
        tipe = token.tipe
        val = token.nilai
        
        if tipe == "NUMBER": 
            return NumberNode(val)
        if tipe == "CHAR_LITERAL": 
            return CharNode(val)
        if tipe == "STRING_LITERAL": 
            return StringNode(val)
        if tipe == "IDENTIFIER": 
            return VarNode(val) 
        if tipe == "KEYWORD": 
             if val in ["benar", "salah"]: 
                 return BooleanNode(val)
             return val 
        if "OPERATOR" in tipe:
            return OperatorNode(val)
        
        return val if val else tipe 

    def visit_ProgramNode(self, node):
        header = self.transform(node.children[0])
        decl = self.transform(node.children[1])
        body = self.transform(node.children[2])
        return ProgramNode(header, decl, body)

    def visit_ProgramHeaderNode(self, node):
        id_node = self.transform(node.children[1]) # returns VarNode
        return ProgramHeaderNode(id_node.identifier)

    def visit_DeclarationPartNode(self, node):
        return DeclarationPartNode(
            self.transform(node.children[0]),
            self.transform(node.children[1]),
            self.transform(node.children[2]),
            self.transform(node.children[3])
        )


    def visit_ConstSectionNode(self, node):
        if not node.children:
            return ConstSectionNode(None, None)
        return ConstSectionNode(
            self.transform(node.children[0]),
            self.transform(node.children[1])
        )

    def visit_ConstDeclarationNode(self, node):
        return ConstDeclNode(
            self.transform(node.children[1]),
            self.transform(node.children[2])
        )

    def visit_ConstItemNode(self, node):
        return ConstItemNode(
            self.get_token_val(node.children[0]),
            self.get_token_val(node.children[1]),
            self.transform(node.children[2])
        )

    def visit_ConstItemTailNode(self, node):
        if not node.children:
            return ConstTailNode(None, None)
        return ConstTailNode(
            self.transform(node.children[0]),
            self.transform(node.children[1])
        )

    def visit_TypeSectionNode(self, node):
        if not node.children:
            return TypeSectionNode(None, None)
        return TypeSectionNode(
            self.transform(node.children[0]),
            self.transform(node.children[1])
        )

    def visit_TypeDeclarationNode(self, node):
        return TypeDeclNode(
            self.transform(node.children[1]),
            self.transform(node.children[2])
        )

    def visit_TypeItemNode(self, node):
        id_node = self.transform(node.children[0])
        return TypeItemNode(
            id_node.identifier,
            self.transform(node.children[2])
        )

    def visit_TypeItemTailNode(self, node):
        if not node.children:
            return TypeTailNode(None, None)
        return TypeTailNode(
            self.transform(node.children[0]),
            self.transform(node.children[1])
        )

    def visit_TypeDefinitionNode(self, node):
        return self.transform(node.children[0])

    def visit_TypeNode(self, node):
        child = self.transform(node.children[0])
        if isinstance(child, ArrayTypeNode):
            return child
        if isinstance(child, VarNode):
            return TypeNode(child.identifier)
        return TypeNode(child)

    def visit_ArrayTypeNode(self, node):
        return ArrayTypeNode(
            self.transform(node.children[2]),
            self.transform(node.children[5])
        )

    def visit_RangeNode(self, node):
        return RangeNode(
            self.transform(node.children[0]),
            self.transform(node.children[1]),
            self.transform(node.children[2])
        )

    def visit_RecordTypeNode(self, node):
        return RecordTypeNode(self.transform(node.children[1]))

    def visit_FieldListNode(self, node):
        return FieldListNode(
            self.transform(node.children[0]),
            self.transform(node.children[2]),
            self.transform(node.children[3])
        )

    def visit_FieldListTailNode(self, node):
        if not node.children:
            return FieldListTailNode() 
        return self.transform(node.children[1])

    def visit_VarSectionNode(self, node):
        if not node.children:
            return VarSectionNode(None, None)
        return VarSectionNode(
            self.transform(node.children[0]),
            self.transform(node.children[1])
        )

    def visit_VarDeclarationNode(self, node):
        return VarDeclNode(
            self.transform(node.children[1]),
            self.transform(node.children[2])
        )

    def visit_VarItemNode(self, node):
        return VarItemNode(
            self.transform(node.children[0]),
            self.transform(node.children[2])
        )

    def visit_VarItemTailNode(self, node):
        if not node.children:
            return VarTailNode(None, None)
        return VarTailNode(
            self.transform(node.children[0]),
            self.transform(node.children[1])
        )

    def visit_IdentifierListNode(self, node):
        id_node = self.transform(node.children[0])
        return IdentifierListNode(
            id_node.identifier,
            self.transform(node.children[1])
        )

    def visit_IdentifierListTailNode(self, node):
        if not node.children:
            return IdentifierListTailNode(None, None)
        id_node = self.transform(node.children[1])
        return IdentifierListTailNode(
            id_node.identifier,
            self.transform(node.children[2])
        )

    def visit_SubprogramSectionNode(self, node):
        if not node.children:
            return SubprogramSectionNode(None, None)
        return SubprogramSectionNode(
            self.transform(node.children[0]),
            self.transform(node.children[1])
        )

    def visit_SubprogramDeclarationNode(self, node):
        return self.transform(node.children[0])

    def visit_ProcedureDeclarationNode(self, node):
        id_node = self.transform(node.children[1]).identifier
        
        if len(node.children) == 6:
            return ProcedureNode(
                id_node,
                self.transform(node.children[2]),
                self.transform(node.children[4])
            )
        else:
            return ProcedureNode(
                id_node,
                None,
                self.transform(node.children[3])
            )

    def visit_FunctionDeclarationNode(self, node):
        id_node = self.transform(node.children[1]).identifier
        
        if len(node.children) == 8:
            return FunctionNode(
                id_node,
                self.transform(node.children[2]),
                self.transform(node.children[4]),
                self.transform(node.children[6])
            )
        else:
            return FunctionNode(
                id_node,
                None,
                self.transform(node.children[3]),
                self.transform(node.children[5])
            )

    def visit_FormalParameterListNode(self, node):
        return ParamListNode(
            self.transform(node.children[1]),
            self.transform(node.children[2])
        )

    def visit_ParameterGroupNode(self, node):
        return ParamGroupNode(
            self.transform(node.children[0]),
            self.transform(node.children[1]),
            self.transform(node.children[3])
        )

    def visit_ParameterGroupTailNode(self, node):
        if not node.children:
            return ParamTailNode(None, None, None)
        
        if len(node.children) == 1:
             return ParamTailNode(None, None, None)
             
        return ParamTailNode(
            self.transform(node.children[1]),
            self.transform(node.children[2])
        )

    def visit_ParameterModifierNode(self, node):
        if not node.children:
            return ParamModifierNode(None)
        return ParamModifierNode(self.get_token_val(node.children[0]))

    def visit_BlockNode(self, node):
        return BlockNode(
            self.transform(node.children[0]),
            self.transform(node.children[1])
        )

    def visit_CompoundStatementNode(self, node):
        return CompoundNode(self.transform(node.children[1]))

    def visit_StatementListNode(self, node):
        return StatementListNode(
            self.transform(node.children[0]),
            self.transform(node.children[1])
        )

    def visit_StatementListTailNode(self, node):
        if not node.children:
            return StatementTailNode(None, None)
        return StatementTailNode(
            self.transform(node.children[1]),
            self.transform(node.children[2])
        )

    def visit_StatementNode(self, node):
        return self.transform(node.children[0])

    def visit_AssignmentStatementNode(self, node):
        left = self.transform(node.children[0])
        expr = self.transform(node.children[2])
        
        if isinstance(left, VarNode):
            return AssignNode(left, None, expr)
        elif isinstance(left, FieldAccessNode):
            return AssignNode(None, left, expr)
        return AssignNode(left, None, expr)

    def visit_IfStatementNode(self, node):
        expr = self.transform(node.children[1])
        stmt_then = self.transform(node.children[3])
        
        stmt_else = None
        if len(node.children) > 4:
            stmt_else = self.transform(node.children[5])
            
        return IfNode(expr, stmt_then, stmt_else)

    def visit_WhileStatementNode(self, node):
        return WhileNode(
            self.transform(node.children[1]),
            self.transform(node.children[3])
        )

    def visit_ForStatementNode(self, node):
        id_node = self.transform(node.children[1]).identifier
        return ForNode(
            id_node,
            self.transform(node.children[3]),
            self.transform(node.children[5]),
            self.get_token_val(node.children[4]),
            self.transform(node.children[7])
        )

    def visit_RepeatStatementNode(self, node):
        return RepeatNode(
            self.transform(node.children[1]),
            self.transform(node.children[3])
        )

    def visit_CaseStatementNode(self, node):
        return CaseNode(
            self.transform(node.children[1]),
            self.transform(node.children[3])
        )

    def visit_CaseListNode(self, node):
        return CaseListNode(
            self.transform(node.children[0]),
            self.transform(node.children[1])
        )

    def visit_CaseListTailNode(self, node):
        if not node.children or len(node.children) == 1:
            return CaseListTailNode(None, None)
        return CaseListTailNode(
            self.transform(node.children[1]),
            self.transform(node.children[2])
        )

    def visit_CaseElementNode(self, node):
        return CaseElementNode(
            self.transform(node.children[0]),
            self.transform(node.children[2])
        )

    def visit_ExpressionStatementNode(self, node):
        return self.transform(node.children[0])

    def visit_EmptyStatementNode(self, node):
        return EmptyNode()

    def visit_ExpressionNode(self, node):
        if len(node.children) == 3:
            return BinOpNode(
                self.transform(node.children[1]),
                self.transform(node.children[0]),
                self.transform(node.children[2])
            )
        else:
            return self.transform(node.children[0])

    def visit_SimpleExpressionNode(self, node):
        
        if len(node.children) == 3:
            return UnaryOpNode(
                self.transform(node.children[0]),
                self.transform(node.children[1]),
                None,
                self.transform(node.children[2])
            )
        else:
            return SimpleExprNode(
                self.transform(node.children[0]),
                self.transform(node.children[1])
            )

    def visit_SimpleExpressionTailNode(self, node):
        if not node.children:
            return SimpleExprTailNode(None, None, None)
        return SimpleExprTailNode(
            self.transform(node.children[0]),
            self.transform(node.children[1]),
            self.transform(node.children[2])
        )

    def visit_TermNode(self, node):
        return TermNode(
            self.transform(node.children[0]),
            self.transform(node.children[1])
        )

    def visit_TermTailNode(self, node):
        if not node.children:
            return TermTailNode(None, None, None)
        return TermTailNode(
            self.transform(node.children[0]),
            self.transform(node.children[1]),
            self.transform(node.children[2])
        )

    def visit_FactorNode(self, node):
        first = node.children[0]
        
        if isinstance(first, Token):
            if first.tipe == "LPARENTHESIS":
                return self.transform(node.children[1])
            if first.nilai == "tidak":
                return UnaryOpNode(
                    OperatorNode("tidak"),
                    None,
                    self.transform(node.children[1]),
                    None
                )
        
        return self.transform(first)

    def visit_ValueNode(self, node):
        return self.transform(node.children[0])

    def visit_CallNode(self, node):
        id_node = self.transform(node.children[0]).identifier
        
        params = None
        if len(node.children) == 4:
            params = self.transform(node.children[2])
            
        return CallNode(id_node, params)

    def visit_ParameterListNode(self, node):
        return ParamListNode(
            self.transform(node.children[0]),
            self.transform(node.children[1])
        )

    def visit_ParameterListTailNode(self, node):
        if not node.children:
            return ParamTailNode(None, None, None)
        return ParamTailNode(
            self.transform(node.children[1]),
            self.transform(node.children[2])
        )

    def visit_NumberNode(self, node):
        if len(node.children) == 3:
            val1 = self.get_token_val(node.children[0])
            dot = self.get_token_val(node.children[1])
            val2 = self.get_token_val(node.children[2])
            return NumberNode(val1, dot, val2)
        else:
            val1 = self.get_token_val(node.children[0])
            return NumberNode(val1, None, None)

    def visit_FieldAccessNode(self, node):
        id1 = self.transform(node.children[0]).identifier
        id2 = self.transform(node.children[2]).identifier
        tail = self.transform(node.children[3])
        return FieldAccessNode(id1, id2, tail)

    def visit_FieldAccessTailNode(self, node):
        if not node.children:
            return FieldAccessTailNode(None, None)
        id_node = self.transform(node.children[1])
        return FieldAccessTailNode(
            id_node.identifier,
            self.transform(node.children[2])
        )

    def visit_RelationalOperatorNode(self, node):
        return self.transform(node.children[0])

    def visit_AdditiveOperatorNode(self, node):
        return self.transform(node.children[0])

    def visit_MultiplicativeOperatorNode(self, node):
        return self.transform(node.children[0])
