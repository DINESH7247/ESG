from datetime import datetime
from decimal import Decimal, InvalidOperation

from ingestion.models import ActivityRecord

GERMAN_DATE_FORMATS = ["%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"]
UNIT_CONVERSIONS = {
    "l": Decimal("1"),
    "liter": Decimal("1"),
    "liters": Decimal("1"),
    "gallon": Decimal("3.78541"),
    "gallons": Decimal("3.78541"),
}
FUEL_KEYWORDS = ("diesel", "petrol", "benzin", "fuel")
PROCUREMENT_KEYWORDS = ("procurement", "einkauf", "material", "purchase")


def _parse_date(value):
    for fmt in GERMAN_DATE_FORMATS:
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except (ValueError, AttributeError):
            continue
    raise ValueError(f"Unsupported SAP date: {value}")


def _to_decimal(value):
    try:
        return Decimal(str(value).replace(",", ".").strip())
    except (InvalidOperation, AttributeError):
        raise ValueError(f"Invalid numeric value: {value}")


def _normalize_unit(quantity, unit):
    unit_key = str(unit or "").strip().lower()
    if unit_key not in UNIT_CONVERSIONS:
        raise ValueError(f"Invalid unit: {unit}")
    return (quantity * UNIT_CONVERSIONS[unit_key], "liters" if unit_key in {"l", "liter", "liters", "gallon", "gallons"} else "kg")


def normalize_row(raw_row, raw_record, tenant):
    activity_date = _parse_date(raw_row.get("Buchungsdatum", ""))
    facility = (raw_row.get("Werk") or "").strip()
    material = (raw_row.get("Material") or "").strip()
    quantity = _to_decimal(raw_row.get("Menge", "0"))
    original_unit = (raw_row.get("Einheit") or "").strip().lower()

    if quantity < 0:
        raise ValueError("Negative SAP quantity")

    if any(keyword in material.lower() for keyword in FUEL_KEYWORDS):
        activity_type = ActivityRecord.ACTIVITY_FUEL
        scope = 1
        normalized_quantity, normalized_unit = _normalize_unit(quantity, original_unit)
        emission_factor = Decimal("2.680000")
        source_reference = f"sap:{facility}:{material}:{activity_date.isoformat()}"
    elif any(keyword in material.lower() for keyword in PROCUREMENT_KEYWORDS):
        activity_type = ActivityRecord.ACTIVITY_PROCUREMENT
        scope = 3
        if original_unit not in {"kg", "kilogram", "kilograms"}:
            raise ValueError(f"Invalid procurement unit: {original_unit}")
        normalized_quantity = quantity
        normalized_unit = "kg"
        emission_factor = Decimal("1.200000")
        source_reference = f"sap:{facility}:{material}:{activity_date.isoformat()}"
    else:
        raise ValueError(f"Unsupported SAP material: {material}")

    co2e_kg = (normalized_quantity * emission_factor).quantize(Decimal("0.0001"))
    anomaly_reason = ""
    anomaly_flag = False
    if not facility:
        anomaly_flag = True
        anomaly_reason = "Missing plant code"

    return {
        "tenant": tenant,
        "raw_record": raw_record,
        "activity_type": activity_type,
        "scope": scope,
        "activity_date": activity_date,
        "original_quantity": quantity,
        "original_unit": raw_row.get("Einheit", "").strip(),
        "normalized_quantity": normalized_quantity.quantize(Decimal("0.0001")),
        "normalized_unit": normalized_unit,
        "emission_factor": emission_factor,
        "co2e_kg": co2e_kg,
        "facility": facility,
        "vendor": material,
        "cost_center": facility,
        "review_status": "pending",
        "anomaly_flag": anomaly_flag,
        "anomaly_reason": anomaly_reason,
        "source_reference": source_reference,
    }
