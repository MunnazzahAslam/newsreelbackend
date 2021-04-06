from django.contrib import admin

from reviews.models import Review, Reply


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'rating']


admin.site.register(Reply)

