from django.contrib import admin
from .models import Listing, Category

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'price')
    list_filter = ('title',)
    search_fields = ('title', 'description')
    ordering = ('-id',)

class CategoyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    prepopulated_fields = {
        "slug": ("name",)
    }


admin.site.register(Listing, ProductAdmin)
admin.site.register(Category, CategoyAdmin)