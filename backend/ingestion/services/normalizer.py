from decimal import Decimal

from django.db import transaction

from ingestion.models import ActivityRecord, AirportLookup, AuditLog, RawRecord
from .sap_normalizer import normalize_row as normalize_sap_row
from .travel_normalizer import normalize_row as normalize_travel_row
from .utility_normalizer import normalize_row as normalize_utility_row


SOURCE_NORMALIZERS = {
    "sap": normalize_sap_row,
    "utility": normalize_utility_row,
    "travel": normalize_travel_row,
}


def _previous_utility_kwh(meter_id):
    prior = (
        ActivityRecord.objects.filter(
            activity_type=ActivityRecord.ACTIVITY_ELECTRICITY,
            facility=meter_id,
        )
        .order_by("-activity_date", "-created_at")
        .first()
    )
    return prior.normalized_quantity if prior else None


@transaction.atomic
def process_raw_row(datasource, raw_record):
    source_type = datasource.source_type
    normalizer = SOURCE_NORMALIZERS[source_type]
    row = raw_record.raw_json
    tenant = datasource.tenant

    if source_type == "utility":
        previous_kwh = _previous_utility_kwh((row.get("meter_id") or "").strip())
        payload = normalizer(row, raw_record, tenant, previous_kwh=previous_kwh)
    else:
        payload = normalizer(row, raw_record, tenant)

    activity = ActivityRecord.objects.create(**{k: v for k, v in payload.items() if k not in {"billing_start", "billing_end", "cost"}})
    if payload.get("anomaly_flag"):
        activity.anomaly_flag = True
        if payload.get("anomaly_reason"):
            activity.anomaly_reason = payload["anomaly_reason"]
        activity.save(update_fields=["anomaly_flag", "anomaly_reason", "updated_at"])
    raw_record.processing_status = RawRecord.STATUS_PROCESSED
    raw_record.error_message = ""
    raw_record.save(update_fields=["processing_status", "error_message"])
    return activity


@transaction.atomic
def process_raw_row_with_failure(datasource, raw_record):
    try:
        return process_raw_row(datasource, raw_record), None
    except Exception as exc:
        raw_record.processing_status = RawRecord.STATUS_FAILED
        raw_record.error_message = str(exc)
        raw_record.save(update_fields=["processing_status", "error_message"])
        return None, str(exc)
