from django.contrib import admin

from .models import Filament


@admin.register(Filament)
class FilamentAdmin(admin.ModelAdmin):
    list_display = ("brand", "model", "type", "color", "quantity_grams", "price", "price_per_gram", "bought", "used_up")
    list_filter = ("brand", "type", "texture")
    search_fields = ("brand", "model", "color", "store_code", "make_code", "nfc", "notes")
    readonly_fields = ("price_per_gram",)
