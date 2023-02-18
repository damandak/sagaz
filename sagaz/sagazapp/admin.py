from django.contrib import admin
from .models import Lake, LakeMeasurement

admin.site.register(Lake)
# Make Lakemeasurements searchable by lake and date
class LakeMeasurementAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'lake', 'date')
    list_filter = ('lake', 'date')
    search_fields = ('__str__', 'lake', 'date')
admin.site.register(LakeMeasurement, LakeMeasurementAdmin)
