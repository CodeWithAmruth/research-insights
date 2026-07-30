# Django Project Setup Guide

This project supports both **Linux/macOS** and **Windows**.

- **Linux/macOS** users can use the provided `Makefile`.
- **Windows** users can run the equivalent commands manually.

---

# Requirements

- Python 3.10+
- Git
- Virtual Environment (`venv`)
- Node.js & npm (for Tailwind CSS)
- Database (SQLite/PostgreSQL/MySQL depending on your project)

---

# Clone the Repository

```bash
git clone <repository-url>
cd <project-folder>
```

---

# Linux / macOS

## 1. Create Virtual Environment

```bash
make create_venv
```

or

```bash
python3 -m venv venv
```

---

## 2. Install Dependencies

```bash
make install_packages
```

---

## 3. Create `.env`

Copy the sample environment file.

```bash
cp .env.example .env
```

Update the values according to your environment.

---

## 4. Apply Migrations

```bash
make migrate
```

---

## 5. Create Superuser

```bash
make superuser
```

---

## 6. Run Development Server

```bash
make run
```

---

## 7. Start Tailwind CSS

```bash
make tailwind
```

---

## 8. Run Django + Tailwind Together

```bash
make dev-all
```

---

# Windows

Windows does not include `make` by default, so run the equivalent commands manually.

---

## 1. Create Virtual Environment

```powershell
python -m venv venv
```

---

## 2. Activate Virtual Environment

### Command Prompt (CMD)

```cmd
venv\Scripts\activate
```

### PowerShell

```powershell
venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## 4. Create `.env`

Copy

```
.env.example
```

to

```
.env
```

and update the required values.

---

## 5. Apply Migrations

```powershell
python manage.py migrate
```

---

## 6. Create Superuser

```powershell
python manage.py createsuperuser
```

---

## 7. Start Django Server

```powershell
python manage.py runserver
```

---

## 8. Start Tailwind

Open a second terminal.

```powershell
python manage.py tailwind start
```

---

# Common Commands

| Task                       | Linux/macOS             | Windows                                    |
| -------------------------- | ----------------------- | ------------------------------------------ |
| Create Virtual Environment | `make create_venv`      | `python -m venv venv`                      |
| Install Dependencies       | `make install_packages` | `pip install -r requirements.txt`          |
| Freeze Requirements        | `make freeze`           | `pip freeze > requirements.txt`            |
| Run Server                 | `make run`              | `python manage.py runserver`               |
| Start Tailwind             | `make tailwind`         | `python manage.py tailwind start`          |
| Build Tailwind             | `make tailwind-build`   | `python manage.py tailwind build`          |
| Create Migrations          | `make makemigrations`   | `python manage.py makemigrations`          |
| Apply Migrations           | `make migrate`          | `python manage.py migrate`                 |
| Show Migrations            | `make showmigrations`   | `python manage.py showmigrations`          |
| Create Superuser           | `make superuser`        | `python manage.py createsuperuser`         |
| Django Shell               | `make shell`            | `python manage.py shell`                   |
| Run Tests                  | `make test`             | `python manage.py test`                    |
| Verbose Tests              | `make test-v2`          | `python manage.py test -v 2`               |
| Collect Static Files       | `make collectstatic`    | `python manage.py collectstatic --noinput` |
| Add Cron Jobs              | `make cron_add`         | `python manage.py crontab add`             |
| Remove Cron Jobs           | `make cron_remove`      | `python manage.py crontab remove`          |
| Show Cron Jobs             | `make cron_show`        | `python manage.py crontab show`            |

---

# Deployment (Linux)

The project includes helper commands for Apache deployment.

Generate Apache configuration:

```bash
make conf DOMAIN=example.com PORT=8000 SITE_NAME=myproject
```

Deploy:

```bash
make deploy-server DOMAIN=example.com PORT=8000 SITE_NAME=myproject
```

This will:

- Build Tailwind CSS
- Collect static files
- Generate Apache configuration
- Enable the site
- Restart Apache

---

# Notes

- Linux/macOS users are encouraged to use the provided `Makefile` for convenience.
- Windows users can execute the equivalent Python commands manually.
- Tailwind CSS should be run in a separate terminal during development.
- Before deploying, ensure `DEBUG=False` and configure production settings appropriately.
