from django.contrib import admin
from .models import Draw, DrawResult

# Register your models here.
class DrawResultInline(admin.TabularInline):
    model = DrawResult
    extra = 1
class DrawAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'date',)
    inlines = (DrawResultInline,)
admin.site.register(Draw, DrawAdmin)
#
class DrawResultAdmin(admin.ModelAdmin):
    list_display = ('draw', 'icon',)
admin.site.register(DrawResult, DrawResultAdmin)