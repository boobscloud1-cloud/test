// ... existing code ...
# Telegram Mini App Deployment Guide

## 1. Architecture Overview

Your application consists of two distinct parts that are typically deployed separately:

*   **Frontend (React/Vite):** This is the visual interface users see inside Telegram. It is a "static site" (HTML/CSS/JS).
    *   **Best Host:** Vercel, Netlify, or GitHub Pages.
    *   **Why:** Free, fast, automatic SSL (HTTPS), and easy updates via Git.
*   **Backend (Python/FastAPI):** This handles the logic, database, and API requests.
    *   **Best Host:** Render, Railway, or Heroku.
    *   **Why:** Runs Python code, hosts your database (PostgreSQL/SQLite), and provides an API URL.

---

## 2. Frontend Deployment (The "Mini App")

We will use **Vercel** because it's free, optimized for React/Vite, and gives you a secure URL (`https://your-app.vercel.app`) instantly.

### Steps:
1.  **Create a GitHub Repository:**
    *   Push your project code to a new repository on GitHub.
2.  **Sign up for Vercel:**
    *   Go to [vercel.com](https://vercel.com) and log in with GitHub.
3.  **Import Project:**
    *   Click "Add New" -> "Project".
    *   Select your GitHub repository.
4.  **Configure Build Settings:**
    *   **Root Directory:** Click "Edit" and select `frontend`.
    *   **Framework Preset:** Vite.
    *   **Build Command:** `npm run build` (default).
    *   **Output Directory:** `dist` (default).
5.  **Deploy:**
    *   Click "Deploy".
    *   Once finished, Vercel will give you a domain like `https://tg-miniapp-xyz.vercel.app`.
    *   **Copy this URL.** This is your **WEBAPP_URL**.

---

## 3. Backend Deployment (The API)

We will use **Render** (or Railway) to host the Python code and database.

### Steps (Render.com):
1.  **Sign up for Render:**
    *   Go to [render.com](https://render.com).
2.  **Create Web Service:**
    *   Click "New" -> "Web Service".
    *   Connect your GitHub repository.
3.  **Configure Settings:**
    *   **Root Directory:** `backend`
    *   **Runtime:** Python 3
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4.  **Environment Variables:**
    *   Add the variables from your `.env` file (BOT_TOKEN, SECRET_KEY, etc.).
    *   **Important:** For `DATABASE_URL`, Render provides a managed PostgreSQL database. You will need to create one in Render and link it, or use a persistent disk for SQLite (easier for testing, harder for scaling).
5.  **Deploy:**
    *   Render will build your app and give you a URL like `https://my-backend.onrender.com`.

---

## 4. Connecting the Pieces

1.  **Update Frontend:**
    *   In your local `frontend/.env` (or Vercel Environment Variables), set `VITE_API_URL` to your new Backend URL (`https://my-backend.onrender.com`).
    *   Redeploy Frontend.
2.  **Update Backend:**
    *   In Render Environment Variables, set `WEBAPP_URL` to your new Frontend URL (`https://tg-miniapp-xyz.vercel.app`).
    *   Redeploy Backend.
3.  **Update Bot:**
    *   In your `backend/.env` (or wherever the bot runs), set `WEBAPP_URL` to the Frontend URL.
    *   Restart the bot.

---

## 5. Custom Domains & SSL (Optional)

Both Vercel and Render provide free SSL (HTTPS) on their subdomains. If you want a custom domain (e.g., `supergame.com`):

1.  **Buy a Domain:** Namecheap, GoDaddy, or Google Domains.
2.  **Configure in Vercel:**
    *   Go to Project Settings -> Domains.
    *   Add `supergame.com`.
    *   Vercel will show you DNS records (A record or CNAME) to add to your domain registrar.
    *   Vercel automatically generates an SSL certificate for your custom domain.