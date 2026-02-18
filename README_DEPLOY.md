# Quick Deploy to Render

## Fast Setup (5 minutes)

### 1. Push to GitHub
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2. Deploy Backend

1. Go to [render.com](https://render.com) → Sign up/Login
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo
4. Settings:
   - **Name**: `lintora-api`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `Dockerfile`
   - **Health Check**: `/health`
5. Add Environment Variable:
   - `GROQ_API_KEY` = your Groq API key
6. Click **"Create Web Service"**
7. Wait for deployment (~5 min)
8. **Copy the URL** (e.g., `https://lintora-api.onrender.com`)

### 3. Deploy Frontend

1. Click **"New +"** → **"Static Site"**
2. Connect same GitHub repo
3. Settings:
   - **Name**: `lintora-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. Add Environment Variable:
   - `VITE_API_URL` = `https://lintora-api.onrender.com` (your backend URL)
5. Click **"Create Static Site"**
6. Wait for deployment (~3 min)

### 4. Done! 🎉

Your app is live at the frontend URL!

## Troubleshooting

- **Backend not starting?** Check logs in Render dashboard
- **Frontend can't connect?** Verify `VITE_API_URL` matches backend URL
- **Build fails?** Check Node.js version (should auto-detect)

## Cost

- **Free**: Backend spins down after 15 min (good for testing)
- **$7/month**: Backend always on (recommended for production)
