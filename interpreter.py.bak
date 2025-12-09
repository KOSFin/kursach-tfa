class NodeVisitor:
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'No visit_{type(node).__name__} method')

class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
        self.GLOBAL_SCOPE = {}
        self.TYPES = {}

    def visit_Program(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_VarDecl(self, node):
        type_map = {'%': int, '!': float, '$': bool}
        py_type = type_map.get(node.type_node)
        for name in node.names:
            if name in self.GLOBAL_SCOPE:
                raise Exception(f"Variable {name} already declared")
            self.GLOBAL_SCOPE[name] = None
            self.TYPES[name] = py_type

    def visit_Compound(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_Assign(self, node):
        var_name = node.name
        if var_name not in self.GLOBAL_SCOPE:
            raise Exception(f"Variable {var_name} not declared")
        
        val = self.visit(node.expr)
        expected_type = self.TYPES[var_name]
        
        if expected_type == int:
            if isinstance(val, bool): pass # Bool is int subclass
            elif not isinstance(val, int):
                # Try casting if float is integer
                if isinstance(val, float) and val.is_integer():
                    val = int(val)
                else:
                    raise Exception(f"Type mismatch: {var_name} expects %, got {type(val)}")
        elif expected_type == float:
            if isinstance(val, int):
                val = float(val)
            elif not isinstance(val, float):
                raise Exception(f"Type mismatch: {var_name} expects !, got {type(val)}")
        elif expected_type == bool:
            if not isinstance(val, bool):
                 raise Exception(f"Type mismatch: {var_name} expects $, got {type(val)}")

        self.GLOBAL_SCOPE[var_name] = val

    def visit_Var(self, node):
        var_name = node.name
        if var_name not in self.GLOBAL_SCOPE:
            raise Exception(f"Variable {var_name} not declared")
        val = self.GLOBAL_SCOPE[var_name]
        if val is None:
            raise Exception(f"Variable {var_name} not initialized")
        return val

    def visit_Num(self, node):
        token = node.token
        if token.type == 'DEC':
            return int(token.value.rstrip('Dd'))
        elif token.type == 'BIN':
            return int(token.value.rstrip('Bb'), 2)
        elif token.type == 'OCT':
            return int(token.value.rstrip('Oo'), 8)
        elif token.type == 'HEX':
            return int(token.value.rstrip('Hh'), 16)
        elif token.type == 'REAL':
            return float(token.value)
        elif token.type == 'KEYWORD':
            return True if token.value == 'true' else False
        return 0

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        op = node.op
        if op == '+': return left + right
        elif op == '-': return left - right
        elif op == '*': return left * right
        elif op == '/': return left / right
        elif op == '||': return bool(left) or bool(right)
        elif op == '&&': return bool(left) and bool(right)
        elif op == '==': return left == right
        elif op == '!=': return left != right
        elif op == '<': return left < right
        elif op == '<=': return left <= right
        elif op == '>': return left > right
        elif op == '>=': return left >= right
        return 0

    def visit_UnOp(self, node):
        op = node.op
        val = self.visit(node.expr)
        if op == '!':
            return not bool(val)
        return val

    def visit_If(self, node):
        if self.visit(node.condition):
            self.visit(node.then_stmt)
        elif node.else_stmt:
            self.visit(node.else_stmt)

    def visit_While(self, node):
        while self.visit(node.condition):
            self.visit(node.body)

    def visit_For(self, node):
        self.visit(node.assign)
        # Loop variable
        var_name = node.assign.name
        
        while True:
            current_val = self.GLOBAL_SCOPE[var_name]
            to_val = self.visit(node.to_expr)
            step_val = self.visit(node.step_expr) if node.step_expr else 1
            
            # Check condition (assuming loop continues while var <= to if step > 0, etc)
            # Standard BASIC/Pascal for loop behavior
            if step_val >= 0:
                if current_val > to_val: break
            else:
                if current_val < to_val: break
            
            self.visit(node.body)
            
            # Increment
            self.GLOBAL_SCOPE[var_name] = current_val + step_val

    def visit_Read(self, node):
        for name in node.names:
            if name not in self.GLOBAL_SCOPE:
                raise Exception(f"Variable {name} not declared")
            val_str = input(f"Enter value for {name}: ")
            # Try to parse input
            try:
                if self.TYPES[name] == int:
                    val = int(val_str)
                elif self.TYPES[name] == float:
                    val = float(val_str)
                elif self.TYPES[name] == bool:
                    val = val_str.lower() == 'true'
                self.GLOBAL_SCOPE[name] = val
            except ValueError:
                print("Invalid input format")

    def visit_Write(self, node):
        vals = [str(self.visit(expr)) for expr in node.exprs]
        print(" ".join(vals))

    def interpret(self):
        tree = self.parser.parse()
        self.visit(tree)
