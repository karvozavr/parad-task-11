#!/usr/bin/env python3


from io import StringIO
import sys
from unittest.mock import patch
from yat.model import *


@patch('sys.stdout', new_callable=StringIO)
def get_value(number, mock_stdout):
    Print(number).evaluate(Scope())
    return int(mock_stdout.getvalue())


class TestScope:
    def test_scope_set(self):
        s = Scope()
        s['a'] = Number(7)
        assert get_value(s['a']) == get_value(Number(7))

    def test_scope_get_from_parent(self, monkeypatch):
        parent = Scope()
        child = Scope(parent)
        parent['a'] = Number(7)
        assert get_value(child['a']) == get_value(Number(7))


class TestNumber:
    def test_number_value(self):
        assert get_value(Number(7)) == 7

    def test_number_evaluate(self):
        assert get_value(Number(7).evaluate(Scope())) == 7


class TestBinOp:
    def test_bin_op_plus(self):
        bin_op = BinaryOperation
        parent = Scope()
        result = get_value(bin_op(Number(3), '+', Number(2)).evaluate(parent))
        assert result == 5

    def test_bin_op_minus(self):
        bin_op = BinaryOperation
        parent = Scope()
        result = get_value(bin_op(Number(3), '-', Number(2)).evaluate(parent))
        assert result == 1

    def test_bin_op_mul(self):
        bin_op = BinaryOperation
        parent = Scope()
        result = get_value(bin_op(Number(3), '*', Number(2)).evaluate(parent))
        assert result == 6

    def test_bin_op_div(self):
        bin_op = BinaryOperation
        parent = Scope()
        result = get_value(bin_op(Number(3), '/', Number(2)).evaluate(parent))
        assert result == 1

    def test_bin_op_mod(self):
        bin_op = BinaryOperation
        parent = Scope()
        result = get_value(bin_op(Number(3), '%', Number(2)).evaluate(parent))
        assert result == 1

    def test_bin_op_less(self):
        bin_op = BinaryOperation
        parent = Scope()
        result = get_value(bin_op(Number(3), '<', Number(2)).evaluate(parent))
        assert result == 0

    def test_bin_op_greater(self):
        bin_op = BinaryOperation
        parent = Scope()
        result = get_value(bin_op(Number(3), '>', Number(2)).evaluate(parent))
        assert result != 0

    def test_bin_op_eq(self):
        bin_op = BinaryOperation
        parent = Scope()
        result = get_value(bin_op(Number(3), '==', Number(2)).evaluate(parent))
        assert result == 0

    def test_bin_op_leq(self):
        bin_op = BinaryOperation
        parent = Scope()
        result = get_value(bin_op(Number(3), '<=', Number(2)).evaluate(parent))
        assert result == 0

    def test_bin_op_geq(self):
        bin_op = BinaryOperation
        parent = Scope()
        result = get_value(bin_op(Number(3), '>=', Number(2)).evaluate(parent))
        assert result != 0

    def test_bin_op_and(self):
        bin_op = BinaryOperation
        parent = Scope()
        result = get_value(bin_op(Number(3), '&&', Number(2)).evaluate(parent))
        assert result != 0

    def test_bin_op_or(self):
        bin_op = BinaryOperation
        parent = Scope()
        result = get_value(bin_op(Number(3), '||', Number(2)).evaluate(parent))
        assert result != 0

    def test_bin_op_eval(self):
        bin_op = BinaryOperation
        assert get_value(bin_op(Number(3),
                                '*',
                                bin_op(Number(8),
                                       '+',
                                       Number(1))).evaluate(Scope())) == 27


class TestUnOp:
    def test_un_op_all(self):
        un_op = UnaryOperation

        result = get_value(un_op('!', Number(3)).evaluate(Scope()))
        assert result == 0

        result = get_value(un_op('!', Number(0)).evaluate(Scope()))
        assert result != 0

        result = get_value(un_op('-', Number(3)).evaluate(Scope()))
        assert result == -3

    def test_un_op_eval(self):
        bin_op = BinaryOperation
        un_op = UnaryOperation
        sc = Scope()

        assert get_value(un_op('!',
                               bin_op(Number(3),
                                      '*',
                                      bin_op(Number(8),
                                             '+',
                                             Number(1)))).evaluate(sc)) == 0
        assert get_value(un_op('-',
                               bin_op(Number(3),
                                      '*',
                                      bin_op(Number(8),
                                             '+',
                                             Number(1)))).evaluate(sc)) == -27


