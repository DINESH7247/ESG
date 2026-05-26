# ESG Enterprise Ingestion Prototype

This repository contains a production-style prototype for ESG analysts reviewing enterprise emissions activity data before audit signoff.

## What it does

- Ingests SAP fuel and procurement exports
- Ingests utility electricity exports
- Ingests corporate travel exports
- Preserves raw source rows
- Normalizes records into a unified activity schema
- Flags anomalies and failed rows
- Supports analyst review, approval, and audit logging

## Architecture

Source files flow into raw ingestion rows, then into source-specific normalizers, then into a unified activity table, and finally into the analyst review queue.

## Stack

- Backend: Django, Django REST Framework, PostgreSQL
- Frontend: React, TailwindCSS, Axios
- Deployment target: Render for the backend, Vercel for the frontend

## Local setup

### Backend

1. Create and activate a Python environment.
2. Install dependencies from [backend/requirements.txt](backend/requirements.txt).
3. Copy [.env.example](.env.example) and fill in environment values.
4. Run migrations and start the API:

```bash
cd backend
python manage.py migrate
python manage.py runserver
```

### Frontend

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Start the dev server:

```bash
npm run dev
```

## API

- `POST /upload`
- `GET /records`
- `GET /records/:id`
- `PATCH /records/:id/review`
- `GET /audit-logs/:record_id`

## Sample data

Messy CSV fixtures live in [sample_data/](sample_data/) and are intentionally imperfect so the normalization and anomaly handling paths are visible.

## Deployment

- Backend: Render service defined in [render.yaml](render.yaml)
- Frontend: Vercel app under [frontend/](frontend/)

## Notes

- The app is intentionally small and explainable.
- Emissions factors are placeholders, not audit-grade values.
- Utility ingestion is CSV-only by design for this prototype.
