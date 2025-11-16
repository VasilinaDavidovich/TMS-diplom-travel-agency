from django.shortcuts import render, get_object_or_404
from typing import Any, Dict

from .models import Hotel


# главная страница
def home_page(request) -> Any:
    # Выводится 6 рандомных отелей из базы данных
    hotels = Hotel.objects.all().order_by('?')[:6]
    context: Dict[str, Any] = {'hotels': hotels}
    return render(request, 'home.html', context)


# страница конкретного отеля
def hotel_detail_page(request, hotel_id: int) -> Any:
    hotel = get_object_or_404(Hotel, id=hotel_id)
    context: Dict[str, Any] = {'hotel': hotel}
    return render(request, 'hotel_detail.html', context)

# страница результатов поиска
def search_results_page(request) -> Any:
    return render(request, 'search_results.html')