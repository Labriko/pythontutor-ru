#!/usr/bin/env python2
# -*- coding: utf-8 -*-


import re

# set these variables by calling config_workarounds() function
my_raw_input = None
my_stdout = None
my_true_stdout = None


def config_workarounds(passed_raw_input, passed_stdout, passed_true_stdout):
    global my_raw_input
    global my_stdout
    global true_stdout
    my_raw_input = passed_raw_input
    my_stdout = passed_stdout
    my_true_stdout = passed_true_stdout


def split_by_string_literals(three):
    '''
        >>> three = r"""s = "a'"; b = 'b"'; c = 42"""
        >>> split_by_string_literals(three)
        [('s = ', None), ("a'", <type 'str'>), ('; b = ', None), ('b"', <type 'str'>), ('; c = 42', None)]
    '''

    '''
        parsing is done by the following finite state automaton:


               |--------------------|
               |                   [']
               v                    |
        |> NOT_A_STR  ---[']--->  'STR  ---[\]--->  '\STR --|
        |      |                    ^                       |
        |      |                    |--------[any]----------|
        |      |  
        |      |             
        |      |                    |--------[any]----------|                                
        |      |                    v                       |       
        |      |------["]------>  "STR  ---[\]--->  "\STR --|
        |                           |
        |-----------["]-------------|
    '''
    TRANSITIONS = {'NOT_A_STR': {"'": ("'STR", 'finish', None, 'post'), '"': ('"STR', 'finish', None, 'post'), 'any': ('NOT_A_STR', 'push')},
                   "'STR"     : {"\\": ("'\STR", 'push'), "'": ('NOT_A_STR', 'finish', str, 'pre'), 'any': ("'STR", 'push')},
                   "'\STR"    : {'any': ("'STR", 'push')},
                   '"STR'     : {"\\": ('"\STR', 'push'), '"': ('NOT_A_STR', 'finish', str, 'pre'), 'any': ('"STR', 'push')},
                   '"\STR'    : {'any': ('"STR', 'push')},
                  }

    parts = []
    current_part = []
    current_state = 'NOT_A_STR'

    for symbol in three:
        if symbol in TRANSITIONS[current_state]:
            transition = TRANSITIONS[current_state][symbol]
        else:
            transition = TRANSITIONS[current_state]['any']
        current_state = transition[0]
        if transition[1] == 'push':
            current_part.append(symbol)
        else:
            if transition[3] == 'pre':
                current_part.append(symbol)
            parts.append((''.join(current_part), transition[2]))
            if transition[3] == 'post':
                current_part = [symbol]
            else:
                current_part = []

    parts.append((''.join(current_part), None))
    return parts


def three_to_two(three):
    # input vs. raw_input is hardcoded into pg_logger
    three_parts = split_by_string_literals(three)
    process_none = lambda code: str_to_unicode(ceil_floor_3to2(range_3to2(division_3to2(print_function_3to2(code)))))
    process_str = lambda x: 'unicode(' + x + ')'
    return ''.join([process_str(code) if codetype is str else process_none(code) for code, codetype in three_parts])


def str_to_unicode(three):
    return re.sub(r"str\s*\(", 'unicode(', three)


def print_function_3to2(three):
    '''
        >>> print_function_3to2('print(3, 5)')
        'print__workaround(3, 5)'
    '''
    return re.sub(r"print\s*\(", 'print__workaround(', three)
    #return re.sub(r"(?=[\s^]*)print\s*\(([^\n]*)\)", r"print \1", three)
    #return three


def print__workaround(*args, **kwargs):
    sep = kwargs.get('sep', ' ')
    end = kwargs.get('end', '\n')
    my_stdout.write(sep.join([str(e) for e in args]) + end)


def range_3to2(three):
    '''
        >>> range_3to2('a, b = range(3, 4, 2), 4')
        'a, b = xrange(3, 4, 2), 4'
    '''
    return re.sub(r"([\W^])range(?=\s*\()", r"\1xrange", three)
    return three


def division_3to2(three):
    '''
        >>> division_3to2('3 / 4')
        '3 * 1. / 4'
    '''
    return re.sub(r"([^/])/([^/])", r"\1* 1. /\2", three)
    return three


def by_bytes(s):
    return ', '.join(['{0} ({1})'.format(ord(i), repr(i)) for i in s])


def input__workaround():
    s = ''.join([i for i in my_raw_input() if ord(i) != 0])
    # print >> true_stdout, 'input__workaround returns {0} : {1}'.format(s, by_bytes(s))
    return s


# def unicode_literals_3to2(three):
#     u'''
#         >>> unicode_literals_3to2(u'a = "щф"')
#         u'a = unicode("\u0449\u0444")'
#         >>> unicode_literals_3to2(u"a = 'щф'")
#         u"a = unicode('\u0449\u0444')"
#     '''
#     return re.sub(r'"([^\n"]*)"', r'unicode("\1")', re.sub(r"'([^\n']*)'", r"unicode('\1')", three))


def ceil__workaround(x):
    import math
    return int(math.ceil(x))


def floor__workaround(x):
    import math
    return int(math.floor(x))


def ceil_floor_3to2(three):
    return re.sub(r"(?:math\s*\.\s*)?floor\s*\(", 'floor__workaround(', re.sub(r"(?:math\s*\.\s*)?ceil\s*\(", 'ceil__workaround(', three))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    code = """from math import floor, ceil
                  import math

                  for i in range(2, 4):
                      print(floor(i), ceil (i), math.floor(i), math.ceil(i), sep=', ', end='.')
                      print(5 / 12)
                      print('5 / 12', "5 / 12")
                      print(5 / 12)
            """
    expectation = """from math import floor, ceil
          import math

          for i in xrange(2, 4):
              print__workaround(floor__workaround(i), ceil__workaround(i), floor__workaround(i), ceil__workaround(i), sep=', ', end='.')
              print__workaround(5 * 1. / 12)
              print__workaround('5 / 12', "5 / 12")
              print__workaround(5 * 1. / 12)
        """

    print("Test:")
    print(code)
    print("Expected:")
    print(expectation)
    print("Got:")
    print((three_to_two(code)))
