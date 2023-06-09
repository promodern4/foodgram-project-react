from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'password'
    )
    list_editable = ('password', )
    search_fields = ('username', 'email')
    list_filter = ('role',)
    empty_value_display = '-empty-'
