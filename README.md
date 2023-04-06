# Team Transparency - IDA

***⚠️ This is a university course prototype project; do not use this in any production environment. ⚠️***

## 🖥️What is IDA?

IDA, or ISS Data Archive, is a secure repository software that offers secure storage and access to information. Encrypted information is processed, decrypted on-premises, and stored in a secure local database. Authenticated users can access and optionally manipulate the data via a locally hosted web interface.

## 🤝What is Team Transparency?

Team Transparency is a group of students in the _University of Essex Online - Secure Software Development (PCOM7E January 2023)_ course.

## 👋What is the purpose of this repository?

This repository is used to store the code for the IDA project. For a full list of project technologies used, see the [Dependencies](#🗃️dependencies) section.

## 🤔How to set up the project

For MacOS: Python 2.7 might be installed by default, make sure you're running Python 3.11+ (`python --version` in terminal)

For Windows: use Powershell or Git Bash to run commands (not CMD)

- Ensure [prerequisites](#❗prerequisites) are done
- See [Run the project](#🏃‍♂️run-the-project)
- For issues running the project see [Issues](#😡issues)

## ❗Prerequisites

- Install [Python 3](https://www.python.org/downloads/), version 3.11.2 or higher, ensure it is added to your PATH (MacOS might have issues with this, might need to do some research)
- You should be linting your project with flake8 in your IDE
  - You can ignore E501 (line too long), or if using vscode: suppress it in vscode by adding this to settings: `"flake8.args": ["--ignore=E501"],`
- Restart your terminal (so PATH changes take effect)
- Git clone this repository and navigate to the project root
- Install virtualenv: `pip install virtualenv==20.19.0`
- Install pipenv: `pip install pipenv==2023.2.18`

## 🏃‍♂️Run the project

- Run the following to enter the virtual env (run this in the project root): `pipenv shell`
- Install all required packages from the Pipfile (run this in the project root): `pipenv install`
- If you don't have a database file (ida.db in project root), run `python database.py` to create one.
  - **NOTE: If you have one and you run this, it will overwrite it with default values.**
  - Use a SQLite viewer like [SQLiteStudio](https://sqlitestudio.pl/)(Windows) or [DB Browser for SQLite](https://sqlitebrowser.org/)(All platforms) to view the database.
- Run `python ida.py` to start the IDA app
- Access the web interface at `http://localhost:8080/`
- Run `python iss.py` to start the ISS app; this serves as a mock ISS. It runs on port 8081 and sends a POST request to `IDA/records` to create a new record every 3 seconds.
- ~~See the API documentation at `http://localhost:8080/api`~~ do this later if there's time; for now look at `/routes`

## 👀 Features

- Sessions; a uuid and a username are stored as cookies. When endpoints require authentication, the uuid is checked against the database to see if it's valid. If it is, the user is authenticated. This is also how users are checked if they are admin.
- Login/logout
- Dashboard to view records
- ISS microservice that generates and sends a "data file" to the IDA /records CREATE endpoint every 3 seconds

## ⚠️ Unimplemented Features

Keep in mind that this is very much a prototype and is not production ready, and could be improved in many ways. Some of these improvements are listed below.

- Production ready webserver or framework; would use something more tried and tested such as Django/PostgreSQL
- Editing of database items (users, records, etc) via the UI
- Efficient database queries; currently, the database is queried for every single record, and then the results are filtered in Python. This is inefficient and should be done in the database.
- More robust error handling
- More secure session handling and authentication
- More secure validation
- Securing configuration variables; Fernet key is in plaintext in the code. This is not secure and should be stored in a secure location, such as a .env file.
- More secure database; currently, the database is stored in plaintext. This is not secure and should be encrypted.
- More secure encryption; currently, the encryption is done with a Fernet key. This is not secure and should be replaced with a more secure encryption method.
- Password hashing; currently passwords are stored in plaintext, they should be hashed/salted, encypted when being communicated, etc.
- Many, many more

## 🗃️Dependencies

| Software                                                  | Version        |
| --------------------------------------------------------- | -------------- |
| Python                                                    | 3.11.2         |
| Bottle (micro web framework and web server)               | 0.12.25        |
| sqlite3 (database)                                        | 3.39.x         |
| pip (python package installer)                            | 22.3.1, 23.0.1 |
| virtualenv (lib - virtual Python environment builder)     | 20.19.0        |
| pipenv (lib - Python dependency management)               | 2023.2.18      |
| cryptography (lib - cryptographic recipes and primitives) | 39.0.1         |
| requests (lib - 'Python HTTP for Humans')                 | 2.28.2         |

## 📖Reading Material

- [Bottle Templating](https://bottlepy.org/docs/stable/stpl.html)
- [pipenv Basics](https://pipenv-fork.readthedocs.io/en/latest/basics.html)
- [Microservices](https://microservices.io/)

## 🔠Fonts

['Tilt Warp' Font (display)](https://fonts.google.com/specimen/Tilt+Warp)

['Inter' Font (text)](https://fonts.google.com/specimen/Inter)

## 😡Issues

**Commands aren't working correctly or at all**:

- make sure you're using Powershell or Git Bash on Windows
- make sure you're using Python 3.11 or higher

**ModuleNotFoundError: No module named 'bottle'**:

- make sure you're running the project in the virtual environment - run `pipenv shell` in the root of the project

## 📝Code References

- Nadalin, A. (2018) Web Security: How to Harden your HTTP cookies. Available at: [https://www.freecodecamp.org/news/web-security-hardening-http-cookies-be8d8d8016e1/](https://www.freecodecamp.org/news/web-security-hardening-http-cookies-be8d8d8016e1/) [Accessed 28 March 2023]
