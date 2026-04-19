from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ['username', 'get_full_name', 'email', 'role', 'is_active']
    list_filter   = ['role', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email']

    # Ajouter le champ role dans le formulaire d'édition
    fieldsets = UserAdmin.fieldsets + (
        ('Profil', {'fields': ('role', 'telephone')}),
    )
