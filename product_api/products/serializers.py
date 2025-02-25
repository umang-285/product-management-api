from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "category_name", "description", "parent", "subcategories"]

    def get_subcategories(self, obj):
        return CategorySerializer(
            obj.subcategories.filter(is_deleted=False), many=True
        ).data


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.category_name", read_only=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "category_name",
            "product_name",
            "product_description",
            "product_price",
            "currency",
            "stock_qty",
            "sku",
            "image_url",
        ]


class UploadFileSerializer(serializers.Serializer):
    file = serializers.FileField()
