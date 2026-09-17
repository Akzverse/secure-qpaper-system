# Secure Management of Competitive Examination Question Papers

A Flask web application that protects examination papers before release. It provides role-based access control, encrypted storage, SHA-256 integrity checking, audit logs, and controlled release. It runs locally with SQLite or in the cloud with free Supabase PostgreSQL and Render hosting.

> Educational prototype only. Do not use it for real high-stakes examinations without a security review, real MFA, HTTPS, managed key storage, backups, and penetration testing.

## Features

- Four roles: Question Setter, Reviewer, Exam Officer, and Administrator
- Password hashing, session timeout, and role-based access control
- AES-256 encryption with HMAC-SHA-256 integrity protection for stored papers
- SHA-256 integrity verification before download
- Locked papers, time-checked approval/release workflow, and audit logging
- Cloud-ready environment configuration and `/health` endpoint

## Technologies

- Python 3.8+, Flask, SQLAlchemy, and Cryptography
- SQLite locally; PostgreSQL on Supabase for free cloud data
- Render free web service deployment

## Run locally

1. Open PowerShell in the project folder.
2. With standard Windows Python, run:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python init_demo_users.py
   python app.py
   ```

3. Open `http://127.0.0.1:5000`.

Tip: on Windows you can also double-click `run.bat`. If you use Git Bash/MSYS Python, use `source venv/bin/activate` instead of the Windows `Scripts` activation command.

If you uploaded papers using the older project version, start with a fresh test database before testing the new encryption format. Back up any files you need first, then delete only the ignored `instance/qpaper_system.db` file and run `python init_demo_users.py` again.

Demo accounts: `admin / admin@123`, `qs1 / password123`, `reviewer1 / password123`, and `officer1 / password123`.

## Free cloud deployment

Supabase provides a free PostgreSQL database and Render provides a free web service for small class demonstrations. These services sleep/pause when inactive, so do not store real confidential papers. Follow [CLOUD_SETUP.md](CLOUD_SETUP.md) for the click-by-click setup.

## Project structure

```text
app.py                 Flask application and database models
init_demo_users.py     Creates test accounts for every role
templates/             Web pages
requirements.txt       Python dependencies
requirements-cloud.txt PostgreSQL driver used only by the cloud deployment
.env.example           Safe configuration template
Procfile               Render start command
CLOUD_SETUP.md         Free cloud deployment instructions
docs/architecture.svg  Editable architecture diagram source
output/pdf/secure-qpaper-architecture.pdf  Ready-to-upload architecture PDF
SAMPLE_IO.md           More sample input/output cases
```

## Sample input and output

**Input:** A Question Setter uploads `Mathematics Final 2026.pdf`, subject `Mathematics`, with a future exam date.

**Output:** The dashboard shows the paper as `DRAFT`; encrypted bytes and a SHA-256 hash are saved. A pre-release download returns:

```json
{"error":"Question paper cannot be accessed before exam date"}
```

After review approval and Exam Officer release, an authorized user can download the integrity-verified file.

## Security notes

- Never commit `.env`, `encryption.key`, or any database containing real papers.
- In Render, set `SECRET_KEY` and `ENCRYPTION_KEY` as environment variables only.
- Change demo passwords before any demonstration.
- Use `SESSION_COOKIE_SECURE=True` on the HTTPS cloud deployment.

## Submission checklist

- [ ] Run the project and take a dashboard screenshot.
- [ ] Upload `output/pdf/secure-qpaper-architecture.pdf` as the architecture diagram.
- [ ] Push source files, `requirements.txt`, README, cloud guide, and diagram.
- [ ] Do **not** push `.env`, `encryption.key`, `venv`, or the local database.
