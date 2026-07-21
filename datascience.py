import pandas as pd

# 예시 매출 데이터
sales = pd.DataFrame({
    "Day":      ["Mon","Mon","Tue"],
    "Item":     ["Coffee","Cookie","Tea"],
    "Category": ["Drink","Dessert","Drink"],
    "Price":    [3000,2000,2500],
    "Qty":      [10,15,8]
})

# 그룹화로 카테고리별 평균 가격과 총수량 계산
group = sales.groupby("Category").agg(
    avg_price=("Price","mean"),
    total_qty=("Qty","sum")
)

# 피벗 테이블로 요일×카테고리 교차 합계 구성
pivot = sales.pivot_table(
    values="Qty", index="Day", columns="Category",
    aggfunc="sum", fill_value=0
)

print(group)
print(pivot)

