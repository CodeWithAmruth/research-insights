# Django Project Setup Guide

This project supports both **Linux/macOS** and **Windows**.

- **Linux/macOS** users can use the provided `Makefile`.
- **Windows** users can run the equivalent commands manually.

---

# Requirements

- Python 3.10+
- Git
- Node.js (LTS) and npm
- Python Virtual Environment (`venv`)
- Database (SQLite/PostgreSQL/MySQL depending on your project)

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

## 2. Install Python Dependencies

```bash
make install_packages
```

---

## 3. Install Tailwind Dependencies

Since `theme/static_src/node_modules` is removed/ignored by Git, install the Node packages after cloning:

```bash
make tailwind-install
```

---

## 4. Create `.env`

```bash
cp .env.example .env
```

Update the values according to your environment.

---

## 5. Apply Migrations

```bash
make migrate
```

---

## 6. Create Superuser

```bash
make superuser
```

---

## 7. Run Development Server

```bash
make run
```

---

## 8. Start Tailwind CSS

```bash
make tailwind
```

---

## 9. Run Django + Tailwind Together

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

## 2. Activate the Virtual Environment

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

## 3. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

---

## 4. Install Tailwind Dependencies

```powershell
python manage.py tailwind install
```

---

## 5. Create `.env`

Copy:

```
.env.example
```

to:

```
.env
```

and update the required values.

---

## 6. Apply Migrations

```powershell
python manage.py migrate
```

---

## 7. Create Superuser

```powershell
python manage.py createsuperuser
```

---

## 8. Start Django Server

```powershell
python manage.py runserver
```

---

## 9. Start Tailwind CSS

Open a second terminal:

```powershell
python manage.py tailwind start
```

---

# Common Commands

| Task                              | Linux/macOS             | Windows                                    |
| --------------------------------- | ----------------------- | ------------------------------------------ |
| Create Virtual Environment        | `make create_venv`      | `python -m venv venv`                      |
| Install Python Dependencies       | `make install_packages` | `pip install -r requirements.txt`          |
| **Install Tailwind Dependencies** | `make tailwind-install` | `python manage.py tailwind install`        |
| Freeze Requirements               | `make freeze`           | `pip freeze > requirements.txt`            |
| Run Server                        | `make run`              | `python manage.py runserver`               |
| Start Tailwind                    | `make tailwind`         | `python manage.py tailwind start`          |
| Build Tailwind                    | `make tailwind-build`   | `python manage.py tailwind build`          |
| Create Migrations                 | `make makemigrations`   | `python manage.py makemigrations`          |
| Apply Migrations                  | `make migrate`          | `python manage.py migrate`                 |
| Show Migrations                   | `make showmigrations`   | `python manage.py showmigrations`          |
| Create Superuser                  | `make superuser`        | `python manage.py createsuperuser`         |
| Django Shell                      | `make shell`            | `python manage.py shell`                   |
| Run Tests                         | `make test`             | `python manage.py test`                    |
| Verbose Tests                     | `make test-v2`          | `python manage.py test -v 2`               |
| Collect Static Files              | `make collectstatic`    | `python manage.py collectstatic --noinput` |
| Add Cron Jobs                     | `make cron_add`         | `python manage.py crontab add`             |
| Remove Cron Jobs                  | `make cron_remove`      | `python manage.py crontab remove`          |
| Show Cron Jobs                    | `make cron_show`        | `python manage.py crontab show`            |

---

# Deployment (Linux)

Generate the Apache configuration:

```bash
make conf DOMAIN=example.com PORT=8000 SITE_NAME=myproject
```

Deploy the application:

```bash
make deploy-server DOMAIN=example.com PORT=8000 SITE_NAME=myproject
```

This command will:

- Build Tailwind CSS
- Collect static files
- Generate the Apache configuration
- Enable the Apache site
- Restart Apache

---

# Notes

- `theme/static_src/node_modules` is ignored by Git and **must be installed after cloning** using `make tailwind-install` (Linux/macOS) or `python manage.py tailwind install` (Windows).
- Linux/macOS users are encouraged to use the provided `Makefile`.
- Windows users can run the equivalent Django commands manually.
- Run the Django server and Tailwind watcher in separate terminals during development.
- Before deploying, ensure `DEBUG=False` and your production settings are configured correctly.
