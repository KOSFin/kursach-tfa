import re

class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {self.value}, {self.line}, {self.column})"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def error(self, msg):
        raise Exception(f"Lexer error at {self.line}:{self.column}: {msg}")

    def tokenize(self):
        while self.pos < len(self.text):
            char = self.text[self.pos]
            
            if char == ' ' or char == '\t' or char == '\r':
                self.pos += 1
                self.column += 1
                continue
            
            if char == '\n':
                self.tokens.append(Token('NEWLINE', '\n', self.line, self.column))
                self.pos += 1
                self.line += 1
                self.column = 1
                continue

            if char == '(' and self.pos + 1 < len(self.text) and self.text[self.pos+1] == '*':
                self.pos += 2
                self.column += 2
                while self.pos + 1 < len(self.text) and not (self.text[self.pos] == '*' and self.text[self.pos+1] == ')'):
                    if self.text[self.pos] == '\n':
                        self.line += 1
                        self.column = 1
                    else:
                        self.column += 1
                    self.pos += 1
                if self.pos + 1 >= len(self.text):
                    self.error("Unclosed comment")
                self.pos += 2
                self.column += 2
                continue

            if re.match(r'[A-Za-z]', char):
                start = self.pos
                while self.pos < len(self.text) and re.match(r'[A-Za-z0-9]', self.text[self.pos]):
                    self.pos += 1
                    self.column += 1
                value = self.text[start:self.pos]
                
                if value in ['end', 'begin', 'if', 'else', 'for', 'to', 'step', 'next', 'while', 'readln', 'writeln', 'true', 'false']:
                    self.tokens.append(Token('KEYWORD', value, self.line, self.column - len(value)))
                elif re.match(r'[0-9A-F]+[Hh]', value): 
                    self.tokens.append(Token('HEX', value, self.line, self.column - len(value)))
                elif re.match(r'[0-7]+[Oo]', value):
                    self.tokens.append(Token('OCT', value, self.line, self.column - len(value)))
                elif re.match(r'[01]+[Bb]', value):
                    self.tokens.append(Token('BIN', value, self.line, self.column - len(value)))
                elif re.match(r'[0-9]+[Dd]', value):
                    self.tokens.append(Token('DEC', value, self.line, self.column - len(value)))
                else:
                    self.tokens.append(Token('ID', value, self.line, self.column - len(value)))
                continue

            if re.match(r'[0-9]', char):
                start = self.pos
                is_real = False
                while self.pos < len(self.text):
                    if re.match(r'[0-9]', self.text[self.pos]):
                        self.pos += 1
                        self.column += 1
                    elif self.text[self.pos] == '.':
                        if is_real: break
                        is_real = True
                        self.pos += 1
                        self.column += 1
                    elif self.text[self.pos] in ['E', 'e']:
                        is_real = True
                        self.pos += 1
                        self.column += 1
                        if self.pos < len(self.text) and self.text[self.pos] in ['+', '-']:
                            self.pos += 1
                            self.column += 1
                    elif self.text[self.pos] in ['H', 'h', 'O', 'o', 'B', 'b', 'D', 'd']:
                        self.pos += 1
                        self.column += 1
                        break 
                    else:
                        break
                
                value = self.text[start:self.pos]
                if value[-1] in ['H', 'h']:
                     self.tokens.append(Token('HEX', value, self.line, self.column - len(value)))
                elif value[-1] in ['O', 'o']:
                     self.tokens.append(Token('OCT', value, self.line, self.column - len(value)))
                elif value[-1] in ['B', 'b']:
                     self.tokens.append(Token('BIN', value, self.line, self.column - len(value)))
                elif value[-1] in ['D', 'd']:
                     self.tokens.append(Token('DEC', value, self.line, self.column - len(value)))
                elif is_real:
                     self.tokens.append(Token('REAL', value, self.line, self.column - len(value)))
                else:
                     self.tokens.append(Token('DEC', value, self.line, self.column - len(value)))
                continue

            if char == ':' and self.pos + 1 < len(self.text) and self.text[self.pos+1] == '=':
                self.tokens.append(Token('ASSIGN', ':=', self.line, self.column))
                self.pos += 2
                self.column += 2
                continue
            
            if char == '=' and self.pos + 1 < len(self.text) and self.text[self.pos+1] == '=':
                self.tokens.append(Token('EQ', '==', self.line, self.column))
                self.pos += 2
                self.column += 2
                continue

            if char == '!' and self.pos + 1 < len(self.text) and self.text[self.pos+1] == '=':
                self.tokens.append(Token('NEQ', '!=', self.line, self.column))
                self.pos += 2
                self.column += 2
                continue
            
            if char == '<' and self.pos + 1 < len(self.text) and self.text[self.pos+1] == '=':
                self.tokens.append(Token('LE', '<=', self.line, self.column))
                self.pos += 2
                self.column += 2
                continue

            if char == '>' and self.pos + 1 < len(self.text) and self.text[self.pos+1] == '=':
                self.tokens.append(Token('GE', '>=', self.line, self.column))
                self.pos += 2
                self.column += 2
                continue

            if char == '|' and self.pos + 1 < len(self.text) and self.text[self.pos+1] == '|':
                self.tokens.append(Token('OR', '||', self.line, self.column))
                self.pos += 2
                self.column += 2
                continue

            if char == '&' and self.pos + 1 < len(self.text) and self.text[self.pos+1] == '&':
                self.tokens.append(Token('AND', '&&', self.line, self.column))
                self.pos += 2
                self.column += 2
                continue

            if char in ['+', '-', '*', '/', '!', '<', '>', '=', ':', ';', ',', '(', ')', '%', '$']:
                # Note: ! is unary NOT, but also Real type. 
                # Wait, ! is Real type in declarations. ! is NOT in expressions.
                # Context matters? No, lexer just emits token.
                # But wait, ! is a single char token.
                self.tokens.append(Token('CHAR', char, self.line, self.column))
                self.pos += 1
                self.column += 1
                continue

            self.error(f"Unknown character: {char}")
        
        self.tokens.append(Token('EOF', '', self.line, self.column))
        return self.tokens
