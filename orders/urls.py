from django.urls import path
from .views import (
    create_order, order_list, delete_order,
    category_list, create_category, edit_category, delete_category,
    product_list, create_product, edit_product, delete_product,
    get_product_price
)

urlpatterns = [
    # Order URLs
    path('order/create/', create_order, name='create_order'),
    path('orders/', order_list, name='order_list'),
    path('order/delete/<int:order_id>/', delete_order, name='delete_order'),
    
    # Category URLs
    path('categories/', category_list, name='category_list'),
    path('category/create/', create_category, name='create_category'),
    path('category/edit/<int:category_id>/', edit_category, name='edit_category'),
    path('category/delete/<int:category_id>/', delete_category, name='delete_category'),
    
    # Product URLs
    path('products/', product_list, name='product_list'),
    path('product/create/', create_product, name='create_product'),
    path('product/edit/<int:product_id>/', edit_product, name='edit_product'),
    path('product/delete/<int:product_id>/', delete_product, name='delete_product'),
    path('api/product/<int:product_id>/price/', get_product_price, name='get_product_price'),
]