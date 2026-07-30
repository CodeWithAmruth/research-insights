# ========================
# Environment selection
# ========================
# Load single .env file
ifneq (,$(wildcard .env))
include .env
export
endif


# ========================
# Base Settings
# ========================
BASE_DIR := $(shell pwd)

VENV ?= venv
PY=$(VENV)/bin/python
ACTIVATE=. $(VENV)/bin/activate

# ========================
# Deployment Settings
# ========================
DOMAIN ?= localhost
SERVER_ALIAS=
ADMIN_EMAIL=admin@localhost
PORT ?= 
SITE_NAME ?= erp
VENV_PATH=$(BASE_DIR)/$(VENV)

# ========================
# Django Dev Settings
# ========================
HOST=0.0.0.0




#? For deploying run `make deploy`

outdated:
	@echo "Checking for outdated packages ..."
	@bash -c '$(ACTIVATE) && \
	pip list --outdated'

create_venv:
	@echo "Creating virtual environment ..."
	@bash -c 'python -m venv $(VENV)'

install_packages:
	@echo "Installing packages ..."
	@bash -c '$(ACTIVATE) && \
	pip install -r requirements.txt'

install_packages_and_freeze:
	@echo "Installing packages and freezing dependencies ..."
	@bash -c '$(ACTIVATE) && \
	pip install -r requirements.txt && \
	pip freeze > requirements.txt'

freeze:
	@echo "Freezing dependencies..."
	@bash -c '$(ACTIVATE) && pip freeze > requirements.txt'

run:
	@echo "Starting Django server on $(HOST):$(PORT)..."
	@bash -c '$(ACTIVATE) && $(PY) manage.py runserver $(HOST):$(PORT)'


tailwind:
	@echo "Starting Tailwind ..."
	@bash -c '$(ACTIVATE) && $(PY) manage.py tailwind start'

tailwind-build:
	@echo "Starting Tailwind ..."
	@bash -c '$(ACTIVATE) && $(PY) manage.py tailwind build'

makemigrations:
	@echo "Making migrations ..."
	@bash -c '$(ACTIVATE) && $(PY) manage.py makemigrations'

migrate:
	@echo "Migrating ..."
	@bash -c '$(ACTIVATE) && $(PY) manage.py migrate'



showmigrations:
	@echo "Showing migrations ..."
	@bash -c '$(ACTIVATE) && $(PY) manage.py showmigrations'

superuser:
	@echo "Creating superuser ..."
	@bash -c '$(ACTIVATE) && $(PY) manage.py createsuperuser'

shell:
	@echo "Starting Django shell ..."
	@bash -c '$(ACTIVATE) && $(PY) manage.py shell'

test:
	@echo "Running tests ..."
	@bash -c '$(ACTIVATE) && $(PY) manage.py test'

test-v2:
	@echo "Running tests with pytest ..."
	@bash -c '$(ACTIVATE) && $(PY) manage.py test -v 2'

dev-all:
	@echo "Starting Django + Tailwind..."
	@bash -c '$(ACTIVATE) && \
	$(PY) manage.py tailwind start & \
	$(PY) manage.py runserver $(HOST):$(PORT)

collectstatic:
	@bash -c '$(ACTIVATE) && $(PY) manage.py collectstatic --noinput'


cron_add:
	@echo "Adding cron jobs..."
	@bash -c '$(ACTIVATE) && $(PY) manage.py crontab add'

cron_remove:
	@echo "Removing cron jobs..."
	@bash -c '$(ACTIVATE) && $(PY) manage.py crontab remove'

cron_show:
	@echo "Showing cron jobs..."	
	@bash -c '$(ACTIVATE) && $(PY) manage.py crontab show'


conf:
	@echo "Generating Apache config file..."
	@DOMAIN=$(DOMAIN) \
	SERVER_ALIAS=$(SERVER_ALIAS) \
	ADMIN_EMAIL=$(ADMIN_EMAIL) \
	PORT=$(PORT) \
	VENV_PATH=$(VENV_PATH) \
	$(PY) generate_apache_conf.py

ensure_port:
	@if [ -n "$(PORT)" ]; then \
		grep -q "Listen $(PORT)" /etc/apache2/ports.conf || \
		echo "Listen $(PORT)" | sudo tee -a /etc/apache2/ports.conf; \
	fi


deploy-server: tailwind-build collectstatic conf ensure_port
	@echo "Syncing Apache config..."
	@sudo rsync -av $(SITE_NAME)_core_$(PORT).conf /etc/apache2/sites-available/
	@sudo a2ensite $(SITE_NAME)_core_$(PORT).conf
	@sudo systemctl restart apache2
	@echo "Deployment complete 🚀"

