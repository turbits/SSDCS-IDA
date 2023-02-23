# Team Transparency - IDA

## What is IDA?

IDA, or ISS Data Archive, is a secure repository software that offers secure storage and access to information. Encrypted information is processed, decrypted on-premises, and stored in a secure local database. Authenticated users can access and optionally manipulate the data via a locally hosted web interface.

## What is Team Transparency?

Team Transparency is a group of students in the _University of Essex Online - Secure Software Development (PCOM7E January 2023)_ course.

## What is the purpose of this repository?

This repository is used to store the code for the IDA project. For a full list of project technologies used, see the [Dependencies](#dependencies) section.

## How to run the project locally

[I'm having issues running the project or installing packages](#issues-with-project)

These steps use Unix-style commands. These commands will generally work on Linux and MacOS without issue. For Windows, you must use either Powershell or Git Bash, alternatively install and use [Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/install).

**CMD will not work.**

For MacOS specifically, Python 2.7 is installed by default. Python 3 may take a bit of effort to install, or you may specifically have to use `python3`, `pip3`, etc., for commands. If you have issues with installing Python 3 on MacOS please search online for guides/documentation.

### Prerequisites

- Install [PostgreSQL 15.2](https://www.postgresql.org/download/) or higher, ensure it is added to your PATH
- Install [Python 3](https://www.python.org/downloads/), version 3.11.2 or higher, ensure it is added to your PATH
- Restart your terminal (so PATH changes take effect)
- Git clone this repository and navigate to the project root
- Install virtualenv: `pip install virtualenv==20.19.0`
- Install pipenv: `pip install pipenv==2023.2.18`
- Run the following to enter the virtual env (run this in the project root): `pipenv shell`
- Install all required packages from the Pipfile (run this in the project root): `pipenv install`
- Add the `.env` file provided to you to the root of the project
  - **IMPORTANT**: add your local PostgreSQL superuser credentials to the `.env` file; the default is `postgres` for username, and password is whatever it was set to during/after installation
- TODO: write steps to set up the database and users (or automate it)
- Run the following command to start the server:
  - `pipenv run python manage.py runserver`
- Access the web interface at `http://localhost:8000/`

# Dependencies

| Software                                                  | Version        |
| --------------------------------------------------------- | -------------- |
| Python                                                    | 3.11.2         |
| Django (web framework and basic server)                   | 4.1.7          |
| PostgreSQL (database)                                     | 15.2           |
| pip (python package installer)                            | 22.3.1, 23.0.1 |
| virtualenv (lib - virtual Python environment builder)     | 20.19.0        |
| pipenv (lib - Python dependency management)               | 2023.2.18      |
| django-environ (lib - for secure .env)                    | 0.9.0          |
| psycopg2 (lib - PostgreSQL database adapter for Python)   | 2.9.5          |
| cryptography (lib - cryptographic recipes and primitives) | 39.0.1         |

# Reading Material

- [pipenv Basics](https://pipenv-fork.readthedocs.io/en/latest/basics.html)
- [Microservices](https://microservices.io/)
- [Django Docs](https://docs.djangoproject.com/en/4.1/)

# PostgreSQL Commands

- `psql -U postgres` - from a command line; connect to psql interface as the superuser

## psql Commands

SQL commands must end with a semicolon. Pressing enter without a semicolon will add a new line to the command instead of executing it.

- `\l` - list all databases
  - `SELECT datname FROM pg_database;` - equivalent SQL command
- `\c <database>` - connect to a database
  - `USE <database>;` - equivalent SQL command
- `\dt` - list all tables in the current database
  - `SELECT * FROM pg_catalog.pg_tables;` - equivalent SQL command
- `\d <table>` - 'describe' a table, i.e., list all columns in a table
- `\d+ <table>` - 'describe' a table, i.e., list all columns in a table, and extra data
- `\du` - list all roles (users)
  - `SELECT * FROM pg_roles;` - equivalent SQL command
- `\du <role>` - list all roles (users) matching the given pattern
- `\q` - quit psql interface

## Issues With Project

If you have the project set up, it's very important that you are installing or uninstalling packages using `pipenv` instead of `pip`. This is because `pipenv` will automatically update the `Pipfile` and `Pipfile.lock` files, which are used to ensure that everyone has the same dependencies installed.

If you are running into issues, ensure you are in the pipenv shell: `pipenv shell` in the root directory.
