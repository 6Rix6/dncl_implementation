"""
Main entry point for DNCL interpreter.
Supports both REPL mode and file execution.
"""

import sys
import argparse
from pathlib import Path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='DNCL インタプリタ (共通テスト手順記述標準言語)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用方法:
  python main.py              # REPLモードで起動
  python main.py file.dncl    # ファイルを実行
        """
    )
    parser.add_argument('file', nargs='?', help='実行するDNCLファイル')
    parser.add_argument('-v', '--verbose', action='store_true', help='詳細な出力')
    
    args = parser.parse_args()
    
    if args.file:
        # File execution mode
        execute_file(args.file, args.verbose)
    else:
        # REPL mode
        from repl import REPL
        repl = REPL()
        repl.run()


def execute_file(filepath: str, verbose: bool = False):
    """Execute a DNCL file."""
    from lexer import Lexer
    from parser import Parser
    from interpreter import Interpreter
    
    # Read file
    path = Path(filepath)
    if not path.exists():
        print(f"エラー: ファイル '{filepath}' が見つかりません", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            source = f.read()
    except Exception as e:
        print(f"エラー: ファイルの読み込みに失敗しました: {e}", file=sys.stderr)
        sys.exit(1)
    
    if verbose:
        print(f"=== {filepath} を実行中 ===\n")
    
    try:
        # Lex
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        if verbose:
            print("=== トークン ===")
            for token in tokens:
                if token.type.name != 'NEWLINE' and token.type.name != 'EOF':
                    print(f"  {token}")
            print()
        
        # Parse
        parser = Parser(tokens)
        ast = parser.parse()
        
        if verbose:
            print("=== AST ===")
            print(f"  {ast}")
            print()
            print("=== 実行結果 ===")
        
        # Interpret
        interpreter = Interpreter()
        interpreter.run(ast)
        
        if verbose:
            print("\n=== 実行完了 ===")
        
    except SyntaxError as e:
        print(f"構文エラー: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"実行エラー: {e}", file=sys.stderr)
        import traceback
        if verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
