from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('student', 'teacher', 'course', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'teacher')
    search_fields = ('student__username', 'teacher__user__username', 'comment')
    date_hierarchy = 'created_at'
