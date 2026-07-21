# import sys
# print(sys.getsizeof("a"),sys.getsizeof("ab"),sys.getsizeof("abc"))
# name = "Alex"
# age = 23
# print(f"My name is {name}, I am {age}years old")

word = input("input a word:")
word_list = list(word)
print("world list:" , word_list)

result = []
for i in range(len(word_list)):
    result.append(word_list.pop())

print("result:",result)
print(f"reverse world:{word[::-1]}")