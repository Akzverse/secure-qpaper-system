# Free cloud setup: Supabase + Render

Use this after the local app works. It is suitable for a small academic demonstration.

## A. Create the free cloud database

1. Open [Supabase](https://supabase.com/dashboard), sign in, then choose **New project**.
2. Select the **Free** plan, name the project `secure-qpaper-system`, choose a strong database password, and create it.
3. When ready, click **Connect** and copy the **Session pooler** connection string.
4. Replace `[YOUR-PASSWORD]` in that string with your database password. Keep the completed string private.

## B. Push to GitHub

Follow the GitHub instructions in the main README. Never upload `.env`, `encryption.key`, `venv`, or `instance/qpaper_system.db`.

## C. Deploy on Render

1. Open [Render](https://dashboard.render.com), sign in with GitHub, and select **New > Web Service**.
2. Select your `secure-qpaper-system` repository.
3. Enter:

   ```text
   Language: Python 3
   Build Command: pip install -r requirements.txt -r requirements-cloud.txt
   Start Command: gunicorn app:app
   Instance Type: Free
   ```

4. Under **Environment**, add:

   ```text
   DATABASE_URL=<your Supabase Session pooler connection string>
   SECRET_KEY=<a long random value>
   ENCRYPTION_KEY=<key generated in step 5>
   SESSION_COOKIE_SECURE=True
   SESSION_COOKIE_HTTPONLY=True
   SESSION_COOKIE_SAMESITE=Lax
   ```

5. Generate a Fernet key locally:

   ```powershell
   python -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"
   ```

   Paste its result into Render as `ENCRYPTION_KEY`. Never commit it.
6. Create the service, wait for deployment, then visit `https://your-render-url/health`. It should show `"status":"ok"` and `"database":"cloud-postgresql"`.
7. Register users through the deployed application, or run `python init_demo_users.py` once after temporarily using the same `DATABASE_URL` in a local `.env`.

## Free-plan limitations

- Supabase free projects pause after inactivity.
- Render free web services sleep after 15 minutes without traffic and may take about a minute to start again.
- Do not store real confidential question papers in this student deployment.
