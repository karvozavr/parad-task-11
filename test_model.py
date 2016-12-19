#!/usr/bin/env python3


from yat.model import *
from io import StringIO
import sys
from unittest.mock import patch


# Scope tests


def test_scope_set():
    s = Scope()
    s['a'] = Number(7)
    assert s['a'].value == Number(7).value


def test_scope_get_from_parent():
    parent = Scope()
    child = Scope(parent)
    parent['a'] = Number(7)
    assert child['a'].value == Number(7).value


def test_scope_get():
    main = Scope()
    main['a'] = Number(1)
    main['b'] = Number(2)
    scope = Scope(main)
    scope['a'] = Number(3)
    assert Print(Reference('a')).evaluate(scope).value == 3
    assert Print(scope['b']).evaluate(scope).value == 2
    assert main['a'].value == 1


# Number tests


def test_number_value():
    assert Number(7).value == 7


def test_number_evaluate():
    assert Number(7).evaluate(Scope()).value == 7


# BinaryOperation tests


def test_bin_op_all():
    ref = Reference
    bin_op = BinaryOperation
    main = Scope()

    for l in range(-10, 10):
        for r in range(1, 10):
            main['a'] = Number(l)
            main['b'] = Number(r)

            result = bin_op(ref('a'), '+', ref('b')).evaluate(main).value
            assert l + r == result
            print('{lv}{op}{rv}={res}'.format(lv=l, op='+', rv=r, res=result))

            result = bin_op(ref('a'), '-', ref('b')).evaluate(main).value
            assert l - r == result
            print('{lv}{op}{rv}={res}'.format(lv=l, op='-', rv=r, res=result))

            result = bin_op(ref('a'), '*', ref('b')).evaluate(main).value
            assert l * r == result
            print('{lv}{op}{rv}={res}'.format(lv=l, op='*', rv=r, res=result))

            result = bin_op(ref('a'), '/', ref('b')).evaluate(main).value
            assert l // r == result
            print('{lv}{op}{rv}={res}'.format(lv=l, op='/', rv=r, res=result))

            result = bin_op(ref('a'), '%', ref('b')).evaluate(main).value
            assert l % r == result
            print('{lv}{op}{rv}={res}'.format(lv=l, op='%', rv=r, res=result))

            result = bin_op(ref('a'), '<', ref('b')).evaluate(main).value
            assert int(l < r) == result
            print('{lv}{op}{rv}={res}'.format(lv=l, op='<', rv=r, res=result))

            result = bin_op(ref('a'), '>', ref('b')).evaluate(main).value
            assert int(l > r) == result
            print('{lv}{op}{rv}={res}'.format(lv=l, op='>', rv=r, res=result))

            result = bin_op(ref('a'), '==', ref('b')).evaluate(main).value
            assert int(l == r) == result
            print('{lv}{op}{rv}={res}'.format(lv=l, op='==', rv=r, res=result))

            result = bin_op(ref('a'), '<=', ref('b')).evaluate(main).value
            assert int(l <= r) == result
            print('{lv}{op}{rv}={res}'.format(lv=l, op='<=', rv=r, res=result))

            result = bin_op(ref('a'), '>=', ref('b')).evaluate(main).value
            assert int(l >= r) == result
            print('{lv}{op}{rv}={res}'.format(lv=l, op='>=', rv=r, res=result))

            result = bin_op(ref('a'), '&&', ref('b')).evaluate(main).value
            assert int(l and r) == result
            print('{lv}{op}{rv}={res}'.format(lv=l, op='&&', rv=r, res=result))

            result = bin_op(ref('a'), '||', ref('b')).evaluate(main).value
            assert int(l or r) == result


def test_bin_op_eval():
    bin_op = BinaryOperation
    assert bin_op(Number(3),
                  '*',
                  bin_op(Number(8),
                         '+',
                         Number(1))).evaluate(Scope()).value == 27


# UnaryOperation tests


def test_un_op_all():
    un_op = UnaryOperation

    for i in range(-100, 100):
        result = un_op('!', Number(i)).evaluate(Scope()).value
        assert int(not i) == result

        result = un_op('-', Number(i)).evaluate(Scope()).value
        assert int(-i) == result


def test_un_op_eval():
    bin_op = BinaryOperation
    un_op = UnaryOperation

    assert un_op('!', bin_op(Number(3),
                             '*',
                             bin_op(Number(8),
                                    '+',
                                    Number(1)))).evaluate(Scope()).value == 0
    assert un_op('-', bin_op(Number(3),
                             '*',
                             bin_op(Number(8),
                                    '+',
                                    Number(1)))).evaluate(Scope()).value == -27


# Reference tests


