from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from django.contrib.auth.models import Group
from .models import User
from invoice.models import Commission

# Register your models here.
admin.site.unregister(Group)

class CommissionInline(admin.TabularInline):
    model = Commission
    extra = 1
#
class UserAdmin(_UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_banker', 'is_betting_agency_staff', 'is_active')
    fieldsets = (
        (None, {
            'fields': ('username', 'password',)
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Lottery info', {
            'fields': ('betting_agency', 'is_banker', 'is_betting_agency_staff',)
        }),
        ('Other', {
            'fields': ('is_active', 'banker', 'is_system_manager')
        }),
    )
    inlines = (CommissionInline,)
#
admin.site.register(User, UserAdmin)