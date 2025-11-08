from django.contrib import admin
from .models import Country, City, Hotel, HotelImage, Review, Booking


class CityInline(admin.TabularInline):
    """Inline для отображения городов внутри страны"""

    model = City
    extra = 2
    show_change_link = True


class CountryAdmin(admin.ModelAdmin):
    """Админка для стран"""

    list_display = ['name']
    list_display_links = ['name']
    search_fields = ['name']
    inlines = [CityInline]


class HotelImageInline(admin.TabularInline):
    """Inline для отображения изображений отеля"""

    model = HotelImage
    extra = 3
    fields = ['image', 'preview']
    readonly_fields = ['preview']

    def preview(self, obj: HotelImage) -> str:
        """Показать превью изображения"""
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 100px;" />'
        return "Нет изображения"

    preview.allow_tags = True
    preview.short_description = "Превью"


class HotelAdmin(admin.ModelAdmin):
    """Админка для отелей"""

    list_display = [
        'name',
        'country',
        'city',
        'stars',
        'price_per_night',
        'created_at',
    ]
    list_display_links = ['name']
    list_filter = ['country', 'stars', 'created_at']
    search_fields = ['name', 'description', 'address']
    readonly_fields = ['created_at']
    inlines = [HotelImageInline]
    list_per_page = 20


class ReviewAdmin(admin.ModelAdmin):
    """Админка для отзывов"""

    list_display = [
        'hotel',
        'user',
        'rating',
        'created_at',
    ]
    list_display_links = ['hotel']
    list_filter = ['rating', 'created_at', 'hotel']
    search_fields = ['hotel__name', 'user__username', 'comment']
    readonly_fields = ['created_at']
    list_per_page = 20


class BookingAdmin(admin.ModelAdmin):
    """Админка для бронирований"""

    list_display = [
        'hotel',
        'user',
        'check_in',
        'check_out',
        'guests',
        'total_price',
        'created_at',
    ]
    list_display_links = ['hotel']
    list_filter = ['check_in', 'check_out', 'created_at']
    search_fields = [
        'hotel__name',
        'user__username',
        'user__email',
    ]
    readonly_fields = ['created_at', 'total_price']
    list_per_page = 20


# Регистрация моделей в админке
admin.site.register(Country, CountryAdmin)
admin.site.register(City)
admin.site.register(Hotel, HotelAdmin)
admin.site.register(HotelImage)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Booking, BookingAdmin)