from datetime import datetime
from decimal import Decimal, InvalidOperation
import math

from ingestion.models import ActivityRecord, AirportLookup

DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]
DEFAULT_AIRPORTS = {
    "JFK": (Decimal("40.6413"), Decimal("-73.7781")),
    "LHR": (Decimal("51.4700"), Decimal("-0.4543")),
    "FRA": (Decimal("50.0379"), Decimal("8.5622")),
    "SFO": (Decimal("37.6213"), Decimal("-122.3790")),
    "ORD": (Decimal("41.9742"), Decimal("-87.9073")),
    "AMS": (Decimal("52.3105"), Decimal("4.7683")),
}


def _parse_date(value):
    if not value:
        raise ValueError("Missing travel date")
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except (ValueError, AttributeError):
            continue
    raise ValueError(f"Unsupported travel date: {value}")


def _to_decimal(value, default="0"):
    try:
        source = default if value in (None, "") else value
        return Decimal(str(source).replace(",", ".").strip())
    except (InvalidOperation, AttributeError):
        raise ValueError(f"Invalid numeric value: {value}")


def _airport_point(code):
    code = (code or "").strip().upper()
    airport = AirportLookup.objects.filter(code=code).first()
    if airport:
        return Decimal(str(airport.latitude)), Decimal(str(airport.longitude))
    if code in DEFAULT_AIRPORTS:
        return DEFAULT_AIRPORTS[code]
    return None


def _haversine_km(origin_point, destination_point):
    if not origin_point or not destination_point:
        return None
    lat1, lon1 = [math.radians(float(value)) for value in origin_point]
    lat2, lon2 = [math.radians(float(value)) for value in destination_point]
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return Decimal(str(6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))))


def _derive_distance_km(origin, destination):
    route_distance = {
        ("JFK", "LHR"): Decimal("5540"),
        ("LHR", "FRA"): Decimal("654"),
        ("SFO", "ORD"): Decimal("2971"),
        ("AMS", "JFK"): Decimal("5850"),
    }
    origin_code = (origin or "").strip().upper()
    destination_code = (destination or "").strip().upper()
    if (origin_code, destination_code) in route_distance:
        return route_distance[(origin_code, destination_code)]
    point = _haversine_km(_airport_point(origin_code), _airport_point(destination_code))
    if point is not None:
        return point.quantize(Decimal("0.1"))
    raise ValueError("Missing destination and no airport lookup available")


def normalize_row(raw_row, raw_record, tenant):
    employee = (raw_row.get("employee") or "").strip()
    travel_type = (raw_row.get("travel_type") or "").strip().lower()
    origin = (raw_row.get("origin") or "").strip()
    destination = (raw_row.get("destination") or "").strip()
    distance_value = raw_row.get("distance_km", "")
    hotel_nights = _to_decimal(raw_row.get("hotel_nights", "0"))

    activity_date = _parse_date(raw_row.get("travel_date") or raw_row.get("date") or raw_row.get("expense_date"))

    if travel_type not in {"flight", "hotel", "taxi"}:
        raise ValueError(f"Unsupported travel type: {travel_type}")

    if travel_type == "hotel":
        normalized_quantity = hotel_nights
        normalized_unit = "nights"
        activity_type = ActivityRecord.ACTIVITY_HOTEL
        emission_factor = Decimal("18.5000")
        source_reference = f"travel:hotel:{employee}:{activity_date.isoformat()}"
        anomaly_flag = hotel_nights <= 0
        anomaly_reason = "Missing hotel nights" if anomaly_flag else ""
    else:
        anomaly_flag = False
        anomaly_reason = ""
        if distance_value in (None, "", "NA"):
            if destination:
                distance_km = _derive_distance_km(origin, destination)
            else:
                distance_km = Decimal("0")
                anomaly_flag = True
                anomaly_reason = "Missing destination"
        else:
            distance_km = _to_decimal(distance_value)
        normalized_quantity = distance_km
        normalized_unit = "km"
        if travel_type == "flight":
            activity_type = ActivityRecord.ACTIVITY_FLIGHT
            emission_factor = Decimal("0.1580")
        else:
            activity_type = ActivityRecord.ACTIVITY_TAXI
            emission_factor = Decimal("0.2100")
        source_reference = f"travel:{activity_type}:{origin}:{destination}:{activity_date.isoformat()}"
        anomaly_flag = anomaly_flag or (not destination and travel_type == "flight")
        anomaly_reason = anomaly_reason or ("Missing destination" if not destination else "")

    if normalized_quantity < 0:
        raise ValueError("Negative travel quantity")

    co2e_kg = (normalized_quantity * emission_factor).quantize(Decimal("0.0001"))
    return {
        "tenant": tenant,
        "raw_record": raw_record,
        "activity_type": activity_type,
        "scope": 3,
        "activity_date": activity_date,
        "original_quantity": normalized_quantity,
        "original_unit": normalized_unit,
        "normalized_quantity": normalized_quantity.quantize(Decimal("0.0001")),
        "normalized_unit": normalized_unit,
        "emission_factor": emission_factor,
        "co2e_kg": co2e_kg,
        "facility": origin,
        "vendor": employee,
        "cost_center": "",
        "review_status": "pending",
        "anomaly_flag": anomaly_flag,
        "anomaly_reason": anomaly_reason,
        "source_reference": source_reference,
    }
