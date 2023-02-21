import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path
import os
import environ

env = environ.Env(
    DEBUG=(bool, False)
)

BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(env_file=os.path.join(BASE_DIR, '.env'))

# connect to PostgreSQL DBMS
# don't forget to change these in .env to your local postgres super admin credentials/postgres database management system
dbcon = None

try:
  dbcon = psycopg2.connect(f"user={env('PGDBMS_USER')} host={env('PGDBMS_HOST')} password={env('PGDBMS_PASS')} port={env('PGDBMS_PORT')}")
except:
  print("CRITICAL: Unable to connect to PostgreSQL DBMS")

if dbcon is not None:
  dbcon.autocommit = True
  dbcur = dbcon.cursor()
  dbcur.execute("SELECT datname FROM pg_database;")

  db_list = dbcur.fetchall()

  # check if ida_system user exists
  dbcur.execute("SELECT usename FROM pg_user;")
  user_list = dbcur.fetchall()

  if (env('DB_USER'),) in user_list:
    # does
    print(f"INFO: User {env('DB_USER')} already exists; make sure the password is the same as DB_PASS in the .env file")
  else:
    # doesnt; create ida_system superuser
    dbcur.execute(f"CREATE ROLE {env('DB_USER')} LOGIN SUPERUSER WITH ENCRYPTED PASSWORD {env('DB_PASS')};")
    print(f"INFO: User {env('DB_USER')} created")

  # check if ida_db database exists
  if (env('DB_NAME'),) in db_list:
    # does
    print(f"INFO: Database {env('DB_NAME')} already exists")
    dbcon.close()
    exit()
  else:
    # doesnt; create ida_db database and set ida_system as owner
    dbcur.execute(f"CREATE DATABASE {env('DB_NAME')} OWNER {env('DB_USER')} ENCODING 'UTF8';")
    print(f"INFO: Database {env('DB_NAME')} created and {env('DB_USER')} set as owner")
  
  print(f"INFO: Database setup complete")
  dbcon.close()
else:
  print("CRITICAL: Unable to connect to PostgreSQL DBMS")
