import csv
import io

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ActivityRecord, AuditLog, DataSource, RawRecord, Tenant
from .serializers import ActivityRecordSerializer, AuditLogSerializer
from .services.parsers import parse_csv
from .services.normalizer import process_raw_row_with_failure


class UploadView(APIView):
    def post(self, request):
        upload = request.FILES.get("file")
        source_type = request.data.get("source_type")
        tenant_name = request.data.get("tenant_name", "Default Tenant")
        uploaded_by = request.data.get("uploaded_by", "analyst")

        if not upload or source_type not in {"sap", "utility", "travel"}:
            return Response({"detail": "file and valid source_type are required"}, status=status.HTTP_400_BAD_REQUEST)

        tenant, _ = Tenant.objects.get_or_create(name=tenant_name)
        datasource = DataSource.objects.create(
            tenant=tenant,
            source_type=source_type,
            filename=upload.name,
            uploaded_by=uploaded_by,
        )

        rows = parse_csv(upload)
        results = []
        processed = 0
        failed = 0

        for row in rows:
            raw_record = RawRecord.objects.create(datasource=datasource, raw_json=row)
            activity, error_message = process_raw_row_with_failure(datasource, raw_record)
            if activity:
                processed += 1
                results.append({"raw_record_id": raw_record.id, "activity_record_id": activity.id, "status": "processed"})
            else:
                failed += 1
                results.append({"raw_record_id": raw_record.id, "status": "failed", "error_message": error_message})

        return Response(
            {
                "datasource_id": datasource.id,
                "tenant": tenant.name,
                "filename": datasource.filename,
                "source_type": datasource.source_type,
                "rows_received": len(rows),
                "processed": processed,
                "failed": failed,
                "results": results[:10],
            },
            status=status.HTTP_201_CREATED,
        )


class RecordsView(APIView):
    def get(self, request):
        status_filter = request.query_params.get("status", "all")
        tenant_id = request.query_params.get("tenant")
        source_type = request.query_params.get("source_type")

        activity_qs = ActivityRecord.objects.select_related("tenant", "raw_record__datasource").order_by("-created_at")
        if tenant_id:
            activity_qs = activity_qs.filter(tenant_id=tenant_id)
        if source_type:
            activity_qs = activity_qs.filter(raw_record__datasource__source_type=source_type)

        if status_filter == "pending":
            activity_qs = activity_qs.filter(review_status="pending")
            payload = [ActivityRecordSerializer(record).data for record in activity_qs]
        elif status_filter == "approved":
            activity_qs = activity_qs.filter(review_status="approved")
            payload = [ActivityRecordSerializer(record).data for record in activity_qs]
        elif status_filter == "rejected":
            activity_qs = activity_qs.filter(review_status="rejected")
            payload = [ActivityRecordSerializer(record).data for record in activity_qs]
        elif status_filter == "anomalies":
            activity_qs = activity_qs.filter(anomaly_flag=True)
            payload = [ActivityRecordSerializer(record).data for record in activity_qs]
        elif status_filter == "failed":
            raw_qs = RawRecord.objects.select_related("datasource__tenant").filter(processing_status="failed").order_by("-created_at")
            if tenant_id:
                raw_qs = raw_qs.filter(datasource__tenant_id=tenant_id)
            if source_type:
                raw_qs = raw_qs.filter(datasource__source_type=source_type)
            payload = [
                {
                    "kind": "failed_raw",
                    "id": f"raw-{record.id}",
                    "tenant": record.datasource.tenant_id,
                    "tenant_name": record.datasource.tenant.name,
                    "source_type": record.datasource.source_type,
                    "source_filename": record.datasource.filename,
                    "uploaded_by": record.datasource.uploaded_by,
                    "raw_json": record.raw_json,
                    "error_message": record.error_message,
                    "created_at": record.created_at,
                    "review_status": "failed",
                    "anomaly_flag": True,
                    "anomaly_reason": record.error_message,
                }
                for record in raw_qs
            ]
        else:
            activity_payload = [ActivityRecordSerializer(record).data for record in activity_qs]
            raw_qs = RawRecord.objects.select_related("datasource__tenant").filter(processing_status="failed").order_by("-created_at")
            if tenant_id:
                raw_qs = raw_qs.filter(datasource__tenant_id=tenant_id)
            if source_type:
                raw_qs = raw_qs.filter(datasource__source_type=source_type)
            failed_payload = [
                {
                    "kind": "failed_raw",
                    "id": f"raw-{record.id}",
                    "tenant": record.datasource.tenant_id,
                    "tenant_name": record.datasource.tenant.name,
                    "source_type": record.datasource.source_type,
                    "source_filename": record.datasource.filename,
                    "uploaded_by": record.datasource.uploaded_by,
                    "raw_json": record.raw_json,
                    "error_message": record.error_message,
                    "created_at": record.created_at,
                    "review_status": "failed",
                    "anomaly_flag": True,
                    "anomaly_reason": record.error_message,
                }
                for record in raw_qs
            ]
            payload = activity_payload + failed_payload

        return Response({"results": payload})

    def patch(self, request, pk):
        if str(pk).startswith("raw-"):
            return Response({"detail": "Failed raw rows cannot be reviewed"}, status=status.HTTP_400_BAD_REQUEST)

        record = get_object_or_404(ActivityRecord, pk=pk)
        old_value = ActivityRecordSerializer(record).data
        changed_fields = []

        for field in ["review_status", "facility", "vendor", "cost_center", "anomaly_flag", "anomaly_reason"]:
            if field in request.data:
                value = request.data[field]
                if getattr(record, field) != value:
                    setattr(record, field, value)
                    changed_fields.append(field)

        if changed_fields:
            record.save(update_fields=changed_fields + ["updated_at"])
            AuditLog.objects.create(
                activity_record=record,
                action="review_update",
                old_value=old_value,
                new_value=ActivityRecordSerializer(record).data,
                changed_by=request.data.get("changed_by", "analyst"),
            )

        return Response(ActivityRecordSerializer(record).data)


class RecordDetailView(APIView):
    def get(self, request, pk):
        if str(pk).startswith("raw-"):
            raw_id = int(str(pk).replace("raw-", ""))
            record = get_object_or_404(RawRecord.objects.select_related("datasource__tenant"), pk=raw_id)
            return Response(
                {
                    "kind": "failed_raw",
                    "id": f"raw-{record.id}",
                    "tenant": record.datasource.tenant_id,
                    "tenant_name": record.datasource.tenant.name,
                    "source_type": record.datasource.source_type,
                    "source_filename": record.datasource.filename,
                    "uploaded_by": record.datasource.uploaded_by,
                    "raw_json": record.raw_json,
                    "error_message": record.error_message,
                    "created_at": record.created_at,
                    "review_status": "failed",
                    "anomaly_flag": True,
                    "anomaly_reason": record.error_message,
                }
            )

        record = get_object_or_404(ActivityRecord.objects.select_related("tenant", "raw_record__datasource"), pk=pk)
        return Response(ActivityRecordSerializer(record).data)


class AuditLogView(APIView):
    def get(self, request, record_id):
        logs = AuditLog.objects.filter(activity_record_id=record_id).order_by("-changed_at")
        return Response({"results": AuditLogSerializer(logs, many=True).data})
