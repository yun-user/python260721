# def f(x):
#     return 2 * x + 7
# def g(x):
#     return x ** 2

# x = 2 
# print(f(x) + g(x) + f(g(x))+ g(f(x)))
# def spam(eggs):
#     eggs.append(1)
#     eggs = [2,3]

# ham = [0]
# spam(ham)
# print(ham)

# def f():
#     global s
#     s = " I love London!"
#     print(s)
# s = "I love paris!"
# f()
# print(s)

def calculate(x,y):
    total = x + y
    print("In function")
    print(
        "a: ",str(a),
        "b:",str(b),
        "a + b: ", str(a + b),
        "total: ", str(total)
    )
    return total

a = 5
b = 7
total = 0
print("In program - 1")
print(
    "a: ", str(a),
    "b: ",str(b),
    "a + b: ", str(a + b),
)
sum = calculate(a,b)
print("After Calculation")
print("Total: ",str(total),"sum: ",str(sum))

# def factorial(n):
#     if n == 1:
#         return 1
#     else:
#         return n * factorial(n - 1)
# print(factorial(int(input("Input Number for Factorial Calculation:"))))

# def print_something(my_name,your_name):
#     print("Hello {0}, My name is {1}".format(your_name,my_name))

# print_something("Sungchul","TEAMLAB")
# print_something(your_name="Sungchul",my_name="TEAMLAB")

# def print_something(my_name,your_name = "TEAMLAB"):
#     print("Hello {0}, My name is {1}".format(your_name,my_name))
# print_something("TEAMLAB","Sungchul")
# print_something("Sungchul")

# def asterisk_test(a,b,*args):
#     return a + b + sum(args)

# print(asterisk_test(1,2,3,4,5))

# def asterisk_test(a,b,*args):
#     print(args)
# print(asterisk_test(1,2,3,4,5))

# def asterisk_test_2(*args):
#     x,y,*z = args
#     return x, y ,z

# print(asterisk_test_2(3,4,5))

# def kwargs_test(**kwargs):
#     print(kwargs)
#     print("First value is {first}".format(**kwargs))
#     print("Second value is {second}".format(**kwargs))
#     print("Third value is {third}".format(**kwargs))

# print(kwargs_test(first = 3 , second = 4, third = 5))