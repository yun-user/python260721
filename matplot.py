import matplotlib.pyplot as plt

# x= [1,2,3,4,5]
# y = [2,4,6,8,10]

# plt.plot(x,y,marker = 'o')
# plt.title("simple Line Plot")
# plt.xlabel("X axis")
# plt.ylabel("Y axis")
# plt.show()

scores = [55,60,65,70,72,75,78,80,82,85,88,90,92,95,98]

plt.hist(scores, bins = 8, color ="skyblue", edgecolor = "black")
plt.title("Score Distribution")
plt.xlabel("Score")
plt.ylabel("Frequency")
plt.show()