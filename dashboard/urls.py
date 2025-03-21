from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from . import views

urlpatterns = [

    # path('logout/', views.logout, name='logout'),
    path('', views.dashboard, name='dashboard'),

]
