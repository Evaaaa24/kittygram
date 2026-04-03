from django.contrib import admin

from .models import Contribution, Need


class ContributionInline(admin.TabularInline):
    model = Contribution
    extra = 0


@admin.register(Need)
class NeedAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'priority', 'status',
                    'quantity_required', 'unit', 'created_by', 'created_at')
    list_filter = ('category', 'priority', 'status')
    search_fields = ('title', 'description')
    inlines = [ContributionInline]


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ('need', 'contributor', 'quantity', 'created_at')
    list_filter = ('need',)
