from django.urls import path
from . import views

app_name = 'amazon'

urlpatterns = [
    path('lp/', views.Lp.as_view(), name='lp'),
    path('items/', views.ItemList.as_view(), name='item_list'),
    path('items/<int:pk>', views.ItemDetail.as_view(), name='item_detail')
]