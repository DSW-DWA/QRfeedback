from django.contrib import admin

from .models import Review


@admin.register(Review)
class AuthorAdmin(admin.ModelAdmin):
    readonly_fields = ['pub_date']
