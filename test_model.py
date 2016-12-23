#!/usr/bin/env python3


from io import StringIO
from unittest.mock import patch

from yat.model import *


class TestScope:
    def test_scope_set(self):
        s = Scope()
        s['a'] = Number(7)
        assert s['a'].value == Number(7).value

    def test_scope_get_from_parent(self):
        parent = Scope()
        child = Scope(parent)
        parent['a'] = Number(7)
        assert child['a'].value == Number(7).value

    def test_scope_get(self):
        parent = Scope()
        parent['a'] = Number(1)
        parent['b'] = Number(2)
        scope = Scope(parent)
        scope['a'] = Number(3)
        assert Print(Reference('a')).evaluate(scope).value == 3
        assert Print(scope['b']).evaluate(scope).value == 2
        assert parent['a'].value == 1


class TestNumber:
    def test_number_value(self):
        assert Number(7).value == 7

    def test_number_evaluate(self):
        assert Number(7).evaluate(Scope()).value == 7


class TestBinOp:
    def test_bin_op_all(self):
        bin_op = BinaryOperation
        parent = Scope()

        result = bin_op(Number(3), '+', Number(2)).evaluate(parent).value
        assert result == 5

        result = bin_op(Number(3), '-', Number(2)).evaluate(parent).value
        assert result == 1

        result = bin_op(Number(3), '*', Number(2)).evaluate(parent).value
        assert result == 6

        result = bin_op(Number(3), '/', Number(2)).evaluate(parent).value
        assert result == 1

        result = bin_op(Number(3), '%', Number(2)).evaluate(parent).value
        assert result == 1

        result = bin_op(Number(3), '<', Number(2)).evaluate(parent).value
        assert result == 0

        result = bin_op(Number(3), '>', Number(2)).evaluate(parent).value
        assert result != 0

        result = bin_op(Number(3), '==', Number(2)).evaluate(parent).value
        assert result == 0

        result = bin_op(Number(3), '<=', Number(2)).evaluate(parent).value
        assert result == 0

        result = bin_op(Number(3), '-', Number(2)).evaluate(parent).value
        assert result != 0

        result = bin_op(Number(3), '&&', Number(2)).evaluate(parent).value
        assert result != 0

        result = bin_op(Number(3), '||', Number(2)).evaluate(parent).value
        assert result != 0

    def test_bin_op_eval(self):
        bin_op = BinaryOperation
        assert bin_op(Number(3),
                      '*',
                      bin_op(Number(8),
                             '+',
                             Number(1))).evaluate(Scope()).value == 27


class TestUnOp:
    def test_un_op_all(self):
        un_op = UnaryOperation

        result = un_op('!', Number(3)).evaluate(Scope()).value
        assert result == 0

        result = un_op('!', Number(0)).evaluate(Scope()).value
        assert result != 0

        result = un_op('-', Number(3)).evaluate(Scope()).value
        assert result == -3

    def test_un_op_eval(self):
        bin_op = BinaryOperation
        un_op = UnaryOperation
        sc = Scope()

        assert un_op('!', bin_op(Number(3),
                                 '*',
                                 bin_op(Number(8),
                                        '+',
                                        Number(1)))).evaluate(sc).value == 0
        assert un_op('-', bin_op(Number(3),
                                 '*',
                                 bin_op(Number(8),
                                        '+',
                                        Number(1)))).evaluate(sc).value == -27


class ReferenceTests:
    def test_reference(self):
        parent = Scope()
        parent['a'] = Number(5)
        assert Reference('a').evaluate(parent).value == 5

    def test_reference_parent(self):
        parent = Scope()
        child = Scope(parent)
        parent['a'] = Number(5)
        assert Reference('a').evaluate(child).value == 5


