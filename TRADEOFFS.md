# Tradeoffs

1. No authentication or role-based access control. This keeps the prototype focused on ingestion and review, but it means tenant access is trusted by convention and would need hardening before any real customer rollout.
2. No background job queue. Rows are normalized synchronously during upload so the system is easy to explain, but large files would eventually need async processing and progress tracking.
3. No OCR or PDF ingestion. Utility bills are treated as CSV exports only, which preserves the scope of the prototype but deliberately ignores the harder bill-parsing problem.
