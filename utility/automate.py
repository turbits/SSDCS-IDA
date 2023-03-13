import subprocess

# TODO: rewrite for Bottle/sqlite

# TODO: run db_setup

# TODO: run db_seed

# err_dbsetup = None
# err_djangosetup = None

# # run database setup
# try:
#     p = subprocess.run(['python', 'utility/database_setup.py'], shell=True)
# except Exception as e:
#     err_makemigrations = e

# print(f"ERROR: Database Setup failed\n{err_dbsetup}") if err_dbsetup is not None else print("INFO: Database Setup complete")

# # run django setup
# try:
#     p = subprocess.run(['python', 'utility/django_setup.py'], shell=True)
# except Exception as e:
#     err_makemigrations = e

# print(f"ERROR: Django Setup failed\n{err_djangosetup}") if err_djangosetup is not None else print("INFO: Django Setup complete")
