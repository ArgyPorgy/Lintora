# 🚀 Deploying Lintora to Render

This guide will help you deploy both the backend API and frontend to Render.

## Prerequisites

1. A [Render](https://render.com) account
2. Your code pushed to a Git repository (GitHub, GitLab, or Bitbucket)
3. Your Groq API key ready

## Step 1: Deploy Backend API

1. **Go to Render Dashboard** → Click "New +" → Select "Web Service"

2. **Connect your repository**:
   - Connect your Git provider
   - Select the `Lintora` repository
   - Choose the branch (usually `main` or `master`)

3. **Configure the service**:
   - **Name**: `lintora-api`
   - **Environment**: `Docker`
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave empty (root of repo)
   - **Dockerfile Path**: `Dockerfile`
   - **Docker Context**: `.` (root)

4. **Environment Variables**:
   - `GROQ_API_KEY`: Your Groq API key (mark as "Secret")
   - `HOST`: `0.0.0.0`
   - `PORT`: `8000`

5. **Health Check Path**: `/health`

6. **Plan**: Start with "Starter" ($7/month) or "Free" (spins down after inactivity)

7. Click **"Create Web Service"**

8. **Note the URL**: After deployment, you'll get a URL like `https://lintora-api.onrender.com`

## Step 2: Deploy Frontend

1. **Go to Render Dashboard** → Click "New +" → Select "Static Site"

2. **Connect your repository**:
   - Same repository as backend
   - Same branch

3. **Configure the service**:
   - **Name**: `lintora-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

4. **Environment Variables**:
   - `VITE_API_URL`: `https://lintora-api.onrender.com` (use your actual backend URL)

5. Click **"Create Static Site"**

6. **Note the URL**: You'll get a URL like `https://lintora-frontend.onrender.com`

## Step 3: Update Frontend API URL

After the backend is deployed, update the frontend environment variable:

1. Go to your frontend service on Render
2. Go to "Environment" tab
3. Update `VITE_API_URL` to your backend URL: `https://lintora-api.onrender.com`
4. Click "Save Changes"
5. Render will automatically rebuild

## Step 4: Update Navbar Links (if needed)

The navbar links should automatically use the `VITE_API_URL` environment variable. If they don't work, check that the environment variable is set correctly.

## Alternative: Using render.yaml (Recommended)

If you prefer, you can use the `render.yaml` file:

1. **Push render.yaml to your repo** (already created)

2. **In Render Dashboard**:
   - Click "New +" → "Blueprint"
   - Connect your repository
   - Render will automatically detect `render.yaml`
   - Review the services and click "Apply"

3. **Set Environment Variables**:
   - Go to each service
   - Add `GROQ_API_KEY` to the backend service
   - Add `VITE_API_URL` to the frontend service (pointing to backend URL)

## Troubleshooting

### Backend Issues

- **Build fails**: Check Docker logs in Render dashboard
- **Health check fails**: Ensure `/health` endpoint is working
- **Port issues**: Make sure `PORT` env var is set to `8000`

### Frontend Issues

- **API calls fail**: Check `VITE_API_URL` is set correctly
- **Build fails**: Check Node.js version (should be 18+)
- **CORS errors**: Backend should allow requests from frontend domain

### Environment Variables

Make sure to set:
- **Backend**: `GROQ_API_KEY` (required for AI analysis)
- **Frontend**: `VITE_API_URL` (must point to your backend URL)

## Cost Estimate

- **Free Tier**: 
  - Backend: Spins down after 15 min inactivity (free)
  - Frontend: Free static hosting
- **Starter Plan**: 
  - Backend: $7/month (always on)
  - Frontend: Free static hosting

## Post-Deployment

1. Test the frontend URL
2. Test uploading a ZIP file
3. Check that API docs work at `{backend-url}/docs`
4. Monitor logs in Render dashboard

## Custom Domain (Optional)

1. Go to your service settings
2. Click "Custom Domains"
3. Add your domain
4. Follow DNS configuration instructions

---

**Your Lintora app should now be live on Render!** 🎉
