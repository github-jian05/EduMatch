from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile

class RoleFilter(admin.SimpleListFilter):
    title = 'Role'  # Label for the filter
    parameter_name = 'role'

    def lookups(self, request, model_admin):
        # Provide a list of filter options (based on the roles available in your app)
        # Replace the choices list below with your actual ROLE_CHOICES
        return [
            ('role1', 'Role 1'),
            ('role2', 'Role 2'),
            # Add more roles as needed
        ]

    def queryset(self, request, queryset):
        # Filter the queryset based on the value selected in the filter dropdown
        value = self.value()
        if value:
            return queryset.filter(profile__role=value)
        return queryset

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'get_role']
    list_filter = []  # Use the custom `RoleFilter`

    def get_role(self, obj):
        return obj.profile.role if hasattr(obj, 'profile') else 'No Profile'

    get_role.short_description = 'Role'

# Move registration OUTSIDE of CustomUserAdmin
admin.site.register(CustomUser, CustomUserAdmin)
