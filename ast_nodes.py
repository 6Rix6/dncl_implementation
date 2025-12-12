"""
AST (Abstract Syntax Tree) node definitions for DNCL.
"""

from typing import Any, List, Optional
from dataclasses import dataclass


# Base classes
@dataclass
class ASTNode:
    """Base class for all AST nodes."""
    pass


@dataclass
class Statement(ASTNode):
    """Base class for all statements."""
    pass


@dataclass
class Expression(ASTNode):
    """Base class for all expressions."""
    pass


# Literals and Variables
@dataclass
class Number(Expression):
    """Numeric literal."""
    value: float


@dataclass
class String(Expression):
    """String literal."""
    value: str


@dataclass
class Boolean(Expression):
    """Boolean literal."""
    value: bool


@dataclass
class Variable(Expression):
    """Variable reference."""
    name: str


@dataclass
class ArrayAccess(Expression):
    """Array element access (e.g., Tokuten[2] or Gyoretu[3, 2])."""
    name: str
    indices: List[Expression]


@dataclass
class ArrayLiteral(Expression):
    """Array literal (e.g., {87, 45, 72, 100})."""
    elements: List[Expression]


# Operators
@dataclass
class BinaryOp(Expression):
    """Binary operation (e.g., x + y, a かつ b)."""
    left: Expression
    operator: str  # '+', '-', '*', '/', '//', '%', '=', '!=', '>', '>=', '<', '<=', 'かつ', 'または'
    right: Expression


@dataclass
class UnaryOp(Expression):
    """Unary operation (e.g., でない x)."""
    operator: str  # 'でない'
    operand: Expression


# Statements
@dataclass
class Assignment(Statement):
    """Assignment statement (e.g., x ← 5, Tokuten[2] ← 100)."""
    target: str  # variable name or array name
    indices: Optional[List[Expression]]  # None for simple variables, list for arrays
    value: Expression


@dataclass
class ArrayAssignAll(Statement):
    """Assign same value to all array elements (e.g., Tokuten のすべての要素に 0 を代入する)."""
    array_name: str
    value: Expression


@dataclass
class Increment(Statement):
    """Increment statement (e.g., kosu を 1 増やす)."""
    variable: str
    amount: Expression


@dataclass
class Decrement(Statement):
    """Decrement statement (e.g., saihu を syuppi 減らす)."""
    variable: str
    amount: Expression


@dataclass
class Display(Statement):
    """Display statement (e.g., kosu と「個見つかった」を表示する)."""
    expressions: List[Expression]


@dataclass
class IfStatement(Statement):
    """
    Conditional statement.
    もし <condition> ならば
        <then_body>
    を実行し、そうでなくもし <elif_conditions>
        <elif_bodies>
    を実行し、そうでなければ
        <else_body>
    を実行する
    """
    condition: Expression
    then_body: List[Statement]
    elif_conditions: Optional[List[Expression]] = None
    elif_bodies: Optional[List[List[Statement]]] = None
    else_body: Optional[List[Statement]] = None


@dataclass
class WhileStatement(Statement):
    """
    While loop (前判定).
    <condition> の間、
        <body>
    を繰り返す
    """
    condition: Expression
    body: List[Statement]


@dataclass
class DoUntilStatement(Statement):
    """
    Do-until loop (後判定).
    繰り返し、
        <body>
    を、<condition> になるまで実行する
    """
    body: List[Statement]
    condition: Expression


@dataclass
class ForStatement(Statement):
    """
    For loop (順次繰返し).
    <variable> を <start> から <end> まで <step> ずつ増やしながら、
        <body>
    を繰り返す
    """
    variable: str
    start: Expression
    end: Expression
    step: Expression
    increment: bool  # True for 増やしながら, False for 減らしながら
    body: List[Statement]


@dataclass
class FunctionDef(Statement):
    """
    Function definition.
    関数 <name>(<params>) を
        <body>
    と定義する
    """
    name: str
    params: List[str]
    body: List[Statement]
    returns_value: bool = True  # True if function returns a value, False otherwise


@dataclass
class FunctionCall(Expression):
    """Function call expression (e.g., 二乗(x), べき乗(x, y))."""
    name: str
    arguments: List[Expression]


@dataclass
class FunctionCallStatement(Statement):
    """Function call as a statement (for functions that don't return values)."""
    name: str
    arguments: List[Expression]


@dataclass
class Return(Statement):
    """Return statement (implicit in DNCL through result values)."""
    value: Optional[Expression] = None


@dataclass
class Program(ASTNode):
    """Root node representing the entire program."""
    statements: List[Statement]
