import json
from celery import shared_task
from .models import Category, Product

@shared_task
def process_json_file(file_data):
    data = json.loads(file_data)

    # Process Categories
    for category in data.get("categories", []):
        Category.objects.update_or_create(
            id=category['id'],
            defaults={
                'category_name': category['category_name'],
                'description': category.get('category_description', ""),
            }
        )
    
    # Process Products
    for product in data.get("products", []):
        category = Category.objects.get(id=product['category_id'])
        if category:
            Product.objects.update_or_create(
                id=product['id'],
                defaults={
                    "category": category,
                    "product_name": product["product_name"],
                    "product_description": product.get("product_description", ""),
                    "product_price": product["product_price"],
                    "currency": product.get("currency", "INR"),
                    "stock_qty": product["stock_quantity"],
                    "sku": product["sku"],
                    "image_url": product.get("image_url", ""),
                }
            )
