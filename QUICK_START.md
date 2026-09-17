# Quick Start Guide - 5 Hour Sprint

## ⏱️ Timeline: 5 Hours Total

### Phase 1: Local Setup (30 mins)
### Phase 2: Testing (30 mins)
### Phase 3: GitHub Push (30 mins)
### Phase 4: AWS Deployment (1.5 hours) - Optional
### Phase 5: Final Check & Buffer (1 hour)

---

## Phase 1: Local Setup (30 Minutes)

### On Windows:
```bash
# 1. Open Command Prompt in project folder
# 2. Run this single command:
run.bat
```

### On macOS/Linux:
```bash
# 1. Open Terminal in project folder
# 2. Make script executable:
chmod +x run.sh

# 3. Run this single command:
./run.sh
```

**What it does:**
- Creates virtual environment
- Installs all dependencies
- Initializes database
- Creates demo users
- Starts the app at http://localhost:5000

---

## Phase 2: Testing Application (30 Minutes)

### Test All User Roles:

**1. Admin (Approx 5 mins)**
```
Login: admin / admin@123
Do: Click "Users" → See all users
Do: Click "Audit Logs" → See all activities
```

**2. Question Setter (Approx 10 mins)**
```
Login: qs1 / password123
Do: Click "Upload" 
Do: Fill:
    - Title: Math Final 2026
    - Subject: Mathematics
    - Exam Date: 2026-10-15 14:00 (future date!)
    - File: Any PDF (create a dummy if needed)
Do: Click Upload
Do: Back to dashboard, should see paper in DRAFT status
```

**3. Reviewer (Approx 7 mins)**
```
Login: reviewer1 / password123
Do: Dashboard shows uploaded paper
Do: Click "Approve" button
Do: Return to see status changed to APPROVED
```

**4. Exam Officer (Approx 8 mins)**
```
Login: officer1 / password123
Do: Dashboard shows only APPROVED papers
Do: Can see "Release" button (releases after exam date/time)
Do: Note: Can't download yet (before exam date)
```

---

## Phase 3: GitHub Push (30 Minutes)

### Step 1: Create GitHub Repo (5 mins)
```bash
1. Go to https://github.com/new
2. Create repo: secure-qpaper-system
3. DON'T add README (we have one)
4. Click Create Repository
5. Copy the HTTPS URL
```

### Step 2: Configure Git Locally (10 mins)
```bash
# In project folder:
git init
git add .
git commit -m "Initial commit: Secure Question Paper Management System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/secure-qpaper-system.git
git push -u origin main
```

### Step 3: Verify Upload (5 mins)
```bash
1. Go to your GitHub repo page
2. Refresh
3. See all files uploaded ✓
```

### Step 4: Get Repository Link
```bash
Copy this URL: https://github.com/YOUR_USERNAME/secure-qpaper-system
This is what you submit to the Google Form!
```

---

## Phase 4: Fill Google Form Submission (10 Minutes)

```
Register Number: 2403717610422070
Name: Akshaya A
Project Title: Secure Cloud-Based Question Paper Management System

GitHub Repository Link: https://github.com/YOUR_USERNAME/secure-qpaper-system

Technologies/Tools Used:
Python 3.8+, Flask 2.3.3, SQLAlchemy, Cryptography (AES-256), 
SHA-256 Hashing, SQLite/PostgreSQL, AWS S3 (optional)

Checklist:
☑ GitHub repo contains complete source code
☑ README.md with project description and setup instructions
☑ requirements.txt with all dependencies
☑ All HTML templates in templates/ folder
☑ Sample input/output documentation (in README)
☑ Code quality: Modular, well-commented, follows best practices
☑ Security: Encryption, RBAC, Audit Logging implemented
☑ Database: Models and migrations included
```

---

## Phase 5: AWS Deployment (Optional - 1.5 Hours)

### Skip if time is running out!

If you have extra time and want to deploy to AWS:

```bash
# 1. Create AWS account (free tier)
# 2. Create EC2 instance (Ubuntu 20.04)
# 3. SSH into instance
# 4. Clone repo:
git clone https://github.com/YOUR_USERNAME/secure-qpaper-system.git
cd secure-qpaper-system

# 5. Install Python:
sudo apt update && sudo apt install python3-pip python3-venv

# 6. Setup and run:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_demo_users.py

# 7. Install Gunicorn:
pip install gunicorn

# 8. Run in production:
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 9. Note the public IP from AWS console
# Application will be at: http://your-public-ip:5000
```

---

## Important Files for Submission

### MUST HAVE:
✓ `app.py` - Main application  
✓ `requirements.txt` - Dependencies  
✓ `README.md` - Complete documentation  
✓ `templates/` - All HTML files  
✓ `.gitignore` - Don't commit secrets  
✓ `.env.example` - Config template  

### AUTOMATICALLY CREATED:
- `encryption.key` - Generated on first run
- `qpaper_system.db` - Database created on first run
- `venv/` - Virtual environment (not pushed to GitHub)

---

## Evaluation Checklist (20 Marks)

### ✓ Functionality (10 Marks)
- User registration and login
- Upload and encrypt question papers
- Role-based access control (4 roles)
- Time-based release (can't access before exam date)
- Integrity verification (SHA-256)
- Audit logging (all actions)
- Download/view encrypted papers

### ✓ Documentation (5 Marks)
- README.md with all sections
- Architecture diagram (in README)
- Code comments
- Setup instructions
- Sample input/output

### ✓ Code Quality (5 Marks)
- Modular code structure
- Database models properly designed
- Security best practices
- Error handling
- Input validation

---

## Troubleshooting Quick Fixes

**App won't start?**
```bash
# Check Python version
python --version  # Should be 3.8+

# Force reinstall dependencies
pip install --upgrade -r requirements.txt

# Delete old database and try again
rm qpaper_system.db
python app.py
```

**Can't login?**
```bash
# Reinitialize demo users
python init_demo_users.py
```

**Port 5000 in use?**
```bash
# Change port in app.py last line:
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Git push failed?**
```bash
# Check remote
git remote -v

# Update remote if wrong
git remote set-url origin https://github.com/YOUR_USERNAME/secure-qpaper-system.git

# Try again
git push -u origin main
```

---

## Final Checklist Before Submission

### Local Testing ✓
- [ ] App starts without errors
- [ ] Can login as admin
- [ ] Can register new user
- [ ] Can upload question paper
- [ ] Can approve/release paper
- [ ] Can view audit logs
- [ ] All 4 roles work

### GitHub ✓
- [ ] Repository created
- [ ] All files pushed
- [ ] .gitignore prevents secret commits
- [ ] README is clear and complete
- [ ] No sensitive data in repo

### Form Submission ✓
- [ ] Roll number: 2403717610422070
- [ ] Name: Akshaya A
- [ ] GitHub link copied correctly
- [ ] Project title matches
- [ ] All fields filled
- [ ] Checkbox marked: "Code quality includes security features"

---

## Support

If you get stuck:
1. Check README.md troubleshooting section
2. Verify all files are in correct folders
3. Ensure requirements.txt is installed completely
4. Check if Python path is set correctly

Good luck! 🚀

---

**Submitted by:** Akshaya A (2403717610422070)  
**Date:** 2026-09-17  
**Time Spent:** ~5 hours  
