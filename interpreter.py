"""
Interpreter for DNCL (共通テスト手順記述標準言語).
Executes the Abstract Syntax Tree (AST).
"""

import sys
from typing import Any, Dict, List, Optional
from ast_nodes import *
import random


class Environment:
    """Environment for variable storage with scope support."""
    
    def __init__(self, parent: Optional['Environment'] = None):
        self.variables: Dict[str, Any] = {}
        self.parent = parent
    
    def get(self, name: str) -> Any:
        """Get variable value."""
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Variable '{name}' is not defined")
    
    def set(self, name: str, value: Any):
        """Set variable value."""
        self.variables[name] = value
    
    def update(self, name: str, value: Any):
        """Update existing variable."""
        if name in self.variables:
            self.variables[name] = value
        elif self.parent:
            self.parent.update(name, value)
        else:
            self.variables[name] = value


class ReturnValue(Exception):
    """Exception used to implement return statements."""
    def __init__(self, value: Any):
        self.value = value


class Interpreter:
    """Interpreter for DNCL AST."""
    
    def __init__(self):
        self.global_env = Environment()
        self.current_env = self.global_env
        self.functions: Dict[str, FunctionDef] = {}
        self.output_buffer: List[str] = []
        
        # Register built-in functions
        self.register_builtins()
    
    def register_builtins(self):
        """Register built-in functions."""
        # These can be overridden by user-defined functions
        self.builtin_functions = {
            'input': self._builtin_input,
            '乱数': self._builtin_random,
            '奇数': self._builtin_is_odd,
            '二乗': self._builtin_square,
            'べき乗': self._builtin_power,
        }
    
    def _builtin_input(self, args: List[Any]) -> Any:
        """Built-in input function."""
        return input()
    
    def _builtin_random(self, args: List[Any]) -> int:
        """Built-in random function: 乱数(m, n) returns random int between m and n."""
        if len(args) != 2:
            raise ValueError("乱数 requires 2 arguments")
        m, n = int(args[0]), int(args[1])
        return random.randint(m, n)
    
    def _builtin_is_odd(self, args: List[Any]) -> bool:
        """Built-in odd check: 奇数(n) returns true if n is odd."""
        if len(args) != 1:
            raise ValueError("奇数 requires 1 argument")
        return int(args[0]) % 2 == 1
    
    def _builtin_square(self, args: List[Any]) -> float:
        """Built-in square function: 二乗(x) returns x²."""
        if len(args) != 1:
            raise ValueError("二乗 requires 1 argument")
        x = args[0]
        return x * x
    
    def _builtin_power(self, args: List[Any]) -> float:
        """Built-in power function: べき乗(m, n) returns m^n."""
        if len(args) != 2:
            raise ValueError("べき乗 requires 2 arguments")
        m, n = args[0], args[1]
        return m ** n
    
    def run(self, program: Program):
        """Run the program."""
        self.visit_program(program)
    
    def visit_program(self, node: Program):
        """Visit program node."""
        for statement in node.statements:
            self.visit_statement(statement)
    
    def visit_statement(self, node: Statement) -> Any:
        """Visit statement node."""
        if isinstance(node, Assignment):
            return self.visit_assignment(node)
        elif isinstance(node, ArrayAssignAll):
            return self.visit_array_assign_all(node)
        elif isinstance(node, Increment):
            return self.visit_increment(node)
        elif isinstance(node, Decrement):
            return self.visit_decrement(node)
        elif isinstance(node, Display):
            return self.visit_display(node)
        elif isinstance(node, IfStatement):
            return self.visit_if_statement(node)
        elif isinstance(node, WhileStatement):
            return self.visit_while_statement(node)
        elif isinstance(node, DoUntilStatement):
            return self.visit_do_until_statement(node)
        elif isinstance(node, ForStatement):
            return self.visit_for_statement(node)
        elif isinstance(node, FunctionDef):
            return self.visit_function_def(node)
        elif isinstance(node, FunctionCallStatement):
            return self.visit_function_call_statement(node)
        elif isinstance(node, Return):
            raise ReturnValue(self.visit_expression(node.value) if node.value else None)
        else:
            raise NotImplementedError(f"Statement type {type(node).__name__} not implemented")
    
    def visit_assignment(self, node: Assignment):
        """Visit assignment node."""
        value = self.visit_expression(node.value)
        
        if node.indices is None:
            # Simple variable assignment
            self.current_env.set(node.target, value)
        else:
            # Array element assignment
            array = self.current_env.get(node.target)
            indices = [int(self.visit_expression(idx)) for idx in node.indices]
            
            if len(indices) == 1:
                array[indices[0]] = value
            elif len(indices) == 2:
                array[indices[0]][indices[1]] = value
            else:
                raise ValueError(f"Arrays with {len(indices)} dimensions not supported")
    
    def visit_array_assign_all(self, node: ArrayAssignAll):
        """Visit array assign all node."""
        value = self.visit_expression(node.value)
        array = self.current_env.get(node.array_name)
        
        if isinstance(array, list):
            for i in range(len(array)):
                if isinstance(array[i], list):
                    for j in range(len(array[i])):
                        array[i][j] = value
                else:
                    array[i] = value
    
    def visit_increment(self, node: Increment):
        """Visit increment node."""
        current = self.current_env.get(node.variable)
        amount = self.visit_expression(node.amount)
        self.current_env.update(node.variable, current + amount)
    
    def visit_decrement(self, node: Decrement):
        """Visit decrement node."""
        current = self.current_env.get(node.variable)
        amount = self.visit_expression(node.amount)
        self.current_env.update(node.variable, current - amount)
    
    def visit_display(self, node: Display):
        """Visit display node."""
        parts = []
        for expr in node.expressions:
            value = self.visit_expression(expr)
            parts.append(str(value))
        output = ''.join(parts)
        print(output)
        self.output_buffer.append(output)
    
    def visit_if_statement(self, node: IfStatement):
        """Visit if statement node."""
        condition = self.visit_expression(node.condition)
        
        if self.is_truthy(condition):
            for stmt in node.then_body:
                self.visit_statement(stmt)
        else:
            # Check elif conditions
            if node.elif_conditions:
                for i, elif_cond in enumerate(node.elif_conditions):
                    if self.is_truthy(self.visit_expression(elif_cond)):
                        for stmt in node.elif_bodies[i]:
                            self.visit_statement(stmt)
                        return
            
            # Execute else body
            if node.else_body:
                for stmt in node.else_body:
                    self.visit_statement(stmt)
    
    def visit_while_statement(self, node: WhileStatement):
        """Visit while statement node."""
        while self.is_truthy(self.visit_expression(node.condition)):
            for stmt in node.body:
                self.visit_statement(stmt)
    
    def visit_do_until_statement(self, node: DoUntilStatement):
        """Visit do-until statement node."""
        while True:
            for stmt in node.body:
                self.visit_statement(stmt)
            if self.is_truthy(self.visit_expression(node.condition)):
                break
    
    def visit_for_statement(self, node: ForStatement):
        """Visit for statement node."""
        start = self.visit_expression(node.start)
        end = self.visit_expression(node.end)
        step = self.visit_expression(node.step)
        
        self.current_env.set(node.variable, start)
        
        if node.increment:
            while self.current_env.get(node.variable) <= end:
                for stmt in node.body:
                    self.visit_statement(stmt)
                current = self.current_env.get(node.variable)
                self.current_env.set(node.variable, current + step)
        else:
            while self.current_env.get(node.variable) >= end:
                for stmt in node.body:
                    self.visit_statement(stmt)
                current = self.current_env.get(node.variable)
                self.current_env.set(node.variable, current - step)
    
    def visit_function_def(self, node: FunctionDef):
        """Visit function definition node."""
        self.functions[node.name] = node
    
    def visit_function_call_statement(self, node: FunctionCallStatement):
        """Visit function call statement node."""
        self.call_function(node.name, node.arguments)
    
    def visit_expression(self, node: Expression) -> Any:
        """Visit expression node."""
        if isinstance(node, Number):
            return node.value
        elif isinstance(node, String):
            return node.value
        elif isinstance(node, Boolean):
            return node.value
        elif isinstance(node, Variable):
            return self.current_env.get(node.name)
        elif isinstance(node, ArrayAccess):
            return self.visit_array_access(node)
        elif isinstance(node, ArrayLiteral):
            return self.visit_array_literal(node)
        elif isinstance(node, BinaryOp):
            return self.visit_binary_op(node)
        elif isinstance(node, UnaryOp):
            return self.visit_unary_op(node)
        elif isinstance(node, FunctionCall):
            return self.call_function(node.name, node.arguments)
        else:
            raise NotImplementedError(f"Expression type {type(node).__name__} not implemented")
    
    def visit_array_access(self, node: ArrayAccess) -> Any:
        """Visit array access node."""
        array = self.current_env.get(node.name)
        indices = [int(self.visit_expression(idx)) for idx in node.indices]
        
        result = array
        for idx in indices:
            result = result[idx]
        return result
    
    def visit_array_literal(self, node: ArrayLiteral) -> List[Any]:
        """Visit array literal node."""
        return [self.visit_expression(elem) for elem in node.elements]
    
    def visit_binary_op(self, node: BinaryOp) -> Any:
        """Visit binary operation node."""
        left = self.visit_expression(node.left)
        right = self.visit_expression(node.right)
        
        if node.operator == '+':
            return left + right
        elif node.operator == '-':
            return left - right
        elif node.operator == '*':
            return left * right
        elif node.operator == '/':
            return left / right
        elif node.operator == '//':
            return int(left) // int(right)
        elif node.operator == '%':
            return int(left) % int(right)
        elif node.operator == '=':
            return left == right
        elif node.operator == '!=':
            return left != right
        elif node.operator == '>':
            return left > right
        elif node.operator == '>=':
            return left >= right
        elif node.operator == '<':
            return left < right
        elif node.operator == '<=':
            return left <= right
        elif node.operator == 'かつ':
            return self.is_truthy(left) and self.is_truthy(right)
        elif node.operator == 'または':
            return self.is_truthy(left) or self.is_truthy(right)
        else:
            raise ValueError(f"Unknown operator: {node.operator}")
    
    def visit_unary_op(self, node: UnaryOp) -> Any:
        """Visit unary operation node."""
        operand = self.visit_expression(node.operand)
        
        if node.operator == '-':
            return -operand
        elif node.operator == 'でない':
            return not self.is_truthy(operand)
        else:
            raise ValueError(f"Unknown unary operator: {node.operator}")
    
    def call_function(self, name: str, arguments: List[Expression]) -> Any:
        """Call a function."""
        # Evaluate arguments
        args = [self.visit_expression(arg) for arg in arguments]
        
        # Check for built-in functions
        if name in self.builtin_functions:
            return self.builtin_functions[name](args)
        
        # Check for user-defined functions
        if name not in self.functions:
            raise NameError(f"Function '{name}' is not defined")
        
        func = self.functions[name]
        
        # Create new environment for function
        func_env = Environment(self.global_env)
        
        # Bind parameters
        if len(args) != len(func.params):
            raise ValueError(f"Function '{name}' expects {len(func.params)} arguments, got {len(args)}")
        
        for param, arg in zip(func.params, args):
            func_env.set(param, arg)
        
        # Save current environment
        prev_env = self.current_env
        self.current_env = func_env
        
        try:
            # Execute function body
            for stmt in func.body:
                self.visit_statement(stmt)
            result = None
        except ReturnValue as ret:
            result = ret.value
        finally:
            # Restore environment
            self.current_env = prev_env
        
        return result
    
    def is_truthy(self, value: Any) -> bool:
        """Determine if value is truthy."""
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        return bool(value)


def interpret_dncl(source: str):
    """Convenience function to interpret DNCL source code."""
    from parser import parse_dncl
    
    ast = parse_dncl(source)
    interpreter = Interpreter()
    interpreter.run(ast)
