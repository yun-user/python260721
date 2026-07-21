# import matplotlib.pyplot as plt

# x = [1, 2, 3, 4, 5]
# y = [2, 4, 6, 8, 10]

# plt.plot(x, y, marker="o")  # 선 그래프 marker은 점 모양 설정
# plt.title("Simple Line Plot")
# plt.xlabel("X Axis")
# plt.ylabel("Y Axis")
# plt.show()
#===================================================================================
# import matplotlib.pyplot as plt

# scores = [55, 60, 65, 70, 72, 75, 78, 80, 82, 85, 88, 90, 92, 95, 98]

# plt.hist(scores, bins=8, color="skyblue", edgecolor="black") #bins는 막대 개수,edgecolor는 막대 테두리 색,color는 막대 색
# plt.title("Score Distribution")
# plt.xlabel("Score")
# plt.ylabel("Frequency")
# plt.show()
#==========================================================================================
# '''Figure–Axes–Axis 구조 다이어그램'''

# import matplotlib.pyplot as plt
# from matplotlib.patches import Rectangle
# import numpy as np

# fig, ax = plt.subplots(figsize=(6, 4))
# ax.set_xlim(0, 10)
# ax.set_ylim(0, 7)
# ax.axis("off")

# # Figure 영역
# fig_box = Rectangle((0.5, 0.5), 9, 6, fill=False, linewidth=2)
# ax.add_patch(fig_box)
# ax.text(0.6, 6.7, "Figure", fontsize=12, va="bottom")

# # Axes 영역
# axes_box = Rectangle((1.3, 1.3), 7.4, 4.6, fill=False, linewidth=2)
# ax.add_patch(axes_box)
# ax.text(1.4, 5.9, "Axes", fontsize=12, va="bottom")

# # 축 레이블 표시
# ax.text(8.5, 1.1, "x-axis (Axis)", fontsize=10)
# ax.text(1.0, 5.0, "y-axis (Axis)", fontsize=10, rotation=90)

# # 눈금 흉내
# for t in np.linspace(1.5, 8.3, 6):
#     ax.plot([t, t], [1.3, 1.4])
# for t in np.linspace(1.7, 5.7, 5):
#     ax.plot([1.3, 1.4], [t, t])

# # Axes 내부 데이터 예시
# xs = np.linspace(1.5, 8.5, 100)
# ys = 3 + 1.2*np.sin((xs-1.5)/7.0 * 2*np.pi)
# ax.plot(xs, ys)

# plt.show()
#==========================================================================================
# import numpy as np
# import matplotlib.pyplot as plt

# # 난수 생성기 시드 고정 (재현 가능성을 위해 항상 동일한 난수 생성)
# np.random.seed(19680801)  

# # 데이터 딕셔너리 생성
# data = {
#     'a': np.arange(50),                   # 0부터 49까지 정수 (x축 데이터)
#     'c': np.random.randint(0, 50, 50),    # 0~49 사이 난수 50개 (색상 값으로 활용)
#     'd': np.random.randn(50)              # 표준정규분포 난수 50개 (크기 값으로 활용)
# }

# # y축 데이터 'b' = x축 데이터 'a' + 잡음(정규분포 * 10)
# data['b'] = data['a'] + 10 * np.random.randn(50)

# # 'd' 값을 양수로 변환 후 100배 확대 (산점도의 점 크기로 사용)
# data['d'] = np.abs(data['d']) * 100

# # Figure(전체 캔버스), Axes(데이터 영역) 생성
# # figsize: 그래프 크기, layout='constrained': 자동으로 여백 최적화
# fig, ax = plt.subplots(figsize=(5, 2.7), layout='constrained')

# # 산점도(scatter plot) 그리기
# # 'a' → x축, 'b' → y축, 'c' → 점 색상, 'd' → 점 크기
# ax.scatter('a', 'b', c='c', s='d', data=data)

# # x축, y축 라벨 설정
# ax.set_xlabel('entry a')
# ax.set_ylabel('entry b')