def test_reference():
    main = Scope()
    main['a'] = Number(5)
    assert Reference('a').evaluate(main).value == 5


def test_reference_parent():
    main = Scope()
    child = Scope(main)
    main['a'] = Number(5)
    assert Reference('a').evaluate(child).value == 5


# Functions test


def test_func_base():
    main = Scope()
    main['foo'] = Function(('a', 'b'),
                           [BinaryOperation(Reference('a'),
                                            '+',
                                            Reference('b'))])
    assert FunctionCall(FunctionDefinition('foo', main['foo']),
                        [Number(5),
                         UnaryOperation('-',
                                        Number(3))]).evaluate(main).value == 2


def test_func_in_func():
    f_def = FunctionDefinition
    main = Scope()
    main['foo'] = Function((),
                           [
                               Number(10)
                           ])
    main['bar'] = Function((),
                           [
                               Number(20)
                           ])
    main['chose_func'] = Function(('a', 'b'),
                                  [
                                      Conditional(
                                          BinaryOperation(
                                              Reference('a'),
                                              '>',
                                              Reference('b')
                                          ),
                                          [
                                              f_def('foo', main['foo'])
                                          ],
                                          [
                                              f_def('bar', main['bar'])
                                          ]
                                      )
                                  ])
    main['a'] = Number(2)
    main['b'] = Number(1)
    main['new_foo'] = FunctionCall(f_def('chose_func', main['chose_func']),
                                   [main['a'], main['b']]).evaluate(main)
    assert FunctionCall(f_def('new_foo', main['new_foo']),
                        []).evaluate(main).value == 10
    main['b'] = Number(3)
    main['new_bar'] = FunctionCall(f_def('chose_func', main['chose_func']),
                                   [main['a'], main['b']]).evaluate(main)
    assert FunctionCall(f_def('new_bar', main['new_bar']),
                        []).evaluate(main).value == 20


def test_func_def():
    main = Scope()
    f_def = FunctionDefinition(
        'foo',
        Function(['arg'],
                 [
                     Reference('arg')
                 ]
                 )
    )
    assert FunctionCall(f_def, [Number(25)]).evaluate(main).value == 25


def test_func_call():
    main = Scope()
    main['arg'] = Number(1)
    f_def = FunctionDefinition(
        'foo',
        Function(['arg'],
                 [
                     Reference('arg')
                 ]
                 )
    )
    FunctionCall(f_def, [Number(25)]).evaluate(main)
    assert Reference('arg').evaluate(main).value == 1


# Conditional test


def test_cond_base():
    # if condition is not Number(0) it's true
    main = Scope()
    assert Conditional(Number(0), [Number(1)],
                       [Number(2)]).evaluate(main).value == 2
    assert Conditional(Number(3), [Number(1)],
                       [Number(2)]).evaluate(main).value == 1


def test_cond_in_func():
    for a in range(-10, 10):
        for b in range(-10, 10):
            for c in range(-10, 10):
                _helper_test_cond(a, b, c, c if a + b == c else -1)


def _helper_test_cond(a, b, c, res):
    bin_op = BinaryOperation
    st = '{}\n{}\n{}\n'.format(a, b, c)
    with patch('sys.stdin', StringIO(st)):
        main = Scope()
        main['foo'] = Function(('enum', 'denom', 'val'),
                               [
                                   Conditional(
                                       FunctionCall(Reference('check_answer'),
                                                    [Reference('enum'),
                                                     Reference('denom'),
                                                     Reference('val')]),
                                       [
                                           Reference('val')
                                       ],
                                       [
                                           Number(-1)
                                       ]
                                   )
                               ])
        main['check_answer'] = Function(('a', 'b', 'c'),
                                        [
                                            Conditional(
                                                bin_op(Reference('c'),
                                                       '==',
                                                       bin_op(Reference('a'),
                                                              '+',
                                                              Reference('b'))),
                                                [
                                                    Number(1)
                                                ],
                                                [
                                                    Number(0)
                                                ])
                                        ])
        assert FunctionCall(FunctionDefinition('foo', main['foo']),
                            [
                                Read('first'),
                                Read('second'),
                                Read('third')
                            ]).evaluate(main).value == res


# Read test


def test_read_base():
    st = str(7)
    with patch('sys.stdin', StringIO(st)):
        main = Scope()
        assert Read('b').evaluate(main).value == 7


def test_read_scope():
    st = str(7)
    with patch('sys.stdin', StringIO(st)):
        main = Scope()
        Read('a').evaluate(main)
        assert main['a'].value == 7


# Print test


def test_print_base():
    st = StringIO()
    with patch('sys.stdout', st):
        assert Print(Number(5)).evaluate(Scope()).value == 5
        assert st.getvalue() == '5\n'
