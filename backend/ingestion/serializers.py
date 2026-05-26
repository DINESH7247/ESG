from rest_framework import serializers

from .models import ActivityRecord, AuditLog, DataSource, RawRecord, Tenant


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ["id", "name", "created_at"]


class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSource
        fields = ["id", "tenant", "source_type", "filename", "uploaded_by", "uploaded_at"]


class RawRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawRecord
        fields = ["id", "datasource", "raw_json", "processing_status", "error_message", "created_at"]


class ActivityRecordSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source="tenant.name", read_only=True)
    source_filename = serializers.CharField(source="raw_record.datasource.filename", read_only=True)
    source_type = serializers.CharField(source="raw_record.datasource.source_type", read_only=True)
    raw_json = serializers.JSONField(source="raw_record.raw_json", read_only=True)
    uploaded_by = serializers.CharField(source="raw_record.datasource.uploaded_by", read_only=True)

    class Meta:
        model = ActivityRecord
        fields = [
            "id",
            "tenant",
            "tenant_name",
            "raw_record",
            "source_type",
            "source_filename",
            "uploaded_by",
            "activity_type",
            "scope",
            "activity_date",
            "original_quantity",
            "original_unit",
            "normalized_quantity",
            "normalized_unit",
            "emission_factor",
            "co2e_kg",
            "facility",
            "vendor",
            "cost_center",
            "review_status",
            "anomaly_flag",
            "anomaly_reason",
            "source_reference",
            "raw_json",
            "created_at",
            "updated_at",
        ]


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ["id", "activity_record", "action", "old_value", "new_value", "changed_by", "changed_at"]
