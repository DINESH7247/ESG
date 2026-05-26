# Model Design

## Multi-tenancy

The model is tenant-first. Every uploaded `DataSource`, every parsed `RawRecord`, every normalized `ActivityRecord`, and every `AuditLog` entry is tied back to a `Tenant` through direct foreign keys. That makes tenant filtering straightforward and keeps the review queue isolated by customer boundary rather than by file name or upload session.

## Raw versus normalized separation

`RawRecord` stores the imported row exactly as received in `raw_json`. `ActivityRecord` stores the normalized, reviewable representation of that same row. The raw row is never overwritten, so the team can explain exactly what was received, what was normalized, and what was changed later by an analyst.

## Auditability

`AuditLog` records the action, old value, new value, actor label, and timestamp whenever a reviewer changes a record. That is enough to support a clean signoff trail without introducing a larger workflow engine or state machine.

## Source-of-truth tracking

`ActivityRecord.raw_record` is the primary linkage between normalized output and the source file row. `source_reference` adds a stable human-readable provenance token so an analyst can trace the record back to the original source context even after it has been edited.

## Scope and categories

The unified activity table supports a single analyst workflow across Scope 1, 2, and 3.

- SAP fuel maps to Scope 1.
- SAP procurement maps to Scope 3.
- Utility electricity maps to Scope 2.
- Travel maps to Scope 3.

That gives the analysts one queue instead of three separate mini-apps.

## Unit normalization strategy

Each source adapter owns its own canonical unit conversion:

- SAP fuel normalizes to liters.
- SAP procurement normalizes to kilograms.
- Utility electricity normalizes to `kWh`.
- Travel flights and taxis normalize to kilometers.
- Travel hotels normalize to nights.

The prototype stores both the original and normalized values so reviewers can see the conversion rather than trusting a hidden transform.

## Editing model

Review edits are intentionally limited to analyst-facing fields such as review status, facility, vendor, cost center, and anomaly annotations. The prototype is not trying to become a full source correction system; it is a signoff surface.
