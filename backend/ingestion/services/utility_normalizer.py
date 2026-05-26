from datetime import datetime
from decimal import Decimal, InvalidOperation

from ingestion.models import ActivityRecord

DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]


def _parse_date(value):
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except (ValueError, AttributeError):
            continue
    raise ValueError(f"Unsupported utility date: {value}")


def _to_decimal(value):
    try:
        return Decimal(str(value).replace(",", ".").strip())
    except (InvalidOperation, AttributeError):
        raise ValueError(f"Invalid numeric value: {value}")


def normalize_row(raw_row, raw_record, tenant, previous_kwh=None):
    meter_id = (raw_row.get("meter_id") or "").strip()
    billing_start = _parse_date(raw_row.get("billing_start", ""))
    billing_end = _parse_date(raw_row.get("billing_end", ""))
    kwh = _to_decimal(raw_row.get("kwh", "0"))
    cost = _to_decimal(raw_row.get("cost", "0"))
    tariff = (raw_row.get("tariff") or "").strip()

    if kwh < 0:
        raise ValueError("Negative electricity usage")

    emission_factor = Decimal("0.394000")
    co2e_kg = (kwh * emission_factor).quantize(Decimal("0.0001"))
    anomaly_flag = False
    anomaly_reason = ""
    if previous_kwh and previous_kwh > 0 and kwh > previous_kwh * Decimal("3"):
        anomaly_flag = True
        anomaly_reason = f"Electricity spike above 3x previous billing period ({previous_kwh} kWh)"

    if not meter_id:
        anomaly_flag = True
        anomaly_reason = anomaly_reason or "Missing meter identifier"

    return {
        "tenant": tenant,
        "raw_record": raw_record,
        "activity_type": ActivityRecord.ACTIVITY_ELECTRICITY,
        "scope": 2,
        "activity_date": billing_end,
        "original_quantity": kwh,
        "original_unit": "kWh",
        "normalized_quantity": kwh.quantize(Decimal("0.0001")),
        "normalized_unit": "kWh",
        "emission_factor": emission_factor,
        "co2e_kg": co2e_kg,
        "facility": meter_id,
        "vendor": tariff,
        "cost_center": "",
        "review_status": "pending",
        "anomaly_flag": anomaly_flag,
        "anomaly_reason": anomaly_reason,
        "source_reference": f"utility:{meter_id}:{billing_start.isoformat()}:{billing_end.isoformat()}",
        "billing_start": billing_start,
        "billing_end": billing_end,
        "cost": cost,
    }
