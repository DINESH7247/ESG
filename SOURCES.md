# Sources

## SAP fuel and procurement

I researched SAP IDoc-style exports and the surrounding SAP integration model. The important takeaway is that SAP integration data is typically structured, segment-based, and traceable rather than clean spreadsheet output: there is a control record, data segments, and status records. That informed the decision to accept a messy CSV extract as the prototype input, while still preserving the raw row unchanged for auditability.

What the sample imitates:

- German column headers such as `Buchungsdatum`, `Werk`, `Material`, `Menge`, and `Einheit`
- Inconsistent date formats
- Mixed units such as liters, gallons, and kilograms
- Plant codes that are only meaningful once normalized against business context
- Duplicate and invalid rows so the reviewer sees both normal and failed ingestion outcomes

What would break in production:

- Real SAP exports may arrive as IDoc, flat files, or OData payloads, and the prototype only handles CSV input
- Material and plant semantics are simplified to a narrow subset
- Actual SAP master-data lookups, accounting dimensions, and document flows are not modeled

## Utility electricity

I researched the Green Button CMD standard because it is the clearest public model for utility usage and billing data. The useful part is that utility data is not just "kWh"; it often includes billing periods, tariff names, demand or administrative charges, and usage data at interval or monthly granularity.

What the sample imitates:

- Portal CSV exports with `meter_id`, `billing_start`, `billing_end`, `kwh`, `cost`, and `tariff`
- Billing periods that do not align to calendar months
- Missing or malformed readings
- Usage spikes that need analyst attention

What would break in production:

- A real utility may expose XML, EDI, API, or portal exports with different schemas
- Interval reads and billing summaries often need separate treatment
- Tariff logic can be much more complex than a single flat emission factor

## Corporate travel

I researched SAP Concur developer documentation and the public API surface around travel, expense, hotel, and ground-transport workflows. The public docs make clear that the travel platform exposes structured entities and can support reporting/reconciliation, but the exact shape depends on which API family or extract is used.

What the sample imitates:

- Concur/Navan-style CSV exports with traveler, travel type, origin, destination, distance, and hotel nights
- Flight, hotel, and taxi rows with different emission semantics
- Missing airport distance values that have to be derived from airport codes
- Incomplete rows that should be flagged instead of dropped

What would break in production:

- Real integrations often require auth and scoped API access rather than a plain CSV upload
- Travel platforms may split itinerary, expense, and booking objects across separate APIs
- Distance derivation would need a proper airport lookup and routing model, not the small lookup table used here

## Production limitations

The prototype intentionally uses placeholder emission factors and a simplified normalization pipeline. It is designed to be explainable and auditable, not certified for external reporting.
