import sys
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "program.txt"

    try:
        with open(filename, 'r') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return

    lexer = Lexer(text)
    # tokens = lexer.tokenize()
    # for t in tokens: print(t)
    
    # Re-init lexer for parser (tokenize consumes)
    lexer = Lexer(text)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    interpreter = Interpreter(parser)
    
    try:
        interpreter.interpret()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
