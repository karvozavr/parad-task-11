class Scope:
    def __init__(self, parent=None):
        self.dict_values = {}
        self.parent = parent

    def __getitem__(self, key):
        if key in self.dict_values:
            return self.dict_values[key]
        elif self.parent is not None:
            return self.parent[key]
        else:
            raise KeyError

    def __setitem__(self, key, value):
        self.dict_values[key] = value


class Number:
    def __init__(self, value):
        self.value = int(value)

    def evaluate(self, scope):
        return self

    def accept(self, visitor):
        return visitor.visit_number(self)


class Function:
    def __init__(self, args, body):
        self.args = args
        self.body = body

    def evaluate(self, scope):
        return do_operations(self.body, scope)


class FunctionDefinition:
    def __init__(self, name, function):
        self.name = name
        self.function = function

    def evaluate(self, scope):
        scope[self.name] = self.function
        return self.function

    def accept(self, visitor):
        return visitor.visit_function_def(self)


class Conditional:
    def __init__(self, cond, if_true, if_false=None):
        self.cond = cond
        self.if_true = if_true
        self.if_false = if_false

    def evaluate(self, scope):
        result = self.cond.evaluate(scope)
        if result.value != 0:
            return do_operations(self.if_true, scope)
        else:
            return do_operations(self.if_false, scope)

    def accept(self, visitor):
        return visitor.visit_conditional(self)


class Print:
    def __init__(self, expr):
        self.expr = expr

    def evaluate(self, scope):
        val = self.expr.evaluate(scope)
        print(val.value)
        return val

    def accept(self, visitor):
        return visitor.visit_print(self)


class Read:
    def __init__(self, name):
        self.name = name

    def evaluate(self, scope):
        scope[self.name] = Number(input())
        return scope[self.name]

    def accept(self, visitor):
        return visitor.visit_read(self)


class FunctionCall:
    def __init__(self, fun_expr, args):
        self.fun_expr = fun_expr
        self.args = args

    def evaluate(self, scope):
        local_scope = Scope(scope)
        func = self.fun_expr.evaluate(scope)
        for arg_name, arg in zip(func.args, self.args):
            local_scope[arg_name] = arg.evaluate(scope)
        return func.evaluate(local_scope)

    def accept(self, visitor):
        return visitor.visit_function_call(self)


class Reference:
    def __init__(self, name):
        self.name = name

    def evaluate(self, scope):
        return scope[self.name]

    def accept(self, visitor):
        return visitor.visit_reference(self)


class BinaryOperation:
    """BinaryOperation - представляет бинарную операцию над двумя выражениями.
    Результатом вычисления бинарной операции является объект Number.
    Поддерживаемые операции:
    “+”, “-”, “*”, “/”, “%”, “==”, “!=”,
    “<”, “>”, “<=”, “>=”, “&&”, “||”."""

    bin_ops = {
        '+': lambda l, r: l + r,
        '-': lambda l, r: l - r,
        '*': lambda l, r: l * r,
        '/': lambda l, r: l // r,
        '%': lambda l, r: l % r,
        '<': lambda l, r: l < r,
        '>': lambda l, r: l > r,
        '==': lambda l, r: l == r,
        '!=': lambda l, r: l != r,
        '<=': lambda l, r: l <= r,
        '>=': lambda l, r: l >= r,
        '&&': lambda l, r: l and r,
        '||': lambda l, r: l or r
    }

    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.op = op

    def evaluate(self, scope):
        op = self.bin_ops[self.op]
        l_val = self.lhs.evaluate(scope).value
        r_val = self.rhs.evaluate(scope).value
        result = int(op(l_val, r_val))
        return Number(result)

    def accept(self, visitor):
        return visitor.visit_bin_op(self)


class UnaryOperation:
    """UnaryOperation - представляет унарную операцию над выражением.
    Результатом вычисления унарной операции является объект Number.
    Поддерживаемые операции: “-”, “!”."""

    un_ops = {
        '-': lambda val: -val,
        '!': lambda val: not val
    }

    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def evaluate(self, scope):
        self.op = self.un_ops[self.op]
        val = self.expr.evaluate(scope).value
        return Number(self.op(val))

    def accept(self, visitor):
        return visitor.visit_un_op(self)


def do_operations(operations, scope):
    retval = None
    for op in operations or []:
        retval = op.evaluate(scope)
    return retval
