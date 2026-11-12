from django.urls import path
from . import views

app_name = 'lost_and_found'

urlpatterns = [
    path('', views.listing_list, name='listing_list'),
    path('<int:id>/', views.listing_detail, name='listing_detail'),
]