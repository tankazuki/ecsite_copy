from django.urls import path
from . import views
from django.contrib.auth import views as auth_view

app_name = 'amazon'

urlpatterns = [
    path('lp/', views.Lp.as_view(), name='lp'),
    path('items/', views.ItemList.as_view(), name='item_list'),
    path('items/<int:pk>', views.ItemDetail.as_view(), name='item_detail'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout', auth_view.LogoutView.as_view(), name='logout'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('signup/done/<token>', views.SignUpDone.as_view(), name='signup_done'),
    path('cart/<int:pk>', views.ShoppingCartDetail.as_view(), name='cart'),
    path('ajax_amount/', views.update_cart_item, name='update_cart_item_amount'),
    path('ajax_delete', views.delete_cart_item, name='delete_cart_item'),
]