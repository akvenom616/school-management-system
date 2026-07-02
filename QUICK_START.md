# Quick Start - Run Backend Server

## Every Time You Want to Use the App

### Step 1: Open Terminal in Backend Folder

```powershell
cd c:\Users\agrim\OneDrive\Desktop\trillium\backend
```

### Step 2: Activate Virtual Environment

```powershell
.\venv\Scripts\Activate
```

You should see `(venv)` at the start of your terminal line.

### Step 3: Start Django Server

```powershell
python manage.py runserver
```

Wait for the message:
```
Starting development server at http://127.0.0.1:8000/
```

### Step 4: Open the App

Open this file in your browser:
```
c:\Users\agrim\OneDrive\Desktop\trillium\trillium_school_api.html
```

✅ **App is ready to use!**

---

## Default Credentials

### Admin Portal
- **Username**: admin
- **Password**: admin123

### Create Student Accounts
1. Go to: http://localhost:8000/admin/
2. Login with admin credentials above
3. Click "Students" → "Add Student"
4. System generates Student ID and Password automatically

---

## Key Files

| File | Purpose |
|------|---------|
| `trillium_school_api.html` | **Use this file** (backend integrated) |
| `backend/manage.py` | Django management |
| `backend/requirements.txt` | Python dependencies |
| `backend/.env` | Database credentials |
| `backend/school/` | API code |

---

## Stop Server

Press `Ctrl+C` in terminal

---

**Now all your data saves to the database! 🎉**