class ReferenceTests:
    def test_reference(self):
        parent = Scope()
        parent['a'] = Number(5)
        assert get_value(Reference('a').evaluate(parent)) == 5

    def test_reference_parent(self):
        parent = Scope()
        child = Scope(parent)
        parent['a'] = Number(5)
        assert get_value(Reference('a').evaluate(child)) == 5


class TestFunction:
    def test_func_base(self):
        sc = Scope()
        nm = Number
        f_call = FunctionCall
        sc['foo'] = Function(('a', 'b'),
                             [BinaryOperation(Reference('a'),
                                              '+',
                                              Reference('b'))])
        assert get_value(f_call(FunctionDefinition('foo', sc['foo']),
                                [nm(5),
                                 UnaryOperation('-',
                                                nm(3))]).evaluate(sc)) == 2

    def test_func_empty(self):
        parent = Scope()
        parent['foo'] = Function(('a', 'b'), [])
        FunctionCall(FunctionDefinition('foo', parent['foo']),
                     [Number(5),
                      Number(3)]).evaluate(parent)

    def test_func_in_func(self):
        f_def = FunctionDefinition
        sc = Scope()
        sc['bar'] = Function((),
                             [
                                 Number(10)
                             ])
        sc['foo'] = Function(('a', 'b'),
                             [
                                 f_def('bar', sc['bar'])
                             ])
        sc['a'] = Number(2)
        sc['b'] = Number(1)
        sc['new_foo'] = FunctionCall(f_def('foo', sc['foo']),
                                     [sc['a'], sc['b']]).evaluate(sc)
        assert get_value(FunctionCall(f_def('new_foo', sc['new_foo']),
                                      []).evaluate(sc)) == 10

    def test_func_def(self):
        parent = Scope()
        f_def = FunctionDefinition(
            'foo',
            Function(['arg'],
                     [
                         Reference('arg')
                     ]
                     )
        )
        assert get_value(FunctionCall(f_def,
                                      [Number(25)]).evaluate(parent)) == 25

    def test_func_call(self):
        parent = Scope()
        parent['arg'] = Number(1)
        f_def = FunctionDefinition(
            'foo',
            Function(['arg'],
                     [
                         Reference('arg')
                     ]
                     )
        )
        FunctionCall(f_def, [Number(25)]).evaluate(parent)
        assert get_value(Reference('arg').evaluate(parent)) == 1


class TestConditional:
    def test_cond_base(self):
        # if condition is not Number(0) it's true
        parent = Scope()
        assert Conditional(Number(0), [Number(1)],
                           [Number(2)]).evaluate(parent).value == 2
        assert Conditional(Number(1), [Number(1)]).evaluate(parent).value == 1
        assert Conditional(Number(3), [Number(1)],
                           [Number(2)]).evaluate(parent).value == 1

    def test_cond_empty(self):
        parent = Scope()
        Conditional(Number(0), [],
                    []).evaluate(parent)
        Conditional(Number(1), [],
                    []).evaluate(parent)
        Conditional(Number(1), None, None).evaluate(parent)


class TestRead:
    def test_read_base(self):
        st = str(7)
        with patch('sys.stdin', StringIO(st)):
            parent = Scope()
            assert get_value(Read('b').evaluate(parent)) == 7

    def test_read_scope(self):
        st = str(7)
        with patch('sys.stdin', StringIO(st)):
            parent = Scope()
            Read('a').evaluate(parent)
            assert get_value(parent['a']) == 7


class TestPrint:
    def test_print_base(self):
        st = StringIO()
        with patch('sys.stdout', st):
            assert get_value(Print(Number(5)).evaluate(Scope())) == 5
            assert st.getvalue() == '5\n'
