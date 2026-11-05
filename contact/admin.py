from django.contrib import admin
from contact import models

@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = 'id', 'first_name', 'last_name', 'phone', 'owner', 'show',
    ordering = '-id',
    list_filter = 'show', 'owner', 'category'
    search_fields = 'id', 'first_name', 'last_name',
    list_per_page = 25
    list_max_show_all = 200
    list_editable = 'first_name', 'last_name', 'show',
    list_display_links = 'id', 'phone',
    
@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = 'name', 'owner'
    ordering = '-id',
    list_filter = 'owner',
    search_fields = 'name', 'owner__username'
