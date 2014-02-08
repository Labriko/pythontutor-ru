# -*- coding: utf-8 -*-

# решим квадратное уравнение ax^2 + bx + c = 0
# программа получает на вход коэффициенты
# программа выводит все корни через пробел

a = int(eval(input()))
b = int(eval(input()))
c = int(eval(input()))

d = b ** 2 - 4 * a * c

if d > 0:
    x1 = (-b - d ** 0.5) / (2 * a)
    x2 = (-b + d ** 0.5) / (2 * a)
    print((x1, x2))
elif d == 0:
    x = -b / (2 * a)
    print(x)