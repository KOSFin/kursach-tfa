import os
import sys
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

def run_test(filename):
    print(f"\n{'='*20} Running {filename} {'='*20}")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return

    print("--- Source Code ---")
    print(text)
    print("-------------------")

    try:
        # Lexer
        lexer = Lexer(text)
        tokens = lexer.tokenize()
        print("Tokens:", tokens) 

        # Parser
        lexer = Lexer(text) # Re-init because tokenize consumes
        tokens = lexer.tokenize()
        # print("Tokens:", tokens) 
        parser = Parser(tokens)
        # tree = parser.parse() # Interpreter will parse
        
        # Interpreter
        print("--- Output ---")
        interpreter = Interpreter(parser)
        # We need to capture stdout to show it nicely, but for now direct print is fine
        # Note: Interpreter uses print() directly.
        interpreter.interpret()
        print("\n--- Result: SUCCESS ---")

    except Exception as e:
        print(f"\n--- Result: CAUGHT ERROR ---")
        print(f"Error: {e}")

def main():
    test_dir = "tests"
    if not os.path.exists(test_dir):
        print(f"Directory {test_dir} not found.")
        return

    files = sorted(os.listdir(test_dir))
    for f in files:
        if f.endswith(".txt"):
            run_test(os.path.join(test_dir, f))

if __name__ == "__main__":
    main()
