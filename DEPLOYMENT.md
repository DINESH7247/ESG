# Deployment Guide

## Prerequisites

- GitHub account (already done: https://github.com/DINESH7247/ESG)
- Render.com account (free tier)
- Vercel.com account (free tier)

## Step 1: Deploy Backend on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Select **"Build and deploy from a Git repository"**
4. Connect your GitHub account if not already connected
5. Search for and select the **ESG** repository
6. Fill in the form:
   - **Name**: `esg-backend`
   - **Environment**: `Docker`
   - **Region**: Choose closest to you (e.g., `Virginia`)
   - **Branch**: `main`
   - **Root Directory**: `backend`

7. Click **"Create Web Service"**
8. Wait for the build to complete (3-5 minutes)
9. Once live, copy the URL from the top (e.g., `https://esg-backend.onrender.com`)

## Step 2: Deploy Frontend on Vercel

1. Go to https://vercel.com/new
2. Import your **ESG** GitHub repository
3. Fill in the form:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

4. Add **Environment Variables**:
   - Key: `VITE_API_BASE_URL`
   - Value: `https://esg-backend.onrender.com` (from Step 1)

5. Click **"Deploy"**
6. Wait for the build to complete (2-3 minutes)
7. Once live, you'll get a Vercel URL (e.g., `https://esg-frontend-xyz.vercel.app`)

## Step 3: Test the Deployment

**Backend health check:**
```
https://esg-backend.onrender.com/records
```
Should return a JSON list (empty at first).

**Frontend:**
Open the Vercel URL in a browser. You should see the ESG Review Console dashboard.

## Step 4: Upload Sample Data

1. Navigate to the **Upload** tab in the frontend
2. Choose a source type (SAP, Utility, or Travel)
3. Upload a CSV from [sample_data/](sample_data/):
   - `sap_fuel_procurement.csv` for SAP
   - `utility_electricity.csv` for Utility
   - `travel_expenses.csv` for Travel

4. Review the results in the **Review Queue** tab

## Environment Variables Reference

### Backend (Render)

These are automatically set by Render if you use `render.yaml`:

- `DEBUG`: `false`
- `SECRET_KEY`: Auto-generated
- `ALLOWED_HOSTS`: `*`
- `DATABASE_URL`: Auto-connected PostgreSQL

No manual env var setup needed if using `render.yaml`.

### Frontend (Vercel)

Required:
- `VITE_API_BASE_URL`: Your Render backend URL

## Troubleshooting

### Backend won't deploy

- Check the Render build logs for Django errors
- Ensure `render.yaml` is in the root directory
- Verify PostgreSQL is provisioned in Render dashboard

### Frontend can't reach backend

- Verify `VITE_API_BASE_URL` environment variable is set correctly in Vercel
- Check browser console for CORS errors
- Ensure backend is running and accessible

### Database connection errors

- Render auto-provisions PostgreSQL; check the **Databases** tab in Render
- Verify all migrations ran successfully in Render logs

## Custom Domain (Optional)

**Render backend:**
1. Go to your Web Service settings
2. Scroll to **Custom Domain**
3. Add your domain

**Vercel frontend:**
1. Go to your project settings
2. Click **Domains**
3. Add your domain

## Next Steps

- Share the frontend URL with your team
- Add authentication layer (not in prototype, but recommended for production)
- Connect real data sources instead of sample CSVs
- Set up CI/CD for automatic redeployment on git push
