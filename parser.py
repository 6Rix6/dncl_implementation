"""
Parser for DNCL (共通テスト手順記述標準言語).
Converts tokens into an Abstract Syntax Tree (AST).
"""

from typing import List, Optional
from lexer import Token, TokenType, Lexer
from ast_nodes import *


class Parser:
    """Parser for DNCL source code."""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = [t for t in tokens if t.type != TokenType.NEWLINE]  # Filter out newlines for easier parsing
        self.pos = 0
    
    def error(self, message: str):
        """Raise a parser error."""
        token = self.current()
        raise SyntaxError(f"Parser error at {token.line}:{token.column}: {message}")
    
    def current(self) -> Token:
        """Get current token."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # Return EOF
    
    def peek(self, offset: int = 1) -> Token:
        """Look ahead at token."""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]  # Return EOF
    
    def advance(self) -> Token:
        """Consume and return current token."""
        token = self.current()
        if token.type != TokenType.EOF:
            self.pos += 1
        return token
    
    def expect(self, token_type: TokenType) -> Token:
        """Consume token of expected type or raise error."""
        token = self.current()
        if token.type != token_type:
            self.error(f"Expected {token_type.name}, got {token.type.name}")
        return self.advance()
    
    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        return self.current().type in token_types
    
    def parse(self) -> Program:
        """Parse the entire program."""
        statements = []
        while not self.match(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return Program(statements)
    
    def parse_statement(self) -> Optional[Statement]:
        """Parse a single statement."""
        # Function definition
        if self.match(TokenType.FUNCTION):
            return self.parse_function_def()
        
        # Control structures
        if self.match(TokenType.IF):
            return self.parse_if_statement()
        
        if self.match(TokenType.DO_REPEAT):
            return self.parse_do_until()
        
        # Identifier - could be assignment, increment/decrement, array assignment, for loop, or start of expression
        if self.match(TokenType.IDENTIFIER):
            return self.parse_identifier_statement()
        
        # Expression-based statements (display, function calls, while loops)
        # These can start with STRING, NUMBER, or other expressions
        if self.match(TokenType.STRING, TokenType.NUMBER, TokenType.LPAREN):
            return self.parse_expression_statement()
        
        self.error(f"Unexpected token: {self.current().type.name}")
    
    def parse_identifier_statement(self) -> Statement:
        """Parse statement starting with identifier."""
        name = self.expect(TokenType.IDENTIFIER).value
        
        # Check for array assignment: "のすべての要素に"
        if self.match(TokenType.ALL_ELEMENTS):
            self.advance()
            value = self.parse_expression()
            self.expect(TokenType.ASSIGN_TO)
            return ArrayAssignAll(name, value)
        
        # Check for array indexing
        if self.match(TokenType.LBRACKET):
            indices = self.parse_array_indices()
            if self.match(TokenType.ASSIGN):
                # Array element assignment: Tokuten[i] ← value
                self.advance()
                value = self.parse_expression()
                return Assignment(name, indices, value)
            else:
                # Array access in expression (e.g., display): Tokuten[i] を表示する
                # Create ArrayAccess node and continue parsing as expression statement
                array_access = ArrayAccess(name, indices)
                return self._parse_expression_continuation(array_access)
        
        # Check for assignment
        if self.match(TokenType.ASSIGN):
            self.advance()
            value = self.parse_expression()
            return Assignment(name, None, value)
        
        # Check for "を" followed by number (for loop vs increment/decrement)
        if self.match(TokenType.FOR_WO):
            self.advance()
            
            # Parse the value after を
            value = self.parse_expression()
            
            # Check what comes after the value
            if self.match(TokenType.FROM):
                # It's a for loop: "i を 1 から 10 まで..."
                # value is the start value
                self.advance()  # skip から
                end = self.parse_expression()
                self.expect(TokenType.FOR_TO)
                step_value = self.parse_expression()
                self.expect(TokenType.FOR_BY)
                
                increment = True
                if self.match(TokenType.FOR_INCREASE):
                    self.advance()
                    increment = True
                elif self.match(TokenType.FOR_DECREASE):
                    self.advance()
                    increment = False
                else:
                    self.error("Expected 増やしながら or 減らしながら")
                
                # Skip optional trailing comma
                if self.match(TokenType.COMMA):
                    self.advance()
                
                body = self.parse_block(TokenType.REPEAT)
                self.expect(TokenType.REPEAT)
                
                return ForStatement(name, value, end, step_value, increment, body)
            
            elif self.match(TokenType.INCREASE):
                # It's an increment: "i を 1 増やす"
                self.advance()
                return Increment(name, value)
            
            elif self.match(TokenType.DECREASE):
                # It's a decrement: "i を 1 減らす"
                self.advance()
                return Decrement(name, value)
            
            elif self.match(TokenType.DISPLAY):
                # It's a display statement of単独 variable: "i を表示する"
                # Backtrack and handle as expression statement
                self.pos -= 2  # Go back past FOR_WO and name
                return self.parse_expression_statement()
            
            else:
                self.error(f"Expected FROM, INCREASE, DECREASE or DISPLAY after を, got {self.current().type.name}")
        
        # Check for condition (while loop): "x ＜ 10 の間"
        # Backtrack and parse as expression statement (display, while, or function call)
        self.pos -= 1  # Go back
        return self.parse_expression_statement()
    
    def parse_expression_statement(self) -> Statement:
        """Parse expression-based statement (display, while loop, or function call)."""
        # Try to parse as condition for while loop or display statement
        condition = self.parse_expression()
        
        if self.match(TokenType.WHILE):
            self.advance()
            # Skip optional comma
            if self.match(TokenType.COMMA):
                self.advance()
            body = self.parse_block(TokenType.REPEAT)
            self.expect(TokenType.REPEAT)
            return WhileStatement(condition, body)
        
        # Check for display
        expressions = [condition]
        while self.match(TokenType.AND):
            self.advance()
            expressions.append(self.parse_expression())
        
        if self.match(TokenType.DISPLAY):
            self.advance()
            return Display(expressions)
        
        # Could be function call statement
        if isinstance(condition, FunctionCall):
            return FunctionCallStatement(condition.name, condition.arguments)
        
        self.error("Expected statement")
    
    def _parse_expression_continuation(self, start_expr: Expression) -> Statement:
        """Continue parsing expression-based statement from a given expression."""
        # Similar to parse_expression_statement but starts with existing expression
        
        # Check for while loop
        if self.match(TokenType.WHILE):
            self.advance()
            # Skip optional comma
            if self.match(TokenType.COMMA):
                self.advance()
            body = self.parse_block(TokenType.REPEAT)
            self.expect(TokenType.REPEAT)
            return WhileStatement(start_expr, body)
        
        # Check for display
        expressions = [start_expr]
        while self.match(TokenType.AND):
            self.advance()
            expressions.append(self.parse_expression())
        
        if self.match(TokenType.DISPLAY):
            self.advance()
            return Display(expressions)
        
        # Could be function call statement
        if isinstance(start_expr, FunctionCall):
            return FunctionCallStatement(start_expr.name, start_expr.arguments)
        
        self.error("Expected statement after expression")
    
    
    def parse_if_statement(self) -> IfStatement:
        """Parse if statement."""
        self.expect(TokenType.IF)
        condition = self.parse_expression()
        self.expect(TokenType.THEN)
        
        then_body = self.parse_block(TokenType.EXECUTE, TokenType.AND_EXECUTE)
        
        elif_conditions = []
        elif_bodies = []
        else_body = None
        
        # Check for elif and else
        if self.match(TokenType.AND_EXECUTE):
            self.advance()
            
            # Check for elif
            while self.match(TokenType.ELIF):
                self.advance()
                elif_cond = self.parse_expression()
                self.expect(TokenType.THEN)
                elif_body = self.parse_block(TokenType.EXECUTE, TokenType.AND_EXECUTE)
                elif_conditions.append(elif_cond)
                elif_bodies.append(elif_body)
                
                if self.match(TokenType.AND_EXECUTE):
                    self.advance()
                else:
                    break
            
            # Check for else
            if self.match(TokenType.ELSE):
                self.advance()
                else_body = self.parse_block(TokenType.EXECUTE)
        
        self.expect(TokenType.EXECUTE)
        
        return IfStatement(
            condition,
            then_body,
            elif_conditions if elif_conditions else None,
            elif_bodies if elif_bodies else None,
            else_body
        )
    
    def parse_do_until(self) -> DoUntilStatement:
        """Parse do-until loop."""
        self.expect(TokenType.DO_REPEAT)
        # Skip optional trailing comma after 繰り返し
        if self.match(TokenType.COMMA):
            self.advance()
        body = self.parse_block(TokenType.FOR_WO)  # を
        self.expect(TokenType.FOR_WO)
        # Skip optional trailing comma after を
        if self.match(TokenType.COMMA):
            self.advance()
        condition = self.parse_expression()
        self.expect(TokenType.UNTIL)
        return DoUntilStatement(body, condition)
    
    def parse_for_loop(self, variable: str) -> ForStatement:
        """Parse for loop (variable already consumed)."""
        start = self.parse_expression()
        self.expect(TokenType.FROM)  # から
        end = self.parse_expression()
        self.expect(TokenType.FOR_TO)
        step_value = self.parse_expression()
        self.expect(TokenType.FOR_BY)

        
        increment = True
        if self.match(TokenType.FOR_INCREASE):
            self.advance()
            increment = True
        elif self.match(TokenType.FOR_DECREASE):
            self.advance()
            increment = False
        else:
            self.error("Expected 増やしながら or 減らしながら")
        
        # Skip optional trailing comma
        if self.match(TokenType.COMMA):
            self.advance()
        
        body = self.parse_block(TokenType.REPEAT)
        self.expect(TokenType.REPEAT)
        
        return ForStatement(variable, start, end, step_value, increment, body)
    
    def parse_function_def(self) -> FunctionDef:
        """Parse function definition."""
        self.expect(TokenType.FUNCTION)
        
        # Function name (can be Japanese)
        if not self.match(TokenType.IDENTIFIER):
            self.error("Expected function name")
        
        # Read function name (may include Japanese characters)
        name_parts = []
        while not self.match(TokenType.LPAREN):
            if self.match(TokenType.IDENTIFIER):
                name_parts.append(self.advance().value)
            else:
                name_parts.append(self.advance().value)  # Could be keyword used as name
        
        name = ''.join(name_parts)
        
        # Parameters
        self.expect(TokenType.LPAREN)
        params = []
        if not self.match(TokenType.RPAREN):
            params.append(self.expect(TokenType.IDENTIFIER).value)
            while self.match(TokenType.COMMA):
                self.advance()
                params.append(self.expect(TokenType.IDENTIFIER).value)
        self.expect(TokenType.RPAREN)
        
        self.expect(TokenType.FOR_WO)  # を
        
        # Body
        body = self.parse_block(TokenType.DEFINE)
        self.expect(TokenType.DEFINE)
        
        return FunctionDef(name, params, body)
    
    def parse_block(self, *end_tokens: TokenType) -> List[Statement]:
        """Parse a block of statements until end token."""
        statements = []
        while not self.match(*end_tokens) and not self.match(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return statements
    
    def parse_array_indices(self) -> List[Expression]:
        """Parse array indices [i] or [i, j]."""
        indices = []
        self.expect(TokenType.LBRACKET)
        indices.append(self.parse_expression())
        while self.match(TokenType.COMMA):
            self.advance()
            indices.append(self.parse_expression())
        self.expect(TokenType.RBRACKET)
        return indices
    
    def parse_expression(self) -> Expression:
        """Parse expression with logical operators."""
        return self.parse_logical_or()
    
    def parse_logical_or(self) -> Expression:
        """Parse 'または' (OR) expression."""
        left = self.parse_logical_and()
        
        while self.match(TokenType.LOGICAL_OR):
            op = self.advance().value
            right = self.parse_logical_and()
            left = BinaryOp(left, 'または', right)
        
        return left
    
    def parse_logical_and(self) -> Expression:
        """Parse 'かつ' (AND) expression."""
        left = self.parse_logical_not()
        
        while self.match(TokenType.LOGICAL_AND):
            op = self.advance().value
            right = self.parse_logical_not()
            left = BinaryOp(left, 'かつ', right)
        
        return left
    
    def parse_logical_not(self) -> Expression:
        """Parse 'でない' (NOT) expression."""
        if self.match(TokenType.LOGICAL_NOT):
            self.advance()
            operand = self.parse_logical_not()
            return UnaryOp('でない', operand)
        
        return self.parse_comparison()
    
    def parse_comparison(self) -> Expression:
        """Parse comparison expression."""
        left = self.parse_additive()
        
        if self.match(TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.GREATER,
                     TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            op_token = self.advance()
            op_map = {
                TokenType.EQUAL: '=',
                TokenType.NOT_EQUAL: '!=',
                TokenType.GREATER: '>',
                TokenType.GREATER_EQUAL: '>=',
                TokenType.LESS: '<',
                TokenType.LESS_EQUAL: '<=',
            }
            right = self.parse_additive()
            return BinaryOp(left, op_map[op_token.type], right)
        
        return left
    
    def parse_additive(self) -> Expression:
        """Parse addition/subtraction."""
        left = self.parse_multiplicative()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            right = self.parse_multiplicative()
            left = BinaryOp(left, '+' if op in ['＋', '+'] else '-', right)
        
        return left
    
    def parse_multiplicative(self) -> Expression:
        """Parse multiplication/division/modulo."""
        left = self.parse_unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.INT_DIVIDE, TokenType.MODULO):
            op_token = self.advance()
            right = self.parse_unary()
            
            op_map = {
                '×': '*',
                '*': '*',
                '/': '/',
                '÷': '//',
                '％': '%',
                '%': '%',
            }
            left = BinaryOp(left, op_map[op_token.value], right)
        
        return left
    
    def parse_unary(self) -> Expression:
        """Parse unary expression."""
        if self.match(TokenType.MINUS):
            self.advance()
            return UnaryOp('-', self.parse_unary())
        
        return self.parse_primary()
    
    def parse_primary(self) -> Expression:
        """Parse primary expression."""
        # Number
        if self.match(TokenType.NUMBER):
            value = self.advance().value
            return Number(value)
        
        # String
        if self.match(TokenType.STRING):
            value = self.advance().value
            return String(value)
        
        # External input
        if self.match(TokenType.INPUT):
            self.advance()
            return FunctionCall('input', [])
        
        # Parenthesized expression
        if self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        # Array literal
        if self.match(TokenType.LBRACE):
            return self.parse_array_literal()
        
        # Variable or function call
        if self.match(TokenType.IDENTIFIER):
            name = self.advance().value
            
            # Array access
            if self.match(TokenType.LBRACKET):
                indices = self.parse_array_indices()
                return ArrayAccess(name, indices)
            
            # Function call
            if self.match(TokenType.LPAREN):
                self.advance()
                args = []
                if not self.match(TokenType.RPAREN):
                    args.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        self.advance()
                        args.append(self.parse_expression())
                self.expect(TokenType.RPAREN)
                return FunctionCall(name, args)
            
            # Simple variable
            return Variable(name)
        
        self.error(f"Unexpected token in expression: {self.current().type.name}")
    
    def parse_array_literal(self) -> ArrayLiteral:
        """Parse array literal {1, 2, 3}."""
        self.expect(TokenType.LBRACE)
        elements = []
        if not self.match(TokenType.RBRACE):
            elements.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                self.advance()
                elements.append(self.parse_expression())
        self.expect(TokenType.RBRACE)
        return ArrayLiteral(elements)


def parse_dncl(source: str) -> Program:
    """Convenience function to parse DNCL source code."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()
