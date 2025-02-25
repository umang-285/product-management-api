from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import CategoryViewset, ProductViewSet

router = SimpleRouter()
router.register("categories", CategoryViewset, basename='category')
router.register("", ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]
