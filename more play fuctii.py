def f(x):
    #Возвращает целое число в квадрате
    return x**2
print(f(4))

def stroka(x):
    #Возвращает строку
    return x
print(stroka("Привет"))

def y(x, n, p=2, z=4, b=9):
    #Принимает 3 значенрия + 2 обязательных суммирует их и выводит результат
    return x + n + p + z + b
result = y(2,4,8,)
print(result)

def divide(x):
    #Первая функция целое число делит на 2 , Вторая фунцкия берет результат первой и умножает на 4
    return x / 2


def multiply(x):
    return x * 4

y = divide(4)
z = multiply(y)

print(z)

def strong(string):
    # возвращает строку в float , но при этом сделали исключение
    return float (string)
try:
    a = strong("neb")
    print(a)
except ValueError:
    print("строка не может быть числом ")




