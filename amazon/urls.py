from django.urls import path
from . import views

appname = 'amazon'

urlpatterns = [
    path('lp/', views.Lp.as_view(), name='lp')
]