# # 그래프 출력
# plt.show()
#==========================================================================================
# import numpy as np
# import matplotlib.pyplot as plt

# x = np.linspace(0, 2, 100)  # 샘플 데이터 생성

# fig, ax = plt.subplots(figsize=(5, 2.7), layout='constrained')

# 서로 다른 함수 플로팅
# ax.plot(x, x, label='linear')        # y = x
# ax.plot(x, x**2, label='quadratic')  # y = x^2
# ax.plot(x, x**3, label='cubic')      # y = x^3
# ax.plot(x,x**4,label='quartic') # y = x^4
# # 축과 제목 설정
# ax.set_xlabel('x label')
# ax.set_ylabel('y label')
# ax.set_title("Simple Plot")

# # 범례 추가
# ax.legend()

# plt.show()
#==========================================================================================
# import seaborn as sns
# import matplotlib.pyplot as plt

# tips = sns.load_dataset("tips")
# print(type(tips))
# sns.scatterplot(data=tips, x="total_bill", y="tip")
# plt.title("Total Bill vs Tip")
# plt.show()
#==========================================================================================
# import seaborn as sns
# import matplotlib.pyplot as plt
# import pandas as pd
# import numpy as np

# # 가상 데이터 생성 
# # 난수 시드 고정 → 항상 동일한 값 생성
# np.random.seed(0)

# days = ["Sun", "Sat", "Thur", "Fri"]
# times = ["Lunch", "Dinner"]

# data = []
# for day in days:
#   for time in times:
#     # 각 조합에 대해 총 30개 샘플 생성
#     bills = np.random.normal(
#       loc=20 if time=="Lunch" else 25,  # 정규분포의 평균
#       scale=8,                          # 정규분포의 표준편차
#       size=30                           # 샘플 개수
#     )
#     for b in bills:
#       data.append({"day": day, "time": time, "total_bill": b})

# df = pd.DataFrame(data)

# # Boxplot 그리기
# sns.boxplot(
#   data=df, 
#   x="day",          # x축: 요일
#   y="total_bill",   # y축: 총 금액
#   hue="time",       # 'time' 기준으로 색상 구분: 점심/저녁
#   order=days        # x축 순서 지정
# )

# plt.title("Total Bill by Day and Time (Fake Data)")
# plt.show()
#==========================================================================================
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Theme once
sns.set_theme(style="whitegrid")

# Reproducibility
np.random.seed(42)
n = 150

# 공통적으로 사용할 데이터
df = pd.DataFrame({
    "category": np.random.choice(["A", "B", "C"], size=n, p=[0.4, 0.35, 0.25]),
    "value": np.concatenate([
        np.random.normal(0.0, 1.0, 60),
        np.random.normal(0.5, 1.2, 50),
        np.random.normal(-0.3, 0.8, 40)
    ]),
    "group": np.random.choice(["G1", "G2"], size=n),
    "feature1": np.random.normal(0, 1, n),
    "feature2": np.random.normal(1, 1.2, n),
    "feature3": np.random.normal(-0.5, 0.7, n),
})

# 여기에 Seaborn 플롯 별로 사용할 코드를 여기에 붙이기
# Copy & paste codes here!
# Code snippet -> 복사하여 공통 헤더 블록의 플롯 별로 사용할 코드 영역에 붙이기

# Violinplot: 분포 모양과 중앙값, 사분위수 표현
# split=True → hue가 두 그룹일 때 두 그룹을 한 축에 나누어 그림

# Figure와 Axes 객체 생성
fig, ax = plt.subplots(figsize=(6, 4))

# Violinplot 그리기
sns.violinplot(
    data=df, x="category", y="value", hue="group", split=True,
    linewidth=1.0,  # 테두리 선 두께
    ax=ax
)

# 제목 설정
ax.set_title("Seaborn Violinplot: Distribution by Category (split by Group)")

# 레이아웃 조정
fig.tight_layout()
plt.show()