class TestFunction:
    def test_func_base(self):
        sc = Scope()
        nm = Number
        sc['foo'] = Function(('a', 'b'),
                             [BinaryOperation(Reference('a'),
                                              '+',
                                              Reference('b'))])
        assert FunctionCall(FunctionDefinition('foo', sc['foo']),
                            [nm(5),
                             UnaryOperation('-',
                                            nm(3))]).evaluate(sc).value == 2

    def test_func_empty(self):
        parent = Scope()
        parent['foo'] = Function(('a', 'b'), [])
        FunctionCall(FunctionDefinition('foo', parent['foo']),
                     [Number(5),
                      Number(3)]).evaluate(parent)

    def test_func_in_func(self):
        f_def = FunctionDefinition
        sc = Scope()
        sc['foo'] = Function((),
                             [
                                 Number(10)
                             ])
        sc['bar'] = Function((),
                             [
                                 Number(20)
                             ])
        sc['chose_func'] = Function(('a', 'b'),
                                    [
                                        Conditional(
                                            BinaryOperation(
                                                Reference('a'),
                                                '>',
                                                Reference('b')
                                            ),
                                            [
                                                f_def('foo', sc['foo'])
                                            ],
                                            [
                                                f_def('bar', sc['bar'])
                                            ]
                                        )
                                    ])
        sc['a'] = Number(2)
        sc['b'] = Number(1)
        sc['new_foo'] = FunctionCall(f_def('chose_func', sc['chose_func']),
                                     [sc['a'], sc['b']]).evaluate(sc)
        assert FunctionCall(f_def('new_foo', sc['new_foo']),
                            []).evaluate(sc).value == 10
        sc['b'] = Number(3)
        sc['new_bar'] = FunctionCall(f_def('chose_func', sc['chose_func']),
                                     [sc['a'], sc['b']]).evaluate(sc)
        assert FunctionCall(f_def('new_bar', sc['new_bar']),
                            []).evaluate(sc).value == 20

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
        assert FunctionCall(f_def, [Number(25)]).evaluate(parent).value == 25

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
        assert Reference('arg').evaluate(parent).value == 1


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

    def test_cond_in_func(self):
        for a in range(-10, 10):
            for b in range(-10, 10):
                for c in range(-10, 10):
                    self._helper_test_cond(a, b, c, c if a + b == c else -1)

    # this condition checks if a + b == c in a combination of functions
    def _helper_test_cond(self, a, b, c, res):
        ref = Reference
        bin_op = BinaryOperation
        st = '{}\n{}\n{}\n'.format(a, b, c)
        with patch('sys.stdin', StringIO(st)):
            parent = Scope()
            parent['foo'] = Function(('enum', 'denom', 'val'),
                                     [
                                         Conditional(
                                             FunctionCall(ref('check_answer'),
                                                          [ref('enum'),
                                                           ref('denom'),
                                                           ref('val')]),
                                             [
                                                 ref('val')
                                             ],
                                             [
                                                 Number(-1)
                                             ]
                                         )
                                     ])
            parent['check_answer'] = Function(('a', 'b', 'c'),
                                              [
                                                  Conditional(
                                                      bin_op(ref('c'),
                                                             '==',
                                                             bin_op(ref('a'),
                                                                    '+',
                                                                    ref('b'))),
                                                      [
                                                          Number(1)
                                                      ],
                                                      [
                                                          Number(0)
                                                      ])
                                              ])
            assert FunctionCall(FunctionDefinition('foo', parent['foo']),
                                [
                                    Read('first'),
                                    Read('second'),
                                    Read('third')
                                ]).evaluate(parent).value == res


class TestRead:
    def test_read_base(self):
        st = str(7)
        with patch('sys.stdin', StringIO(st)):
            parent = Scope()
            assert Read('b').evaluate(parent).value == 7

    def test_read_scope(self):
        st = str(7)
        with patch('sys.stdin', StringIO(st)):
            parent = Scope()
            Read('a').evaluate(parent)
            assert parent['a'].value == 7


class TestPrint:
    def test_print_base(self):
        st = StringIO()
        with patch('sys.stdout', st):
            assert Print(Number(5)).evaluate(Scope()).value == 5
            assert st.getvalue() == '5\n'
