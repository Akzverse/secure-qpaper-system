# Free Cloud Setup: Supabase + Render

This guide walks you through deploying the Secure Question Paper Management System to the cloud using **Supabase** (PostgreSQL Database) and **Render** (Web Hosting).

---

## Step 1: Create the Cloud PostgreSQL Database on Supabase

1. Open [Supabase Dashboard](https://supabase.com/dashboard) and sign in.
2. Click **New project**.
3. Choose the **Free** tier, name the project `secure-qpaper-system`, and set a strong database password.
   > **Note on Special Characters**: If your database password contains characters like `@`, `#`, `:`, or `/`, make sure to URL-encode them in the connection string (e.g., `@` becomes `%40`), or use an alphanumeric password.
4. Once provisioned, click **Connect** (top right) -> **URI**.
5. Select **Session pooler** (recommended) or **Direct connection**.
6. Copy the connection string. Replace `[YOUR-PASSWORD]` with your actual database password. Keep this string private.

---

## Step 2: Push Your Code to GitHub

Ensure all your latest changes are pushed to GitHub:
```powershell
git status
git add .
git commit -m "Configure cloud deployment with Render and Supabase"
git push origin main
```
*(Never commit `.env`, `encryption.key`, or SQLite `.db` files)*

---

## Step 3: Deploy on Render

You can deploy using either **Option A (Render Blueprint - Easiest)** or **Option B (Manual Web Service)**.

### Option A: 1-Click Blueprint (Recommended)
1. Open [Render Dashboard](https://dashboard.render.com) and click **New > Blueprint**.
2. Select your `secure-qpaper-system` GitHub repository.
3. Render reads `render.yaml` automatically.
4. When prompted for environment variables:
   - **`DATABASE_URL`**: Paste your Supabase connection string.
   - **`ENCRYPTION_KEY`**: Generate one locally using:
     ```powershell
     python -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"
     ```
     Paste the generated string into `ENCRYPTION_KEY`.
5. Click **Apply**. Render will build and deploy your application automatically.

---

### Option B: Manual Web Service
1. Open [Render Dashboard](https://dashboard.render.com) and click **New > Web Service**.
2. Connect your `secure-qpaper-system` repository.
3. Configure the service settings:
   - **Name**: `secure-qpaper-system`
   - **Language / Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt -r requirements-cloud.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free`
4. Under **Environment Variables**, add:
   - `PYTHON_VERSION`: `3.11.9`
   - `DATABASE_URL`: `<your Supabase Session pooler connection string>`
   - `SECRET_KEY`: `<generate a random secret or leave Render to create one>`
   - `ENCRYPTION_KEY`: `<output of the Fernet key generator command above>`
   - `SESSION_COOKIE_SECURE`: `True`
   - `SESSION_COOKIE_HTTPONLY`: `True`
   - `SESSION_COOKIE_SAMESITE`: `Lax`
5. Click **Deploy Web Service**.

---

## Step 4: Verify Deployment and Initialize Users

1. Once the deploy succeeds, visit:
   `https://<your-service-name>.onrender.com/health`
   You should see:
   ```json
   {
     "status": "ok",
     "database": "cloud-postgresql",
     "database_connected": true
   }
   ```
2. The application automatically initializes tables and creates the default admin user:
   - **Username**: `admin`
   - **Password**: `admin@123`
3. To populate all standard demo roles (question setters, reviewers, officers) in your cloud database:
   - Temporarily set `DATABASE_URL=<your Supabase string>` in your local `.env` file.
   - Run locally:
     ```powershell
     python init_demo_users.py
     ```
   - All demo users will be inserted into your Supabase database and available immediately on your Render URL!

---

## Troubleshooting & Notes

- **Password encoding**: If Supabase connection fails with "FATAL: password authentication failed", check if your password contains `@` or special characters. URL-encode them or reset your password on Supabase to an alphanumeric one.
- **Supabase inactivity**: Supabase free projects pause after 1 week of inactivity. Unpause from the Supabase dashboard if needed.
- **Render free tier spin-down**: Render free web services sleep after 15 minutes of inactivity and take ~50 seconds to wake on the next request.
- **Persistent Encryption**: Always ensure `ENCRYPTION_KEY` is set in Render environment variables. This ensures previously uploaded files can always be decrypted even when Render restarts or redeploys.

