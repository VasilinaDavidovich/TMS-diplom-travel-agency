from django.urls import path
from . import views

urlpatterns = [
    # Frontend страницы (доступны по корневым URL)
    path('', views.home_page, name='home'),
    path('hotel/<int:hotel_id>/', views.hotel_detail_page, name='hotel-detail-page'),
    path('search/', views.search_results_page, name='search-results'),
]