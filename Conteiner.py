fruit = ["Персик", "ЯБлоко", "Киска"]
#Добавление в контейнер(списка) новые значения
fruit.append("Банан")
fruit.append("a")

print (fruit)

#Создание контейнера(списка)
random = []
random.append("true")
random.append(100)
random.append(1.1)
random.append("Hello")

print(random)
#Замена параметра в контейнере(списка)
random[2] = "privet"

#Удаление из контейнера(списка) значения ( крайнего)
item = random.pop()

print(item)
print(random)

print(random + fruit)
#Проверка , что 100 есть в контейнере(списка) рандом
yes = 100 in random

print(yes)
#Проверка , что 100 нету в контейнере(списка) рандом
no = 100 not in random

print(no)

#Узнаем длину контейнера(Списка)

print(len(random))



