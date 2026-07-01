# Trillium School - Backend Setup Guide

This is a Django REST API backend for the Trillium School management system.

## Prerequisites

- Python 3.8+
- MySQL Server
- pip (Python package manager)

## Installation Steps

### 1. Create MySQL Database

```sql
CREATE DATABASE trillium_school;
CREATE USER 'school_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON trillium_school.* TO 'school_user'@'localhost';
FLUSH PRIVILEGES;
```

### 2. Set Up Python Virtual Environment

```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the `backend` directory (copy from `.env.example`):

```bash
copy .env.example .env
```

Edit `.env` and update the values:

```
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=trilliumschool.in,www.trilliumschool.in,localhost,127.0.0.1
LOGIN_ATTEMPT_LIMIT=5
LOGIN_ATTEMPT_LOCKOUT_MINUTES=15

DB_ENGINE=django.db.backends.mysql
DB_NAME=trillium_school
DB_USER=school_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

### 5. Run Database Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

The server will start at `http://localhost:8000`

## API Endpoints

### Authentication
- **POST** `/api/students/login/` - Student login

### Students
- **GET** `/api/students/` - List all students
- **POST** `/api/students/` - Create new student
- **GET** `/api/students/{id}/` - Get student details
- **PUT** `/api/students/{id}/` - Update student
- **DELETE** `/api/students/{id}/` - Delete student
- **POST** `/api/students/{id}/reset_password/` - Reset student password
- **GET** `/api/students/{id}/dashboard/` - Get student dashboard

### Fee Components
- **GET** `/api/fee-components/` - List fee components
- **POST** `/api/fee-components/` - Create fee component
- **PUT** `/api/fee-components/{id}/` - Update fee component
- **DELETE** `/api/fee-components/{id}/` - Delete fee component

### Student Fee Components
- **GET** `/api/student/{student_id}/fee-components/` - List student fee components
- **POST** `/api/student/{student_id}/fee-components/` - Add fee component to student
- **DELETE** `/api/student/{student_id}/fee-components/{id}/` - Remove fee component

### Fee Payments
- **GET** `/api/fee-payments/` - List all payments
- **POST** `/api/fee-payments/` - Record new payment
- **GET** `/api/fee-payments/student_payments/?student_id={id}` - Get student payment history

### Notices
- **GET** `/api/notices/` - List all notices
- **POST** `/api/notices/` - Create new notice
- **PUT** `/api/notices/{id}/` - Update notice
- **DELETE** `/api/notices/{id}/` - Delete notice
- **GET** `/api/notices/latest/?limit=5` - Get latest notices

## Admin Panel

Access Django admin panel at `http://localhost:8000/admin/`

Login with the superuser credentials created during setup.

## Frontend Integration

Update your `trillium_school.html` to use the API endpoints instead of local storage:

1. Replace all `localStorage` calls with API calls
2. Update the `API_BASE_URL` in the HTML file
3. Implement proper error handling and loading states

Example API call:

```javascript
const API_BASE_URL = 'http://localhost:8000/api';

async function getStudents() {
    const response = await fetch(`${API_BASE_URL}/students/`);
    const data = await response.json();
    return data;
}

async function loginStudent(studentId, password) {
    const response = await fetch(`${API_BASE_URL}/students/login/`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({student_id: studentId, password: password})
    });
    return await response.json();
}
```

## Security Hardening Checklist

- Restrict ALLOWED_HOSTS to the production domain names.
- Keep CSRF enabled and trust only your production origins.
- Enforce passwords with 10-12 characters, uppercase/lowercase, numbers, and special characters.
- Limit login attempts to 5 failures and lock the account for 15 minutes.
- Store session cookies securely with HttpOnly and Secure flags.
- Schedule daily backups, weekly full backups, and monthly archives in a separate storage location.
- Run Django behind Nginx and Gunicorn with systemd to restart automatically after crashes.

## Backup Strategy

Suggested schedule:
- Daily backup of database and media files
- Weekly full backup
- Monthly archive stored off-site or in a separate cloud bucket

## Deployment Notes

Use Nginx as a reverse proxy, Gunicorn as the application server, and systemd to ensure automatic restarts after failures.

## Troubleshooting

### MySQL Connection Error
- Ensure MySQL server is running
- Check database credentials in `.env`
- Verify database exists

### Port Already in Use
```bash
python manage.py runserver 8001
```

### Module Not Found
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## Development Notes

- All dates should be in YYYY-MM-DD format
- Amounts are stored as Decimal with 2 decimal places
- Student IDs are auto-generated as STU{5-digit-number}
- Passwords are auto-generated as random 12-character strings

## Next Steps

1. Update frontend HTML to use API endpoints
2. Test all endpoints in Postman or similar tool
3. Deploy to production server
4. Configure SSL/HTTPS for production
