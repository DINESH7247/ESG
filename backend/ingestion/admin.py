from django.contrib import admin

from .models import AirportLookup, ActivityRecord, AuditLog, DataSource, RawRecord, Tenant

admin.site.register(Tenant)
admin.site.register(DataSource)
admin.site.register(RawRecord)
admin.site.register(ActivityRecord)
admin.site.register(AuditLog)
admin.site.register(AirportLookup)
