from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

app = FastAPI()
products = [
    {"product_id": 123, "name": "Smartphone",  "category": "Electronics", "price": 599.99},
    {"product_id": 456, "name": "Phone Case",  "category": "Accessories", "price": 19.99},
    {"product_id": 789, "name": "Iphone",       "category": "Electronics", "price": 1299.99},
    {"product_id": 101, "name": "Headphones",  "category": "Accessories", "price": 99.99},
    {"product_id": 202, "name": "Smartwatch",  "category": "Electronics", "price": 299.99},
]

@app.get('/product/{product_id}')
async def get_product_by_id(product_id: int):
    for product in products:
        if product["product_id"] == product_id:
            return product

@app.get("/products/search")
def search_products(
    keyword: str,
    category: Optional[str] = None,
    limit: int = 10
    ):
    results = []
    for product in products:
        if keyword.lower() not in product["name"].lower():
            continue
        if category and product["category"].lower() != category.lower():
            continue
        results.append(product)

    return results[:limit]