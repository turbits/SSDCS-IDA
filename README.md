# Team Transparency - IDA

***⚠️ DISCLAIMER ⚠️***

***This is a university course prototype project! Do not use this in any production environment.***

You will see several security flaws, and possibly many lax design choices. This is not a production ready project, and is not intended to be used in any production environment. The .env file is included here for ease of use; this is not secure and should never be done in a production environment.

## 🖥️ What is IDA?

IDA, or ISS Data Archive, is a secure repository software that offers secure storage and access to information. Encrypted information is processed, decrypted on-premises, and stored in a secure local database. Authenticated users can access and optionally manipulate the data via a locally hosted web interface.

## 🤝 What is Team Transparency?

Team Transparency is a group of students in the _University of Essex Online - Secure Software Development (PCOM7E January 2023)_ course.

## 👋 What is the purpose of this repository?

This repository is used to store the code for the IDA project. For a full list of project technologies used, see the [Dependencies](#🗃️dependencies) section.

## 🤔 How to set up the project

For MacOS: Python 2.7 might be installed by default, make sure you're running Python 3.11+ (`python --version` in terminal)

For Windows: use Powershell or Git Bash to run commands (not CMD)

- Ensure [prerequisites](#❗prerequisites) are done
- See [Run the project](#🏃‍♂️run-the-project)
- For issues running the project see [Issues](#😡issues)

## ❗ Prerequisites

- Install [Python 3](https://www.python.org/downloads/), version 3.11.2 or higher, ensure it is added to your PATH (MacOS might have issues with this, might need to do some research)
- You should be linting your project with flake8 in your IDE
  - You can ignore E501 (line too long), or if using vscode: suppress it in vscode by adding this to settings: `"flake8.args": ["--ignore=E501"],`
- Restart your terminal (so PATH changes take effect)
- Git clone this repository and navigate to the project root
- Install virtualenv: `pip install virtualenv==20.19.0`
- Set up a virtual environment (run in project root): `py -3 venv venv` on Windows, and `python3 -m venv venv` on Linux/MacOS
- Activate the virtual environment. This can be a bit tedious in Windows, unfortunately.:
  - Windows (PowerShell): change directory to the `./venv/Scripts` folder, then run `. activate` - do not forget the space after the dot
  - Linux/MacOS/Windows(GitBash): run `source ./venv/bin/activate`
  - This should then show `(venv)` as an output in your terminal. If it doesn't, you are not in the virtual environment.
  - You can check by running `deactivate`; if it returns without an error, you were in the virtual env (so just run activate again to get back in)
  - For Windows, you may also have to run `Set-ExecutionPolicy Unrestricted` in an admin PowerShell session if you get an error about scripts being disabled on this system.
- Run `pip install -r requirements.txt` to install all required packages and dependencies
- That's it! Proceed to Run the Project below

## 🏃‍♂️ Run the project

- Ensure you're in the virtual environment; usually `source ./venv/Scripts/activate`, otherwise see prerequisites above
- Install all required packages as listed in the prerequisites section
- Run `python database.py` to create and seed the default database
  - **NOTE: If you have one and you run this, it will overwrite it with default values.**
  - Use a SQLite viewer like [SQLiteStudio](https://sqlitestudio.pl/)(Windows) or [DB Browser for SQLite](https://sqlitebrowser.org/)(All platforms) for a visual view of the database
- Run `python ida/ida.py` to start the IDA app
- Access the web interface at `http://127.0.0.1:8080/`
- Open a new terminal window and activate the virtual environment in this window as well, `source ./venv/Scripts/activate`
- Run `python iss/iss.py` in the new window to start the ISS microservice; this serves as a mock ISS. It runs on 127.0.0.1, port 8081, and sends a POST request to `IDA/records` to create a new record every 10 seconds.

## 👀 Features

- Sessions; a uuid and a username are stored as cookies. When endpoints require authentication or authorization, the uuid is checked against the database to see if it's valid. If it is, the user is authenticated/authorized.
- Endpoint authorization; see previous
- Login/logout
- Dashboard to view records
- ISS microservice that generates and sends a "data file" to the IDA /records CREATE endpoint every 10 seconds

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

## 🗃️ Packages/Dependencies

| Software                                                  | Version        |
| --------------------------------------------------------- | -------------- |
| Python                                                    | 3.11.2         |
| Flask (micro web framework and web server)               | 2.2.3        |
| sqlite3 (database)                                        | 3.39.x         |
| pip (python package installer)                            | 22.3.1, 23.0.1 |
| virtualenv (lib - virtual Python environment builder)     | 20.19.0        |
| pipenv (lib - Python dependency management)               | 2023.2.18      |
| cryptography (lib - cryptographic recipes and primitives) | 39.0.1         |
| requests (lib - 'Python HTTP for Humans')                 | 2.28.2         |

## 📖 Reading Material

- [Bottle Templating](https://bottlepy.org/docs/stable/stpl.html)
- [pipenv Basics](https://pipenv-fork.readthedocs.io/en/latest/basics.html)
- [Microservices](https://microservices.io/)

## 🔠 Fonts

['Tilt Warp' Font (display)](https://fonts.google.com/specimen/Tilt+Warp)

['Inter' Font (text)](https://fonts.google.com/specimen/Inter)

## 😡 Issues

**Commands aren't working correctly or at all**:

- make sure you're using Powershell or Git Bash on Windows
- make sure you're using Python 3.11 or higher

**ModuleNotFoundError: No module named 'flask'**:

- make sure you're running the project in the virtual environment - run `source ./venv/Scripts/activate` in the root of the project; different if using PowerShell - see Prerequisites section

**Windows: something about running scripts being disabled on this system**:

- run `Set-ExecutionPolicy Unrestricted` in an admin PowerShell session and try again (might have to restart terminal)



## 📝 Code References

- Nadalin, A. (2018) Web Security: How to Harden your HTTP cookies. Available at: [https://www.freecodecamp.org/news/web-security-hardening-http-cookies-be8d8d8016e1/](https://www.freecodecamp.org/news/web-security-hardening-http-cookies-be8d8d8016e1/) [Accessed 28 March 2023]
