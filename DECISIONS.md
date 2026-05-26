# Decisions

## Why CSV instead of APIs

I chose CSV upload for all three sources because it is the most realistic least-common-denominator shape for an onboarding prototype. SAP, facilities, and travel teams all routinely export files for finance or sustainability ops, and CSV lets the team validate normalization, anomaly handling, and auditability before dealing with auth, rate limits, or vendor-specific API contracts.

## SAP subset handled

I handled a small SAP subset on purpose: fuel and procurement rows with German-style headers, mixed units, inconsistent dates, and plant codes that need business context. I did not try to model the broader SAP landscape such as IDoc inbound/outbound processing, BAPI behavior, accounting documents, or master-data synchronization.

## Utility subset handled

I chose utility portal CSV rather than PDF because a PDF bill would pull the prototype into OCR and invoice parsing instead of ingestion and review. The implementation assumes meter-level or bill-level CSV exports with billing periods, kWh usage, cost, and tariff name. That is enough to exercise Scope 2 normalization without pretending to solve utility statement extraction.

## Travel subset handled

I modeled Concur/Navan-style travel exports as CSV because the assignment is about downstream ESG review, not building a travel integration platform. The prototype handles flight, hotel, and taxi rows, plus a small airport lookup path when distance is missing. I intentionally skipped policy approval, booking changes, and reimbursement workflows.

## Assumptions

- The analyst uploads one source file at a time.
- Uploaded rows are row-level facts, not invoices or ledgers.
- Placeholder emission factors are acceptable for prototype review flows.
- Review actions are performed by a named analyst label rather than a full identity system.
- Raw failures stay visible in the queue instead of being silently discarded.

## PM questions

- Which source should be prioritized for production onboarding first?
- Which tenant boundary matters most in practice: legal entity, region, or business unit?
- Should approval require one analyst or a dual-approval signoff?
- Should the downstream output be CSV, API, or auditor-ready PDF/Excel?
