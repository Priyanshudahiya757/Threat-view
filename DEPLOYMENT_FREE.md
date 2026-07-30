# 🚀 100% Permanently Free Deployment Guide ($0 Forever)

Follow this guide to host **ThreatView** online completely free forever with zero credit card required.

---

## 📍 Architecture ($0 Forever)

| Component | Provider | Free Tier Policy |
|---|---|---|
| 🗄️ **PostgreSQL DB** | **[Neon.tech](https://neon.tech/)** | 0.5 GB storage, permanently free, 0$ forever |
| 💻 **React Frontend** | **[Vercel](https://vercel.com/)** | Unlimited bandwidth, global CDN, 100% free forever |
| ⚙️ **Flask Backend** | **[Render Web Service](https://render.com/)** | 750 free hours/month, automatically sleeps when idle |

---

## ⚡ Step 1: Create Free PostgreSQL Database (Neon.tech — 30 seconds)

1. Open **[https://neon.tech/](https://neon.tech/)** and click **Sign Up** (with GitHub).
2. Create a project named `threatview`.
3. Copy the **Connection String** (looks like `postgresql://alex:password@ep-cool-name.us-east-2.aws.neon.tech/neondb?sslmode=require`).

---

## ⚡ Step 2: Deploy Backend API (Render Web Service — 2 minutes)

1. Open **[https://dashboard.render.com/](https://dashboard.render.com/)** and click **New +** -> **Web Service**.
2. Select **Build and deploy from a Git repository** and pick `Priyanshudahiya757/Threat-view`.
3. Fill in the fields:
   - **Name**: `threatview-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()" && gunicorn run:app --bind 0.0.0.0:$PORT`
   - **Instance Type**: **Free**
4. Under **Environment Variables**, add:
   - `DATABASE_URL`: *(Paste your Neon connection string from Step 1)*
   - `CORS_ORIGINS`: `*`
   - `FLASK_ENV`: `production`
5. Click **Create Web Service**.
6. Copy your live backend URL (e.g. `https://threatview-backend.onrender.com`).

---

## ⚡ Step 3: Deploy Frontend UI (Vercel — 1 minute)

1. Open **[https://vercel.com/new](https://vercel.com/new)** and import `Priyanshudahiya757/Threat-view`.
2. Set **Root Directory** to `frontend`.
3. Under **Environment Variables**, add:
   - `VITE_API_URL`: `https://threatview-backend.onrender.com/api` *(replace with your backend URL from Step 2)*
4. Click **Deploy**.

---

🎉 **Done!** Your ThreatView platform is now live online 100% free forever!
