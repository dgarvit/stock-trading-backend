from django.urls import path
from django.contrib.auth import views as auth_views
from .import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.login, {'template_name': 'login.html'}, name='login'),
    path('logout/', auth_views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('buy/', views.buy_stock, name='buy'),
    path('sell/', views.sell_stock, name='sell'),
    path('history/', views.view_txns, name='history'),
    path('transactions/', views.view_txns_user, name='user_transactions'),
]
