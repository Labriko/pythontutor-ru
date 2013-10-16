--- DONE ---

a = input
b = input
print(a + b)
TypeError: unsupported operand type(s) for +: 'builtin_function_or_method' and 'builtin_function_or_method'

a = []
a[0] = 1
IndexError: list assignment index out of range

EOFError: EOF when reading a line


a = input()
b = input()
print(a % b)
TypeError: not all arguments converted during string formatting


if True:
a = 2
Error: expected an indented block


a = 2
 b = 3
Error: unexpected indent


def f(a):
    print(a)
f()

def f(a, b):
    print(a, b)
f()
TypeError: f() takes exactly 1 argument (0 given)


def f():
    pass
f(9)
TypeError: f() takes no arguments (1 given)


print(a)
NameError: name 'a' is not defined


numEggs = 12
print('I have ' + numEggs + ' eggs.')

s = '3' + 2
TypeError: cannot concatenate 'str' and 'int' objects


for i in range([1, 2]):
    print(i)
TypeError: an integer is required


a = 'abc'
a[1] = 'd'
TypeError: 'str' object does not support item assignment

spam = range(10)
spam[4] = -1
TypeError: 'xrange' object does not support item assignment


print('Hello!)
Error: EOL while scanning string literal




------------------------------------------------------- TODO --------------------------------------------------
------------------------------------------------------- TODO --------------------------------------------------


Развести Invalid syntax:
    a := 5
    if a = 5:
    if a == 4
    unmatched parentheses
    keyword as variable name
    a++




spam = 'THIS IS IN LOWERCASE.'
spam = spam.lowerr()
AttributeError: 'str' object has no attribute 'lowerr'


spam = {'cat': 'Zophie', 'dog': 'Basil', 'mouse': 'Whiskers'}
print('The name of my pet zebra is ' + spam['zebra'])


someVar = 42
def myFunction():
    print(someVar)
    someVar = 100
myFunction()
UnboundLocalError: local variable 'foobar' referenced before assignment



--- NON-PYTHONIC STYLE ---

Don't :

for i in range(len(tab)) :
    print tab[i]
Do :

for elem in tab :
    print elem

Use enumerate if you really need both the index and the element.

for i, elem in enumerate(tab):
     print i, elem


concatenation without join


else if


[[0] * 5] * 9


def foo(bar=[]):
    bar.append('baz')
    return bar