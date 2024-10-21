from django.urls import path
from .views import ProductListView, ProductDetailView, CreateProduct, UpdateProduct, TaskDelete, CustomLoginView, logout_view

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('', ProductListView.as_view(), name='product'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='products'),
    path('add-product/', CreateProduct.as_view(), name='add-product'),
    path('update-product/<int:pk>/', UpdateProduct.as_view(), name='update-product'),
    path('delete-product/<int:pk>/', TaskDelete.as_view(), name='delete-product'),
]