from django.contrib import admin

# Register your models here.
from .models import CustomUser
from .models import TaskConfiguration


admin.site.register(CustomUser)


@admin.register(TaskConfiguration)
class TaskConfigurationAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_type', 'count', 'price_range_low', 'price_range_high', 'commission_percentage')
    list_filter = ('account_type',)
    search_fields = ('user__username', 'account_type')