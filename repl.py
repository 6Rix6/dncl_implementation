"""
REPL (Read-Eval-Print Loop) for DNCL.
Interactive shell for testing DNCL code.
"""

import sys
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from ast_nodes import Program


class REPL:
    """Interactive REPL for DNCL."""
    
    def __init__(self):
        self.interpreter = Interpreter()
        self.history = []
    
    def run(self):
        """Run the REPL."""
        print("DNCL インタプリタ (共通テスト手順記述標準言語)")
        print("終了するには 'exit' または Ctrl+C を入力してください\n")
        
        while True:
            try:
                # Read input
                line = input(">>> ")
                
                if line.strip().lower() in ['exit', 'quit', 'exit()', 'quit()']:
                    print("終了します")
                    break
                
                if not line.strip():
                    continue
                
                # Add to history
                self.history.append(line)
                
                # Check for multi-line input (ends with を実行する, を繰り返す, etc.)
                lines = [line]
                while not self._is_complete_statement(line):
                    line = input("... ")
                    lines.append(line)
                    self.history.append(line)
                
                source = '\n'.join(lines)
                
                # Execute
                self.execute(source)
                print()
                
            except KeyboardInterrupt:
                print("\n終了します")
                break
            except EOFError:
                print("\n終了します")
                break
            except Exception as e:
                print(f"エラー: {e}")
                import traceback
                traceback.print_exc()
                print()
    
    def _is_complete_statement(self, line: str) -> bool:
        """Check if statement is complete (heuristic)."""
        line = line.strip()
        
        # Simple statements that are complete on one line
        if '←' in line and not line.endswith('，'):
            return True
        if 'を表示する' in line:
            return True
        if 'を増やす' in line or 'を減らす' in line:
            return True
        
        # Check if it's a start of a multi-line structure
        if line.startswith('もし') and not 'を実行する' in line:
            return False
        if line.startswith('繰り返し') and not 'を実行する' in line:
            return False
        if 'の間' in line and not 'を繰り返す' in line:
            return False
        if 'から' in line and 'まで' in line and not 'を繰り返す' in line:
            return False
        if line.startswith('関数') and not 'と定義する' in line:
            return False
        
        return True
    
    def execute(self, source: str):
        """Execute DNCL source code."""
        try:
            # Lex
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            
            # Parse
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Interpret
            self.interpreter.run(ast)
            
        except SyntaxError as e:
            print(f"構文エラー: {e}")
        except Exception as e:
            print(f"実行エラー: {e}")
            raise


if __name__ == '__main__':
    repl = REPL()
    repl.run()
