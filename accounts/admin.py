from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'phone', 'city', 'state')
    search_fields = ('user__username', 'company_name', 'phone')
