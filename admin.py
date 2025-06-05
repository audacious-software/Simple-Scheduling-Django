from prettyjson import PrettyJSONWidget

from django.contrib import admin
from django.db import models

from .models import ScheduledItem

@admin.register(ScheduledItem)
class ScheduledItemAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.JSONField: {
            'widget': PrettyJSONWidget(attrs={'initial': 'parsed'})
        }
    }

    list_display = ('identifier', 'action', 'when', 'resolved', 'outcome',)
    search_fields = ('identifier', 'context', 'outcome', 'outcome_log',)
    list_filter = ('when', 'resolved', 'outcome', 'action', )
