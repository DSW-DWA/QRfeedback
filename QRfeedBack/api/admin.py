from django.contrib import admin

from .models import Review, Image


@admin.register(Review)
class AuthorAdmin(admin.ModelAdmin):
    readonly_fields = ['pub_date']


admin.site.register(Image)
