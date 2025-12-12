"""
Lexer for DNCL (共通テスト手順記述標準言語).
Tokenizes DNCL source code into a stream of tokens.
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    """Token types for DNCL."""
    # Literals
    NUMBER = auto()
    STRING = auto()
    
    # Identifiers and Keywords
    IDENTIFIER = auto()
    
    # Keywords
    IF = auto()                  # もし
    THEN = auto()                # ならば
    ELSE = auto()                # そうでなければ
    ELIF = auto()                # そうでなくもし
    EXECUTE = auto()             # を実行する
    AND_EXECUTE = auto()         # を実行し
    
    WHILE = auto()               # の間
    REPEAT = auto()              # を繰り返す
    DO_REPEAT = auto()           # 繰り返し
    UNTIL = auto()               # になるまで実行する
    
    FOR_WO = auto()              # を (for loops and general)
    FROM = auto()                # から  
    FOR_TO = auto()              # まで
    FOR_BY = auto()              # ずつ
    FOR_INCREASE = auto()        # 増やしながら
    FOR_DECREASE = auto()        # 減らしながら
    
    DISPLAY = auto()             # を表示する
    AND = auto()                 # と (for display)
    
    FUNCTION = auto()            # 関数
    DEFINE = auto()              # と定義する
    
    ALL_ELEMENTS = auto()        # のすべての要素に
    ASSIGN_TO = auto()           # を代入する
    
    INCREASE = auto()            # を〜増やす
    DECREASE = auto()            # を〜減らす
    
    INPUT = auto()              # 外部からの入力
    
    # Operators
    ASSIGN = auto()              # ← 
    PLUS = auto()                # ＋
    MINUS = auto()               # －
    MULTIPLY = auto()            # ×
    DIVIDE = auto()              # /
    INT_DIVIDE = auto()          # ÷
    MODULO = auto()              # ％
    
    # Comparison operators
    EQUAL = auto()               # ＝
    NOT_EQUAL = auto()           # ≠
    GREATER = auto()             # ＞
    GREATER_EQUAL = auto()       # ≧
    LESS = auto()                # ＜
    LESS_EQUAL = auto()          # ≦
    
    # Logical operators
    LOGICAL_AND = auto()         # かつ
    LOGICAL_OR = auto()          # または
    LOGICAL_NOT = auto()         # でない
    
    # Delimiters
    LPAREN = auto()              # (
    RPAREN = auto()              # )
    LBRACKET = auto()            # [ or 「 (for arrays)
    RBRACKET = auto()            # ] or 」
    LBRACE = auto()              # {
    RBRACE = auto()              # }
    COMMA = auto()               # , or ，
    
    # Special
    NEWLINE = auto()
    EOF = auto()


@dataclass
class Token:
    """Represents a single token."""
    type: TokenType
    value: any
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"


class Lexer:
    """Tokenizer for DNCL source code."""
    
    # Japanese keywords mapping
    KEYWORDS = {
        'もし': TokenType.IF,
        'ならば': TokenType.THEN,
        'そうでなければ': TokenType.ELSE,
        'そうでなくもし': TokenType.ELIF,
        'を実行する': TokenType.EXECUTE,
        'を実行し': TokenType.AND_EXECUTE,
        'の間': TokenType.WHILE,
        'を繰り返す': TokenType.REPEAT,
        '繰り返し': TokenType.DO_REPEAT,
        'になるまで実行する': TokenType.UNTIL,
        'を': TokenType.FOR_WO,
        'から': TokenType.FROM,
        'まで': TokenType.FOR_TO,
        'ずつ': TokenType.FOR_BY,
        '増やしながら': TokenType.FOR_INCREASE,
        '減らしながら': TokenType.FOR_DECREASE,
        'を表示する': TokenType.DISPLAY,
        'と': TokenType.AND,
        '関数': TokenType.FUNCTION,
        'と定義する': TokenType.DEFINE,
        'のすべての要素に': TokenType.ALL_ELEMENTS,
        'を代入する': TokenType.ASSIGN_TO,
        '増やす': TokenType.INCREASE,
        '減らす': TokenType.DECREASE,
        'かつ': TokenType.LOGICAL_AND,
        'または': TokenType.LOGICAL_OR,
        'でない': TokenType.LOGICAL_NOT,
        '【外部からの入力】': TokenType.INPUT,
    }
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def error(self, message: str):
        """Raise a lexer error."""
        raise SyntaxError(f"Lexer error at {self.line}:{self.column}: {message}")
    
    def peek(self, offset: int = 0) -> Optional[str]:
        """Look ahead at character without consuming."""
        pos = self.pos + offset
        if pos < len(self.source):
            return self.source[pos]
        return None
    
    def advance(self) -> Optional[str]:
        """Consume and return current character."""
        if self.pos >= len(self.source):
            return None
        
        char = self.source[self.pos]
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char
    
    def skip_whitespace(self):
        """Skip whitespace except newlines."""
        while self.peek() and self.peek() in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        """Skip comments (if we decide to support them)."""
        # DNCL spec doesn't mention comments, but we could add support for # or //
        pass
    
    def read_number(self) -> Token:
        """Read a numeric literal."""
        start_line, start_col = self.line, self.column
        num_str = ''
        
        while self.peek() and (self.peek().isdigit() or self.peek() in '.'):
            num_str += self.advance()
        
        value = float(num_str) if '.' in num_str else int(num_str)
        return Token(TokenType.NUMBER, value, start_line, start_col)
    
    def read_string(self, end_char: str) -> Token:
        """Read a string literal."""
        start_line, start_col = self.line, self.column
        self.advance()  # Skip opening quote
        
        value = ''
        while self.peek() and self.peek() != end_char:
            value += self.advance()
        
        if not self.peek():
            self.error(f"Unterminated string starting at {start_line}:{start_col}")
        
        self.advance()  # Skip closing quote
        return Token(TokenType.STRING, value, start_line, start_col)
    
    def read_identifier_or_keyword(self) -> Token:
        """Read an identifier or keyword."""
        start_line, start_col = self.line, self.column
        
        # Check for multi-character keywords first
        for keyword in sorted(self.KEYWORDS.keys(), key=len, reverse=True):
            if self.source[self.pos:self.pos + len(keyword)] == keyword:
                self.pos += len(keyword)
                self.column += len(keyword)
                return Token(self.KEYWORDS[keyword], keyword, start_line, start_col)
        
        # Read identifier (alphanumeric + underscore)
        identifier = ''
        while self.peek() and (self.peek().isalnum() or self.peek() == '_'):
            identifier += self.advance()
        
        return Token(TokenType.IDENTIFIER, identifier, start_line, start_col)
    
    def tokenize(self) -> List[Token]:
        """Tokenize the entire source code."""
        while self.pos < len(self.source):
            self.skip_whitespace()
            
            if self.pos >= len(self.source):
                break
            
            char = self.peek()
            
            # Newline
            if char == '\n':
                token = Token(TokenType.NEWLINE, char, self.line, self.column)
                self.advance()
                self.tokens.append(token)
                continue
            
            # Numbers
            if char.isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # String literals with 「」
            if char == '「':
                self.tokens.append(self.read_string('」'))
                continue
            
            # String literals with ""
            if char == '"':
                self.tokens.append(self.read_string('"'))
                continue
            
            # Operators and special characters
            token_line, token_col = self.line, self.column
            
            if char == '←':
                self.advance()
                self.tokens.append(Token(TokenType.ASSIGN, char, token_line, token_col))
            elif char == '＋':
                self.advance()
                self.tokens.append(Token(TokenType.PLUS, char, token_line, token_col))
            elif char == '－' or char == '-':
                self.advance()
                self.tokens.append(Token(TokenType.MINUS, char, token_line, token_col))
            elif char == '×':
                self.advance()
                self.tokens.append(Token(TokenType.MULTIPLY, char, token_line, token_col))
            elif char == '/':
                self.advance()
                self.tokens.append(Token(TokenType.DIVIDE, char, token_line, token_col))
            elif char == '÷':
                self.advance()
                self.tokens.append(Token(TokenType.INT_DIVIDE, char, token_line, token_col))
            elif char == '％' or char == '%':
                self.advance()
                self.tokens.append(Token(TokenType.MODULO, char, token_line, token_col))
            elif char == '＝':
                self.advance()
                self.tokens.append(Token(TokenType.EQUAL, char, token_line, token_col))
            elif char == '≠':
                self.advance()
                self.tokens.append(Token(TokenType.NOT_EQUAL, char, token_line, token_col))
            elif char == '＞':
                self.advance()
                self.tokens.append(Token(TokenType.GREATER, char, token_line, token_col))
            elif char == '≧':
                self.advance()
                self.tokens.append(Token(TokenType.GREATER_EQUAL, char, token_line, token_col))
            elif char == '＜':
                self.advance()
                self.tokens.append(Token(TokenType.LESS, char, token_line, token_col))
            elif char == '≦':
                self.advance()
                self.tokens.append(Token(TokenType.LESS_EQUAL, char, token_line, token_col))
            elif char == '(':
                self.advance()
                self.tokens.append(Token(TokenType.LPAREN, char, token_line, token_col))
            elif char == ')':
                self.advance()
                self.tokens.append(Token(TokenType.RPAREN, char, token_line, token_col))
            elif char == '[':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACKET, char, token_line, token_col))
            elif char == ']':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACKET, char, token_line, token_col))
            elif char == '{':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACE, char, token_line, token_col))
            elif char == '}':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACE, char, token_line, token_col))
            elif char == ',' or char == '，':
                self.advance()
                self.tokens.append(Token(TokenType.COMMA, char, token_line, token_col))
            
            # Identifiers and keywords
            elif char.isalpha() or char.isalnum() or ord(char) > 127:  # Japanese characters
                self.tokens.append(self.read_identifier_or_keyword())
            
            else:
                self.error(f"Unexpected character: {char!r}")
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens
