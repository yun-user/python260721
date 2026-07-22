import sqlite3
from dataclasses import dataclass


@dataclass
class Product:
    productID: int
    productName: str
    productPrice: int


class ProductDB:
    def __init__(self, db_file: str = r"c:\work\MyProduct.db"):
        self.db_file = db_file
        self.con = sqlite3.connect(self.db_file)
        self.cur = self.con.cursor()
        self.create_table()

    def create_table(self):
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Products (
                productID INTEGER PRIMARY KEY,
                productName TEXT NOT NULL,
                productPrice INTEGER NOT NULL
            );
            """
        )
        self.con.commit()

    def insert_product(self, product_id: int, product_name: str, product_price: int):
        self.cur.execute(
            "INSERT OR REPLACE INTO Products (productID, productName, productPrice) VALUES (?, ?, ?);",
            (product_id, product_name, product_price),
        )
        self.con.commit()

    def insert_products(self, products):
        self.cur.executemany(
            "INSERT OR REPLACE INTO Products (productID, productName, productPrice) VALUES (?, ?, ?);",
            [(p.productID, p.productName, p.productPrice) for p in products],
        )
        self.con.commit()

    def update_product(self, product_id: int, product_name: str, product_price: int):
        self.cur.execute(
            "UPDATE Products SET productName = ?, productPrice = ? WHERE productID = ?;",
            (product_name, product_price, product_id),
        )
        self.con.commit()

    def delete_product(self, product_id: int):
        self.cur.execute("DELETE FROM Products WHERE productID = ?;", (product_id,))
        self.con.commit()

    def select_all_products(self):
        self.cur.execute("SELECT productID, productName, productPrice FROM Products ORDER BY productID;")
        return self.cur.fetchall()

    def select_product(self, product_id: int):
        self.cur.execute(
            "SELECT productID, productName, productPrice FROM Products WHERE productID = ?;",
            (product_id,),
        )
        return self.cur.fetchone()

    def close(self):
        if self.con:
            self.con.close()


def make_sample_products(count: int = 1000):
    products = []
    for i in range(1, count + 1):
        product_name = f"전자제품_{i:04d}"
        product_price = 10000 + (i * 137) % 900000
        products.append(Product(i, product_name, product_price))
    return products


if __name__ == "__main__":
    db = ProductDB()

    sample_products = make_sample_products(1000)
    db.insert_products(sample_products)

    print("전체 상품 수:", len(db.select_all_products()))
    print("1번 상품:", db.select_product(1))

    db.update_product(1, "전자제품_0001_수정", 99999)
    print("수정 후 1번 상품:", db.select_product(1))

    db.delete_product(1000)
    print("삭제 후 전체 상품 수:", len(db.select_all_products()))

    db.close()