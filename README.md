### Hexlet tests and linter status:
[![Actions Status](https://github.com/Un1que11/python-project-83/workflows/hexlet-check/badge.svg)](https://github.com/Un1que11/python-project-83/actions)
[![project-check](https://github.com/Un1que11/python-project-83/actions/workflows/project-check.yml/badge.svg)](https://github.com/Un1que11/python-project-83/actions/workflows/project-check.yml)
[![Maintainability](https://api.codeclimate.com/v1/badges/b13557f2ce35f1b9af90/maintainability)](https://codeclimate.com/github/Un1que11/python-project-83/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/b13557f2ce35f1b9af90/test_coverage)](https://codeclimate.com/github/Un1que11/python-project-83/test_coverage)

# Page-analyzer
## Description:
A web application that execute requests over the network and stores data in a database. 
## Dependencies:
* Python 3.8
* Flask 2.2.2
* PostgreSQL 14.5
* Bootstrap 5.2.3

## Installation:
Use the package manager pip:

    pip install --user git+https://github.com/Un1que11/python-project-83.git
### Or
Clone repository and use poetry:

        git clone https://github.com/Un1que11/python-project-83.git
        cd python-project-83
        make build
        make install
1. Create PostgreSQL database with cheatsheet (database.sql)
2. Create .env file and add variables or add them straight into your environment with export

         DATABASE_URL={provider}://{user}:{password}@{host}:{port}/{db}

         SECRET_KEY='secret_key'
3. Run make dev for debugging (WSGI debug='True'), or make start for production (gunicorn)