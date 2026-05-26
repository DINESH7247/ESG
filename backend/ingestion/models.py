from django.db import models


class Tenant(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class DataSource(models.Model):
    SOURCE_SAP = "sap"
    SOURCE_UTILITY = "utility"
    SOURCE_TRAVEL = "travel"
    SOURCE_CHOICES = [
        (SOURCE_SAP, "SAP"),
        (SOURCE_UTILITY, "Utility"),
        (SOURCE_TRAVEL, "Travel"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="data_sources")
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    filename = models.CharField(max_length=255)
    uploaded_by = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tenant} - {self.filename}"


class RawRecord(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PROCESSED = "processed"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSED, "Processed"),
        (STATUS_FAILED, "Failed"),
    ]

    datasource = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name="raw_records")
    raw_json = models.JSONField()
    processing_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ActivityRecord(models.Model):
    ACTIVITY_FUEL = "fuel"
    ACTIVITY_ELECTRICITY = "electricity"
    ACTIVITY_FLIGHT = "flight"
    ACTIVITY_HOTEL = "hotel"
    ACTIVITY_TAXI = "taxi"
    ACTIVITY_PROCUREMENT = "procurement"
    ACTIVITY_CHOICES = [
        (ACTIVITY_FUEL, "Fuel"),
        (ACTIVITY_ELECTRICITY, "Electricity"),
        (ACTIVITY_FLIGHT, "Flight"),
        (ACTIVITY_HOTEL, "Hotel"),
        (ACTIVITY_TAXI, "Taxi"),
        (ACTIVITY_PROCUREMENT, "Procurement"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="activity_records")
    raw_record = models.ForeignKey(RawRecord, on_delete=models.CASCADE, related_name="activity_records")
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    scope = models.PositiveSmallIntegerField()
    activity_date = models.DateField()
    original_quantity = models.DecimalField(max_digits=18, decimal_places=4)
    original_unit = models.CharField(max_length=32)
    normalized_quantity = models.DecimalField(max_digits=18, decimal_places=4)
    normalized_unit = models.CharField(max_length=32)
    emission_factor = models.DecimalField(max_digits=18, decimal_places=6)
    co2e_kg = models.DecimalField(max_digits=18, decimal_places=4)
    facility = models.CharField(max_length=255, blank=True)
    vendor = models.CharField(max_length=255, blank=True)
    cost_center = models.CharField(max_length=255, blank=True)
    review_status = models.CharField(max_length=20, default="pending")
    anomaly_flag = models.BooleanField(default=False)
    anomaly_reason = models.TextField(blank=True)
    source_reference = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.activity_type} on {self.activity_date}"


class AuditLog(models.Model):
    activity_record = models.ForeignKey(ActivityRecord, on_delete=models.CASCADE, related_name="audit_logs")
    action = models.CharField(max_length=100)
    old_value = models.JSONField(default=dict)
    new_value = models.JSONField(default=dict)
    changed_by = models.CharField(max_length=255)
    changed_at = models.DateTimeField(auto_now_add=True)


class AirportLookup(models.Model):
    code = models.CharField(max_length=10, unique=True)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.code
