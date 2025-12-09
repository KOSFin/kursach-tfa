from lexer import Token

class AST:
    pass

class Program(AST):
    def __init__(self, statements):
        self.statements = statements

class VarDecl(AST):
    def __init__(self, names, type_node):
        self.names = names
        self.type_node = type_node

class Compound(AST):
    def __init__(self, statements):
        self.statements = statements

class Assign(AST):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class If(AST):
    def __init__(self, condition, then_stmt, else_stmt=None):
        self.condition = condition
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

class For(AST):
    def __init__(self, assign, to_expr, step_expr, body):
        self.assign = assign
        self.to_expr = to_expr
        self.step_expr = step_expr
        self.body = body

class While(AST):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class Read(AST):
    def __init__(self, names):
        self.names = names

class Write(AST):
    def __init__(self, exprs):
        self.exprs = exprs

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnOp(AST):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Var(AST):
    def __init__(self, token):
        self.token = token
        self.name = token.value

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos]

    def error(self, msg):
        raise Exception(f"Parser error at {self.current_token.line}:{self.current_token.column}: {msg}")

    def eat(self, type, value=None):
        if self.current_token.type == type and (value is None or self.current_token.value == value):
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
        else:
            self.error(f"Expected {type} {value}, got {self.current_token.type} {self.current_token.value}")

    def parse(self):
        statements = []
        # print(f"DEBUG: Starting parse loop. Token: {self.current_token}")
        while self.current_token.type != 'EOF' and (self.current_token.type != 'KEYWORD' or self.current_token.value != 'end'):
            # Skip separators
            while self.current_token.type == 'CHAR' and self.current_token.value == ':':
                self.eat('CHAR', ':')
            while self.current_token.type == 'NEWLINE':
                self.eat('NEWLINE')
            
            if self.current_token.type == 'EOF' or (self.current_token.type == 'KEYWORD' and self.current_token.value == 'end'):
                break

            # print(f"DEBUG: Parsing statement. Token: {self.current_token}")
            # Declaration starts with ID list then :
            # Statement starts with ID (assign), begin, if, for, while, readln, writeln
            # Ambiguity: ID could be start of Assign or Decl.
            # Lookahead needed.
            
            if self.current_token.type == 'ID':
                idx = self.pos
                is_decl = False
                while idx < len(self.tokens):
                    tok = self.tokens[idx]
                    if tok.type == 'CHAR' and tok.value == ':':
                        is_decl = True
                        break
                    if tok.type == 'ASSIGN':
                        is_decl = False
                        break
                    if tok.type == 'CHAR' and tok.value == ';':
                        pass
                    idx += 1
                
                if is_decl:
                    statements.append(self.declaration())
                else:
                    statements.append(self.statement())
            else:
                statements.append(self.statement())
            
            # Expect separator or end
            if self.current_token.type == 'CHAR' and self.current_token.value == ':':
                self.eat('CHAR', ':')
            elif self.current_token.type == 'NEWLINE':
                self.eat('NEWLINE')
            elif self.current_token.type == 'KEYWORD' and self.current_token.value == 'end':
                pass # Loop will handle
            elif self.current_token.type == 'EOF':
                pass
            else:
                # Maybe inside a block, ; is separator?
                # No, program structure uses : or newline.
                # But Compound uses ;
                pass

        # print(f"DEBUG: Before eating end. Token: {self.current_token}")
        self.eat('KEYWORD', 'end')
        return Program(statements)

    def declaration(self):
        names = [self.current_token.value]
        self.eat('ID')
        while self.current_token.type == 'CHAR' and self.current_token.value == ',':
            self.eat('CHAR', ',')
            names.append(self.current_token.value)
            self.eat('ID')
        
        self.eat('CHAR', ':')
        
        type_node = self.current_token.value
        if self.current_token.value in ['%', '!', '$']:
            self.eat('CHAR')
        else:
            self.error("Expected type %, !, or $")
        
        self.eat('CHAR', ';')
        return VarDecl(names, type_node)

    def statement(self):
        if self.current_token.type == 'KEYWORD':
            if self.current_token.value == 'begin':
                return self.compound_statement()
            elif self.current_token.value == 'if':
                return self.if_statement()
            elif self.current_token.value == 'for':
                return self.for_statement()
            elif self.current_token.value == 'while':
                return self.while_statement()
            elif self.current_token.value == 'readln':
                return self.read_statement()
            elif self.current_token.value == 'writeln':
                return self.write_statement()
        
        if self.current_token.type == 'ID':
            return self.assign_statement()
        
        self.error("Unexpected statement")

    def compound_statement(self):
        self.eat('KEYWORD', 'begin')
        
        while self.current_token.type == 'NEWLINE':
            self.eat('NEWLINE')
            
        statements = []
        statements.append(self.statement())
        while self.current_token.type == 'CHAR' and self.current_token.value == ';':
            self.eat('CHAR', ';')
            while self.current_token.type == 'NEWLINE':
                self.eat('NEWLINE')
            statements.append(self.statement())
            
        while self.current_token.type == 'NEWLINE':
            self.eat('NEWLINE')
            
        self.eat('KEYWORD', 'end')
        return Program(statements)

    def assign_statement(self):
        name = self.current_token.value
        self.eat('ID')
        self.eat('ASSIGN')
        expr = self.expression()
        return Assign(name, expr)

    def if_statement(self):
        self.eat('KEYWORD', 'if')
        self.eat('CHAR', '(')
        cond = self.expression()
        self.eat('CHAR', ')')
        
        while self.current_token.type == 'NEWLINE':
            self.eat('NEWLINE')
            
        then_stmt = self.statement()
        
        # Lookahead for else, skipping newlines
        idx = self.pos
        while idx < len(self.tokens) and self.tokens[idx].type == 'NEWLINE':
            idx += 1
        
        else_stmt = None
        if idx < len(self.tokens) and self.tokens[idx].type == 'KEYWORD' and self.tokens[idx].value == 'else':
            # Consume newlines
            while self.current_token.type == 'NEWLINE':
                self.eat('NEWLINE')
            self.eat('KEYWORD', 'else')
            
            while self.current_token.type == 'NEWLINE':
                self.eat('NEWLINE')
                
            else_stmt = self.statement()
            
        return If(cond, then_stmt, else_stmt)

    def for_statement(self):
        self.eat('KEYWORD', 'for')
        # Assign
        name = self.current_token.value
        self.eat('ID')
        self.eat('ASSIGN')
        start_expr = self.expression()
        assign = Assign(name, start_expr)
        
        self.eat('KEYWORD', 'to')
        to_expr = self.expression()
        
        step_expr = None
        if self.current_token.type == 'KEYWORD' and self.current_token.value == 'step':
            self.eat('KEYWORD', 'step')
            step_expr = self.expression()
        
        while self.current_token.type == 'NEWLINE':
            self.eat('NEWLINE')
            
        body = self.statement()
        
        while self.current_token.type == 'NEWLINE':
            self.eat('NEWLINE')
            
        self.eat('KEYWORD', 'next')
        return For(assign, to_expr, step_expr, body)

    def while_statement(self):
        self.eat('KEYWORD', 'while')
        self.eat('CHAR', '(')
        cond = self.expression()
        self.eat('CHAR', ')')
        
        while self.current_token.type == 'NEWLINE':
            self.eat('NEWLINE')
            
        body = self.statement()
        return While(cond, body)

    def read_statement(self):
        self.eat('KEYWORD', 'readln')
        names = [self.current_token.value]
        self.eat('ID')
        while self.current_token.type == 'CHAR' and self.current_token.value == ',':
            self.eat('CHAR', ',')
            names.append(self.current_token.value)
            self.eat('ID')
        return Read(names)

    def write_statement(self):
        self.eat('KEYWORD', 'writeln')
        exprs = [self.expression()]
        while self.current_token.type == 'CHAR' and self.current_token.value == ',':
            self.eat('CHAR', ',')
            exprs.append(self.expression())
        return Write(exprs)

    def expression(self):
        node = self.simple_expr()
        while self.current_token.type in ['EQ', 'NEQ', 'LE', 'GE', 'CHAR'] and self.current_token.value in ['==', '!=', '<=', '>=', '<', '>']:
            op = self.current_token.value
            if self.current_token.type == 'CHAR': self.eat('CHAR')
            else: self.eat(self.current_token.type)
            right = self.simple_expr()
            node = BinOp(node, op, right)
        return node

    def simple_expr(self):
        node = self.term()
        while (self.current_token.type == 'CHAR' and self.current_token.value in ['+', '-']) or (self.current_token.type == 'OR'):
            op = self.current_token.value
            if self.current_token.type == 'CHAR': self.eat('CHAR')
            else: self.eat('OR')
            right = self.term()
            node = BinOp(node, op, right)
        return node

    def term(self):
        node = self.factor()
        while (self.current_token.type == 'CHAR' and self.current_token.value in ['*', '/']) or (self.current_token.type == 'AND'):
            op = self.current_token.value
            if self.current_token.type == 'CHAR': self.eat('CHAR')
            else: self.eat('AND')
            right = self.factor()
            node = BinOp(node, op, right)
        return node

    def factor(self):
        token = self.current_token
        if token.type == 'CHAR' and token.value == '!':
            self.eat('CHAR', '!')
            node = self.factor()
            return UnOp('!', node)
        elif token.type == 'CHAR' and token.value == '(':
            self.eat('CHAR', '(')
            node = self.expression()
            self.eat('CHAR', ')')
            return node
        elif token.type in ['DEC', 'BIN', 'OCT', 'HEX', 'REAL']:
            self.eat(token.type)
            return Num(token)
        elif token.type == 'KEYWORD' and token.value in ['true', 'false']:
            self.eat('KEYWORD')
            return Num(token) # Treat bool as num/const
        elif token.type == 'ID':
            self.eat('ID')
            return Var(token)
        else:
            self.error("Unexpected token in factor")
